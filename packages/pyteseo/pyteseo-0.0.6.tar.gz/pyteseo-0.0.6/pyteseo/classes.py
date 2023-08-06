from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd

from pyteseo.defaults import COORDINATE_NAMES, VARIABLE_NAMES, FILE_NAMES

from pyteseo.io.grid import read_grid
from pyteseo.io.coastline import read_coastline, coastline_df_to_gdf
from pyteseo.io.forcings import read_forcing, read_cte_forcing
from shapely import box


def _calculate_cell_properties(df: pd.DataFrame, coordname: str):
    if coordname in df:
        d_cell = np.unique(np.diff(df[coordname].round(6).unique())).mean().round(6)
        n_cell = len(np.unique(df[coordname]))
        return d_cell, n_cell
    else:
        return None, None


class Grid:
    def __init__(self, path: str):
        """centralize grid data and properties

        Args:
            path (str): path to grid file
        """
        self.path = str(Path(path).resolve())
        df = read_grid(self.path)
        self.extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
        (self.x_min, self.y_min, self.x_max, self.y_max) = self.extent.bounds
        (self.dx, self.nx) = _calculate_cell_properties(df, COORDINATE_NAMES["x"])
        (self.dy, self.ny) = _calculate_cell_properties(df, COORDINATE_NAMES["y"])

    def get_df(self) -> pd.DataFrame:
        return read_grid(self.path)

    def get_ds(self) -> xr.Dataset:
        df = self.get_df()
        df = df.set_index(["lon", "lat"], drop=True)
        return df.to_xarray()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class Coastline:
    def __init__(self, path: str):
        """centralize coastline data and properties

        Args:
            path (str): path to coastline file
        """
        self.path = str(Path(path).resolve())
        df = read_coastline(self.path)
        self.extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
        (self.x_min, self.y_min, self.x_max, self.y_max) = self.extent.bounds
        self.n_polygons = len(df["polygon"].unique())

    def get_df(self) -> pd.DataFrame:
        return read_coastline(self.path)

    def get_gdf(self) -> gpd.GeoDataFrame:
        df = self.get_df()
        return coastline_df_to_gdf(df)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class Currents:
    def __init__(self, lst_path: str, dt_cte: float = 1.0):
        """centralize currents data and properties

        Args:
            lst_path (str): path to lst-file of currents foncing
            dt_cte (float, optional): time step for currents if spatially cte. Defaults to 1.0.
        """
        self.forcing_type = "currents"
        self.varnames = VARIABLE_NAMES[self.forcing_type]
        self.path = str(Path(lst_path).resolve())

        df = read_forcing(self.path, self.forcing_type, dt_cte)
        if "lon" in df.columns and "lat" in df.columns:
            # 2D
            self.extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
            (self.x_min, self.y_min, self.x_max, self.y_max) = self.extent.bounds
            (self.dx, self.nx) = _calculate_cell_properties(df, COORDINATE_NAMES["x"])
            (self.dy, self.ny) = _calculate_cell_properties(df, COORDINATE_NAMES["y"])
            (self.dt, self.nt) = _calculate_cell_properties(df, COORDINATE_NAMES["t"])

        else:
            # CTE - 1Punto
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = 1
            self.ny = 1
            self.nt = len(df)

        # NOTE - Currents depthavg
        if (
            True
            if Path(Path(self.path).parent, FILE_NAMES["currents_depthavg"]).exists()
            else False
        ):
            print("Currents depth average founded!")
            df = read_cte_forcing(
                Path(Path(self.path).parent, FILE_NAMES["currents_depthavg"]),
                "currents_depthavg",
                dt=self.dt,
            )
            self.currents_depthavg = True
            self.currents_depthavg_nt = len(df)
            self.currents_depthavg_path = Path(
                Path(self.path).parent, FILE_NAMES["currents_depthavg"]
            )
        else:
            self.currents_depthavg = False

    def get_df(self):
        return read_forcing(self.path, self.forcing_type)

    def get_ds(self):
        df = self.get_df()
        df = df.set_index(["time", "lon", "lat"], drop=True)
        return df.to_xarray()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lst_path={self.path})"


class Winds:
    def __init__(self, lst_path: str, dt_cte: float = 1.0):
        """centralize winds data and properties

        Args:
            lst_path (str): path to lst-file of winds forcing
            dt_cte (float, optional): time step for winds if spatially cte. Defaults to 1.0.
        """
        self.forcing_type = "winds"
        self.varnames = VARIABLE_NAMES[self.forcing_type]
        self.path = str(Path(lst_path).resolve())

        if len(pd.read_csv(self.path, delimiter="\s+").columns) != 1:
            df = read_cte_forcing(self.path, self.forcing_type, dt_cte)
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = 1
            self.ny = 1
            self.nt = len(df)

        else:
            df = read_forcing(self.path, self.forcing_type)

            self.extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
            (self.x_min, self.y_min, self.x_max, self.y_max) = self.extent.bounds
            (self.dx, self.nx) = _calculate_cell_properties(df, COORDINATE_NAMES["x"])
            (self.dy, self.ny) = _calculate_cell_properties(df, COORDINATE_NAMES["y"])
            (self.dt, self.nt) = _calculate_cell_properties(df, COORDINATE_NAMES["t"])

    def get_df(self):
        return read_forcing(self.path, self.forcing_type)

    def get_ds(self):
        df = self.get_df()
        df = df.set_index(["time", "lon", "lat"], drop=True)
        return df.to_xarray()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lst_path={self.path})"


class Waves:
    def __init__(self, lst_path: str, dt_cte: float = 1.0):
        """centralize wave data and properties

        Args:
            lst_path (str): path to lst-file of waves forcing.
            dt_cte (float, optional): time step for waves if spatially cte. Defaults to 1.0.
        """
        self.forcing_type = "waves"
        self.varnames = VARIABLE_NAMES[self.forcing_type]
        self.path = str(Path(lst_path).resolve())

        if len(pd.read_csv(self.path, delimiter="\s+").columns) != 1:
            df = read_cte_forcing(self.path, self.forcing_type, dt_cte)
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = 1
            self.ny = 1
            self.nt = len(df)
        else:
            df = read_forcing(self.path, self.forcing_type)

            self.extent = box(df.lon.min(), df.lat.min(), df.lon.max(), df.lat.max())
            (self.x_min, self.y_min, self.x_max, self.y_max) = self.extent.bounds
            (self.dx, self.nx) = _calculate_cell_properties(df, COORDINATE_NAMES["x"])
            (self.dy, self.ny) = _calculate_cell_properties(df, COORDINATE_NAMES["y"])
            (self.dt, self.nt) = _calculate_cell_properties(df, COORDINATE_NAMES["t"])

    def get_df(self):
        return read_forcing(self.path, self.forcing_type)

    def get_ds(self):
        df = self.get_df()
        df = df.set_index(["time", "lon", "lat"], drop=True)
        return df.to_xarray()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lst_path={self.path})"
