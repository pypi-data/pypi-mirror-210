import geopandas as gpd
from shapely.geometry import box

from io import BytesIO
from owslib.wfs import WebFeatureService


# WFS SERVICE
def geoserver_wfs_request(
    wfs_url, wfs_version: str, feature_name: str, bbox: tuple = None
) -> BytesIO:
    """Create connection to WFS service of a Geoserver and request a feature.
    Optionally, a bbox can be passed to select features inside and instersected by the box.
    Args:
        wfs_url (str): Url of the WFS service.
        wfs_version (str): version of the WFS service.
        feature_name (str): Name of the feature requested.
        bbox (tuple, optional): boundary box (Xmin, Ymin, Xmax, Ymax). Defaults to None.
    Raises:
        FeatureNameError: Custom error for invalid feature names.
    Returns:
        BytesIO: Geoserver response in JSON format
    """

    wfs = WebFeatureService(url=wfs_url, version=wfs_version)
    if bbox:
        return wfs.getfeature(typename=feature_name, bbox=bbox, outputFormat="json")
    else:
        return wfs.getfeature(typename=feature_name, outputFormat="json")


COASTLINE_DATASETS = {
    "gshhs": {
        "geoserver_url": "https://geoserverdev.ihcantabria.com/geoserver/wfs",
        "geoserver_wfs_version": "1.1.0",
        "feature": "BaseMaps:GSHHS_f_L1",
    },
    "emodnet_2022": {
        "geoserver_url": "https://geoserverdev.ihcantabria.com/geoserver/wfs",
        "geoserver_wfs_version": "1.1.0",
        "feature": "BaseMaps:EMODNET_MSL",
    },
}


def get_coastline(
    dataset: str,
    bbox: tuple = None,
    n_max_pol: int = None,
    output_crs: int = 4326,
) -> None:
    """Extract GSHHS coastline polygons from IHC GeoServer through WFS service.
    Args:
        provider (str): choose between gshhs or emodnet.
        bbox (tuple, optional): boundary box, defined as (Xmin, Ymin, Xmax, Ymax). Defaults to None.
        n_max_pol (int, optional): maximum number of polygon to be selected. Defaults to None.
        output_crs (int, optional): define ouput coordinate reference system. Defaults to None.
        create_gdf (bool, optional): whether creates GeoDataFrame. Defaults to True.
        create_df (bool, optional): whether creates DataFrame. Defaults to True.
    """
    response = geoserver_wfs_request(
        wfs_url=COASTLINE_DATASETS[dataset.lower()]["geoserver_url"],
        wfs_version=COASTLINE_DATASETS[dataset.lower()]["geoserver_wfs_version"],
        feature_name=COASTLINE_DATASETS[dataset.lower()]["feature"],
        bbox=bbox,
    )

    gdf = gpd.read_file(response).explode(index_parts=False).set_crs(4326)

    if bbox:
        extent = box(bbox[0], bbox[1], bbox[2], bbox[3])
        if not all([extent.contains(geom) for geom in gdf.geometry]):
            gdf = gdf.clip_by_rect(*extent.bounds)

    if n_max_pol:
        # project to cartesian to sort areas and filter small polygons then transform back to ellipsoidal
        if len(gdf) > n_max_pol:
            gdf = gdf.to_crs(3857)
            gdf = gdf.sort_values("area", ascending=False)[:n_max_pol]

    if output_crs:
        gdf = gdf.to_crs(output_crs)

    return gdf.reset_index(drop=True)
