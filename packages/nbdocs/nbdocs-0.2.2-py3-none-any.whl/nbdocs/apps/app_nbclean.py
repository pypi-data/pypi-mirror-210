import sys
from dataclasses import dataclass
from typing import Optional, Sequence

from argparsecfg import field_argument, parse_args, ArgumentParserCfg
from rich import print as rprint

from nbdocs.clean import clean_nb_file
from nbdocs.core import get_nb_names
from nbdocs.cfg_tools import get_config


parser_cfg = ArgumentParserCfg(
    description="Clean Nb or notebooks at `nb_path` - metadata and execution counts from nbs."
)


@dataclass
class AppConfig:
    """Config for `app_nbclean`."""

    nb_path: str = field_argument(
        "nb_path", help="Path to NB or folder with Nbs to clean"
    )
    clear_execution_count: bool = field_argument(
        flag="--no-ec",
        default=True,
        action="store_false",
        help="Clean execution counts.",
    )


def nbclean(app_cfg: AppConfig) -> None:
    """Clean Nb or notebooks at `nb_path` - metadata and execution counts from nbs."""
    cfg = get_config(notebooks_path=app_cfg.nb_path)

    nb_names = get_nb_names(cfg.notebooks_path)

    if (num_nbs := len(nb_names)) == 0:
        rprint("No files to clean!")
        sys.exit()

    rprint(f"Clean: {cfg.notebooks_path}, found {num_nbs} notebooks.")

    clean_nb_file(nb_names, app_cfg.clear_execution_count)


def main(args: Optional[Sequence[str]] = None) -> None:
    app_cfg = parse_args(AppConfig, parser_cfg, args)
    nbclean(app_cfg)


if __name__ == "__main__":  # pragma: no cover
    main()
