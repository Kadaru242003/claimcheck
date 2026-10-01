from solution import matmul

def test_cases():
    assert matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [[19, 22], [43, 50]]
    assert matmul([[1, 2, 3]], [[1], [2], [3]]) == [[14]]
