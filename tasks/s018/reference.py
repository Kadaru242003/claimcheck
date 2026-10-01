def count_islands(grid):
    seen = set()
    rows, cols = len(grid), len(grid[0]) if grid else 0
    def fill(r, c):
        stack = [(r, c)]
        while stack:
            r, c = stack.pop()
            if (r, c) in seen or not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != '1':
                continue
            seen.add((r, c))
            stack += [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in seen:
                count += 1
                fill(r, c)
    return count
