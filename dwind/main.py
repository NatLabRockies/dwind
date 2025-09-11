"""Enables running dwind as a CLI tool, the primary interface for working with dwind."""

import typer

from dwind.cli import run, debug, collect


app = typer.Typer()

app.add_typer(
    run.app, name="run", help="Run a dwind analysis via sbatch or in an interactive session."
)

app.add_typer(debug.app, name="debug", help="Help identify issues with analyses that were run.")

app.add_typer(collect.app, name="collect", help="Gather results from a run or rerun analysis.")


if __name__ == "__main__":
    app()
