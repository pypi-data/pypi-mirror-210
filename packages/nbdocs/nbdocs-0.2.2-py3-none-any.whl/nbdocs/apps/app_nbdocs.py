from pathlib import Path
import sys
from dataclasses import dataclass
from typing import Optional, Sequence

from argparsecfg import (
    ArgumentParserCfg,
    add_args_from_dc,
    create_dc_obj,
    create_parser,
    field_argument,
)
from rich import print as rprint

from nbdocs.convert import convert2md, filter_changed
from nbdocs.core import get_nb_names
from nbdocs.cfg_tools import get_config
from nbdocs.default_settings import (
    NBDOCS_SETTINGS,
    MKDOCS_BASE,
    MATERIAL_BASE,
    FOOTER_HTML,
)

parser_cfg = ArgumentParserCfg(
    description="NbDocs. Convert notebooks to docs. Default to .md"
)


@dataclass
class AppConfig:
    force: bool = field_argument(
        "-F",
        default=False,
        help="Force convert all notebooks.",
    )


def nbdocs(
    app_cfg: AppConfig,
) -> None:
    """NbDocs. Convert notebooks to docs. Default to .md"""
    cfg = get_config()
    nb_names = get_nb_names(cfg.notebooks_path)
    nbs_number = len(nb_names)
    if nbs_number == 0:
        rprint("No files to convert!")
        sys.exit()
    rprint(f"Found {nbs_number} notebooks.")
    if not app_cfg.force:
        message = "Filtering notebooks with changes... "
        nb_names = filter_changed(nb_names, cfg)
        if len(nb_names) == nbs_number:
            message += "No changes."
        rprint(message)

    if len(nb_names) == 0:
        rprint("No files to convert!")
        sys.exit()

    rprint(f"To convert: {len(nb_names)} notebooks.")
    convert2md(nb_names, cfg)


@dataclass
class SetupCfg:
    clean: bool = field_argument(
        "-c",
        default=False,
        action="store_true",
        help="Clean MkDocs setup.",
    )


def setup(cfg: SetupCfg) -> None:
    """Initialize config."""
    rprint("Settings up NbDocs.")
    # create nbdocs config - nbdocs.ini
    with open("nbdocs.ini", "w", encoding="utf-8") as f:
        f.write(NBDOCS_SETTINGS)
    # create mkdocs config - mkdocs.yaml
    mkdocs_setup = MKDOCS_BASE
    if not cfg.clean:  # setting mkdocs material
        mkdocs_setup += MATERIAL_BASE
        # create footer with material
        filename = Path("docs/overrides/partials/copyright.html")
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(FOOTER_HTML)
    with open("mkdocs.yaml", "w", encoding="utf-8") as f:
        f.write(mkdocs_setup)
    rprint("Done.")


def main(args: Optional[Sequence[str]] = None) -> None:
    parser = create_parser(parser_cfg)
    add_args_from_dc(parser, AppConfig)
    subparsers = parser.add_subparsers(title="Commands", help="Available commands.")
    parser_init = subparsers.add_parser(
        "init", help="Initialize config", description="Initialize NbDocs config"
    )
    parser_init.set_defaults(command="init")
    add_args_from_dc(parser_init, SetupCfg)
    parsed_args = parser.parse_args(args=args)
    if hasattr(parsed_args, "command"):
        if parsed_args.command == "init":
            setup_cfg = create_dc_obj(SetupCfg, parsed_args)
            setup(setup_cfg)
    else:
        app_cfg = create_dc_obj(AppConfig, parsed_args)
        nbdocs(app_cfg)


if __name__ == "__main__":
    main()
