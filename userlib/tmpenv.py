"""
Provide an environment of temp file
"""
import tempfile
import os
from typing import Callable, Optional


class TmpFile:
    """Wrapped TmpFile Processing"""
    def __init__(
        self,
        prefix: str,
        ext: Optional[str] = None,
        perm: Optional[int] = None
    ):
        self.prefix, self.extension = prefix, ext if ext is not None else ""
        self.fd, self.fp = tempfile.mkstemp(
            prefix=f"{self.prefix}-",
            suffix=f".{self.extension}" if self.extension else ""
        )  # 保留 fd 以备不时之需
        os.chmod(self.fp, perm or 0o644)
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.file.close()
        os.remove(self.fp)

    def open(self, mode: str = "r+"):
        """
        open temp file.
        """
        self.file = open(self.fp, mode)
        return self.file

    def contain(self, f: Callable[[], None]):
        # idea 1: decorator function
        pass


def gen_tmp(*args, **kwargs):
    # idea 2: 'with' syntax
    return TmpFile(**args, **kwargs)
