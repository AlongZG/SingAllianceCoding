import os


def path_wrapper(path: str) -> str:
    """Helper function to create directory if not exit.

    Parameters
    ----------
    - path : str
        The dir path.

    Returns
    -------
    - path : str
        The dir path.
    """
    os.makedirs(path, exist_ok=True)
    return path
