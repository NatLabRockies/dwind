"""Enables running dwind as a CLI tool, the primary interface for working with dwind."""

from __future__ import annotations

from typing import Optional, Annotated
from pathlib import Path

import typer
import pandas as pd

from dwind.cli import utils


app = typer.Typer()

DWIND = Path("/projects/dwind/agents")


@app.command()
def combine_chunks(
    dir_out: Annotated[
        str,
        typer.Argument(
            help=(
                "Path to where the chunked outputs should be saved. Should be the same that was"
                " passed to the run command."
            )
        ),
    ],
    file_name: Annotated[
        Optional[str],  # noqa
        typer.Option(
            "--file-name",
            "-f",
            help="Custom filename, without the extension (e.g. .pqt), for the results data.",
        ),
    ] = None,
    remove_results_chunks: Annotated[
        bool,
        typer.Option(
            "--remove-results-chunks/--no-remove-results-chunks",
            "-rr/-RR",
            help="Delete the individual chunk files after saving the combined results.",
        ),
    ] = True,
):
    """Combine the results of a multi-job run based on the run's TOML configuration. Please note
    this has the potential to combine multiple runs as it does not respect the jobs ran during a
    single cycle.
    """
    dir_out = Path.cwd() if dir_out is None else Path(dir_out).resolve()
    out_path = dir_out / "chunk_files"
    result_files = [f for f in out_path.iterdir() if f.suffix == (".pqt")]

    if len(result_files) > 0:
        file_name = "results" if file_name is None else file_name
        result_agents = pd.concat([pd.read_parquet(f) for f in result_files])
        f_out = dir_out / f"{file_name}.pqt"
        result_agents.to_parquet(f_out)
        print(f"Aggregated results saved to: {f_out}")
        return None

        if remove_results_chunks:
            for f in result_files:
                f.unlink()
                print(f"Removed: {f}")
    else:
        print(f"No chunked results found in: {out_path}.")


@app.command()
def cleanup_agents(
    dir_out: Annotated[
        str,
        typer.Argument(
            help=(
                "Path to where the chunked agents were saved. Should be the same that was"
                " passed to the run command."
            )
        ),
    ],
):
    """Deletes the temporary agent chunk files generated at runtime.

    Args:
        dir_out (str): The base output directory, which should be the same as that passed to the
            run command.
    """
    utils.cleanup_chunks(dir_out, which="agents")


@app.command()
def cleanup_results(
    dir_out: Annotated[
        str,
        typer.Argument(
            help=(
                "Path to where the results agents were saved. Should be the same that was"
                " passed to the run command."
            )
        ),
    ],
):
    """Deletes the chunked results files generated at runtime.

    Args:
        dir_out (str): The base output directory, which should be the same as that passed to the
            run command.
    """
    utils.cleanup_chunks(dir_out, which="results")


if __name__ == "__main__":
    app()
