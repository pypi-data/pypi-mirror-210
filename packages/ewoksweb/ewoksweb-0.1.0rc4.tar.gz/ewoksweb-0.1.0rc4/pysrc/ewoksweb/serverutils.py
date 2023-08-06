import os


def get_static_root() -> str:
    return os.path.join(os.path.dirname(__file__), "static")
