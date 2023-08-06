import os
from pathlib import Path
from shutil import copyfile, rmtree
from datetime import datetime, timedelta

import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.wrapper import TeseoWrapper


data_path = Path(__file__).parent.parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")

TESEO_PATH = os.environ.get("TESEO_PATH")
pytestmark = pytest.mark.skipif(
    TESEO_PATH is None, reason="Path to TESEO model executable not defined!"
)


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


def test_drifter_cte_forcings_without_coastline(setup_teardown):

    input_files = [
        "grid.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "lstcurr.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "input").exists():
        Path(tmp_path, "input").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "input", dst_file))

    job = TeseoWrapper(dir_path=tmp_path)
    job.load_domain(job.input_dir)
    job.load_forcings()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "drifter",
        "forcing_init_datetime": datetime(2023, 1, 1, 0, 0, 0),
        "duration": timedelta(hours=3),
        "timestep": timedelta(minutes=1),
        "use_coastline": False,
        "spill_points": [
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=32),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1,
                "initial_length": 1,
            },
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=12),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1,
                "initial_length": 1,
            },
        ],
    }
    job.setup(parameters)
    job.run()
    job.postprocessing()

    assert Path(job.path, "grid_coordinates.txt").exists()
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_particles_*.txt"))]) > 0
    )
    assert len([str(path) for path in list(Path(job.path).glob("*_grid_*.txt"))]) > 0
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_properties_*.txt"))]) > 0
    )
    assert len([str(path) for path in list(Path(job.output_dir).glob("*.csv"))]) > 0
    assert len([str(path) for path in list(Path(job.output_dir).glob("*.json"))]) > 0
    assert len([str(path) for path in list(Path(job.output_dir).glob("*.nc"))]) > 0


def test_drifter_cte_forcings_with_coastline(setup_teardown):

    input_files = [
        "grid.dat",
        "coastline.dat",
        "costa_poligono1.dat",
        "costa_poligono2.dat",
        "costa_poligono3.dat",
        "costa_poligono4.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "costa.dat",
        "costa_poligono1.dat",
        "costa_poligono2.dat",
        "costa_poligono3.dat",
        "costa_poligono4.dat",
        "lstcurr.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "input").exists():
        Path(tmp_path, "input").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "input", dst_file))

    job = TeseoWrapper(dir_path=tmp_path)
    job.load_domain(job.input_dir)
    job.load_forcings()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "drifter",
        "forcing_init_datetime": datetime(2023, 1, 1, 0, 0, 0),
        "duration": timedelta(hours=3),
        "timestep": timedelta(minutes=1),
        "spill_points": [
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=32),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1,
                "initial_length": 1,
            },
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=12),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1,
                "initial_length": 1,
            },
        ],
    }
    job.setup(parameters)
    job.run()
    assert Path(job.path, "grid_coordinates.txt").exists()
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_particles_*.txt"))]) > 0
    )
    assert len([str(path) for path in list(Path(job.path).glob("*_grid_*.txt"))]) > 0
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_properties_*.txt"))]) > 0
    )


def test_oil_cte_forcings_with_coastline(setup_teardown):

    input_files = [
        "grid.dat",
        "coastline.dat",
        "costa_poligono1.dat",
        "costa_poligono2.dat",
        "costa_poligono3.dat",
        "costa_poligono4.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "costa.dat",
        "costa_poligono1.dat",
        "costa_poligono2.dat",
        "costa_poligono3.dat",
        "costa_poligono4.dat",
        "lstcurr.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "input").exists():
        Path(tmp_path, "input").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "input", dst_file))

    job = TeseoWrapper(dir_path=tmp_path)
    job.load_domain(job.input_dir)
    job.load_forcings()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "oil",
        "forcing_init_datetime": datetime(2023, 1, 1, 0, 0, 0),
        "duration": timedelta(hours=3),
        "timestep": timedelta(minutes=1),
        "spill_points": [
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=32),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1,
                "initial_length": 1,
                "substance": "lagunillas",
                "mass": 1500,
                "thickness": 0.1,
            },
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=12),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1.5,
                "initial_length": 2.5,
                "substance": "tia juana",
                "mass": 3500,
                "thickness": 0.1,
            },
        ],
    }
    job.setup(parameters)
    job.run()
    assert Path(job.path, "grid_coordinates.txt").exists()
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_particles_*.txt"))]) > 0
    )
    assert len([str(path) for path in list(Path(job.path).glob("*_grid_*.txt"))]) > 0
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_properties_*.txt"))]) > 0
    )


def test_hns_cte_forcings_with_coastline(setup_teardown):

    input_files = [
        "grid.dat",
        "coastline.dat",
        "costa_poligono1.dat",
        "costa_poligono2.dat",
        "costa_poligono3.dat",
        "costa_poligono4.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "costa.dat",
        "costa_poligono1.dat",
        "costa_poligono2.dat",
        "costa_poligono3.dat",
        "costa_poligono4.dat",
        "lstcurr.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "input").exists():
        Path(tmp_path, "input").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "input", dst_file))

    job = TeseoWrapper(dir_path=tmp_path)
    job.load_domain(job.input_dir)
    job.load_forcings()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "hns",
        "forcing_init_datetime": datetime(2023, 1, 1, 0, 0, 0),
        "duration": timedelta(hours=3),
        "timestep": timedelta(minutes=1),
        "spill_points": [
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=32),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1,
                "initial_length": 1,
                "substance": "acetona",
                "mass": 1500,
                "thickness": 0.1,
            },
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=12),
                "lon": -3.8,
                "lat": 43.44,
                "initial_width": 1.5,
                "initial_length": 2.5,
                "substance": "benceno",
                "mass": 3500,
                "thickness": 0.1,
            },
        ],
    }
    job.setup(parameters)
    job.run()
    assert Path(job.path, "grid_coordinates.txt").exists()
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_particles_*.txt"))]) > 0
    )
    assert len([str(path) for path in list(Path(job.path).glob("*_grid_*.txt"))]) > 0
    assert (
        len([str(path) for path in list(Path(job.path).glob("*_properties_*.txt"))]) > 0
    )
