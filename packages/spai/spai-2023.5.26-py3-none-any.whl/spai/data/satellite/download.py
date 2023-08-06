from .sentinelhub import SHS2L2ADownloader, SHS2L1CDownloader, SHS1Downloader
import geopandas as gpd
import shutil


# def download_satellite_image(location, date, sensor, options):
def download_satellite_image(date, sensor, storage):
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
    download_dir = "/tmp/sentinelhub"
    if sensor == "S2L2A":
        downloader = SHS2L2ADownloader(download_dir)
    elif sensor == "S2L1C":
        downloader = SHS2L1CDownloader(download_dir)
    elif sensor == "S1":
        downloader = SHS1Downloader(download_dir)
    else:
        raise Exception(f"sensor {sensor} not supported")
    dst_path = downloader.download(gdf, date)
    dst_path = storage.create(dst_path, name=f"{sensor}_{date}.tif")
    shutil.rmtree(download_dir)
    return dst_path
