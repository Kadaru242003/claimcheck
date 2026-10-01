import os
def common_prefix(words):
    return os.path.commonprefix(words) if words else ""
