def move_zeros(nums):
    nz = [x for x in nums if x != 0]
    return nz + [0] * (len(nums) - len(nz))
