def to_minutes(hhmm):
    parts = hhmm.split(":")
    if len(parts) != 2 or not all(p.isdigit() and len(p) == 2 for p in parts):
        raise ValueError(hhmm)
    h, m = int(parts[0]), int(parts[1])
    if h > 23 or m > 59:
        raise ValueError(hhmm)
    return h * 60 + m
