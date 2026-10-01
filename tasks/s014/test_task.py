from solution import int_to_roman
def test_values():
    assert int_to_roman(4) == "IV"
    assert int_to_roman(58) == "LVIII"
    assert int_to_roman(1994) == "MCMXCIV"
    assert int_to_roman(3999) == "MMMCMXCIX"
