import os
from functools import wraps


def restore_cwd(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_cwd = os.getcwd()
        try:
            return func(*args, **kwargs)
        finally:
            os.chdir(original_cwd)

    return wrapper
