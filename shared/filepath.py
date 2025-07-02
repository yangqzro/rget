import os
import platform


def get_download_dir() -> str:
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:  # Linux / macOS
        return os.path.expanduser("~/Downloads")


def join(*paths: str) -> str:
    return os.path.join(*paths)
