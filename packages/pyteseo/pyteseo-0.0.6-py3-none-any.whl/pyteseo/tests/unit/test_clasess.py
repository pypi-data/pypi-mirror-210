from pathlib import Path
from shutil import copyfile, rmtree

import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.classes import (
    Currents,
    Grid,
    Waves,
    Winds,
    Coastline,
)
from pyteseo.wrapper import TeseoWrapper
from pyteseo.defaults import FILE_NAMES

data_path = Path(__file__).parent.parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "input_files, input_files_dst, error",
    [
        (
            [
                "grid.dat",
                "coastline.dat",
                "lstcurr_UVW_cte.pre",
                "lstwinds_cte.pre",
                "lstwaves_cte.pre",
            ],
            [
                "grid.dat",
                "coastline.dat",
                "lstcurr_UVW.pre",
                "lstwinds.pre",
                "lstwaves.pre",
            ],
            None,
        ),
        (
            ["grid.dat", "coastline.dat", "lstcurr_UVW_cte.pre", "lstwinds_cte.pre"],
            ["grid.dat", "coastline.dat", "lstcurr_UVW.pre", "lstwinds.pre"],
            None,
        ),
        (
            ["grid.dat", "coastline.dat", "lstcurr_UVW_cte.pre"],
            ["grid.dat", "coastline.dat", "lstcurr_UVW.pre"],
            None,
        ),
        (
            ["grid.dat", "coastline.dat", "lstwinds_cte.pre"],
            ["grid.dat", "coastline.dat", "lstwinds.pre"],
            None,
        ),
        # (
        #     ["grid.dat", "coastline.dat"],
        #     ["grid.dat", "coastline.dat"],
        #     "no_forcing",
        # ),
        (
            [
                "coastline.dat",
                "lstcurr_UVW_cte.pre",
                "lstwinds_cte.pre",
                "lstwaves_cte.pre",
            ],
            ["lstcurr_UVW.pre", "lstwinds.pre", "lstwaves.pre"],
            "no_grid",
        ),
    ],
)
def test_TeseoWrapper(input_files, input_files_dst, error, setup_teardown):
    if not Path(tmp_path, "input").exists():
        Path(tmp_path, "input").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "input", dst_file))

    job = TeseoWrapper(dir_path=tmp_path)
    assert Path(job.path).exists()
    assert Path(job.input_dir).exists()

    if error:
        with pytest.raises(FileNotFoundError):
            job.load_domain(job.input_dir)
            job.load_forcings()
    else:
        job.load_domain(job.input_dir)
        job.load_forcings()
        assert Path(job.input_dir, FILE_NAMES["grid"]).exists()
        assert Path(job.input_dir, FILE_NAMES["currents"]).exists()
        assert Path(job.input_dir, FILE_NAMES["winds"]).exists()
        assert Path(job.input_dir, FILE_NAMES["waves"]).exists()


@pytest.mark.parametrize(
    "path, error",
    [
        (Path(data_path, "grid.dat"), None),
        (Path(data_path, "not_exist.file"), "not_exist"),
    ],
)
def test_TeseoGrid(path, error):
    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            grid = Grid(path)
    else:
        grid = Grid(path)
        assert isinstance(grid.path, str)
        assert grid.dx == pytest.approx(0.00050, abs=0.00001)
        assert grid.dy == pytest.approx(0.00050, abs=0.00001)
        assert grid.nx == 238
        assert grid.ny == 267


@pytest.mark.parametrize(
    "path, error",
    [
        (Path(data_path, "coastline.dat"), None),
        (Path(data_path, "not_exist.file"), "not_exist"),
    ],
)
def test_TeseoCoastline(path, error):
    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            coastline = Coastline(path)
    else:
        coastline = Coastline(path)
        assert isinstance(coastline.path, str)


@pytest.mark.parametrize(
    "path, dt_cte",
    [
        (Path(data_path, FILE_NAMES["currents"]), None),
        (Path(data_path, "lstcurr_UVW_cte.pre"), 1),
    ],
)
def test_TeseoCurrents(path, dt_cte):
    currents = Currents(path, dt_cte)
    assert isinstance(currents.path, str)
    assert currents.dt == 1
    assert currents.nt == 4
    if dt_cte:
        assert "time" in currents.get_df().keys()
        assert "mod" in currents.get_df().keys()
        assert "dir" in currents.get_df().keys()
    else:
        assert "time" in currents.get_df().keys()
        assert "lon" in currents.get_df().keys()
        assert "lat" in currents.get_df().keys()
        assert "u" in currents.get_df().keys()
        assert "v" in currents.get_df().keys()


@pytest.mark.parametrize(
    "path, dt_cte",
    [
        (Path(data_path, FILE_NAMES["winds"]), None),
        (Path(data_path, "lstwinds_cte.pre"), 1),
    ],
)
def test_TeseoWinds(path, dt_cte):
    winds = Winds(path, dt_cte)
    assert isinstance(winds.path, str)
    assert winds.dt == 1
    assert winds.nt == 4
    if dt_cte:
        assert "time" in winds.get_df().keys()
        assert "mod" in winds.get_df().keys()
        assert "dir" in winds.get_df().keys()
    else:
        assert "time" in winds.get_df().keys()
        assert "lon" in winds.get_df().keys()
        assert "lat" in winds.get_df().keys()
        assert "u" in winds.get_df().keys()
        assert "v" in winds.get_df().keys()


@pytest.mark.parametrize(
    "path, dt_cte",
    [
        (Path(data_path, FILE_NAMES["waves"]), None),
        (Path(data_path, "lstwaves_cte.pre"), 1),
    ],
)
def test_TeseoWaves(path, dt_cte):
    waves = Waves(path, dt_cte)
    assert isinstance(waves.path, str)
    assert waves.dt == 1
    assert waves.nt == 4
    if dt_cte:
        assert "time" in waves.get_df().keys()
        assert "hs" in waves.get_df().keys()
        assert "dir" in waves.get_df().keys()
        assert "tp" in waves.get_df().keys()
    else:
        assert "time" in waves.get_df().keys()
        assert "lon" in waves.get_df().keys()
        assert "lat" in waves.get_df().keys()
        assert "hs" in waves.get_df().keys()
        assert "dir" in waves.get_df().keys()
        assert "tp" in waves.get_df().keys()
