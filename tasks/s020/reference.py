def is_ipv4(s):
    parts = s.split('.')
    if len(parts) != 4:
        return False
    for p in parts:
        if not p.isdigit() or not p.isascii() or (len(p) > 1 and p[0] == '0') or int(p) > 255:
            return False
    return True
