from pathlib import Path
from typing import Any, Callable, Tuple, TypeVar

from click import argument

from . import app, option, option_workdir, options_output

_T = TypeVar("_T", bound=Callable[..., Any])


def _option_minimum_delay(command: _T) -> _T:
    return option(
        "--minimum-delay",
        default=5,
        help="Minimum number of seconds before recompiling",
    )(command)


@app.group()
def watch() -> None:
    """Compile on change"""
    pass


@watch.command()
@argument("targets", nargs=-1)
@options_output(handout=False, presentation=True, print=False)
@_option_minimum_delay
@option_workdir
def deck(
    targets: Tuple[str],
    handout: bool,
    presentation: bool,
    print: bool,
    minimum_delay: int,
    workdir: Path,
) -> None:
    """
    Compile on change.

    Watching can be restricted to given TARGETS.
    """
    from logging import getLogger

    from ..paths import Paths
    from ..running import run
    from ..watching import watch as watching_watch

    logger = getLogger(__name__)

    logger.info("Watching the shared, current and user directories")
    paths = Paths.from_defaults(workdir)
    watching_watch(
        minimum_delay,
        frozenset([paths.shared_dir, paths.current_dir, paths.user_config_dir]),
        frozenset([paths.shared_tikz_pdf_dir, paths.pdf_dir, paths.build_dir]),
        run,
        paths=paths,
        build_handout=handout,
        build_presentation=presentation,
        build_print=print,
        target_whitelist=targets or None,
    )


@watch.command()
@argument("section")
@argument("flavor")
@options_output(handout=False, presentation=True, print=False)
@_option_minimum_delay
@option_workdir
def section(
    section: str,
    flavor: str,
    handout: bool,
    presentation: bool,
    print: bool,
    minimum_delay: int,
    workdir: Path,
) -> None:
    """Compile a specific FLAVOR of a given SECTION on change."""
    from logging import getLogger
    from tempfile import TemporaryDirectory

    from click import launch

    from .. import app_name
    from ..paths import GlobalPaths, Paths
    from ..running import run_section
    from ..watching import watch as watching_watch

    logger = getLogger(__name__)

    logger.info(f"Watching {section} ⋅ {flavor}, the shared and user directories")
    global_paths = GlobalPaths.from_defaults(workdir)
    with TemporaryDirectory(prefix=f"{app_name}-") as build_dir, TemporaryDirectory(
        prefix=f"{app_name}-"
    ) as pdf_dir:
        logger.info(
            f"Output directory located at [link=file://{pdf_dir}]{pdf_dir}[/link]",
            extra=dict(markup=True),
        )
        paths = Paths.from_defaults(
            workdir,
            check_depth=False,
            build_dir=Path(build_dir),
            pdf_dir=Path(pdf_dir),
            company_config=global_paths.template_company_config,
            deck_config=global_paths.template_deck_config,
        )
        launch(str(pdf_dir))
        watching_watch(
            minimum_delay,
            frozenset([paths.shared_dir, paths.user_config_dir]),
            frozenset([paths.shared_tikz_pdf_dir, paths.pdf_dir, paths.build_dir]),
            run_section,
            section=section,
            flavor=flavor,
            paths=paths,
            build_handout=handout,
            build_presentation=presentation,
            build_print=print,
        )


@watch.command()
@argument("latex")
@options_output(handout=False, presentation=True, print=False)
@_option_minimum_delay
@option_workdir
def file(
    latex: str,
    handout: bool,
    presentation: bool,
    print: bool,
    minimum_delay: int,
    workdir: Path,
) -> None:
    """Compile FILE on change, specified relative to share/latex."""
    from logging import getLogger
    from tempfile import TemporaryDirectory

    from click import launch

    from .. import app_name
    from ..paths import GlobalPaths, Paths
    from ..running import run_file
    from ..watching import watch as watching_watch

    logger = getLogger(__name__)

    logger.info(f"Watching {latex}, the shared and user directories")
    global_paths = GlobalPaths.from_defaults(workdir)
    with TemporaryDirectory(prefix=f"{app_name}-") as build_dir, TemporaryDirectory(
        prefix=f"{app_name}-"
    ) as pdf_dir:
        logger.info(
            f"Output directory located at [link=file://{pdf_dir}]{pdf_dir}[/link]",
            extra=dict(markup=True),
        )
        paths = Paths.from_defaults(
            workdir,
            check_depth=False,
            build_dir=Path(build_dir),
            pdf_dir=Path(pdf_dir),
            company_config=global_paths.template_company_config,
            deck_config=global_paths.template_deck_config,
        )
        launch(str(pdf_dir))
        watching_watch(
            minimum_delay,
            frozenset([paths.shared_dir, paths.user_config_dir]),
            frozenset([paths.shared_tikz_pdf_dir, paths.pdf_dir, paths.build_dir]),
            run_file,
            latex=latex,
            paths=paths,
            build_handout=handout,
            build_presentation=presentation,
            build_print=print,
        )


@watch.command()
@_option_minimum_delay
@option_workdir
def standalones(minimum_delay: int, workdir: Path) -> None:
    """Compile standalones on change."""
    from ..paths import GlobalPaths
    from ..running import run_standalones
    from ..watching import watch as watching_watch

    global_paths = GlobalPaths.from_defaults(workdir)

    watching_watch(
        minimum_delay,
        frozenset([global_paths.tikz_dir, global_paths.plt_dir]),
        frozenset([global_paths.shared_tikz_pdf_dir, global_paths.shared_plt_pdf_dir]),
        run_standalones,
        workdir,
    )
