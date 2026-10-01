from solution import remove_vowels

def test_cases():
    assert remove_vowels('Programming') == 'Prgrmmng'
    assert remove_vowels('AEIOU') == ''
