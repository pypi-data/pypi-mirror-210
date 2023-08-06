from __future__ import annotations

from pathlib import Path

import nbconvert
from nbconvert.exporters.exporter import ResourcesDict
from rich.progress import track

from nbdocs.core import read_nb
from nbdocs.process import (
    HideFlagsPreprocessor,
    MarkOutputPreprocessor,
    RemoveEmptyCellPreprocessor,
    copy_images,
    md_correct_image_link,
    md_find_image_names,
    md_process_output_flag,
)
from nbdocs.cfg_tools import NbDocsCfg
from nbdocs.typing import Nb, TPreprocessor


class MdConverter:
    """MdConverter constructor."""

    def __init__(self) -> None:
        self.md_exporter: TPreprocessor = nbconvert.MarkdownExporter()
        self.md_exporter.register_preprocessor(
            RemoveEmptyCellPreprocessor, enabled=True
        )
        self.md_exporter.register_preprocessor(HideFlagsPreprocessor, enabled=True)
        self.md_exporter.register_preprocessor(MarkOutputPreprocessor, enabled=True)

    def nb2md(
        self, nb: Nb, resources: ResourcesDict | None = None
    ) -> tuple[str, ResourcesDict]:
        """Base convert Nb to Markdown"""
        md, result_resources = self.md_exporter.from_notebook_node(nb, resources)
        md = md_process_output_flag(md)
        if image_names := md_find_image_names(md):
            result_resources["image_names"] = image_names
        return md, result_resources

    def __call__(
        self, nb: Nb, resources: ResourcesDict | None = None
    ) -> tuple[str, ResourcesDict]:
        """MdConverter call - export given Nb to Md.

        Args:
            nb (Notebook): Nb to convert.

        Returns:
            Tuple[str, ResourcesDict]: Md, resources
        """
        return self.nb2md(nb, resources)


def convert2md(filenames: Path | list[Path], cfg: NbDocsCfg) -> None:
    """Convert notebooks to markdown.

    Args:
        filenames (List[Path]): List of Nb filenames
        cfg (NbDocsCfg): NbDocsCfg
    """
    if not isinstance(filenames, list):
        filenames = [filenames]
    docs_path = Path(cfg.docs_path)
    docs_path.mkdir(exist_ok=True, parents=True)
    md_convertor = MdConverter()
    for nb_fn in track(filenames):
        nb = read_nb(nb_fn)
        resources = ResourcesDict(filename=nb_fn)
        md, resources = md_convertor.nb2md(nb, resources)

        if image_names := resources["image_names"]:
            # dest_images = Path(cfg.docs_path) / cfg.images_path / f"{nb_fn.stem}_files"
            dest_images = f"{cfg.images_path}/{nb_fn.stem}_files"
            (docs_path / dest_images).mkdir(exist_ok=True, parents=True)

            if len(resources["outputs"]) > 0:  # process outputs images
                for image_name, image_data in resources["outputs"].items():
                    md = md_correct_image_link(md, image_name, dest_images)
                    with open(docs_path / dest_images / image_name, "wb") as fh:
                        fh.write(image_data)
                    image_names.discard(image_name)

            # for image_name in image_names:  # process images at cells source
            #     md = md_correct_image_link(md, image_name, f"../{cfg.notebooks_path}")
            _done, left = copy_images(
                image_names, nb_fn.parent, docs_path / cfg.images_path
            )
            # for image_name in done:
            #     md = md_correct_image_link(md, image_name, cfg.images_path)
            if left:
                print(f"Not fixed image names in nb: {nb_fn}:")
                for image_name in left:
                    print(f"   {image_name}")

        with open(
            Path(cfg.docs_path) / nb_fn.with_suffix(".md").name, "w", encoding="utf-8"
        ) as fh:
            fh.write(md)


def nb_newer(nb_name: Path, docs_path: Path) -> bool:
    """return True if nb_name is newer than docs_path."""
    md_name = (docs_path / nb_name.name).with_suffix(".md")
    return not md_name.exists() or nb_name.stat().st_mtime > md_name.stat().st_mtime


def filter_changed(nb_names: list[Path], cfg: NbDocsCfg) -> list[Path]:
    """Filter list of Nb to changed only (compare modification date with dest name).

    Args:
        nb_names (List[Path]): List of Nb filenames.
        dest (Path, optional): Destination folder for md files.
            If not given default from settings. Defaults to None.

    Returns:
        List[Path]: List of Nb filename with newer modification time.
    """
    docs_path = Path(cfg.docs_path)
    return [nb_name for nb_name in nb_names if nb_newer(nb_name, docs_path)]
