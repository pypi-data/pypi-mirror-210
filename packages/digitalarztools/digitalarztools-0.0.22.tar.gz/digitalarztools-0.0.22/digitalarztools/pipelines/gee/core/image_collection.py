import datetime
from typing import Union

import ee

from digitalarztools.pipelines.gee.core.region import GEERegion


class GEEImageCollection:
    image_type: str = None
    img_collection: ee.ImageCollection = None
    region: GEERegion = None
    date_rage: tuple = None

    def __init__(self, region: Union[GEERegion, dict], image_type: str, date_range: tuple = None, ):
        """
        Parameters
        ----------
        :param image_type:  dataset name or type like 'COPERNICUS/S2_SR' for other check gee documentation
        :param date_range: tuple
            range of date with start and end value like
            ('2021-01-01', '2021-12-31')
            or can be calculated through  time delta
            today = datetime.date.today()
             start_date = today - datetime.timedelta(days=365)
            self.date_range = (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        example:
              s2_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
             .filterDate(start_date, end_date) \
             .filterBounds(fc) \
             .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)
        """
        self.region = GEERegion.from_geojson(region) if isinstance(region, dict) else region
        self.image_type = image_type
        self.img_collection = ee.ImageCollection(image_type)
        self.img_collection = self.img_collection.filterBounds(self.region.bounds)
        # if date_range:
        #     today = datetime.date.today()
        #     # first = today.replace(day=1)
        #     start_date = today - datetime.timedelta(days=365)
        #     self.date_range = (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

        if date_range is not None:
            self.date_range = date_range
            self.img_collection = self.img_collection.filterDate(date_range[0], date_range[1])

    def select_dataset(self, ds_name: str):
        """
        :param ds_name: dataset name like 'precipitation' in  'UCSB-CHG/CHIRPS/DAILY'
        :return:
        """
        self.img_collection = self.img_collection.select(ds_name)

    def select_bands(self, bands: list):
        """
        example
            bands = ['B2', 'B3', 'B4', 'B7', 'B8', 'B8A', 'B11', 'B12']
            indices = ['NDVI', 'NDWI', 'NDBI', 'EVI']  additional bands added
            features = ee.List(bands + indices)
        :param bands:
        :return:
        """
        features = ee.List(bands)
        self.img_collection = self.img_collection.select(features)

    def add_bands(self, types: list):
        """
        use to add bands in the image collection
        :param types: list having value "mask_cloud", "NDVI", "NDWI", "NBI", "EVI"
        :return:
        """
        from digitalarztools.pipelines.gee.analysis.indices import GEEIndices
        for t in types:
            t = t.lower()
            if t == "mask_cloud":
                self.img_collection = self.img_collection.map(self.mask_s2_clouds)
            elif t == "ndvi":
                self.img_collection = self.img_collection.map(GEEIndices.add_ndvi)
            elif t == "ndwi":
                self.img_collection = self.img_collection.map(GEEIndices.add_ndwi)
            elif t == "ndbi":
                self.img_collection = self.img_collection.map(GEEIndices.add_ndbi)
            elif t == "evi":
                self.img_collection = self.img_collection.map(GEEIndices.add_evi)

    @staticmethod
    def mask_s2_clouds(image):
        qa = image.select('QA60')
        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloud_bit_mask = int(2 ** 10)
        cirrus_bit_mask = int(2 ** 11)
        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloud_bit_mask).eq(0). \
            And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))

        return image.updateMask(mask).divide(10000) \
            .select("B.*") \
            .copyProperties(image, ["system:time_start"])

    def get_collection_size(self):
        size = self.img_collection.size().getInfo()
        return size

    def get_collection_list(self):
        return self.img_collection.toList(self.img_collection.size()).getInfo()

    def get_ymd_list(self):
        def iter_func(image, newList):
            date = ee.String(image.date().format("YYYY-MM-dd"))
            newlist = ee.List(newList)
            return ee.List(newlist.add(date).sort())

        return self.get_image_collection().iterate(iter_func, ee.List([])).getInfo()

    def get_image_collection(self):
        return self.img_collection

    def get_image(self, how=None)-> ee.Image:
        """
        :param how: choices are 'median', 'max', 'mean', 'first', 'cloud_cover'
        :return:
        """
        # if collection.size().getInfo() > 0:
        # image: ee.Image = None
        if how == 'median':
            image = self.img_collection.median()
        elif how == 'max':
            image = self.img_collection.max()
        elif how == 'mean':
            image = self.img_collection.mean()
        elif how == 'cloud_cover':
            image = ee.Image(self.img_collection.sort('CLOUD_COVER').first())
        else:
            image = ee.Image(self.img_collection.first())
        return image

    # def temporal_collection(self, temporal1: int, temporal2: int, temporal_type: str = 'day'):
    #     """
    #     Sentinel 2 Refined Image List (after 14-15 days)
    #     :param temporal1: no of days like 14
    #     :param temporal2: no of days like 15 (more than previous one
    #     :param temporal_type: default is day (check gee documentation for other type)
    #     """
    #     self.img_collection = GEEImageCollection.temporal_collection(self.img_collection, self.date_range[0], temporal1,
    #                                                                  temporal2, temporal_type)

    @staticmethod
    def temporal_collection(collection, start, count, interval, units):
        sequence = ee.List.sequence(0, ee.Number(count).subtract(1))
        originalStartDate = ee.Date(start)

        def filter_by_date(i):
            startDate = originalStartDate.advance(ee.Number(interval).multiply(i), units)
            endDate = originalStartDate.advance(ee.Number(interval).multiply(ee.Number(i).add(1)), units)
            resultImage = collection.filterDate(startDate, endDate).median() \
                .set('system:time_start', startDate.millis()) \
                .set('system:time_end', endDate.millis())

            return resultImage

        return ee.ImageCollection(sequence.map(filter_by_date))


