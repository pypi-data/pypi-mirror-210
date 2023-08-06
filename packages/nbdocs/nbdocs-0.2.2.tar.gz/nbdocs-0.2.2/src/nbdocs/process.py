from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from nbconvert.exporters.exporter import ResourcesDict
from nbconvert.preprocessors.base import Preprocessor

from nbdocs.cfg_tools import NbDocsCfg
from nbdocs.typing import CellAndResources, CodeCell, MarkdownCell, Nb, Cell


if sys.version_info.minor < 9:  # pragma: no cover
    from typing import Pattern

    rePattern = Pattern[str]
else:
    rePattern = re.Pattern[str]

# Flags
# Flag is starts with #, at start of the line, no more symbols at this line except whitespaces.
HIDE = ["hide"]  # hide cell
HIDE_INPUT = ["hide_input"]  # hide code from this cell
HIDE_OUTPUT = ["hide_output"]  # hide output from this cell

HIDE_FLAGS = HIDE + HIDE_INPUT + HIDE_OUTPUT

FLAGS: list[str] = [] + HIDE_FLAGS  # here will be more flags.

COLLAPSE_OUTPUT = "collapse_output"


def generate_flags_string(flags: list[str]) -> str:
    """Generate re pattern from list of flags, add flags with '-' instead of '_'.

    Args:
        flags (List[str]): List of flags.

    Returns:
        str: flags, separated by '|'
    """
    result_flags = flags.copy()
    for item in flags:
        if "_" in item:
            result_flags.append(item.replace("_", "-"))
    return "|".join(result_flags)


def get_flags_re(flags: list[str]) -> rePattern:
    """Create Regex pattern from list of flags.

    Args:
        flags (List[str]): List of flags.

    Returns:
        re.Pattern: Regex pattern.
    """
    flag_string = generate_flags_string(flags)
    pattern = rf"^\s*\#\s*({flag_string})\s*$"
    return re.compile(pattern, re.M)


re_flags = get_flags_re(FLAGS)
re_hide = get_flags_re(HIDE)
re_hide_input = get_flags_re(HIDE_INPUT)
re_hide_output = get_flags_re(HIDE_OUTPUT)
re_collapse = get_flags_re([COLLAPSE_OUTPUT])


def cell_check_flags(cell: Cell) -> bool:
    """Check if cell has nbdocs flags.

    Args:
        cell (Cell): Cell to check.

    Returns:
        bool.
    """
    result = False
    if cell.cell_type == "code":
        result = re_flags.search(cell.source) is not None
    return result


def get_image_link_re(image_name: str = "") -> rePattern:
    """Return regex pattern for image link with given name. If no name - any image link.

    Args:
        image_name (str, optional): Name to find. Defaults to ''.

    Returns:
        re.Pattern: Regex pattern for image link.
    """
    if image_name == "":
        image_name = ".*"
    return re.compile(rf"(\!\[.*\])(\s*\(\s*)(?P<path>{image_name})(\s*\))", re.M)


def md_find_image_names(md: str) -> set[str]:
    """Return set of image name from internal mage links

    Args:
        md (str): Markdown str to find names.

    Returns:
        Set[str]: Set of image names
    """
    re_link = get_image_link_re()
    return set(
        path
        for match in re_link.finditer(md)
        if "http" not in (path := match.group("path"))
    )


def md_correct_image_link(md: str, image_name: str, image_path: str) -> str:
    """Change image link at markdown text from local source to image_path.

    Args:
        md (str): Markdown text to process.
        image_name (str): Name for image file.
        image_path (str): Dir name for images at destination.

    Returns:
        str: Text with changed links.
    """
    return re.sub(
        rf"(\!\[.*\])(\s*\(\s*){image_name}(\s*\))",
        rf"\1({image_path}/{image_name})",
        md,
    )


