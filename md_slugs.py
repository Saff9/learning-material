import re
import unicodedata


def slugify(value, separator="-"):
    """GitHub-style slug: remove punctuation, keep consecutive hyphens."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"\s", separator, value)
    return value
