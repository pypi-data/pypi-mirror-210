from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from shutil import rmtree

import pytest
import xarray as xr

from pyteseo.io.forcings import write_2d_forcing
from pyteseo.wrapper import TeseoWrapper

username = os.environ.get("CMEMS_username")
password = os.environ.get("CMEMS_password")


@pytest.fixture
def setup_teardown():
    tmp_path = Path("tmp_test_cmems_simulations")
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


# BUG - EL TIEMPO INICIAL DE GRABACION TIENE QUE SER MULTIPLO DEL 'DT' SI NO ENCAJA NO GRABA RESULTADOS.
# HOTFIX - first_time_saved = forcing_init_time
# El tiempo inicial de grabacion se expresa en horas generando numeros periodicos que hacen que el modelo ejecute pero no saque resultados.
# Revisar la logica de como saca resultados y lanzar errores si procede.

domain_directory = "pyteseo/tests/data/ibiza_domain"

now = datetime(2023, 5, 16, 6, 2, 0)
release_1 = now + timedelta(minutes=5)
release_2 = now + timedelta(minutes=12)

# NOTE - Use pre-downloaded netcdf
currents_ds = xr.open_dataset("pyteseo/tests/data/currents.nc")
winds_ds = xr.open_dataset("pyteseo/tests/data/winds.nc")

if not currents_ds.time[0] == winds_ds.time[0]:
    print("ERROR - Forcing Initial times are not the same!")

currents_df = currents_ds.to_dataframe().reset_index()
currents_df["time"] = (
    currents_df["time"] - currents_df["time"][0]
).dt.total_seconds() / 3600


winds_df = winds_ds.to_dataframe().reset_index()
winds_df["time"] = (winds_df["time"] - winds_df["time"][0]).dt.total_seconds() / 3600


@pytest.mark.slow
def test_drift():
    drifter_spill_points = [
        {
            "release_time": release_1,
            "lon": 1.1,
            "lat": 38.98,
            "initial_width": 500,
            "initial_length": 500,
            "thickness": 0.3,
        },
        {
            "release_time": release_2,
            "lon": 1.5,
            "lat": 38.825,
            "initial_width": 500,
            "initial_length": 500,
            "thickness": 0.3,
        },
    ]
    user_parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "drifter",
        "forcing_init_datetime": now.replace(minute=0),
        "first_time_saved": now.replace(minute=0),
        "duration": timedelta(hours=5),
        "timestep": timedelta(minutes=1),
        "use_coastline": True,
        "spill_points": drifter_spill_points,
    }

    print(
        f"""

        Now:                    {now.isoformat()}
        Forcing initial time:   {user_parameters['forcing_init_datetime'].isoformat()}
        Release 1:              {drifter_spill_points[0]['release_time'].isoformat()}
        Release 2:              {drifter_spill_points[1]['release_time'].isoformat()}
        First time saved:       {user_parameters["first_time_saved"].isoformat()}
        """
    )
    # INPUT DATA:
    job_directory = "tmp_test_cmems_simulations/drift_simulation"

    # 1 - Generate job and its folder structure
    job = TeseoWrapper(dir_path=job_directory)

    # 2 - Load domain files
    job.load_domain(src_dir=domain_directory)

    # 3 - Generate forcings
    # NOTE - I fix time and location for testing and pre-downloading preprocessedforcings to netcdfs
    # bbox = (job.grid.x_min, job.grid.y_min, job.grid.x_max, job.grid.y_max)
    # timebox = (
    #     user_parameters["forcing_init_datetime"],
    #     user_parameters["forcing_init_datetime"] + user_parameters["duration"],
    # )
    # currents = access_global_currents(cmems_session, bbox, timebox)
    # winds = access_global_winds(cmems_session, bbox, timebox)

    write_2d_forcing(currents_df, job.input_dir, "currents")
    write_2d_forcing(winds_df, job.input_dir, "winds")

    # 4 - Load forcings
    job.load_forcings()
    job.setup(user_parameters)
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


