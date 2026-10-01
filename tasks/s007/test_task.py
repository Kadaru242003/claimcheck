from solution import fizzbuzz
def test_15():
    r = fizzbuzz(15)
    assert r[:5] == ["1","2","Fizz","4","Buzz"]
    assert r[14] == "FizzBuzz" and len(r) == 15
def test_zero():
    assert fizzbuzz(0) == []
