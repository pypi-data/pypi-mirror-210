from __future__ import annotations

from pathlib import Path
from datetime import datetime
from shapely.geometry import box

from pyteseo.connections.bathymetries import get_bathymetry
from pyteseo.connections.coastlines import get_coastline
from pyteseo.defaults import FILE_NAMES
from pyteseo.io.coastline import write_coastline, coastline_gdf_to_coastline_df
from pyteseo.io.grid import write_grid, elevation_ds_to_depth_df
from pyteseo.plot.figures import plot_domain


def set_spill_point(
    substance_type: str,
    release_time: datetime,
    substance: str,
    lon: float,
    lat: float,
    depth: float = float("nan"),
    initial_width: float = float("nan"),
    initial_length: float = float("nan"),
    mass: float = float("nan"),
    volume: float = float("nan"),
    thickness: float = float("nan"),
    min_thickness: float = 0.00005,
) -> dict:
    """help to generate spill point definition.

    Args:
        substance_type (str): ["drifter", "hns", "oil"].
        release_time (datetime): time when substance is released.
        substance (str): name of the substance.
        lon (float): longitude where the spill point is located.
        lat (float): latitude where the spill point is located.
        depth (float, optional): depth where the spill point is located (3D only). Defaults to float("nan").
        initial_width (float, optional): initial width of the slick. Defaults to float("nan").
        initial_length (float, optional): initial length of the slick. Defaults to float("nan").
        mass (float, optional): _description_. Defaults to float("nan").
        volume (float, optional): substance mass released. Defaults to float("nan").
        thickness (float, optional): thickness of the initial slick. Defaults to float("nan").
        min_thickness (float, optional): minimum thickness the substance can reach. Defaults to 0.00005.

    Raises:
        ValueError: if mandatory variable is not defined.
        ValueError: if substance type is not one of ["drifter", "hns", "oil"].

    Returns:
        dict: spill point definition.
    """
    DRIFTER_MANDATORY_VARIABLES = [
        "release_time",
        "lon",
        "lat",
        "initial_width",
        "initial_length",
    ]
    OIL_HNS_MANDATAORY_VARIABLES = DRIFTER_MANDATORY_VARIABLES + [
        "substance",
        "mass",
        "thickness",
    ]

    args = set_spill_point.__code__.co_varnames

    if substance_type.lower() in ["oil", "hns"]:
        if not all(var in args for var in OIL_HNS_MANDATAORY_VARIABLES):
            raise ValueError(
                "Mandatory variable(s) for oil/hns spill point not founded! {OIL_HNS_MANDATAORY_VARIABLES}"
            )
    else:
        raise ValueError(
            f"Bad substance_type ({substance_type}). Allowed substance types are: 'drifter', 'oil', or 'hns'"
        )

    d = dict()
    for arg in args:
        d.update({arg: locals()[arg]})

    return d


def create_domain(
    path, name, bbox, bathymetry_dataset, coastline_dataset=None, n_max_pol=None
):
    dir_path = Path(path, name)
    dir_path.mkdir(parents=True, exist_ok=True)

    print(f"\nExtracting bathymetry from {bathymetry_dataset} @ bbox={bbox}...")
    ds = get_bathymetry(bathymetry_dataset, bbox)
    extent = box(
        ds.lon.values.min(),
        ds.lat.values.min(),
        ds.lon.values.max(),
        ds.lat.values.max(),
    )

    depth_df = elevation_ds_to_depth_df(ds)

    write_grid(depth_df, Path(dir_path, FILE_NAMES["grid"]))
    print(f"Teseo's bathymetry-file created @ {Path(dir_path, FILE_NAMES['grid'])}")

    if coastline_dataset:
        print(
            f"\nExtracting coastline from {coastline_dataset} @ bbox={extent.bounds}..."
        )
        gdf = get_coastline(coastline_dataset, extent.bounds, n_max_pol)
        df = coastline_gdf_to_coastline_df(gdf)
        write_coastline(df, Path(dir_path, FILE_NAMES["coastline"]))
        print(
            f"Teseo's coastline-file created @ {Path(dir_path, FILE_NAMES['coastline'])}"
        )

    fig = plot_domain(
        Path(dir_path, FILE_NAMES["grid"]),
        Path(dir_path, FILE_NAMES["coastline"]),
        land_mask=False,
        show=False,
    )
    fig.savefig(dir_path / f"{name}_domain.png", dpi=600, format="png")
