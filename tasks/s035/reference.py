from collections import Counter
def mode(nums):
    c = Counter(nums)
    return min(c, key=lambda x: (-c[x], x))
