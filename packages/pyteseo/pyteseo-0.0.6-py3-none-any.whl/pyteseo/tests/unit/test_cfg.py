from datetime import datetime, timedelta
from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.cfg import (
    _create_spill_points_df,
    _create_substances_df_offline,
)
from pyteseo.wrapper import check_user_minimum_parameters


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
    "user_parameters",
    [
        (
            {
                "forcing_init_datetime": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                ),
                "duration": timedelta(hours=12),
                "spill_points": [
                    {
                        "release_time": datetime.utcnow().replace(
                            second=0, microsecond=0
                        ),
                        "lon": -3.49,
                        "lat": 43.55,
                        "initial_width": 1,
                        "initial_length": 1,
                    },
                ],
            }
        ),
        (
            {
                "substance_type": "drifter",
                "forcing_init_datetime": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                ),
                "duration": timedelta(hours=12),
                "spill_points": [
                    {
                        "release_time": datetime.utcnow().replace(
                            second=0, microsecond=0
                        ),
                        "lat": 43.55,
                        "initial_width": 1,
                        "initial_length": 1,
                    },
                ],
            }
        ),
        (
            {
                "substance_type": "drifter",
                "forcing_init_datetime": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                ),
                "duration": timedelta(hours=12),
                "spill_point": [
                    {
                        "release_time": datetime.utcnow().replace(
                            second=0, microsecond=0
                        ),
                        "lon": -3.49,
                        "lat": 43.55,
                        "initial_width": 1,
                        "initial_length": 1,
                    },
                ],
            }
        ),
        (
            {
                "substance_type": "drifter",
                "forcing_init_datetime": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                ),
                "spill_points": [
                    {
                        "release_time": datetime.utcnow().replace(
                            second=0, microsecond=0
                        ),
                        "lon": -3.49,
                        "lat": 43.55,
                        "initial_width": 1,
                        "initial_length": 1,
                    },
                ],
            }
        ),
    ],
)
def test_check_minimum_cfg_parameters(user_parameters):
    with pytest.raises(KeyError):
        check_user_minimum_parameters(user_parameters)


def test_convert_spill_points_to_df():
    df = _create_spill_points_df(
        [
            {
                "release_time": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                )
                + timedelta(minutes=80),
                "lon": -3.80,
                "lat": 43.44,
                "substance": "oil_example",
                "mass": 1000,
                "thickness": 0.15,
            },
            {
                "release_time": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                )
                + timedelta(minutes=60),
                "lon": -3.879,
                "lat": 43.43,
                "substance": "oil_example",
                "mass": 1500,
                "thickness": 0.25,
            },
        ],
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_get_offline_substances(
    substance_names=["lagunillas", "tia juana"], substance_type="oil"
):
    substances = _create_substances_df_offline(substance_names, substance_type)
    assert len(substances) == len(substance_names)
    assert substances["name"].to_list() == substance_names
