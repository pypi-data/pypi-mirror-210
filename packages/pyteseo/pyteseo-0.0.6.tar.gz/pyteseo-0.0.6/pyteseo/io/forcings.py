"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pyteseo.defaults import FILE_NAMES, FILE_PATTERNS, VARIABLE_NAMES
from pyteseo.io.utils import (
    _check_cte_dt,
    _warn_lonlat_range,
    _check_varnames,
    _check_n_vars,
    _warn_lonlat_soting,
)


def read_cte_forcing(path: str, forcing_type: str, dt: float) -> pd.DataFrame:
    """read spatially cte forcings

    Args:
        path (str): path to forcing lst-file 'lst*.pre'
        forcing_type (str): 'currents', 'winds', or 'waves'
        dt (float): time step of the data

    Returns:
        pd.DataFrame: forcing DataFrame, columns=[time, var1, var2, ..., varN]
    """
    file_column_names = VARIABLE_NAMES[forcing_type]["vars"]

    path = Path(path)
    df = pd.read_csv(path, delimiter="\s+", header=None)
    _check_n_vars(df, file_column_names)
    df.columns = file_column_names

    df.insert(0, "time", df.index.values * dt)

    # FIXME - Use always UV
    if forcing_type in ["currents", "winds"]:
        df = df.rename(columns={"u": "mod", "v": "dir"})

    return df


def read_forcing(path: str, forcing_type: str, dt: float = 1.0) -> pd.DataFrame:
    """Read TESEO 2d forcings from list files

    Args:
        path (str): path to forcing lst-file 'lst*.pre'
        forcing_type (list): 'currents', 'winds', or 'waves'

    Returns:
        pd.DataFrame: forcing DataFrame, columns=[time, lon, lat, var1, var2, ..., varN]
    """

    path = Path(path)
    files = read_lst_file(path)

    if files:
        return read_2d_forcing(files, forcing_type)
    else:
        return read_cte_forcing(path, forcing_type, dt)


def read_lst_file(path: str) -> list:
    """read realative paths stored in lst-file

    Args:
        path (str): path to forcing lst-file 'lst*.pre'

    Returns:
        list: list of relative paths
    """
    path = Path(path)
    with open(path, "r") as f:
        files = [Path(path.parent, line.rstrip()) for line in f]
    if all(file.exists() for file in files):
        return files


def read_2d_forcing(files: list, forcing_type: str) -> pd.DataFrame:
    """read forcing [time, lon, lat]

    Args:
        files (list): list of file paths.
        forcing_type (str): type of forcing. ["currents", "winds", "waves"]

    Raises:
        ValueError: If the readed files are not homogeneous.

    Returns:
        pd.DataFrame: forcing data
    """
    coordnames = VARIABLE_NAMES[forcing_type]["coords"]
    varnames = VARIABLE_NAMES[forcing_type]["vars"]
    file_column_names = (coordnames + varnames)[1:]

    df_list = []
    for file in files:
        df = pd.read_csv(file, delimiter="\s+", header=None)
        _check_n_vars(df, file_column_names)
        df.columns = file_column_names
        _warn_lonlat_range(df)
        _warn_lonlat_soting(df)

        df.insert(loc=0, column="time", value=float(file.stem[-4:-1]))
        df_list.append(df)

    n_rows = list(set([len(df.index) for df in df_list]))
    if len(n_rows) != 1:
        raise ValueError("Number of lines in each file are not equal!")

    df = pd.concat(df_list)
    _check_cte_dt(df)
    return df


def write_cte_forcing(
    df: pd.DataFrame, dir_path: str, forcing_type: str, nan_value=0
) -> None:
    """write lst file for spatially cte forcing from a DataFrame with the required variables.
        currents: [time, u, v]
        winds: [time, u, v]
        waves: [time, hs, dir, tp]

    Args:
        df (pd.DataFrame): DataFrame with required variable names
        dir_path (str): path to the 'inputs' directory of the simulation
        forcing_type (str): 'currents', 'winds', 'waves', 'currents_depthavg'
        nan_value (int, optional): value for NaN sustitution. Defaults to 0.
    """
    lst_filename = FILE_NAMES[forcing_type]
    coordnames = VARIABLE_NAMES[forcing_type]["coords"][0]
    varnames = VARIABLE_NAMES[forcing_type]["vars"]

    # BUG - Use always UV - FIXME in the FORTRAN
    if forcing_type in ["currents", "winds"]:
        varnames = ["mod", "dir"]

    path = Path(dir_path, lst_filename)

    df = df.sort_values([coordnames])
    _check_cte_dt(df)

    df.to_csv(
        path,
        sep="\t",
        columns=varnames,
        header=False,
        index=False,
        float_format="%.8e",
        na_rep=nan_value,
    )


def write_2d_forcing(
    df: pd.DataFrame, dir_path: str, forcing_type: str, nan_value: int = 0
) -> None:
    """write lst-file and forcing files per time from a DataFrame with the required variables.
        currents: [time, lon, lat, u, v]
        winds: [time, lon, lat, u, v]
        waves: [time, lon, lat, hs, dir, tp]

    Args:
        df (pd.DataFrame): DataFrame with required variable names
        dir_path (str): path to the 'inputs' directory of the simulation
        forcing_type (str): 'currents', 'winds', or 'waves'
        nan_value (int, optional): value for NaN sustitution. Defaults to 0.
    """
    lst_filename = FILE_NAMES[forcing_type]
    file_pattern = FILE_PATTERNS[forcing_type]
    varnames = VARIABLE_NAMES[forcing_type]["vars"]
    coordnames = VARIABLE_NAMES[forcing_type]["coords"]

    # # BUG - HOTFIX hasta que se toque el codigo de Fortran
    # if forcing_type == "currents":
    #     lst_filename = "lstcurr_UVW.pre"
    # # ---------------------------------------------------

    path = Path(dir_path, lst_filename)

    df = df.sort_values(coordnames)

    _check_varnames(df, varnames + coordnames)
    _warn_lonlat_range(df)
    _check_cte_dt(df)

    for time, group in df.groupby(coordnames[0]):
        with open(path, "a") as f:
            f.write(f"{file_pattern}\n".replace("*", f"{int(time):03d}"))

        path_currents = Path(path.parent, file_pattern.replace("*", f"{int(time):03d}"))
        group.to_csv(
            path_currents,
            sep="\t",
            columns=coordnames[1:] + varnames,
            header=False,
            index=False,
            float_format="%.8e",
            na_rep=nan_value,
        )


def write_null_forcing(dir_path: str, forcing_type: str) -> None:
    """write spatially cte lst-file with null values

    Args:
        dir_path (str): path to the 'inputs' directory of the simulation
        forcing_type (str): 'currents', 'winds', or 'waves'
    """
    columns = [VARIABLE_NAMES[forcing_type]["coords"][0]] + VARIABLE_NAMES[
        forcing_type
    ]["vars"]
    df = pd.DataFrame([{var: 0 for var in columns}])

    # FIXME - Use always UV
    if forcing_type in ["currents", "winds"]:
        df = df.rename(columns={"u": "mod", "v": "dir"})

    write_cte_forcing(df, dir_path, forcing_type, 1)
