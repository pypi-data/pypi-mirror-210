import json

from .fuzzy_json import parse


def loads(source: str):
    """Load data from String"""
    return json.loads(parse(source))


def load(filepath: str):
    """Load data from File"""
    return loads(open(filepath).read())


__all__ = [
    "load",
    "loads",
]
