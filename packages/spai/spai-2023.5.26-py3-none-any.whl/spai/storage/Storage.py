import os
from glob import glob
import rasterio as rio
import numpy as np
import pandas as pd

from .BaseStorage import BaseStorage


class Storage(BaseStorage):
    def __init__(self, path="data"):
        super().__init__()
        self.path = path
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"{path} created")

    def get_path(self, name):
        return os.path.join(self.path, name)

    def create_from_path(self, data, name):
        dst_path = self.get_path(name)
        os.rename(data, dst_path)
        return dst_path

    def create_from_image(self, data, name):
        dst_path = self.get_path(name)
        data.save(dst_path)
        return dst_path

    def create_from_rasterio(self, x, name, ds, window=None):
        dst_path = self.get_path(name)
        kwargs = ds.meta.copy()
        transform = ds.transform if window is None else ds.window_transform(window)
        kwargs.update(
            driver="GTiff",
            count=1 if x.ndim < 3 else x.shape[0],
            height=x.shape[0] if x.ndim < 3 else x.shape[1],
            width=x.shape[1] if x.ndim < 3 else x.shape[2],
            dtype=np.uint8 if x.dtype == "bool" else x.dtype,
            crs=ds.crs,
            transform=transform,
            # nbits=1 if x.dtype == 'bool' else
        )
        with rio.open(dst_path, "w", **kwargs) as dst:
            bands = 1 if x.ndim < 3 else [i + 1 for i in range(x.shape[0])]
            dst.write(x, bands)
        return dst_path

    def create_from_array(self, data, name):
        dst_path = self.get_path(name)
        np.save(dst_path, data)
        return dst_path

    def create_from_csv(self, data, name):
        dst_path = self.get_path(name)
        data.to_csv(dst_path)
        return dst_path

    def create_from_json(self, data, name):
        dst_path = self.get_path(name)
        data.to_json(dst_path)
        return dst_path

    def list(self, pattern="*"):
        paths = glob(os.path.join(self.path, pattern))
        # strip base path
        return [p.replace(self.path + "/", "") for p in paths]

    def read_from_array(self, name, path=None):
        if path is None:
            path = self.get_path(name)
        return np.load(path)

    def read_from_rasterio(self, name):
        return rio.open(self.get_path(name))

    def read_from_csv(self, name):
        return pd.read_csv(self.get_path(name), index_col=0)

    def read_from_json(self, name):
        return pd.read_json(self.get_path(name))
