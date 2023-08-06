from .SHS2Downloader import SHS2Downloader
from sentinelhub import DataCollection


class SHS2L2ADownloader(SHS2Downloader):

    def __init__(self, download_folder='/tmp'):
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL2_L2A
