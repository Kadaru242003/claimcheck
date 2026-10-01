def rotate(matrix):
    return [list(row) for row in zip(*matrix[::-1])]
