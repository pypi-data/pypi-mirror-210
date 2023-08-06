import os
from sentinelhub import SHConfig, SentinelHubCatalog
from sentinelhub import CRS, BBox
from sentinelhub.data_collections import DataCollection


class SHExplorer:
    def __init__(self, time_interval, sensor, **kargs):
        self.query, self.fields = None, {
            "include": ["id", "properties.datetime", "assets.thumbnail.href"],
            "exclude": [],
        }
        self.config = SHConfig()
        if sensor == "S1":
            self.data_collection = DataCollection.SENTINEL1
        elif sensor == "S2L1C" or sensor == "S2L2A":
            # no thumbnail for S2L2A, use the one for S2L1C
            self.data_collection = DataCollection.SENTINEL2_L1C
            if "cloud_cover" in kargs:
                cloud_cover = kargs["cloud_cover"]
                self.query = f"eo:cloud_cover < {cloud_cover}"
                self.fields["include"].append("properties.eo:cloud_cover")
        elif sensor == "S5P":
            self.data_collection = DataCollection.SENTINEL5P
            # self.data_collection = DataCollection.SENTINEL3_OLCI
            self.config.sh_base_url = DataCollection.SENTINEL5P.service_url
            # self.config.sh_base_url = DataCollection.SENTINEL3_OLCI.service_url
        else:
            raise Exception("Invalid sensor")
        self.time_interval = time_interval
        self.config.sh_client_id = os.environ["SH_CLIENT_ID"]
        self.config.sh_client_secret = os.environ["SH_CLIENT_SECRET"]
        self.config.save()

    def search(self, gdf):
        # generate the bbox containing the geometry
        mybbox = BBox(bbox=gdf.total_bounds.tolist(), crs=CRS.WGS84)
        # query (different for each server: pleiades, spot, sentinelhub...)
        catalog = SentinelHubCatalog(config=self.config)
        search_iterator = catalog.search(
            self.data_collection,
            bbox=mybbox,
            time=self.time_interval,
            filter=self.query,
            fields=self.fields,
        )
        _results = list(search_iterator)
        results = []
        for result in _results:
            data = {
                "id": result["id"],
                "thumbnail": result["assets"]["thumbnail"]["href"]
                if "assets" in result
                else None,
                "date": result["properties"]["datetime"],
            }
            if "eo:cloud_cover" in result["properties"]:
                data["cloud_cover"] = result["properties"]["eo:cloud_cover"]
            results.append(data)
        return results
