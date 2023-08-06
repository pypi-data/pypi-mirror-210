from __future__ import annotations

from datetime import datetime, timedelta

import requests
import xarray as xr


def get_gfs_0p25_hourly(
    init_datetime: datetime,
    bbox: tuple,
    variables: list = ["ugrd10m", "vgrd10m"],
    lon_0to360: bool = False,
) -> xr.Dataset:
    """Access NOAA GFS 0.25º hourly dataset and retrieve forecast dataset

    Args:
        init_datetime (datetime): last dataset available including this datatime
        bbox (tuple): boundary box to subset global dataset ([lonmin, latmin, lonmax, latmax], -180to180).
        variables (list, optional): list with the requested variable names. Defaults to ["ugrd10m", "vgrd10m"].
        lon_0to360 (bool, optional): to change convention, bbox convention also will change. Defaults to False.

    Returns:
        xr.Dataset: subset with the requested data
    """

    init_datetime = (
        datetime.utcnow() if init_datetime > datetime.utcnow() else init_datetime
    )

    hour = int(init_datetime.hour / 6) * 6
    dataset_datetime = init_datetime.replace(
        hour=hour, minute=0, second=0, microsecond=0
    )
    dataset = f"gfs{dataset_datetime.strftime('%Y%m%d')}/gfs_0p25_1hr_{dataset_datetime.hour:02d}z"
    access = False

    while access is False:
        print(
            f"Datetime passed: {init_datetime.isoformat()}. Dataset requested: {dataset}."
        )

        info_url = f"https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/{dataset}.info"
        response = requests.get(info_url)

        if "error" in response.text:
            print(f"Dataset ({dataset}) not available! Checking previous one...")
            dataset_datetime -= timedelta(hours=6)
            dataset = f"gfs{dataset_datetime.strftime('%Y%m%d')}/gfs_0p25_1hr_{dataset_datetime.hour:02d}z"

        else:
            opendap_url = f"http://nomads.ncep.noaa.gov:80/dods/gfs_0p25_1hr/{dataset}"
            print(f"\nAccessing @ {dataset}")

            ds = xr.open_dataset(opendap_url).get(variables)
            ds = ds.sel(lat=slice(bbox[1], bbox[3]))
            if lon_0to360:
                ds = ds.sel(lon=slice(bbox[0], bbox[2]))
            else:
                ds = ds.assign_coords(lon=(ds.lon + 180) % 360 - 180).roll(
                    lon=(ds.dims["lon"] // 2), roll_coords=True
                )
                ds = ds.sel(lon=slice(bbox[0], bbox[2]))
                print(
                    f"\033[1;32m access successful @ {opendap_url}! \U0001F642 \033[0;0m\n"
                )
            access = True

    return ds
