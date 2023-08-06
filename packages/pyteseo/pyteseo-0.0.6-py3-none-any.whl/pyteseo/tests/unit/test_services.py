import pytest
from pyteseo.services import set_spill_point
from datetime import datetime


def test_set_spill_point():
    spill_point = set_spill_point(
        substance_type="oil",
        lon=1.45,
        lat=38.85,
        initial_width=10,
        initial_length=10,
        mass=1000,
        thickness=0.1,
        release_time=datetime.utcnow(),
        substance="tia juana",
    )

    assert isinstance(spill_point, dict)
    assert len(set_spill_point.__code__.co_varnames) == len(spill_point.keys())


def test_set_spill_point_fails():
    with pytest.raises(ValueError):
        _ = set_spill_point(
            substance_type="chemical",
            lon=1.45,
            lat=38.85,
            initial_width=10,
            initial_length=10,
            mass=1000,
            thickness=0.1,
            release_time=datetime.utcnow(),
            substance="acetona",
        )
