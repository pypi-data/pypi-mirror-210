from datetime import datetime, timedelta
from dotenv import load_dotenv

from spai.storage import Storage
from spai.data.satellite import explore_satellite_images, download_satellite_image

load_dotenv()

# create time range (3 months)
now = datetime.now()
last_months = now - timedelta(days=30 * 3)
time_interval = (last_months.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

# explore available images
print("Looking for images in the range", time_interval)
images = explore_satellite_images(time_interval, cloud_cover=10)
if len(images) == 0:
    raise ValueError("No images found")

# download images and save locally
storage = Storage("data")
sensor = "S2L2A"  # or 'S2L1C'
existing_images = storage.list(f"{sensor}*.tif")
dates = [image.split("_")[1].split(".")[0] for image in existing_images]
print("Found", len(images), f"image{'s' if len(images) > 1 else ''}")
for image in images:
    # check if image is already downloaded
    date = image["date"].split("T")[0]
    if date in dates:
        print("Image already downloaded:", date)
        continue
    print("Downloading new image:", date)
    path = download_satellite_image(date, sensor, storage)
    print("Image saved at", path)
