import pytest
from pyteseo.io.substances import (
    get_offline_substance,
    get_offline_substance_names,
)


@pytest.mark.parametrize(
    "substance_type, substance_name, exception",
    [
        ("oils", "lagunillas", FileNotFoundError),
        ("hns", "acetonas", ValueError),
    ],
)
def test_get_offline_substance_raises(substance_type, substance_name, exception):
    with pytest.raises(exception):
        df = get_offline_substance(substance_type, substance_name)
        assert df.name.values == substance_name


@pytest.mark.parametrize("substance_type", ["oil", "hns"])
def test_get_offline_substance_names(substance_type):
    substance_names = get_offline_substance_names(substance_type)
    assert len(substance_names) >= 1


def test_get_offline_substance_names_raises(
    substance_type="bad_name", exception=FileNotFoundError
):
    with pytest.raises(exception):
        _ = get_offline_substance_names(substance_type)
