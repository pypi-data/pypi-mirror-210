from pathlib import Path
from nbconvert.exporters.exporter import ResourcesDict
from nbdocs.core import read_nb
from nbdocs.process import (
    CorrectMdImageLinkPreprocessor,
    copy_images,
    correct_markdown_image_link,
    md_correct_image_link,
    get_image_link_re,
    md_find_image_names,
)
from nbdocs.cfg_tools import NbDocsCfg
from nbdocs.tests.base import create_tmp_image_file


new_link_expected = "![dog](images/markdown_image_files/dog.jpg)"
wrong_link = "![dog](images/dogs.jpg)"
external_link = "![dog](https://localhost/dog.jpg)"


text = """
Its a dog image.
here - ![dog](images/dog.jpg) ---
=== cat
--- ![cat](images/cat.jpg) ---
just line,
ext link![mkd link] (https://images/some.jpg) dsf
one more line
output link ![jpg](output.jpg) dsf

second output ![jpg] (output2.jpg) dsf
output image, link with whitespaces ![asdf] ( output.jpg ) dsf
"""

text_with_output_image_link = "some text\n![jpg](output.jpg)\nmore text"


def test_get_image_link_re():
    """get_image_link_re"""
    re_link = get_image_link_re()
    all_links = re_link.findall(text)
    assert len(all_links) == 6
    fn = "output.jpg"
    re_link = get_image_link_re(fn)
    res = re_link.finditer(text)
    assert len(list(res)) == 2
    res = re_link.finditer(text)
    match = next(res)
    assert match.group("path") == fn


def test_md_find_image_names():
    """test md_find_image_names"""
    image_names = md_find_image_names(text)
    assert len(image_names) == 5


def test_copy_images(tmp_path: Path) -> None:
    """test_copy_images"""
    test_names = ["t_1.png", "t_2.jpg"]
    for fn in test_names:
        fn = tmp_path / fn
        create_tmp_image_file(fn)
        assert fn.exists()
    dest = tmp_path / "dest"
    done, left = copy_images(test_names, tmp_path, dest)
    assert len(done) == 2
    assert len(left) == 0
    for fn in test_names:
        assert (dest / fn).exists()


def test_md_correct_image_link():
    """test md_correct_image_link"""
    corrected_text = md_correct_image_link(
        md=text_with_output_image_link, image_name="output.jpg", image_path="images"
    )
    assert "![jpg](images/output.jpg)" in corrected_text
    assert "some text" in corrected_text
    assert "more text" in corrected_text
    # wrong name, nothing changed
    corrected_text = md_correct_image_link(
        md=text_with_output_image_link, image_name="output2.jpg", image_path="images"
    )
    assert corrected_text == text_with_output_image_link


# def test_cell_md_correct_image_link():
#     pass


def test_correct_markdown_image_link(tmp_path: Path) -> None:
    """Correct image link"""
    nb_fn = Path("tests/test_nbs/markdown_image.ipynb")
    nb = read_nb(nb_fn)
    cfg = NbDocsCfg()
    cfg.docs_path = str(tmp_path / "test_docs")
    correct_markdown_image_link(nb, nb_fn, cfg)
    assert (tmp_path / cfg.docs_path / cfg.images_path).exists()
    assert (
        tmp_path / cfg.docs_path / cfg.images_path / "markdown_image_files" / "dog.jpg"
    ).exists()
    assert nb.cells[1].source.splitlines()[1] == new_link_expected
    nb.cells[1].source = external_link
    correct_markdown_image_link(nb, nb_fn, cfg)
    assert nb.cells[1].source == external_link
    nb.cells[1].source = wrong_link
    correct_markdown_image_link(nb, nb_fn, cfg)
    assert nb.cells[1].source == wrong_link
    nb_fn = Path("tests/test_nbs/code_image.ipynb")
    nb = read_nb(nb_fn)
    nb_copy = nb.copy()
    correct_markdown_image_link(nb, nb_fn, cfg)
    assert nb == nb_copy


def test_CorrectMdImageLinkPreprocessor(tmp_path: Path) -> None:
    """test CorrectMdImageLinkPreprocessor"""
    nb_fn = Path("tests/test_nbs/markdown_image.ipynb")
    nb = read_nb(nb_fn)
    cfg = NbDocsCfg()
    cfg.docs_path = str(tmp_path / "test_docs")
    resources = ResourcesDict(filename=nb_fn)
    processor = CorrectMdImageLinkPreprocessor(cfg=cfg)
    processor.enabled = True
    nb, _ = processor(nb, resources)
    assert (tmp_path / cfg.docs_path / cfg.images_path).exists()
    assert (
        tmp_path / cfg.docs_path / cfg.images_path / "markdown_image_files" / "dog.jpg"
    ).exists()
    assert nb.cells[1].source.splitlines()[1] == new_link_expected
    nb.cells[1].source = external_link
    nb, _ = processor(nb, resources)
    assert nb.cells[1].source == external_link
    nb.cells[1].source = wrong_link
    nb, _ = processor(nb, resources)
    assert nb.cells[1].source == wrong_link
    nb_fn = "tests/test_nbs/code_image.ipynb"
    nb = read_nb(nb_fn)
    nb_copy = nb.copy()
    nb, _ = processor(nb, resources)
    assert nb == nb_copy
