import json

import ee
import geopandas as gpd


class GEEFeatureCollection():
    fc = None

    def get_fc(self):
        return self.fc

    @classmethod
    def from_shapefile(cls, shp_path):
        gdf = gpd.read_file(shp_path)
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        geojson = json.loads(gdf.to_json())
        return cls.from_geojson(geojson)

    @classmethod
    def from_geojson(cls, geojson: dict, proj='EPSG:4326'):
        ee_features = []
        for feature in geojson['features']:
            geom = ee.Geometry(feature["geometry"], opt_proj=proj)
            ee_features.append(ee.Feature(geom, feature['properties']))
        obj = cls()
        obj.fc = ee.FeatureCollection(ee_features)
        return obj

    def getInfo(self):
        return self.fc.getInfo()

    def getMapId(self):
        return self.fc.getMapId()