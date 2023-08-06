import os
from datetime import timedelta
from sentinelhub import (
    SHConfig,
    MimeType,
    CRS,
    BBox,
    SentinelHubRequest,
    bbox_to_dimensions,
    BBoxSplitter,
)
import glob
from datetime import datetime
import math


class SHDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder
        self.config = SHConfig()
        self.config.sh_client_id = os.environ["SH_CLIENT_ID"]
        self.config.sh_client_secret = os.environ["SH_CLIENT_SECRET"]
        self.mosaicking_order = None

    def compute_image_size(self, gdf):
        self.bbox = BBox(bbox=gdf.total_bounds.tolist(), crs=CRS.WGS84)
        self.bbox_size = bbox_to_dimensions(self.bbox, resolution=self.resolution)
        return self.bbox_size

    def prepare_time_interval(self, date):
        date = datetime.strptime(date, "%Y-%m-%d")
        date_day_before = date - timedelta(days=1)
        date_next_day = date + timedelta(days=1)
        date_day_before = date_day_before.strftime("%Y-%m-%d")
        date_next_day = date_next_day.strftime("%Y-%m-%d")
        self.time_interval = (date_day_before, date_next_day)

    def download(self, gdf, date):
        self.prepare_time_interval(date)
        self.compute_image_size(gdf)
        if self.bbox_size[0] > 2500 or self.bbox_size[1] > 2500:
            return self.download_large_area(gdf)
        return self.download_small_area(self.bbox)

    def request_bands(self, bbox):
        return SentinelHubRequest(
            data_folder=self.download_folder,
            evalscript=self.script,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=self.data_collection,
                    time_interval=self.time_interval,
                    mosaicking_order=self.mosaicking_order,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=self.bbox,
            size=bbox_to_dimensions(bbox, resolution=self.resolution),
            config=self.config,
        )

    def download_small_area(self, bbox):
        request_bands = self.request_bands(bbox)
        request_bands.save_data()
        downloaded_files = glob.glob(f"{self.download_folder}/*/response.tiff")
        assert len(downloaded_files) > 0, "No files downloaded"
        assert len(downloaded_files) == 1, "There should be only one response file"
        folder = downloaded_files[0]
        return folder

    def get_tiles(self):
        # compute number of images to download
        self.max_resolution = 2500
        return (
            math.ceil(self.bbox_size[0] / self.max_resolution),
            math.ceil(self.bbox_size[1] / self.max_resolution),
        )

    def download_large_area(self, gdf):
        tiles = self.get_tiles()
        geom = gdf.geometry.unary_union  # ???
        bbox_splitter = BBoxSplitter([geom], CRS.WGS84, tiles)
        bbox_list = bbox_splitter.get_bbox_list()
        for i, bbox in enumerate(bbox_list):
            request_bands = self.request_bands(bbox)
            request_bands.save_data()
        downloaded_files = glob.glob(f"{self.download_folder}/*/response.tiff")
        dst_path = self.download_folder + "/output.tiff"
        command = f"gdal_merge.py -o {dst_path} " + " ".join(downloaded_files)
        os.system(command)
        return dst_path
