def second_largest(nums):
    vals = sorted(set(nums), reverse=True)
    return vals[1] if len(vals) > 1 else None
