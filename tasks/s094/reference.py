from itertools import accumulate
def cumulative_max(nums):
    return list(accumulate(nums, max))
