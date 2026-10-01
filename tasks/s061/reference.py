def is_sorted(nums):
    return all(a <= b for a, b in zip(nums, nums[1:]))
