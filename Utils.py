import os


def path_wrapper(path: str):
    os.makedirs(path, exist_ok=True)
    return path
