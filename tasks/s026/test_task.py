from solution import fib
def test_small():
    assert [fib(i) for i in range(8)] == [0,1,1,2,3,5,8,13]
def test_large():
    assert fib(90) == 2880067194370816120
