from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from shapely import box
import geopandas as gpd
import pandas as pd


def _scatter_grid_depth(df_grid: pd.DataFrame, ax: Axes = None) -> None:
    """scattered plot of the grid depth

    Args:
        df_grid (pd.DataFrame): grid data [lon, lat, depth, ...].
        ax (Axes, optional): specific axes to plot on. Defaults to None.
    """
    if not ax:
        _, ax = plt.subplots()
    df_grid.plot.scatter(
        ax=ax, x="lon", y="lat", c="depth", label="depth", colormap="viridis"
    )


def _plot_grid_land_mask(df_grid: pd.DataFrame, ax: Axes = None) -> None:
    """plot land mask of the TESEO grid

    Args:
        df_grid (pd.DataFrame): grid data [lon, lat ,depth]
        ax (Axes): specific axes to plot on. Defaults to None.
    """
    if not ax:
        _, ax = plt.subplots()

    df_grid.loc[df_grid["depth"] <= 0, "depth"] = None
    ax.scatter(
        df_grid[df_grid["depth"].isnull()].lon,
        df_grid[df_grid["depth"].isnull()].lat,
        color="black",
        marker="D",
        label="grid land mask",
        s=10,
    )


def _plot_coastline(gdf_coastline: gpd.GeoDataFrame, ax: Axes = None) -> None:
    """plot coastline polygons

    Args:
        gdf_coastline (gpd.GeoDataFrame): closed polygons of the coastline.
        ax (Axes, optional): specific axes to plot on. Defaults to None.
    """
    if not ax:
        _, ax = plt.subplots()
    gdf_coastline.plot(
        ax=ax, facecolor="lightgrey", edgecolor="grey", label="coastline"
    )
    # Dummy fill to set legend
    ax.fill([], label="coastline", facecolor="lightgrey", edgecolor="grey")


def _plot_grid_extent(df: pd.DataFrame, ax: Axes = None) -> None:
    """plot grid extent

    Args:
        df (pd.DataFrame): TESEO grid data [lon, lat, ...].
        ax (Axes, optional): specific axes to plot on. Defaults to None.
    """
    extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
    if not ax:
        _, ax = plt.subplots()

    ax.fill(
        *extent.exterior.xy,
        facecolor="ivory",
        edgecolor="goldenrod",
        lw=2,
        label="grid extent",
    )


def _plot_currents_extent(df: pd.DataFrame, ax: Axes = None) -> None:
    """plot extent of currents forcing

    Args:
        df (pd.DataFrame): currents data [lon, lat, ...]
        ax (Axes, optional): specific axes to plot on. Defaults to None.
    """
    if "lon" and "lat" in df.columns and len(df) >= 4:
        extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
        if not ax:
            _, ax = plt.subplots()
        ax.fill(
            *extent.exterior.xy,
            edgecolor="dodgerblue",
            facecolor="none",
            lw=2,
            label="currents extent",
        )


def _plot_winds_extent(df: pd.DataFrame, ax=None):
    if "lon" and "lat" in df.columns and len(df) >= 4:
        extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
        if not ax:
            _, ax = plt.subplots()
        ax.fill(
            *extent.exterior.xy,
            edgecolor="lightcoral",
            facecolor="none",
            lw=2,
            label="winds extent",
        )


def _plot_waves_extent(df: pd.DataFrame, ax=None):
    if "lon" and "lat" in df.columns and len(df) >= 4:
        extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
        if not ax:
            _, ax = plt.subplots()
        ax.fill(
            *extent.exterior.xy,
            edgecolor="lightgreen",
            facecolor="none",
            lw=2,
            label="waves extent",
        )


def _plot_properties(df: pd.DataFrame, spill_id: int, ax=None) -> None:
    """plot spill propierties results in a chart

    Args:
        df (pd.DataFrame): spills properties data [time, spill_id, variables...].
        spill_id (int): id of the spill.
        show (bool, optional): visulization flag. Defaults to True.

    Raises:
        ValueError: Wrong spill id.
    """

    if spill_id not in df["spill_id"].unique():
        raise ValueError(
            f"Wrong spill id. Availables spill ids in this DataFrame are={df['spill_id'].unique()}"
        )
    df = df.set_index("time", drop=True)
    df = df[df["spill_id"] == spill_id]

    vars = [
        "surface",
        "beached",
        "evaporated",
        "dispersed",
    ]

    vars_percentage = [
        "surface_percentage",
        "beached_percentage",
        "evaporated_percentage",
        "dispersed_percentage",
    ]

    if not ax:
        _, ax = plt.subplots()

    df[vars].plot(ax=ax)
    ax.set_title(f"Spill {spill_id:02}")
    ax.set_ylabel("Surface density ($kg/m^2$)", color="black")

    ax2 = ax.twinx()
    df[vars_percentage].plot(ax=ax2, legend=False)
    ax2.set_ylabel("percentage (%)", color="black")

    ax.set_xlabel("time (h)")
