import pytest
from solution import to_minutes
def test_valid():
    assert to_minutes("13:45") == 825
    assert to_minutes("00:00") == 0
def test_invalid():
    for bad in ["24:00", "12:60", "1245", "ab:cd", ""]:
        with pytest.raises(ValueError):
            to_minutes(bad)
