"""Provides a series of generic NumPy and Pandas utility functions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def memory_downcaster(df: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Downcasts ``int`` and ``float`` columns to the lowest memory alternative possible. For
    integers this means converting to either signed or unsigned 8-, 16-, 32-, or 64-bit integers,
    and for floats, converting to ``np.float32``.

    Args:
        df (pd.DataFrame | pd.Series): DataFrame or Series to have its memory footprint reduced.

    Returns:
        pd.DataFrame | pd.Series: Reduced footprint version of the passed :py:attr:`df`.
    """
    # if not isinstance(df, pd.DataFrame | pd.Series):
    if not isinstance(df, (pd.DataFrame, pd.Series)):  # noqa
        raise TypeError("Input value must be a Pandas DataFrame or Series.")

    NAlist = []
    for col in df.select_dtypes(include=[np.number]).columns:
        IsInt = False
        mx = df[col].max()
        mn = df[col].min()

        # integer does not support na; fill na
        if not np.isfinite(df[col]).all():
            NAlist.append(col)
            df[col].fillna(mn - 1, inplace=True)

        # test if column can be converted to an integer
        asint = df[col].fillna(0).astype(np.int64)
        result = df[col] - asint
        result = result.sum()
        if result > -0.01 and result < 0.01:
            IsInt = True

        # make integer/unsigned integer datatypes
        if IsInt:
            try:
                if mn >= 0:
                    if mx < 255:
                        df[col] = df[col].astype(np.uint8)
                    elif mx < 65535:
                        df[col] = df[col].astype(np.uint16)
                    elif mx < 4294967295:
                        df[col] = df[col].astype(np.uint32)
                    else:
                        df[col] = df[col].astype(np.uint64)
                else:
                    if mn > np.iinfo(np.int8).min and mx < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif mn > np.iinfo(np.int16).min and mx < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif mn > np.iinfo(np.int32).min and mx < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif mn > np.iinfo(np.int64).min and mx < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)
            except:  # noqa: E722
                df[col] = df[col].astype(np.float32)

        # make float datatypes 32 bit
        else:
            df[col] = df[col].astype(np.float32)

    return df


def split_by_index(
    arr: pd.DataFrame | np.ndarray | pd.Series, n_splits: int
) -> tuple[np.ndarray, np.ndarray]:
    """Split a DataFrame, Series, or array like with np.array_split, but only return the start and
    stop indices, rather than chunks. For Pandas objects, this are equivalent to
    ``arr.iloc[start: end]`` and for NumPy: ``arr[start: end]``. Splits are done according
    to the 0th dimension.

    Args:
        arr(pd.DataFrame | pd.Series | np.ndarray): The array, data frame, or series to split.
        n_splits(:obj:`int`): The number of near equal or equal splits.

    Returns:
        tuple[np.ndarray, np.ndarray]
    """
    size = arr.shape[0]
    base = np.arange(n_splits)
    split_size = size // n_splits
    extra = size % n_splits

    starts = base * split_size
    ends = starts + split_size

    for i in range(extra):
        ends[i:] += 1
        starts[i + 1 :] += 1
    return starts, ends
