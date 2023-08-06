from .SHS2Downloader import SHS2Downloader
from sentinelhub import DataCollection


class SHS2L1CDownloader(SHS2Downloader):
    def __init__(self, download_folder="/tmp"):
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL2_L1C
