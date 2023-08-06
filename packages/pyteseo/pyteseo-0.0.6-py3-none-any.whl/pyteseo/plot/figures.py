"""Predefined figures"""

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from pyteseo.io.coastline import coastline_df_to_gdf, read_coastline
from pyteseo.io.forcings import read_forcing
from pyteseo.io.grid import read_grid
from pyteseo.plot.basics import (
    _plot_currents_extent,
    _plot_coastline,
    _plot_grid_extent,
    _plot_waves_extent,
    _plot_winds_extent,
    _plot_grid_land_mask,
    _scatter_grid_depth,
)


def plot_extents(
    grid_path: str,
    coastline_path: str,
    currents_path: str,
    winds_path: str,
    waves_path: str,
    ax=None,
    show=True,
) -> Figure:
    if not ax:
        fig, ax = plt.subplots(figsize=(16, 9))

    grid_df = read_grid(grid_path)
    gdf_coastline = coastline_df_to_gdf(read_coastline(coastline_path))
    currents_df = read_forcing(currents_path, "currents")
    winds_df = read_forcing(winds_path, "winds")
    waves_df = read_forcing(waves_path, "waves")

    _plot_winds_extent(winds_df, ax)
    _plot_currents_extent(currents_df, ax)
    _plot_waves_extent(waves_df, ax)
    _plot_grid_extent(grid_df, ax)
    _plot_coastline(gdf_coastline, ax)

    ax.set_xlabel("Longitude (º)")
    ax.set_ylabel("Latitude (º)")
    ax.set_title("Model extents")
    plt.grid()
    plt.legend()
    if show:
        plt.show()

    return fig


def plot_domain(
    grid_path: str,
    coastline_path: str,
    land_mask: bool = True,
    show: bool = True,
) -> Figure:
    """Plot domain from bathymetry [lon, lat, depth] and coastline [shapely polygons]

    Args:
        bathymetry_ds (Dataset): xarray DataFrame of the bathymetry.
        coastline_gdf (GeoDataFrame): closed polygons of the coastline.
    """
    grid_df = read_grid(grid_path)
    gdf_coastline = coastline_df_to_gdf(read_coastline(coastline_path))

    fig, ax = plt.subplots(figsize=(16, 9))
    _plot_grid_extent(grid_df, ax=ax)
    _scatter_grid_depth(grid_df, ax=ax)
    _plot_coastline(gdf_coastline, ax=ax)
    if land_mask:
        _plot_grid_land_mask(grid_df, ax=ax)

    ax.set_xlabel("Longitude (º)")
    ax.set_ylabel("Latitude (º)")
    ax.set_title("Model domain")
    plt.grid()
    plt.legend()

    if show:
        plt.show()

    return fig
