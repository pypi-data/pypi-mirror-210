"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from pyteseo.defaults import FILE_PATTERNS


def read_coastline(path: str) -> pd.DataFrame:
    """Read TESEO coastline-file to pandas DataFrame

    Args:
        path (str | PosixPath): path to the coastline-file

    Returns:
        pd.DataFrame: DataFrame with TESEO coastline data [lon, lat]
    """
    path = Path(path)
    df = pd.read_csv(path, delimiter="\s+", header=None)

    if not any(df.iloc[0].isnull()):
        df.loc[-1] = pd.Series([float("nan")] * len(df.columns), index=df.columns)
        df.index = df.index + 1
        df.sort_index(inplace=True)

    if not any(df.iloc[-1].isnull()):
        df.loc[-1] = pd.Series([float("nan")] * len(df.columns), index=df.columns)
        df = df.reset_index(drop=True)

    if df.shape[1] != 2:
        raise ValueError("TESEO coastline-file should contains lon, lat values only!")

    df.columns = ["lon", "lat"]
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        raise ValueError(
            "lon and lat values in TESEO grid-file should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    return _split_polygons(df)


def _split_polygons(df: pd.DataFrame) -> pd.DataFrame:
    """Split DataFrame between nan values

    Args:
        df (pd.DataFrame): input DataFrame with nans

    Returns:
        pd.DataFrame: DataFrame with polygon and point number as indexes
    """
    mask = df.isna().any(axis=1)
    start_mask = (~mask) & mask.shift(fill_value=True)
    df["polygon"] = start_mask.cumsum() - 1
    new_df = df.dropna()

    return new_df


def write_coastline(df: pd.Dataframe, path: str) -> None:
    if (
        "lon" not in df.columns
        or "lat" not in df.columns
        or "polygon" not in df.columns
        or df.shape[1] < 3
    ):
        raise ValueError(
            "DataFrame should contains at least 3 column variables: 'lon', 'lat' and 'polygon'"
        )

    teseo_df = nan_row = pd.DataFrame({"lon": [float("nan")], "lat": [float("nan")]})
    for id, df_ in df.groupby("polygon"):
        teseo_df = pd.concat([teseo_df, df_[["lon", "lat"]]], ignore_index=True)
        teseo_df = pd.concat([teseo_df, nan_row], ignore_index=True)
        polygon_path = Path(path).parent / f"{FILE_PATTERNS['polygons']}".replace(
            "*", f"{id+1}"
        )
        df_.to_csv(
            polygon_path,
            sep="\t",
            columns=["lon", "lat"],
            header=False,
            index=False,
            float_format="%.8e",
            na_rep="NaN",
        )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    teseo_df.to_csv(
        path,
        sep="\t",
        header=False,
        index=False,
        float_format="%.8e",
        na_rep="NaN",
    )


def coastline_df_to_gdf(df: pd.DataFrame, epsg: str = "4326") -> gpd.GeoDataFrame:
    """convert coastline dataframe[lon,lat,polygon] to geodataframe

    Args:
        df (pd.DataFrame): Dataframe with columns [lon, lat, polygon]
        epsg (str, optional): epsg coordinate code. Defaults to "4326" (WGS84).

    Returns:
        gpd.GeoDataFrame: closed polygons of the coastline
    """

    geometry = [
        Polygon(list(zip(df_["lon"], df_["lat"]))) for _, df_ in df.groupby("polygon")
    ]
    gdf = gpd.GeoDataFrame({"geometry": geometry})
    gdf = gdf.set_crs(epsg)

    return gdf


def create_coastline_from_shpapefile(shp_path, coastline_path):
    gdf = gpd.read_file(shp_path)
    gdf = gdf["geometry"].explode(ignore_index=True)
    gdf = gdf.to_crs(epsg="4326")
    df = coastline_gdf_to_coastline_df(gdf)
    write_coastline(df, coastline_path)


def coastline_gdf_to_coastline_df(gdf) -> pd.DataFrame:
    """Convert costaline GeoDataFrame[geometry] to coastline DataFrame [lon, lat, polygon]
    Returns:
        pd.DataFrame: coastlines polygons [polygon, lon, lat]
    """
    multipoints = gdf.geometry.apply(lambda x: list(x.exterior.coords))

    df = pd.DataFrame(
        {
            "polygon": gdf.index.repeat(multipoints.apply(len)),
            "lon": [p[0] for points in multipoints for p in points],
            "lat": [p[1] for points in multipoints for p in points],
        }
    )

    return df.reset_index(drop=True)
