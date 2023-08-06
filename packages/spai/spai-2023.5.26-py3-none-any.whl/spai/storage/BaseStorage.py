from PIL import Image
import numpy as np
import pandas as pd


class BaseStorage:
    def __init__(self):
        pass

    def create(self, data, name, **kwargs):
        if isinstance(data, str):  # puedo asumir que siempre será un path?
            return self.create_from_path(data, name)
        elif isinstance(data, Image.Image):
            return self.create_from_image(data, name)
        elif isinstance(data, np.ndarray):
            ext = name.split(".")[-1]
            if ext in ["tif", "tiff"]:
                if "ds" in kwargs:
                    return self.create_from_rasterio(data, name, kwargs["ds"])
                raise TypeError("Missing ds argument")
            elif ext == "npy":
                return self.create_from_array(data, name)
            else:
                raise TypeError("Not a valid array type")
        elif isinstance(data, pd.core.frame.DataFrame):
            ext = name.split(".")[-1]
            if ext == "csv":
                return self.create_from_csv(data, name)
            elif ext == "json":
                return self.create_from_json(data, name)
            else:
                raise TypeError("Not a valid dataframe type")
        else:
            raise TypeError("Not a valid type")

    def create_from_data(self, data, path):
        with open(path, "wb") as f:
            f.write(data.read())
        return path

    def read(self, name):
        ext = name.split(".")[-1]
        if ext == "npy":
            return self.read_from_array(name)
        elif ext in ["tif", "tiff"]:
            return self.read_from_rasterio(name)
        elif ext == "csv":
            return self.read_from_csv(name)
        elif ext == "json":
            return self.read_from_json(name)
        raise TypeError("Not a valid type")

    def update(self):
        pass

    def delete(self):
        pass

    def list(self, pattern="*"):
        pass
