import re
from collections import Counter
def word_count(text):
    return dict(Counter(re.findall(r"[a-z]+", text.lower())))
