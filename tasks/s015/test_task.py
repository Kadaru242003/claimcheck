from solution import binary_search
def test_found():
    assert binary_search([1,3,5,7,9], 7) == 3
def test_missing():
    assert binary_search([1,3,5], 4) == -1
def test_empty():
    assert binary_search([], 1) == -1
