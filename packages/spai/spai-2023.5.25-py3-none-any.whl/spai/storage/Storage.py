import os

from ..models import *


class Storage:
    def __init__(self, path="data"):
        self.path = path

    def create(self, something):
        if isinstance(something, Path):
            dst_path = os.path.join(self.path, something.name)
            os.rename(something.path, dst_path)
            return dst_path
        pass

    def read():
        pass

    def update():
        pass

    def delete():
        pass
