from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.io.grid import read_grid, write_grid


data_path = Path(__file__).parent.parent / "data"
tmp_path = Path("tmp_tests_io_grid")


@pytest.fixture
def setup_teardown():
    tmp_path.mkdir(exist_ok=True)
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "file, error",
    [
        ("grid.dat", None),
        ("not_existent_file.dat", "not_exist"),
        ("grid_error_var.dat", "bad_format"),
    ],
)
def test_read_grid(file, error):
    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_grid(path, nan_value=-9999)
    elif error == "bad_format":
        with pytest.raises(ValueError):
            df = read_grid(path, nan_value=-9999)
    else:
        df = read_grid(path, nan_value=-9999)
        assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "error",
    [(None), ("df_n_var"), ("df_varnames"), ("lonlat_range"), ("sorting")],
)
def test_write_grid(error, setup_teardown):
    grid_path = Path(data_path, "grid.dat")
    output_path = Path(tmp_path, "test_grid.dat")

    df = read_grid(path=grid_path, nan_value=-9999)

    if error == "df_n_var":
        df["var"] = 123
        with pytest.raises(ValueError):
            write_grid(df=df, path=output_path, nan_value=-999)

    elif error == "df_varnames":
        df = df.rename(columns={"lon": "longitude"})
        with pytest.raises(ValueError):
            write_grid(df=df, path=output_path, nan_value=-999)

    elif error == "lonlat_range":
        df["lon"][0] = 360
        with pytest.raises(ValueError):
            write_grid(df=df, path=output_path, nan_value=-999)

    elif error == "sorting":
        df["lat"][0] == 90
        df["lat"][1] == 89

        write_grid(df=df, path=output_path, nan_value=-999)
        newdf = read_grid(path=output_path)
        output_path.unlink()
        output_path.parent.rmdir()
        assert all(newdf.get(["lon", "lat"]) == df.get(["lon", "lat"])) and all(
            df[df.get("depth").notna()] == newdf[newdf.get("depth").notna()]
        )

    else:
        write_grid(df=df, path=output_path, nan_value=-999)
        newdf = read_grid(path=output_path)
        output_path.unlink()
        output_path.parent.rmdir()
        assert all(newdf.get(["lon", "lat"]) == df.get(["lon", "lat"])) and all(
            df[df.get("depth").notna()] == newdf[newdf.get("depth").notna()]
        )
