import re
def is_hex_color(s):
    return re.fullmatch(r'#[0-9a-fA-F]{6}', s) is not None
