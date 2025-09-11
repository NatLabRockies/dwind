"""Provides the core data loading methods for importing scenario data from flat files or SQL."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from dwind.config import Year


def load_df(file_or_table: str | Path, year: Year | None, sql_constructor: str | None = None):
    """Loads data from either a SQL table or file to a pandas ``DataFrame``.

    Args:
        file_or_table (str | Path): File name or path object, or SQL table where the data are
            located.
        year (:py:class:`dwind.config.Year`, optional): If used, only extracts the single year from
        a column called "year". Defaults to None.
        sql_constructor (str | None, optional): The SQL engine constructor string. Required if
            extracting from SQL. Defaults to None.
    """
    valid_extenstions = (".csv", ".pqt", ".parquet", ".pkl", ".pickle")
    if str(file_or_table).endswith(valid_extenstions):
        return _load_from_file(filename=file_or_table, year=year)

    return _load_from_sql(table=file_or_table, sql_constructor=sql_constructor, year=year)


def _load_from_file(filename: str | Path, year: Year | None) -> pd.DataFrame:
    """Loads tabular data from a file to a ``pandas.DataFrame``."""
    if isinstance(filename, str):
        filename = Path(filename).resolve()
    if not isinstance(filename, Path):
        raise TypeError(f"`filename` must be a valid path, not {filename=}")

    if filename.suffix == ".csv":
        df = pd.read_csv(filename, dtype_backend="pyarrow")
    elif filename.suffix in (".parquet", ".pqt"):
        df = pd.read_parquet(filename, dtype_backend="pyarrow")
    elif filename.suffix in (".pickle", ".pkl"):
        df = pd.read_pickle(filename, dtype_backend="pyarrow")
    else:
        raise ValueError(f"Only CSV, Parquet, and Pickle files allowed, not {filename=}")

    if year is not None:
        df = df.loc[df.year == year]

    return df


def _load_from_sql(table: str, sql_constructor: str, year: Year | None) -> pd.DataFrame:
    """Load tabular data from SQL."""
    where = f"where year = {year}" if year is not None else ""
    sql = f"""select * from diffusion_shared."{table}" {where};"""
    atlas_engine = create_engine(sql_constructor)

    with atlas_engine.connect() as conn:
        df = pd.read_sql(sql, con=conn.connection, dtype_backend="pyarrow")

    atlas_engine.dispose()
    return df
