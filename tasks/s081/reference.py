def triangle_type(a, b, c):
    x, y, z = sorted((a, b, c))
    if x <= 0 or x + y <= z:
        return 'invalid'
    if x == z:
        return 'equilateral'
    if x == y or y == z:
        return 'isosceles'
    return 'scalene'
