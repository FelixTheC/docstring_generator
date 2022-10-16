from pathlib import Path

CACHE_FOLDER = Path(".docstring_generator")

if not CACHE_FOLDER.exists():
    CACHE_FOLDER.mkdir()
