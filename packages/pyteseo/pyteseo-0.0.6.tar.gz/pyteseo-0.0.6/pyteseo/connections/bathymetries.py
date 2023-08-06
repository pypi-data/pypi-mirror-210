"""General classes to access Bathymetries from IHC Thredds"""

import numpy as np
import xarray as xr


BATHYMETRY_DATASETS = {
    "gebco_2020": {
        "url": "https://ihthreddsdev.ihcantabria.com/thredds/dodsC/Bathymetry/Global/Gebco_2020.nc",
        "x": "lon",
        "y": "lat",
        "elevation": "elevation",
    },
    "emodnet_2022": {
        "url": "https://erddap.emodnet.eu/erddap/griddap/bathymetry_2022",
        "x": "longitude",
        "y": "latitude",
        "elevation": "elevation",
    },
}


def normalize_ds_coordinates(
    ds, lon: str = None, lat: str = None, depth: str = None, time: str = None
) -> xr.Dataset:
    d = dict()
    d.update({lon: "lon"}) if lon else None
    d.update({lat: "lat"}) if lat else None
    d.update({depth: "depth"}) if depth else None
    d.update({time: "time"}) if time else None
    if d:
        ds = ds.rename(d)
    return ds


def normalize_ds_elevation_name(ds: xr.Dataset, elevation_name: str) -> xr.Dataset:
    if elevation_name not in ds.variables:
        ds = ds.rename({elevation_name: "elevation"})
    return ds


def spatial_subset(ds: xr.Dataset, bbox: tuple) -> xr.Dataset:
    lon_min = bbox[0] - np.diff(ds["lon"].values).max()
    lon_max = bbox[2] + np.diff(ds["lon"].values).max()
    lon_slice = slice(lon_min, lon_max)

    lat_min = bbox[1] - np.diff(ds["lat"].values).max()
    lat_max = bbox[3] + np.diff(ds["lat"].values).max()
    lat_slice = slice(lat_min, lat_max)

    return ds.sel(lon=lon_slice, lat=lat_slice)


def get_bathymetry(dataset: str, bbox: tuple) -> xr.Dataset:
    ds = xr.open_dataset(BATHYMETRY_DATASETS[dataset.lower()]["url"])
    ds = ds.squeeze(drop=True)
    ds = normalize_ds_elevation_name(
        ds, BATHYMETRY_DATASETS[dataset.lower()]["elevation"]
    )
    ds = normalize_ds_coordinates(
        ds,
        BATHYMETRY_DATASETS[dataset.lower()]["x"],
        BATHYMETRY_DATASETS[dataset.lower()]["y"],
    )
    return spatial_subset(ds, bbox)

    # # TODO - DELETE
    # extent = box(
    #     ds.lon.values.min(),
    #     ds.lat.values.min(),
    #     ds.lon.values.max(),
    #     ds.lat.values.max(),
    # )
    # self.ds = ds
    # self.df = ds.get("elevation").to_dataframe().reset_index()
    # self.df.elevation = self.df.elevation * -1
    # self.df = self.df.rename(columns={"elevation": "depth"})
