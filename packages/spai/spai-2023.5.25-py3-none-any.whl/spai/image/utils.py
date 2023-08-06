import rasterio as rio
import numpy as np
from PIL import Image


# TODO: should know the source in order to generate the rgb thumbnail
def thumbnail(image, size=None, factor=1):
    ds = rio.open(image)
    rgb = ds.read((4, 3, 2)) / 4000
    rgb = np.clip(rgb, 0, 1)
    rgb = np.moveaxis(rgb, 0, -1)
    rgb = (rgb * 255).astype(np.uint8)
    image = Image.fromarray(rgb)
    if size:
        image.thumbnail(size)
    elif factor != 1:
        assert factor > 0, "factor must be greater than 0"
        return image.resize((int(image.width // factor), int(image.height // factor)))
    return image
