from pyteseo.connections.noaa_opendap import get_gfs_0p25_hourly
from datetime import datetime, timedelta
import pytest

# from matplotlib import pyplot as plt


@pytest.mark.slow
def test_opendap_gfs_0p25_hourly_meridian():
    init_datetime = datetime.utcnow() - timedelta(hours=48)

    # Meridian
    bbox = (-7, 37.5, 7, 41.5)

    ds = get_gfs_0p25_hourly(init_datetime, bbox)

    # ds["ugrd10m"].isel(time=0).plot()
    # plt.show()

    assert -180 <= ds.lon.max() <= 180
    assert -180 <= ds.lon.min() <= 180


@pytest.mark.slow
def test_opendap_gfs_0p25_hourly_antimeridian():
    init_datetime = datetime.utcnow() - timedelta(hours=36)

    # Anti-meridian
    # NOTE - bbox and returned ds are in 0-360 longitude axis convention
    bbox = (170, -42, 185, -37)

    ds = get_gfs_0p25_hourly(init_datetime, bbox, lon_0to360=True)

    # ds["ugrd10m"].isel(time=0).plot()
    # plt.show()

    assert 0 <= ds.lon.max() <= 360
    assert 0 <= ds.lon.min() <= 360
