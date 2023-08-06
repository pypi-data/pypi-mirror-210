from __future__ import annotations

from datetime import datetime, timedelta
from requests.sessions import Session

import numpy as np
import xarray as xr
from pydap.cas.get_cookies import setup_session
from pydap.client import open_url


def get_global_phy_ocean_hourly(
    cmems_session: Session,
    bbox: tuple,
    timebox: tuple,
    variables: list = ["utotal", "vtotal"],
) -> xr.Dataset:
    """access to CMEMS GLOBAL and get total currents (circulation + tide + stokes drift)

    Args:
        username (str): CMEMS username for login
        password (str): CMEMS password for login
        bbox (tuple[float, float, float, float]): lon_min, lat_min, lon_max, lat_max
        timebox (tuple[datetime, datetime]): initial_time, end_time

    Returns:
        pd.DataFrame: resulting dataframe with currents data (time, lon, lat, u, v)
    """
    dataset_url = (
        "https://nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy_anfc_merged-uv_PT1H-i"
    )

    ds = opendap_cmems(cmems_session, dataset_url).get(variables)
    ds = ds.squeeze(drop=True)
    ds = set_standard_coordnames(ds, "time", "longitude", "latitude")
    ds = spatial_subset(ds, bbox)
    ds = temporal_subset(ds, timebox, buffer=timedelta(hours=1))
    if any(ds.time.dt.minute != 0):
        ds = ds.resample(time="1H").interpolate("linear")
    ds = temporal_subset(ds, timebox)

    return ds
    # ds = ds.rename(
    #     {varname: new_varname for varname, new_varname in zip(variables, ["u", "v"])}
    # )
    # ds.to_netcdf("currents.nc")
    # df = ds.to_dataframe().reset_index()
    # df["time"] = (df["time"] - df["time"][0]).dt.total_seconds() / 3600

    # return df


def get_global_phy_wind_L4(
    cmems_session: Session,
    bbox: tuple,
    timebox: tuple,
    variables: list = ["eastward_wind", "northward_wind"],
) -> xr.Dataset:
    dataset_url = "https://nrt.cmems-du.eu/thredds/dodsC/cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H"

    ds = opendap_cmems(cmems_session, dataset_url)
    ds = ds.get(variables)
    ds = spatial_subset(ds, bbox)
    ds = temporal_subset(ds, timebox, buffer=timedelta(hours=1))
    if any(ds.time.dt.minute != 0):
        ds = ds.resample(time="1H").interpolate("linear")
    return ds


def opendap_cmems(cmems_session: Session, dataset_url: str) -> xr.Dataset:
    """retrieve dataset from cmems opendap, login needed

    Args:
        cmems_session (Session): active session from login in cmems
        dataset_url (str): url to the cmems opendap service of the dataset

    Returns:
        xr.Dataset: dataset retrieved
    """
    data_store = xr.backends.PydapDataStore(
        open_url(url=dataset_url, session=cmems_session)
    )
    return xr.open_dataset(data_store)


def login_cmems(username: str, password: str) -> Session:
    """login in cmems web and services

    Args:
        username (str): CMEMS username
        password (str): CMEMS password

    Returns:
        Session: active session for CMEMS web and services
    """
    session = setup_session("https://cmems-cas.cls.fr/cas/login", username, password)
    session.cookies.set("CASTGC", session.cookies.get_dict()["CASTGC"])
    print(f"\033[1;32m {username} login successful! \U0001F642 \033[0;0m\n")
    return session


def set_standard_coordnames(
    ds: xr.Dataset,
    ds_t: str,
    ds_x: str,
    ds_y: str,
    ds_z: str = None,
    standard_t: str = "time",
    standard_x: str = "lon",
    standard_y: str = "lat",
    standard_z: str = "depth",
) -> xr.Dataset:
    """standarize main coordinates (t,x,y,z)

    Args:
        ds (xr.Dataset): input dataset.
        ds_t (str): dataset's name for t-coordinate.
        ds_x (str): dataset's name for x-coordinate.
        ds_y (str): dataset's name for y-coordinate.
        ds_z (str, optional): dataset's name for z-coordinate. Defaults to None.
        standard_t (str, optional): standard name for t-coordinate. Defaults to "time".
        standard_x (str, optional): standard name for x-coordinate. Defaults to "lon".
        standard_y (str, optional): standard name for y-coordinate. Defaults to "lat".
        standard_z (str, optional): standard name for z-coordinate. Defaults to "depth".

    Returns:
        xr.Dataset: formatted dataset.
    """
    if ds_z:
        return ds.rename(
            {ds_t: standard_t, ds_x: standard_x, ds_y: standard_y, ds_z: standard_z}
        )
    else:
        return ds.rename({ds_t: standard_t, ds_x: standard_x, ds_y: standard_y})


def spatial_subset(
    ds: xr.Dataset, bbox: tuple[float, float, float, float], buffer: bool = True
) -> xr.Dataset:
    """subset spatially (lon,lat).

    Args:
        ds (xr.Dataset): input dataset.
        bbox (tuple[float, float, float, float]): lon_min, lat_min, lon_max, lat_max coordinates.
        buffer (bool, optional): extends selection to the next outside coordinate. Defaults to None.

    Returns:
        xr.Dataset: subset dataset
    """
    if buffer:
        dx = max(np.unique(ds["lon"].diff("lon").values))
        dy = max(np.unique(ds["lat"].diff("lat").values))

        buffer_value = max([dx, dy])
        return ds.sel(
            lon=slice(bbox[0] - buffer_value, bbox[2] + buffer_value),
            lat=slice(bbox[1] - buffer_value, bbox[3] + buffer_value),
        )
    else:
        return ds.sel(
            lon=slice(bbox[0], bbox[2]),
            lat=slice(bbox[1], bbox[3]),
        )


def temporal_subset(
    ds: xr.Dataset, timebox: tuple[datetime, datetime], buffer: timedelta = None
) -> xr.Dataset:
    """subset temporally.

    Args:
        ds (xr.Dataset): input dataset.
        time_box (tuple[datetime, datetime]): initial_datetime, end_datetime.
        buffer (timedelta): time to extend selection limits.

    Returns:
        xr.Dataset: subset dataset
    """
    if buffer:
        return ds.sel(time=slice(timebox[0] - buffer, timebox[1] + buffer))
    else:
        return ds.sel(time=slice(timebox[0], timebox[1]))
