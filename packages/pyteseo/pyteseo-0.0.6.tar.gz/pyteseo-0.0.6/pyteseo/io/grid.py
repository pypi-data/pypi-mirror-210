from pathlib import Path
import pandas as pd
import xarray as xr
from pyteseo.io.utils import _warn_lonlat_range, _warn_lonlat_soting


def elevation_ds_to_depth_df(ds: xr.Dataset) -> pd.DataFrame:
    """convert elevation dataset to depth dataframe [lon, lat, depth]

    Args:
        ds (xr.Dataset): elevation [lon, lat, elevation]

    Returns:
        pd.DataFrame: depth [lon, lat, depth]
    """
    df = ds.get("elevation").to_dataframe().reset_index()
    df.elevation = df.elevation * -1
    df = df.rename(columns={"elevation": "depth"})

    return df


def read_grid(path: str, nan_value: float = -999) -> pd.DataFrame:
    """Read TESEO grid-file to pandas DataFrame

    Args:
        path (str): path to the grid-file
        nan_value (float, optional): value to set nans. Defaults to -999.

    Returns:
        pd.DataFrame: DataFrame with TESEO grid data [lon, lat, depth]
    """
    path = Path(path)
    df = pd.read_csv(path, delimiter="\s+", na_values=str(nan_value), header=None)

    if df.shape[1] != 3:
        raise ValueError(
            "TESEO grid-file should contains lon, lat and depth values only!"
        )

    df.columns = ["lon", "lat", "depth"]
    _warn_lonlat_range(df)
    _warn_lonlat_soting(df)

    return df


def write_grid(df: pd.DataFrame, path: str, nan_value: float = -999) -> None:
    """Write TESEO grid-file

    Args:
        df (pd.DataFrame): DataFrame with columns 'lon', 'lat', 'depth' (lon:[-180,180], lat:[-90,90])
        path (str): path to the new grid-file
        nan_value (float, optional): define how will be writted nan values in the grid-file. Defaults to -999.
    """
    path = Path(path)

    if (
        "lon" not in df.keys().values
        or "lat" not in df.keys().values
        or "depth" not in df.keys().values
    ):
        raise ValueError(
            "variable names in DataFrame should be 'lon', 'lat' and 'depth'!"
        )

    if df.shape[1] != 3:
        raise ValueError(
            "DataFrame should contains column variables lon, lat and depth only!"
        )

    # FIXME - if [0,360] convert to [-180,180]
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        raise ValueError(
            "lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    df = df.sort_values(["lon", "lat"])
    df.to_csv(
        path,
        sep="\t",
        columns=["lon", "lat", "depth"],
        na_rep=nan_value,
        header=False,
        index=False,
        float_format="%.8e",
    )