def copy_images(
    image_names: list[str], source: Path, dest: Path
) -> tuple[list[str], set[str]]:
    """Copy images from source to dest. Return list of copied and list of left.

    Args:
        image_names (List): List of names
        source (Path): PAth of source dir (parent)
        dest (Path): Destination path

    Returns:
        Tuple[List[str], List[str]]: _description_
    """
    set_image_names = set(image_names)
    done: list[str] = []
    files_to_copy = [
        Path(image_name)
        for image_name in set_image_names
        if (source / image_name).exists()
    ]
    if len(files_to_copy) > 0:
        dest.mkdir(exist_ok=True, parents=True)
        for fn in files_to_copy:
            shutil.copy(source / fn, dest / fn.name)
            done.append(str(fn))
    set_image_names.difference_update(done)
    return done, set_image_names


# check relative link (../../), ? can we correct links after converting
def cell_md_correct_image_link(cell: MarkdownCell, nb_fn: Path, cfg: NbDocsCfg) -> None:
    """Change image links at given markdown cell and copy linked image to image path at dest.

    Args:
        cell (Cell): Markdown cell to process.
    """
    image_names = md_find_image_names(cell.source)
    for image_name in image_names:
        image_fn = nb_fn.parent / image_name  # check relative path in link
        if image_fn.exists():
            # path for images
            dest_images = f"{cfg.images_path}/{nb_fn.stem}_files"
            (dest_path := Path(cfg.docs_path) / dest_images).mkdir(
                exist_ok=True, parents=True
            )
            # change link
            re_path = get_image_link_re(image_name)
            cell.source = re_path.sub(
                rf"\1({dest_images}/{image_fn.name})", cell.source
            )
            # copy source
            copy_name = dest_path / image_fn.name
            shutil.copy(image_fn, copy_name)
        else:
            print(f"Image source not exists! filename: {image_fn}")


def correct_markdown_image_link(nb: Nb, nb_fn: Path, cfg: NbDocsCfg):
    """Change image links at markdown cells and copy linked image to image path at dest.

    Args:
        nb (Notebook): Jupyter notebook to process.
        nb_fn (Path): Notebook filename.
        dest_path (Path): Destination for converted notebook.
        image_path (str): Path for images at destination.
    """
    for cell in nb.cells:
        if cell.cell_type == "markdown":  # look only at markdown cells
            cell_md_correct_image_link(cell, nb_fn, cfg)


class CorrectMdImageLinkPreprocessor(Preprocessor):
    """
    Change image links and copy image at markdown cells at given notebook.
    """

    def __init__(self, cfg: NbDocsCfg, **kw):
        super().__init__(**kw)
        self.cfg = cfg

    def preprocess_cell(
        self, cell: Cell, resources: ResourcesDict, index: int
    ) -> CellAndResources:
        """
        Apply a transformation on each cell. See base.py for details.
        """
        if cell.cell_type == "markdown":
            nb_fn: Path = resources.get("filename")
            cell_md_correct_image_link(cell, nb_fn, self.cfg)  # type: ignore
        return cell, resources


def cell_process_hide_flags(cell: CodeCell) -> None:
    """Process cell - remove input, output or both from markdown cell.

    Args:
        cell (Cell): Notebook markdown cell
    """
    if re_hide.search(cell.source):
        cell.metadata["transient"] = {"remove_source": True}
        cell.source = ""
        cell.outputs = []
    elif re_hide_input.search(cell.source):
        cell.metadata["transient"] = {"remove_source": True}
        cell.source = ""
    elif re_hide_output.search(cell.source):
        cell.outputs = []
        cell.execution_count = None
        cell.source = re_hide_output.sub(r"", cell.source)


class HideFlagsPreprocessor(Preprocessor):
    """
    Process Hide flags - remove cells, code or output marked by HIDE_FLAGS.
    """

    def preprocess_cell(
        self,
        cell: CodeCell,
        resources: ResourcesDict,
        index: int,
    ) -> CellAndResources:
        """
        Apply a transformation on each cell. See base.py for details.
        """
        if cell.cell_type == "code":
            cell_process_hide_flags(cell)
        return cell, resources


