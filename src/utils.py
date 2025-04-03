import os
import platform


def get_init_dir():
    system_name = platform.system()
    if system_name == "Windows":
        return os.path.expandvars("%USERPROFILE%")
    elif system_name == "Linux" or \
            system_name == "macOS" or \
            system_name == "Darwin":
        return os.path.expanduser("~")
    else:
        return ""


def create_logs_directory():
    if not os.path.exists("../logs"):
        os.makedirs("../logs")
