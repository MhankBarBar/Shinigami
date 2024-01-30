import platform


def is_windows() -> bool:
    return platform.system() == "Windows"
