import base64


def fileAsBase64(path: str) -> str:
    """
    Convert a file on disk to a base64 string.

    Args:
        path (str): The path to the file on disk.

    Returns:
        str: The base64 string.
    """
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
