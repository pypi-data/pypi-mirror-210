from __future__ import annotations

from pathlib import Path
import pandas as pd
import xarray as xr

from pyteseo.defaults import COORDINATE_NAMES, FILE_PATTERNS


# TODO - extend addition of utc_datetime to all the exportations


def export_grids(
    df: pd.DataFrame,
    file_format: list,
    output_dir: str = ".",
) -> list:
    """Export TESEO's grids (by spill_id) to CSV, JSON, or NETCDF

    Args:
        df (pd.DataFrame): Grids data obtained with pyteseo.io.read_grids_results
        file_format (list): csv, json, or nc
        output_dir (str, optional): directory to export the files. Defaults to "."

    Returns:
        list: paths to exported files
    """

    allowed_formats = ["csv", "json", "nc"]
    exported_files = []

    output_dir = Path(output_dir)
    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(
            f"Invalid format: {file_format}. Allowed formats {allowed_formats}"
        )
    else:
        output_path_pattern = Path(
            output_dir,
            FILE_PATTERNS["export_grids"].replace(".*", f".{file_format}"),
        )

    for spill_id, df in df.groupby("spill_id"):
        output_path = Path(str(output_path_pattern).replace("*", f"{spill_id:03d}"))
        if file_format == "csv":
            df.to_csv(output_path, index=False)
        elif file_format == "json":
            df.to_json(output_path, orient="index")
        elif file_format == "nc":
            df = df.set_index(
                [
                    COORDINATE_NAMES["t"],
                    COORDINATE_NAMES["x"],
                    COORDINATE_NAMES["y"],
                ]
            )
            ds = df.to_xarray().drop_vars("spill_id")
            ds = _add_general_attributes(ds)
            ds.to_netcdf(output_path)
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"\033[1;32m[spill_{spill_id:03d}] Grids successfully exported to {file_format.upper()} @ {output_path}\033[0;0m\n"
        )

    return exported_files


def _add_general_attributes(ds: xr.Dataset):
    """add attributes to TESEO grided results

    Args:
        ds (xr.Dataset): _description_

    Returns:
        _type_: _description_
    """
    if "lon" in ds.coords:
        ds.lon.attrs = {
            "standard_name": "lon",
            "long_name": "lon",
            "units": "degrees_east",
            "axis": "X",
            "unit_long": "Degrees East",
            "step": [],
            "valid_min": min(ds.lon.values),
            "valid_max": max(ds.lon.values),
            "CoordinateAxisType": "Lon",
        }

    if "lat" in ds.coords:
        ds.lat.attrs = {
            "standard_name": "lat",
            "long_name": "lat",
            "units": "degrees_north",
            "axis": "X",
            "unit_long": "Degrees North",
            "step": [],
            "valid_min": min(ds.lat.values),
            "valid_max": max(ds.lat.values),
            "CoordinateAxisType": "Lat",
        }

    if "time" in ds.coords:
        ds.time.attrs = {
            "standard_name": "time",
            "long_name": "time",
            "axis": "T",
            "CoordinateAxisType": "Time",
        }

    if "surface_mass_per_area" in ds.variables:
        ds.surface_mass_per_area.attrs = {
            "_FillValue": -9999,
            "units": "kg m-2",
            "standard_name": "surface_mass_of_per_area",
            "long_name": "surface_mass_of_per_area",
        }

    if "dissolved_mass_per_area" in ds.variables:
        ds.dissolved_mass_per_area.attrs = {
            "_FillValue": -9999,
            "units": "kg m-2",
            "standard_name": "dissolved_mass_of_per_area",
            "long_name": "dissolved_mass_of_per_area",
        }

    if "presence_probability" in ds.variables:
        ds.presence_probability.attrs = {
            "_FillValue": -9999,
            "units": "% (0-100)",
            "long_name": "presence_probability_of_per_cell",
        }

    if "particles_per_cell" in ds.variables:
        ds.particles_per_cell.attrs = {
            "_FillValue": -9999,
            "units": "-",
            "long_name": "number_of_particles_of_per_cell",
        }

    # Global
    ds.attrs = {
        "title": "Gridded results from TESEO model",
        "project": "Programa de Ciencias Marinas (PCM)",
        "institution": "IHCantabria - https://ihcantabria.com/",
        "source": "Generated using pyTESEO - https://github.com/IHCantabria/pyteseo",
        "numerical_model": "TESEO - https://ihcantabria.com/specialized-software/english-teseo/",
        "lon_min": min(ds.lon.values),
        "lon_max": max(ds.lon.values),
        "lat_min": min(ds.lat.values),
        "lat_max": max(ds.lat.values),
    }

    return ds
