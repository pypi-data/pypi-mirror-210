from pathlib import Path
from shutil import rmtree

import pandas as pd
import geopandas as gpd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.utils import _convert_longitude_range
from pyteseo.io.coastline import (
    _split_polygons,
    read_coastline,
    write_coastline,
    coastline_df_to_gdf,
    create_coastline_from_shpapefile,
)


data_path = Path(__file__).parent.parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "filename", [("coastline.dat"), ("coastline_othernanformat.dat")]
)
def test_split_polygons(filename):
    coastline_path = Path(data_path, filename)
    df = pd.read_csv(coastline_path, delimiter="\s+", header=None, names=["lon", "lat"])

    coastline_df = _split_polygons(df)

    assert isinstance(coastline_df, pd.DataFrame)
    assert len(coastline_df.polygon.unique()) == 4


@pytest.mark.parametrize(
    "file, error",
    [
        ("coastline.dat", None),
        ("not_existent_file.dat", "not_exist"),
        ("coastline_error_range.dat", "bad_format"),
        ("grid.dat", "bad_format"),
    ],
)
def test_read_coastline(file, error):
    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_coastline(path)
    elif error == "bad_format":
        with pytest.raises(ValueError):
            df = read_coastline(path)
    else:
        df = read_coastline(path)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "lon" in df.columns
        assert "lat" in df.columns
        assert "polygon" in df.columns


@pytest.mark.parametrize("error", [(None), ("df_n_var"), ("df_varnames")])
def test_write_coastline(error, setup_teardown):
    coastline_path = Path(data_path, "coastline.dat")
    output_path = Path(tmp_path, "test_coastline.dat")

    df = read_coastline(path=coastline_path)

    if error == "df_n_var":
        df = df[["lon", "lat"]]
        with pytest.raises(ValueError):
            write_coastline(df=df, path=output_path)

    elif error == "df_varnames":
        df = df.rename(columns={"lon": "longitude"})
        with pytest.raises(ValueError):
            write_coastline(df=df, path=output_path)

    else:
        df = _convert_longitude_range(df)
        write_coastline(df=df, path=output_path)
        newdf = read_coastline(path=output_path)

        assert all(newdf.get(["lon", "lat"]) == df.get(["lon", "lat"]))


def test_convert_coastline_df_to_gdf():
    coastline_path = Path(data_path, "coastline.dat")

    df = read_coastline(coastline_path)
    gdf = coastline_df_to_gdf(df)

    assert isinstance(df, pd.DataFrame)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert len(df) != 0
    assert len(gdf) != 0
    assert len(df) > len(gdf)
    assert len(df.polygon.unique()) == len(gdf)


def test_create_coastline_from_shp(setup_teardown):
    shp_file = "pyteseo/tests/data/shapefile_cantabria/Cantabria.shp"
    coastline_path = Path(tmp_path, "costa.dat")
    create_coastline_from_shpapefile(shp_file, coastline_path)
    assert coastline_path.exists()
