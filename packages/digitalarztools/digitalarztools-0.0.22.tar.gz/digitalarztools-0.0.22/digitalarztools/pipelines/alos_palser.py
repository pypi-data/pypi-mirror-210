### https://search.asf.alaska.edu/
import os.path
from multiprocessing import Pool

import geopandas as gpd
import asf_search as asf
from datetime import date

import numpy as np
from dateutil.relativedelta import relativedelta

# from tqdm import tqdm

from digitalarztools.io.file_io import FileIO
from digitalarztools.raster.rio_process import RioProcess
from digitalarztools.raster.rio_raster import RioRaster
from digitalarztools.utils.logger import da_logger
from digitalarztools.vector.gpd_vector import GPDVector
# from settings import EARTHSAT_USER, EARTHSAT_PASSWORD, MEDIA_DIR


class ALOSUtils:
    """
    downloading and processing ALOS Palser data using asf (Alaska Satellite Facility: making remote-sensing data accessibl)
    https://search.asf.alaska.edu/
    """

    @staticmethod
    def get_date_range(no_of_months: int, rel_date=date.today(), is_end=True):
        if is_end:
            end_date = rel_date
            start_date = end_date + relativedelta(months=-no_of_months)
        else:
            start_date = rel_date
            end_date = start_date + relativedelta(months=+no_of_months)
        return start_date, end_date

    @classmethod
    def download_alos_palsar(cls, aoi: GPDVector, aoi_name: str, aoi_buffer: int) -> RioRaster:
        """
        :param aoi:  area of interest as GPDVector
        :param aoi_name: name of the area of interest
        :param aoi_buffer: buffer size in meter for cliping
        :return: DEM as RioRaster
        """
        output_path = os.path.join(MEDIA_DIR, 'alos_palsar_data')

        img_des = os.path.join(output_path, f"alos_dem_{aoi_name.lower().replace(' ', '_')}.tif")
        gpkg_file = os.path.join(output_path, f'aoi_{aoi_name}.gpkg')
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not os.path.exists(img_des):
            urls = cls.get_dem_urls(aoi, gpkg_file)
            session = asf.ASFSession()
            session.auth_with_creds(EARTHSAT_USER, EARTHSAT_PASSWORD)
            required_fn = []
            for i in tqdm(range(len(urls)), desc='ALOS PALSAR Downloading'):
                required_fn.append(urls[i].split("/")[-1])
                if not os.path.exists(os.path.join(output_path, required_fn[-1])):
                    da_logger.warning(f"\ndownloading:{urls[i]}")
                    asf.download_url(url=urls[i], path=output_path, session=session)
            da_logger.critical("\n Downloading finished")
            dem_raster = cls.extract_and_process_data(required_fn, output_path, aoi_name)
            aoi_buffer = aoi.apply_buffer(aoi_buffer)
            dem_raster = dem_raster.clip_raster(aoi_buffer.gdf, aoi.get_crs())
            dem_raster.change_datatype(new_dtype=np.float32)
            dem_raster.save_to_file(img_des)
            da_logger.critical(f"Alos palsar data downloaded at {img_des}")
        return RioRaster(img_des)

    @staticmethod
    def extract_and_process_data(file_list, output_path: str, aoi_name: str) -> RioRaster:
        # file_list = FileIO.get_files_list_in_folder(output_path, "zip")
        extracted_folder = os.path.join(output_path, f'{aoi_name}')
        for fp in file_list:
            fp = os.path.join(output_path, fp)
            try:
                fn = os.path.basename(fp)
                out_folder = FileIO.extract_zip_file(fp, output_path)
                src_folder = os.path.join(out_folder, f"{fn[:-4]}")
                src_file = os.path.join(src_folder, f"{fn[:-3]}dem.tif")
                if not os.path.exists(extracted_folder):
                    os.makedirs(extracted_folder)
                FileIO.copy_file(src_file, extracted_folder)
                FileIO.delete_folder(src_folder)
            except Exception as e:
                da_logger.error(f"error:{fp}")

        rio_raster = RioProcess.mosaic_images(extracted_folder)
        FileIO.delete_folder(extracted_folder)
        return rio_raster

    @classmethod
    def get_dem_urls(cls, aoi, gpkg_file):
        if not os.path.exists(gpkg_file):
            da_logger.debug("Searching for ALOS Palsar data")
            start_date, end_date = cls.get_date_range(18)
            geom = aoi.get_unary_union()
            options = {
                'intersectsWith': geom.wkt,
                'platform': 'ALOS',
                'instrument': 'PALSAR',
                'processingLevel': [
                    # 'RTC_LOW_RES',
                    'RTC_HI_RES'
                ],
                # 'flightDirection': 'Descending',
                # 'maxResults': 250
                # 'start': start_date,
                # 'end': end_date
            }
            results = asf.geo_search(**options)
            res_gdf = gpd.read_file(str(results), driver='GeoJSON')
            # getting latest datasets
            res_gdf = res_gdf.sort_values('startTime', ascending=False).drop_duplicates(['geometry'])
            res_gdf.drop_duplicates()
            # res_df['startTime'] = res_df['startTime'].apply(lambda a: pd.to_datetime(a).date())
            # res_df['stopTime'] = res_df['stopTime'].apply(lambda a: pd.to_datetime(a).date())

            da_logger.info('total tiles:', res_gdf.shape)

            # res_df.to_excel(os.path.join(output_path, 'search_result.xlsx'))
            res_gdf.to_file(gpkg_file, layer='alos_palsar_rtc_hi_res', driver="GPKG")
        else:
            res_gdf = gpd.read_file(gpkg_file, layer='alos_palsar_rtc_hi_res', driver="GPKG")
        return list(res_gdf['url'].values)
