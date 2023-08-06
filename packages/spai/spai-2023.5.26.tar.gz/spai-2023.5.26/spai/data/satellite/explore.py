from .sentinelhub import SHExplorer
import geopandas as gpd


def explore_satellite_images(time_interval, sensor="S2L2A", **kargs):
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
    explorer = SHExplorer(time_interval, sensor, **kargs)
    results = explorer.search(gdf)
    return results
