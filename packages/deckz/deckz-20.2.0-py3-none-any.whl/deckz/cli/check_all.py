from pathlib import Path

from . import app, option_workdir, options_output


@app.command()
@options_output(handout=False, presentation=True, print=False)
@option_workdir
def check_all(handout: bool, presentation: bool, print: bool, workdir: Path) -> None:
    """Compile all shared slides (presentation only by default)."""
    from ..running import run_all as running_run_all

    running_run_all(
        directory=workdir,
        build_handout=handout,
        build_presentation=presentation,
        build_print=print,
    )
