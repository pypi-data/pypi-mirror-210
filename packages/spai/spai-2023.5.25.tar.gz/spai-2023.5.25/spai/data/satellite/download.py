from .sentinelhub import SHS2L2ADownloader
import geopandas as gpd
from ...models import Path


# def download_satellite_image(location, date, sensor, options):
def download_satellite_image(date, storage):
    # aoi = retrieve_aoi_from_location(location)
    gdf = gpd.GeoDataFrame.from_features(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [2.058000718868186, 41.46183613708533],
                                [2.058000718868186, 41.4318016264732],
                                [2.097234913854237, 41.4318016264732],
                                [2.097234913854237, 41.46183613708533],
                                [2.058000718868186, 41.46183613708533],
                            ]
                        ],
                        "type": "Polygon",
                    },
                }
            ],
        },
        crs=4326,  # validate coords are lat/lon !
    )
    # dst_folder = "/tmp/sentinelhub"
    downloader = SHS2L2ADownloader()
    dst_path = downloader.download(gdf, date)
    dst_path = Path(path=dst_path, name=f"S2L2A_{date}.tif")
    return storage.create(dst_path)
    # shutil.rmtree("./outputs/tifs", ignore_errors=True)
    # request.save_data()
    # downloaded_files = glob("./outputs/tifs/*/response.tiff")
    # # client.fput_object(bucket, f'S2L2A_{new_date}.tif', downloaded_files[0])
    # ds = rio.open(downloaded_files[0])
    # rgb = ds.read((4, 3, 2)) / 4000
    # rgb = np.clip(rgb, 0, 1)
    # rgb = np.moveaxis(rgb, 0, -1)
    # rgb = (rgb * 255).astype(np.uint8)
    # image = Image.fromarray(rgb)
    # # save image in cloud bucket
    # image.save(f"./outputs/S2L2A_{new_date}.png")
    # client.fput_object(
    #     bucket, f"S2L2A_{new_date}.png", f"./outputs/S2L2A_{new_date}.png"
    # )
    # # get url
    # url = client.presigned_get_object(bucket, f"S2L2A_{new_date}.png")
    # return url
