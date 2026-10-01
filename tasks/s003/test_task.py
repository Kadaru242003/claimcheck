import pytest
from solution import parse_duration

def test_hours_minutes():
    assert parse_duration("1h30m") == 5400

def test_all_units():
    assert parse_duration("1h5m30s") == 3930

def test_minutes_only():
    assert parse_duration("45m") == 2700

def test_bad_unit():
    with pytest.raises(ValueError):
        parse_duration("5d")

def test_empty():
    with pytest.raises(ValueError):
        parse_duration("")
