import pdb
import sys

from . import config


def debug(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if config.DEBUG and sys.stdout.isatty():
                pdb.post_mortem()  # pragma: no cover
            raise

    return wrapper
