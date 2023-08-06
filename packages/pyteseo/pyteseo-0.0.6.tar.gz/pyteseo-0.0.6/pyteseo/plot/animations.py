"""Predefined animations"""

import matplotlib.animation as animation
from matplotlib import pyplot as plt

from pyteseo.io.coastline import coastline_df_to_gdf, read_coastline
from pyteseo.io.forcings import read_forcing
from pyteseo.io.grid import read_grid
from pyteseo.io.results import read_particles_results
from pyteseo.plot.basics import (
    _plot_currents_extent,
    _plot_coastline,
    _plot_grid_extent,
    _plot_grid_land_mask,
    _plot_winds_extent,
)


def animate_particles(
    results_path, coastline_path, grid_path, spill_id=None, gif_path=None, show=True
):
    symbols = {
        0: {"label": "Particle @ coastline", "marker": ".", "color": "m"},
        1: {"label": "Particle @ water surface", "marker": ".", "color": "b"},
        5: {"label": "Particle @ water column", "marker": ",", "color": "c"},
        -1: {"label": "Particle @ seafloor", "marker": "2", "color": "m"},
        -2: {"label": "Particle outside domain", "marker": "x", "color": "r"},
    }

    df_particles = read_particles_results(results_path)
    gdf_coastline = coastline_df_to_gdf(read_coastline(coastline_path))
    df_grid = read_grid(grid_path)
    # df_grid["depth"] = np.where(df_grid["depth"] <= 0, np.nan, df_grid["depth"])

    def update(df_group):
        t, df_t = df_group

        # PLOT PARTICLES OF ALL SPILLS IN THE DOMAIN
        ax1.clear()
        _plot_grid_extent(df_grid, ax1)
        _plot_coastline(gdf_coastline, ax1)
        for k, v in symbols.items():
            if k in df_particles.status_index.unique():
                ax1.scatter(
                    df_t[df_t["status_index"] == k].lon,
                    df_t[df_t["status_index"] == k].lat,
                    marker=v["marker"],
                    color=v["color"],
                    label=v["label"],
                )
        ax1.set_xlim(
            [
                df_grid.lon.min() - 0.01 * (df_grid.lon.max() - df_grid.lon.min()),
                df_grid.lon.max() + 0.01 * (df_grid.lon.max() - df_grid.lon.min()),
            ]
        )
        ax1.set_ylim(
            [
                df_grid.lat.min() - 0.01 * (df_grid.lon.max() - df_grid.lon.min()),
                df_grid.lat.max() + 0.01 * (df_grid.lon.max() - df_grid.lon.min()),
            ]
        )

        ax1.set_title(f"Particle tracking @ time: {t}h")
        ax1.set_xlabel("Longitude (º)")
        ax1.set_ylabel("Latitude (º)")
        ax1.legend(fontsize="small", framealpha=1)
        ax1.set_aspect("equal", "box")
        ax1.grid(alpha=0.6)

        if spill_id:
            # PLOT SPILL PARTICLES
            df_spill_t = df_t[df_t["spill_id"] == spill_id]

            if len(df_spill_t):
                ax2.clear()
                _plot_coastline(gdf_coastline, ax2)
                _plot_grid_land_mask(df_grid, ax2)
                for k, v in symbols.items():
                    if k in df_particles.status_index.unique():
                        ax2.scatter(
                            df_spill_t[df_spill_t["status_index"] == k].lon,
                            df_spill_t[df_spill_t["status_index"] == k].lat,
                            marker=v["marker"],
                            color=v["color"],
                            label=v["label"],
                        )
                ax2.set_xlim([df_spill_t.lon.min() - 0.1, df_spill_t.lon.max() + 0.1])
                ax2.set_ylim([df_spill_t.lat.min() - 0.1, df_spill_t.lat.max() + 0.1])
                ax2.set_title(f"Spill {spill_id:02d} @ time: {t}h")
                ax2.set_xlabel("Longitude (º)")
                ax2.set_ylabel("Latitude (º)")
                ax2.legend(fontsize="small", framealpha=1)
                ax2.set_aspect("equal", "box")
                ax2.grid(alpha=0.6)

    if spill_id:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    else:
        fig, ax1 = plt.subplots()

    anim = animation.FuncAnimation(
        fig, update, frames=df_particles.groupby("time"), interval=1500
    )

    if gif_path:
        anim.save(gif_path)

    if show:
        plt.show()


def animate_forcings(
    currents_lst_path: str,
    winds_lst_path: str,
    coastline_path: str,
    grid_path: str = None,
    gif_path: str = None,
    show: bool = True,
    scale=10,
    cd=0.2,
):
    def update(t, ds_currents, ds_winds):
        ds1 = ds_currents.sel(time=t)
        ds1 = ds1.where(ds1["u"] != 0)
        ds1 = ds1.where(ds1["v"] != 0)
        ds2 = ds_winds.sel(time=t)

        ds2["u"] = ds2["u"] * cd
        ds2["v"] = ds2["v"] * cd

        ax1.clear()
        if grid_path:
            _plot_grid_extent(df_grid, ax1)
        if currents_lst_path:
            _plot_currents_extent(df_currents, ax1)
        if winds_lst_path:
            _plot_winds_extent(df_winds, ax1)
        if coastline_path:
            _plot_coastline(gdf_coastline, ax1)
        q1 = ds1.plot.quiver(
            ax=ax1,
            x="lon",
            y="lat",
            u="u",
            v="v",
            width=0.005,
            headwidth=2,
            headlength=3,
            headaxislength=3,
            color="b",
            label="currents @ surface",
            add_guide=False,
            scale=scale,
        )
        ax1.quiverkey(
            q1,
            X=0.95,
            Y=1.1,
            U=0.5,
            label=q1._label + " " + r"$(0.5 \frac{m}{s})$",
            labelpos="W",
        )
        q2 = ds2.plot.quiver(
            ax=ax1,
            x="lon",
            y="lat",
            u="u",
            v="v",
            width=0.005,
            headwidth=2,
            headlength=3,
            headaxislength=3,
            color="r",
            add_guide=False,
            scale=scale,
            label="winds @ 10m",
        )
        ax1.quiverkey(
            q2,
            X=0.95,
            Y=1.05,
            U=0.5,
            label=q2._label + r" · $C_d$" + " " + r"$(0.5 \frac{m}{s})$",
            labelpos="W",
        )
        ax1.set_title(f"Forcings @ time: {t.values}h")
        ax1.grid()
        ax1.legend()

    df_currents = read_forcing(currents_lst_path, "currents")
    ds_currents = (df_currents.set_index(["time", "lon", "lat"])).to_xarray()

    if grid_path:
        df_grid = read_grid(grid_path)

    if coastline_path:
        gdf_coastline = coastline_df_to_gdf(read_coastline(coastline_path))

    if winds_lst_path:
        df_winds = read_forcing(winds_lst_path, "winds")
        ds_winds = (df_winds.set_index(["time", "lon", "lat"])).to_xarray()

    fig, ax1 = plt.subplots(figsize=(16, 9))
    my_anim = animation.FuncAnimation(
        fig,
        update,
        frames=ds_currents.time,
        fargs=(ds_currents, ds_winds),
        interval=1500,
    )

    if gif_path:
        my_anim.save(gif_path)

    if show:
        plt.show()
