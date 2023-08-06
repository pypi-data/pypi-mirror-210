from datetime import datetime
from typing import Union

from digitalarztools.pipelines.gee.core.auth import GEEAuth
from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.utils.logger import da_logger


class Precipitation:
    """
    Extrat data from different sources
    """

    @staticmethod
    def chirps_data_using_gee(gee_auth: GEEAuth, region: GEERegion, start_date: Union[str, datetime],
                           end_date: Union[str, datetime], how='mean') -> GEEImage:
        """
        Extract CHIRPS data using following code
        https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
        :param gee_auth: authentiation
        :param gdv: for define AOI
        :param start_date:
        :param end_date:
          :param how: choices are 'median', 'max', 'mean', 'first', 'cloud_cover'
        :return:
        """

        if gee_auth.is_initialized:
            date_range = (start_date, end_date)
            img_collection = GEEImageCollection(region, 'UCSB-CHG/CHIRPS/DAILY', date_range)
            img_collection.select_dataset('precipitation')
            return GEEImage(img_collection.get_image('mean'))
        else:
            da_logger.error("Please initialized GEE before further processing")