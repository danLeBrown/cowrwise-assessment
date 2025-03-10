import re

def slugify(s: str) -> str:
    # remove all non-alphanumeric characters
    s = re.sub(r"[^\w\s-]", "", s)
    # remove all whitespace
    s = re.sub(r"\s+", "-", s)
    # remove leading and trailing whitespace
    s = s.strip("-")
    
    return s.lower().replace(" ", "-")