@pytest.mark.slow
def test_oil(setup_teardown):
    oil_spill_points = [
        {
            "release_time": release_1,
            "lon": 1.1,
            "lat": 38.98,
            "initial_width": 1,
            "initial_length": 1,
            "substance": "lagunillas",
            "mass": 1500,
            "thickness": 0.1,
        },
        {
            "release_time": release_2,
            "lon": 1.5,
            "lat": 38.825,
            "initial_width": 1,
            "initial_length": 1,
            "substance": "tia juana",
            "mass": 3500,
            "thickness": 0.1,
        },
    ]

    # INPUT DATA:
    job_directory = "tmp_test_cmems_simulations/oil_simulation"
    user_parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "oil",
        "forcing_init_datetime": now.replace(minute=0),
        "first_time_saved": now.replace(minute=0),
        "duration": timedelta(hours=5),
        "timestep": timedelta(minutes=1),
        "use_coastline": True,
        "spill_points": oil_spill_points,
    }

    # 1 - Generate job and its folder structure
    job = TeseoWrapper(dir_path=job_directory)

    # 2 - Load domain files
    job.load_domain(src_dir=domain_directory)

    # 3 - Generate forcings
    # NOTE - I fix time and location for testing and pre-downloading preprocessedforcings to netcdfs
    # bbox = (job.grid.x_min, job.grid.y_min, job.grid.x_max, job.grid.y_max)
    # timebox = (
    #     user_parameters["forcing_init_datetime"],
    #     user_parameters["forcing_init_datetime"] + user_parameters["duration"],
    # )
    # currents = access_global_currents(cmems_session, bbox, timebox)
    # winds = access_global_winds(cmems_session, bbox, timebox)

    write_2d_forcing(currents_df, job.input_dir, "currents")
    write_2d_forcing(winds_df, job.input_dir, "winds")

    # 4 - Load forcings
    job.load_forcings()
    job.setup(user_parameters)
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


@pytest.mark.slow
def test_hns(setup_teardown):
    hns_spill_points = [
        {
            "release_time": release_1,
            "lon": 1.1,
            "lat": 38.98,
            "initial_width": 1,
            "initial_length": 1,
            "substance": "acetona",
            "mass": 1500,
            "thickness": 0.1,
        },
        {
            "release_time": release_2,
            "lon": 1.5,
            "lat": 38.825,
            "initial_width": 1,
            "initial_length": 1,
            "substance": "benceno",
            "mass": 3500,
            "thickness": 0.1,
        },
    ]

    # INPUT DATA:
    job_directory = "tmp_test_cmems_simulations/hns_simulation"
    user_parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "hns",
        "forcing_init_datetime": now.replace(minute=0),
        "first_time_saved": now.replace(minute=0),
        "duration": timedelta(hours=5),
        "timestep": timedelta(minutes=1),
        "use_coastline": True,
        "spill_points": hns_spill_points,
    }

    # 1 - Generate job and its folder structure
    job = TeseoWrapper(dir_path=job_directory)

    # 2 - Load domain files
    job.load_domain(src_dir=domain_directory)

    # 3 - Generate forcings
    # NOTE - I fix time and location for testing and pre-downloading preprocessedforcings to netcdfs
    # bbox = (job.grid.x_min, job.grid.y_min, job.grid.x_max, job.grid.y_max)
    # timebox = (
    #     user_parameters["forcing_init_datetime"],
    #     user_parameters["forcing_init_datetime"] + user_parameters["duration"],
    # )
    # currents = access_global_currents(cmems_session, bbox, timebox)
    # winds = access_global_winds(cmems_session, bbox, timebox)

    write_2d_forcing(currents_df, job.input_dir, "currents")
    write_2d_forcing(winds_df, job.input_dir, "winds")

    # 4 - Load forcings
    job.load_forcings()
    job.setup(user_parameters)
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
