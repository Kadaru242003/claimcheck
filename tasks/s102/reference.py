def clamp_all(nums, lo, hi):
    return [max(lo, min(x, hi)) for x in nums]
