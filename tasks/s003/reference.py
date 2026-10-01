import re

def parse_duration(text):
    if not text:
        raise ValueError("empty")
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", text)
    if not m or not any(m.groups()):
        raise ValueError("bad format")
    h, mi, s = (int(g) if g else 0 for g in m.groups())
    return h * 3600 + mi * 60 + s