class RemoveEmptyCellPreprocessor(Preprocessor):
    """
    Remove Empty Cell - remove cells with no code.
    """

    def preprocess_cell(
        self,
        cell: Cell,
        resources: ResourcesDict,
        index: int,
    ) -> CellAndResources:
        """
        Apply a transformation on each cell. See base.py for details.
        """
        if cell.cell_type == "code":
            if cell.source == "":
                cell.metadata["transient"] = {"remove_source": True}
        return cell, resources


def nb_process_hide_flags(nb: Nb) -> None:
    """Process Hide flags - remove cells, code or output marked by HIDE_FLAGS.

    Args:
        nb (Notebook): Notebook to process
    """

    for cell in nb.cells:
        if cell.cell_type == "code":
            cell_process_hide_flags(cell)


OUTPUT_FLAG = "###output_flag###"
OUTPUT_FLAG_COLLAPSE = "###output_flag_collapse###"
# OUTPUT_FLAG_CLOSE = ""
OUTPUT_FLAG_CLOSE = "###output_close###"
# format_output = '\n!!! output ""  \n    '
# format_output = '\n???+ done "output"  \n    <pre>'
# format_output_collapsed = '\n??? done "output"  \n    <pre>'
# format_output_close = ""
format_output = "\n<details open> <summary>output</summary>  \n    </pre>"
format_output_collapsed = "\n<details> <summary>output</summary>  \n    </pre>"
format_output_close = "<pre>\n</details>"


def process_cell_collapse_output(cell: CodeCell) -> str:
    """Process cell for collapse output. Clear flag and return flag for COLLAPSE or not.

    Args:
        cell (CodeCell): CodeCell to process.

    Returns:
        str: flag: OUTPUT_FLAG or OUTPUT_FLAG_COLLAPSE
    """
    result = OUTPUT_FLAG
    if re_collapse.search(cell.source) is not None:
        result = OUTPUT_FLAG_COLLAPSE
        cell.source = re_collapse.sub("", cell.source)

    return result


def mark_output(cell: CodeCell) -> None:
    """Mark text at cell outputs by flag.

    Args:
        cell (CodeCell): CodeCell with outputs.
    """
    output_flag = process_cell_collapse_output(cell)
    for output in cell.outputs:
        # if output.get("name", None) == "stdout":  # output_type - "stream" process stderr!
        if output.output_type == "stream":  # output_type - "stream"
            if output.name == "stdout":  # add process stderr!
                output.text = output_flag + output.text + OUTPUT_FLAG_CLOSE
        elif hasattr(output, "data"):  # ExecuteResult, DisplayData
            if "text/plain" in output.data:
                output.data["text/plain"] = (
                    output_flag + output.data["text/plain"] + OUTPUT_FLAG_CLOSE
                )


def nb_mark_output(nb: Nb):
    """Mark cells with output.
    Better use Preprocessor version

    Args:
        nb (Notebook): Notebook to process
    """
    for cell in nb.cells:
        if cell.cell_type == "code":
            mark_output(cell)


class MarkOutputPreprocessor(Preprocessor):
    """
    Mark outputs at code cells.
    """

    def preprocess_cell(
        self,
        cell: CodeCell,
        resources: ResourcesDict,
        index: int,
    ) -> CellAndResources:
        """
        Apply a transformation on each cell. See base.py for details.
        """
        if cell.cell_type == "code":
            mark_output(cell)

        return cell, resources


def md_process_output_flag(md: str) -> str:
    """Reformat marked output.

    Args:
        md (str): Markdown string

    Returns:
        str: Markdown string.
    """
    result = re.sub(r"\s*\#*output_flag_collapse\#*", format_output_collapsed, md)
    result = re.sub(r"\s*\#*output_flag\#*", format_output, result)
    if OUTPUT_FLAG_CLOSE:
        result = re.sub(rf"\#*{OUTPUT_FLAG_CLOSE}\#*", format_output_close, result)
    return result
