from math import gcd
from functools import reduce
def lcm_all(nums):
    return reduce(lambda a, b: a * b // gcd(a, b), nums)
