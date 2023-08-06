"""Common helper functions."""

import re

def dict_get(data: dict, path: str, default=None):
    """Gets a value from a dict using a given path."""
    path_list = re.split(r"\.", path, flags=re.IGNORECASE)
    result = data
    for key in path_list:
        try:
            key = int(key) if key.isnumeric() else key
            result = result[key]
        except:
            result = default
            break

    return result
