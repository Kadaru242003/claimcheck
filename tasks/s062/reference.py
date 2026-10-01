def diffs(nums):
    return [b - a for a, b in zip(nums, nums[1:])]
