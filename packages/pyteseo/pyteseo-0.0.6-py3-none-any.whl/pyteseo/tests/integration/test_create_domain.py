import pytest
from pathlib import Path
from shutil import rmtree

from pyteseo.defaults import FILE_NAMES
from pyteseo.services import create_domain


tmp_path = Path("tmp_test_domain_generation")
domain_name = "ibiza"
domain_bbox = (1.05, 38.55, 1.7, 39.2)

# FIXME - Make antimeridian compatible!
# convert bbox (175, -20, -175, -15)
# slice(175, -175) to slice = slice1(-lon,lon.max()) | slice2(lon.min(), +lon)

# domain_name = "antimeridiano"
# domain_bbox = (175, -20, -175, -15)


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.slow
def test_create_domain(setup_teardown):
    create_domain(
        tmp_path, domain_name, domain_bbox, "gebco_2020", "gshhs", n_max_pol=9
    )

    assert Path(tmp_path, domain_name, FILE_NAMES["grid"]).exists()
    assert Path(tmp_path, domain_name, FILE_NAMES["coastline"]).exists()
    assert Path(tmp_path, domain_name, f"{domain_name}_domain.png").exists()
