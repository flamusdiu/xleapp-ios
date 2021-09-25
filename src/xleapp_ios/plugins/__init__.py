import importlib
from pathlib import Path


def plugins() -> Path:
    '''Returns path of the plugin folder'''
    return Path(importlib.util.find_spec(__name__).origin).parent
