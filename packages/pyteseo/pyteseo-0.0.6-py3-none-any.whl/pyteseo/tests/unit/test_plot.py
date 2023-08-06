from pathlib import Path
from shutil import rmtree

import pytest

# from matplotlib import pyplot as plt

from pyteseo.io.results import read_properties_results
from pyteseo.plot.animations import animate_forcings, animate_particles
from pyteseo.plot.basics import _plot_properties
from pyteseo.plot.figures import plot_domain, plot_extents

# Domain
coastline_path = "pyteseo/tests/data/ibiza_domain/costa.dat"
grid_path = "pyteseo/tests/data/ibiza_domain/grid.dat"

# Forcings
currents_lst_path = "pyteseo/tests/data/hns_simulation/input/lstcurr_UVW.pre"
winds_lst_path = "pyteseo/tests/data/hns_simulation/input/lstwinds.pre"
waves_lst_path = "pyteseo/tests/data/hns_simulation/input/lstwaves.pre"

# TESEO results
results_path = "pyteseo/tests/data/hns_simulation"

properties_df = read_properties_results(results_path)

tmp_path = Path("tests_plots")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


def test_plot_basics_properties():
    _plot_properties(properties_df, spill_id=1)
    # plt.show()


def test_plot_figures_domain():
    plot_domain(grid_path, coastline_path, show=False)


def test_plot_figures_extents():
    plot_extents(
        grid_path,
        coastline_path,
        currents_lst_path,
        winds_lst_path,
        waves_lst_path,
        show=False,
    )


def test_plot_animations_particles(setup_teardown):
    animate_particles(
        results_path,
        coastline_path,
        grid_path,
        2,
        show=False,
        gif_path=Path(tmp_path, "particles.gif"),
    )


def test_plot_animations_forcings(setup_teardown):
    animate_forcings(
        currents_lst_path,
        winds_lst_path,
        coastline_path,
        grid_path,
        scale=15,
        show=False,
        gif_path=Path(tmp_path, "forcings.gif"),
    )
