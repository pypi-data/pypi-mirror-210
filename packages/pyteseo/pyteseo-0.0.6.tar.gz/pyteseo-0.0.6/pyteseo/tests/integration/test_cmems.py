from __future__ import annotations

import os
import pytest
from datetime import datetime
import xarray as xr
from requests.sessions import Session

from pyteseo.connections.cmems import login_cmems
from pyteseo.connections.cmems import (
    get_global_phy_ocean_hourly,
    get_global_phy_wind_L4,
)


dataset_url = (
    "https://nrt.cmems-du.eu/thredds/dodsC/cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H"
)
bbox = (-4.25, 43.2, -1.25, 44)
timebox = (datetime(2021, 4, 1, 0, 5, 0), datetime(2021, 4, 6, 0, 12, 0))

username = os.environ.get("CMEMS_username")
password = os.environ.get("CMEMS_password")

pytestmark = pytest.mark.skipif(
    username is None or password is None, reason="CMEMS login credentials not defined!"
)


cmems_session = login_cmems(username=username, password=password)
# ds = opendap_cmems(cmems_session, dataset_url)


def test_login():
    assert isinstance(cmems_session, Session)
    assert "CASTGC" in cmems_session.cookies.get_dict()


@pytest.mark.slow
def test_opendap_global_phy_ocean_hourly():
    ds = get_global_phy_ocean_hourly(cmems_session, bbox, timebox)

    assert isinstance(ds, xr.Dataset)
    assert "lon" in ds.coords
    assert "lat" in ds.coords
    assert "time" in ds.coords
    assert all(ds.time.dt.minute) == 0


@pytest.mark.slow
@pytest.mark.depends(on=["test_opendap_global_phy_ocean_hourly"])
def test_opendap_global_phy_wind_L4():
    ds = get_global_phy_wind_L4(cmems_session, bbox, timebox)
    assert "lon" in ds.coords
    assert "lon" in ds.coords
    assert "time" in ds.coords
    assert all(ds.time.dt.minute) == 0
