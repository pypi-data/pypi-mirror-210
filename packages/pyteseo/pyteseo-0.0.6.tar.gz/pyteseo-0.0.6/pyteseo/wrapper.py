from __future__ import annotations

import os
import subprocess
from pathlib import Path
from shutil import copy2


from pyteseo.classes import Coastline, Currents, Grid, Waves, Winds
from pyteseo.defaults import (
    CFG_MAIN_MANDATORY_KEYS,
    CFG_SPILL_POINT_MANDATORY_KEYS,
    DIRECTORY_NAMES,
    FILE_NAMES,
    FILE_PATTERNS,
)
from pyteseo.export.grids import export_grids
from pyteseo.export.particles import export_particles
from pyteseo.export.properties import export_properties
from pyteseo.io.cfg import generate_parameters_for_cfg, write_cfg
from pyteseo.io.forcings import write_null_forcing
from pyteseo.io.hns_calib import write_hns_calib
from pyteseo.io.results import (
    read_grids_results,
    read_particles_results,
    read_properties_results,
)
from pyteseo.io.run import generate_parameters_for_run, write_run


TESEO_PATH = os.environ.get("TESEO_PATH")


class TeseoWrapper:
    def __init__(self, dir_path: str, simulation_keyword: str = "cas1"):
        """wrapper of configuration, execution and postprocess of a TESEO's simulation

        Args:
            path (str): path to the simulation folder
            simulation_keyword (str, optional): keyword to name simulation files. Defaults to "teseo".
        """
        print("\n")
        self.simulation_keyword = simulation_keyword
        self.path = str(Path(dir_path).resolve())
        self.create_folder_structure()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"

    def postprocessing(
        self,
        particles_file_formats=["geojson", "csv"],
        properties_file_formats=["json", "csv"],
        grids_file_formats=["nc"],
    ):
        print("\nPostprocessing results...\n")
        for k, v in {
            "particles": {
                "read": read_particles_results,
                "export": export_particles,
                "file_formats": particles_file_formats,
            },
            "properties": {
                "read": read_properties_results,
                "export": export_properties,
                "file_formats": properties_file_formats,
            },
            "grids": {
                "read": read_grids_results,
                "export": export_grids,
                "file_formats": grids_file_formats,
            },
        }.items():
            print(f"reading {k}...")
            df = v["read"](self.path)

            for file_format in v["file_formats"]:
                v["export"](df, file_format, self.output_dir)

    def create_folder_structure(self):
        """creates folder structure for TESEO simulation"""
        print("Creating TESEO folder structure...")
        path = Path(self.path)
        if not path.exists():
            path.mkdir(parents=True)

        input_dir = Path(path, DIRECTORY_NAMES["input"])
        if not input_dir.exists():
            input_dir.mkdir(parents=True)

        output_dir = Path(path, DIRECTORY_NAMES["output"])
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        self.input_dir = str(input_dir)
        self.output_dir = str(output_dir)
        print(f"DONE! Created @ {self.path}\n")

    def load_domain(self, src_dir: str):
        """load domain files (*.dat) from src_dir and copy them to the job input folder.

        Args:
            src_dir (str): path to the source folder.

        Raises:
            FileNotFoundError: grid file not founded in 'inputs' directory!
        """
        input_dir = Path(self.input_dir).resolve()

        if Path(src_dir).resolve() != input_dir:
            print("copying files to input-job path...")
            file_paths = [file for file in Path(src_dir).glob("*.dat")]
            for file in file_paths:
                copy2(file, Path(self.input_dir, file.name))

        print("Loading grid...")
        if Path(input_dir, FILE_NAMES["grid"]).exists():
            self.grid = Grid(Path(input_dir, FILE_NAMES["grid"]))
        else:
            raise FileNotFoundError("Grid-file is mandatory!")

        print("Loading coastline...")
        if Path(input_dir, FILE_NAMES["coastline"]).exists():
            self.coastline = Coastline(Path(input_dir, FILE_NAMES["coastline"]))
        else:
            print("No coastline defined!")

    def load_forcings(
        self,
        currents_dt_cte: float = 1,
        winds_dt_cte: float = 1,
        waves_dt_cte: float = 1,
    ):
        """load forcing files in simulation 'inputs' directory

        Args:
            currents_dt_cte (float, optional): dt for spatially cte currents (hours). Defaults to 1.
            winds_dt_cte (float, optional):  dt for spatially cte winds (hours). Defaults to 1.
            waves_dt_cte (float, optional):  dt for spatially cte waves (hours). Defaults to 1.
        """
        print("Loading currents...")
        input_dir = Path(self.input_dir).resolve()
        if Path(input_dir, FILE_NAMES["currents"]).exists():
            self.currents = Currents(
                Path(input_dir, FILE_NAMES["currents"]), currents_dt_cte
            )
        else:
            print("No currents defined, creating null currents...")
            write_null_forcing(input_dir, forcing_type="currents")
            self.currents = Currents(
                Path(input_dir, FILE_NAMES["currents"]), currents_dt_cte
            )
        print("Loading winds...")
        if Path(input_dir, FILE_NAMES["winds"]).exists():
            self.winds = Winds(Path(input_dir, FILE_NAMES["winds"]), winds_dt_cte)
        else:
            print("No winds defined, creating null winds...")
            write_null_forcing(input_dir, forcing_type="winds")
            self.winds = Winds(Path(input_dir, FILE_NAMES["winds"]), winds_dt_cte)

        print("Loading waves...")
        if Path(input_dir, FILE_NAMES["waves"]).exists():
            self.waves = Waves(Path(input_dir, FILE_NAMES["waves"]), waves_dt_cte)
        else:
            print("No waves defined, creating null waves...")
            write_null_forcing(input_dir, forcing_type="waves")
            self.waves = Waves(Path(input_dir, FILE_NAMES["waves"]), waves_dt_cte)

        print("DONE!\n")

    def setup(self, user_parameters: dict[str, any]):
        """create TESEO's configuration files (cfg and run)

        Args:
            user_parameters (dict[str, any]): parameters definde by the user to configure the simulation
        """
        check_user_minimum_parameters(user_parameters)
        print("Setting up TESEO's cfg-file...")
        cfg_parameters = generate_parameters_for_cfg(user_parameters)
        forcing_parameters = self._forcing_parameters
        file_parameters = self._file_parameters

        self.cfg_path = str(
            Path(self.path, FILE_PATTERNS["cfg"].replace("*", self.simulation_keyword))
        )
        write_cfg(
            output_path=self.cfg_path,
            filename_parameters=file_parameters,
            forcing_parameters=forcing_parameters,
            simulation_parameters=cfg_parameters,
        )
        print("cfg-file created\n")
        print("Setting up TESEO's cfg-file...")
        if "first_time_saved" not in user_parameters.keys():
            first_time_saved = min(
                [
                    spill_point["release_time"]
                    for spill_point in cfg_parameters["spill_points"]
                ]
            )
        else:
            first_time_saved = user_parameters["first_time_saved"]

        run_parameters = generate_parameters_for_run(user_parameters)
        if "coastline" in dir(self):
            n_coastal_polygons = self.coastline.n_polygons
        else:
            n_coastal_polygons = 0
        self.run_path = str(
            Path(self.path, FILE_PATTERNS["run"].replace("*", self.simulation_keyword))
        )
        write_run(
            path=self.run_path,
            run_parameters=run_parameters,
            first_time_saved=first_time_saved,
            n_coastal_polygons=n_coastal_polygons,
        )
        print("run-file created\n")

        if user_parameters["substance_type"] == "hns":
            print("Setting up TESEO's hns calibration-file")
            write_hns_calib(
                dir_path=self.input_dir, simulation_keyword=self.simulation_keyword
            )
            print("hns calibration-file created\n")
        print("DONE!")

    def run(self):
        """run TESEO simulation"""
        self.check_files()
        if not TESEO_PATH:
            raise NameError("TESEO_PATH environment variable is not defined")
        self.prepare_teseo_binary(TESEO_PATH)
        self.execute_simulation()

    def check_files(self):
        """check if minimum files required exists

        Raises:
            FileNotFoundError: if any file is not found
        """
        for path in [
            self.grid.path,
            self.path,
            self.input_dir,
            self.cfg_path,
            self.run_path,
        ]:
            if not Path(path).exists():
                raise FileNotFoundError(path)

    def prepare_teseo_binary(self, teseo_binary_path: str | Path):
        """copy TESEO model binary to simulation directory

        Args:
            teseo_binary_path (str): path to the binary

        Raises:
            FileNotFoundError: if binary not founded
        """
        if Path(teseo_binary_path).exists():
            self.teseo_binary_path = Path(self.path, Path(teseo_binary_path).name)
            copy2(teseo_binary_path, self.teseo_binary_path)
        else:
            raise FileNotFoundError(teseo_binary_path)

    def execute_simulation(self) -> None:
        """triggers TESEO simulation process"""

        # ------------------------------------------------------------------------
        # BUG - HOTFIX Change lstcurr.pre to lstcurr_UVW.pre when use 2D currents grids
        hotfix_01 = None
        if self.currents.dx and self.currents.dx:
            print("Hotfix_01.rename: lstcurr.pre --> lstcurr_UVW.pre")
            old_path = Path(self.currents.path)
            new_path = Path(old_path.parent, "lstcurr_UVW.pre")
            old_path.rename(new_path)
            hotfix_01 = True
            self.currents.path = str(new_path)
        # ------------------------------------------------------------------------
        hotfix_02 = None
        if self.currents.currents_depthavg:
            print("Hotfix_01.rename: lstcurr_depthavg.pre --> lstcurr_UVW_col.pre")
            old_path = Path(self.currents_depthavg_path)
            new_path = Path(old_path.parent, "lstcurr_UVW_col.pre")
            old_path.rename(new_path)
            hotfix_02 = True
            self.currents_depthavg_path = str(new_path)
        # ------------------------------------------------------------------------

        print(
            f"subprocess running... {self.teseo_binary_path} {Path(self.cfg_path).name} @ {self.path}"
        )
        subprocess.run(
            [f"{self.teseo_binary_path}", f"{Path(self.cfg_path).name}"],
            cwd=self.path,
            check=True,
        )

        # ------------------------------------------------------------------------
        # BUG - HOTFIX Change lstcurr.pre to lstcurr_UVW.pre when use 2D currents grids
        print("Hotfix_01.revert_rename: lstcurr_UVW.pre --> lstcurr.pre")
        if hotfix_01:
            old_path = Path(self.currents.path)
            new_path = Path(old_path.parent, "lstcurr.pre")
            old_path.rename(new_path)
            del hotfix_01
            self.currents.path = str(new_path)
        # ------------------------------------------------------------------------
        # BUG - HOTFIX Change lstcurr.pre to lstcurr_UVW.pre when use 2D currents grids
        print("Hotfix_02.revert_rename: lstcurr_UVW_col.pre --> lstcurr_depthavg.pre")
        if hotfix_02:
            old_path = Path(self.currents_depthavg_path)
            new_path = Path(old_path.parent, "lstcurr_depthavg.pre")
            old_path.rename(new_path)
            del hotfix_02
            self.currents_depthavg_path = str(new_path)
        # ------------------------------------------------------------------------

    @property
    def load_particles(self):
        read_particles_results(self.path)

    @property
    def load_properties(self):
        read_properties_results(self.path)

    @property
    def load_grids(self):
        read_grids_results(self.path)

    @property
    def _file_parameters(self) -> dict:
        d = {}
        d["inputs_directory"] = DIRECTORY_NAMES["input"] + "/"
        d["grid_filename"] = Path(self.grid.path).name
        return d

    @property
    def _forcing_parameters(self) -> dict:
        d = {}
        d["currents_nt"] = self.currents.nt
        d["currents_dt"] = self.currents.dt
        d["currents_n_points"] = self.currents.nx * self.currents.ny
        d["winds_nt"] = self.winds.nt
        d["winds_dt"] = self.winds.dt
        d["winds_n_points"] = self.winds.nx * self.winds.ny
        d["waves_nt"] = self.waves.nt
        d["waves_dt"] = self.waves.dt
        d["waves_n_points"] = self.waves.nx * self.waves.ny
        return d


def check_user_minimum_parameters(
    user_parameters: dict[str, any],
    cfg_mandatory_keys: dict[str, any] = CFG_MAIN_MANDATORY_KEYS,
    cfg_spill_point_mandatory_keys: dict[str, any] = CFG_SPILL_POINT_MANDATORY_KEYS,
) -> None:
    check_keys(d=user_parameters, mandatory_keys=cfg_mandatory_keys)
    for spill_point in user_parameters["spill_points"]:
        if user_parameters["substance_type"] in ["oil", "hns"]:
            check_keys(
                d=spill_point,
                mandatory_keys=cfg_spill_point_mandatory_keys
                + ["substance", "mass", "thickness"],
            )
        else:
            check_keys(d=spill_point, mandatory_keys=cfg_spill_point_mandatory_keys)


def check_keys(d, mandatory_keys: list[str]) -> None:
    for key in mandatory_keys:
        if key not in d.keys():
            raise KeyError(f"Mandatory parameter [{key}] not found")
