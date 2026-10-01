def longest_run(nums):
    best = cur = 0
    for i, x in enumerate(nums):
        cur = cur + 1 if i and x == nums[i - 1] else 1
        best = max(best, cur)
    return best
