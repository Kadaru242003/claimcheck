def max_gap(nums):
    s = sorted(nums)
    return max((b - a for a, b in zip(s, s[1:])), default=0)
