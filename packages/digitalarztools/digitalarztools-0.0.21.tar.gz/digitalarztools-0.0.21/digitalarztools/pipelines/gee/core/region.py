import math
from typing import Union

import ee
from shapely.geometry import box, mapping

from digitalarztools.pipelines.gee.core.feature_collection import GEEFeatureCollection


class GEERegion:
    fc: ee.FeatureCollection = None
    aoi: ee.Geometry.Polygon = None
    bounds: ee.Geometry.Polygon = None
    center: ee.Geometry.Point = None
    vis_params: dict = {'color': 'red'}

    @classmethod
    def from_geojson_polygon(cls, polygon, proj='EPSG:4326'):
        region = cls()
        polygon: ee.Geometry.Polygon = ee.Geometry(polygon, opt_proj=proj)
        region.aoi = polygon
        region.set_center()
        region.set_bounds()
        return region

    @classmethod
    def from_geojson(cls, fc: dict, proj='EPSG:4326'):
        region = cls()
        ee_features = []
        for feature in fc['features']:
            geom = ee.Geometry(feature["geometry"], opt_proj=proj)
            ee_features.append(ee.Feature(geom, feature['properties']))
        region.fc = ee.FeatureCollection(ee_features)
        region.aoi = region.fc.union().geometry()
        region.set_bounds()
        region.set_center()
        return region

    @classmethod
    def from_feature_collection(cls, fc: Union[GEEFeatureCollection, ee.FeatureCollection]):
        region = cls()
        if isinstance(fc, GEEFeatureCollection):
            fc = fc.get_fc()
        region.fc = fc
        region.aoi = region.fc.union().geometry()
        region.set_bounds()
        region.set_center()
        return region

    def set_polygon_region(self, aoi: ee.Geometry.Polygon):
        # ee.FeatureCollection(aoi, {})
        self.aoi = aoi
        self.bounds = self.aoi.bounds()
        self.set_center()

    def set_point_region(self, lon, lat, buffer_size=10):
        point_coords = [lon, lat]
        point_ee = ee.Geometry.Point(point_coords)
        self.aoi = point_ee.buffer(buffer_size)
        self.bounds = self.aoi.bounds()

    def set_extent_region(self, extent):
        # extent: list = [39.2815859031821, -11.99328125, 43.594707856144886, -7.269160156250001]
        self.bounds = ee.Geometry.Rectangle(extent)

    def set_center(self):
        self.center = self.aoi.centroid()

    def set_bounds(self):
        self.bounds = self.aoi.bounds()

    def get_extent(self):
        coordinates = self.bounds.coordinates().getInfo()[0]
        extent = [coordinates[0][0], coordinates[0][1], coordinates[2][0], coordinates[2][1]]
        return extent
        # width = coordinates[2] - coordinates

    def get_coordinates(self):
        return self.bounds.coordinates().getInfo()[0]

    def get_center_coordinates(self):
        return self.center.coordinates().getInfo()

    def get_bbox_region(self):
        extent = self.get_extent()
        return ee.Geometry.BBox(*extent)

    def get_aoi(self):
        return self.aoi

    def calculate_region_img_size(self, no_of_bands: int, bit_depth: int, spatial_res: int):
        extent = self.get_extent()
        col = (extent[2] - extent[0]) * 110 * 1000 / spatial_res
        row = (extent[3] - extent[1]) * 110 * 1000 / spatial_res
        img_size = col * row * no_of_bands * bit_depth / 8
        return img_size

    def get_tiles(self, no_of_bands, spatial_res, bit_depth):
        regions = []
        spatial_res_deg = spatial_res / (110 * 1000)
        max_tile_size = 10 * 1024 * 1024  # 10MB
        # img_res = max_tile_size * 8 / ((no_of_bands + 1) * bit_depth)
        tile_res = max_tile_size / ((no_of_bands + 1) * bit_depth)
        # sqr_length = (math.sqrt(tile_res) * spatial_res) / (110 * 1000)
        tile_length =  math.sqrt(tile_res) * spatial_res_deg
        extent = self.get_extent()
        # print("extent", extent)
        # max_width = (extent[2] - extent[0])
        # max_height = (extent[3] - extent[1])
        min_x, min_y = extent[0], extent[1]
        r, c = 0, 0,
        pad = 0.00001
        while extent[3] >= min_y:
            min_x = extent[0]
            max_y = min_y + tile_length
            max_y = max_y if max_y < extent[3] else extent[3]+pad
            r += 1
            c = 0
            while extent[2] >= min_x:
                max_x = min_x + tile_length
                max_x = extent[2]+pad if max_x > extent[2] else max_x
                n_extent = [min_x, min_y, max_x, max_y]
                # print(n_extent)
                # geometry = box(Polygon.from_bbox)
                # geojson = json.loads(geometry.json)
                geometry = box(*n_extent)
                geojson = mapping(geometry)
                # print(geojson)
                min_x = max_x
                c += 1
                reg = self.from_geojson_polygon(geojson)
                # regions.append([reg, (r, c)])
                yield reg, (r, c)
            min_y = max_y
            # return regions

    def __str__(self):
        # return f"extent:{','.join(str(e) for e in self.get_extent())}"
        return str(self.get_extent())
