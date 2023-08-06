import glob
import os

import pandas as pd
import geopandas as gpd
from landsatxplore.api import API

from digitalarztools.pipelines.config.data_centers import DataCenters
from digitalarztools.pipelines.earth_explorer.m2m import EarthExplorerM2M
from digitalarztools.vector.gpd_vector import GPDVector


class LandSatEE:
    """
    usage:
    ls_ee = LandSatEE('landsat_ot_c2_l2')
    ls_ee.search(extent, start_date_str, end_date_str)
    ls_ee.download_ls(input_folder_LS_RAW)

    # IDs of GeoTIFF data product for each dataset
    DATA_PRODUCTS = {
        "landsat_tm_c1": "5e83d08fd9932768",
        "landsat_etm_c1": "5e83a507d6aaa3db",
        "landsat_8_c1": "5e83d0b84df8d8c2",
        "landsat_tm_c2_l1": "5e83d0a0f94d7d8d",
        "landsat_etm_c2_l1": "5e83d0d0d2aaa488",
        "landsat_ot_c2_l1": "5e81f14ff4f9941c",
        "landsat_tm_c2_l2": "5e83d11933473426",
        "landsat_etm_c2_l2": "5e83d12aada2e3c5",
        "landsat_ot_c2_l2": "5e83d14f30ea90a9",
        "sentinel_2a": "5e83a42c6eba8084",
    }
    """
    search_res_gdv: GPDVector
    dataset_name: str

    def __init__(self, dataset_name):
        """
        search for dataset from landsat_tm_c1, landsat_tm_c2_l1, landsat_tm_c2_l2, landsat_etm_c1,
        landsat_etm_c2_l1, landsat_etm_c2_l2, landsat_8_c1, landsat_ot_c2_l1, landsat_ot_c2_l2, sentinel_2a

        :param dataset_name:  Case-insensitive dataset alias default value is landsat_ot_c2_l1
        """
        self.dataset_name = dataset_name

    def search_ls(self, extent, start_date, end_date, max_cloud_cover=10):
        # """
        # :param extent: tuple of  form (xmin, ymin, xmax, ymax)
        # :param start_date: str, YYYY-MM-DD like '1995-01-01',
        # :param end_date: str YYYY-MM-DD like '1995-10-01',
        # :param max_cloud_cover: percentage default value is 10
        # :return: json of scenes information
        # """
        # username, password = DataCenters().get_server_account("EARTHEXPLORER")
        # api = API(username=username, password=password)
        # scenes = api.search(
        #     dataset=self.dataset_name,
        #     bbox=extent,
        #     start_date=start_date,
        #     end_date=end_date,
        #     max_cloud_cover=max_cloud_cover
        # )
        # api.logout()
        # df = pd.DataFrame(scenes)
        # df = df.sort_values(['acquisition_date', 'cloud_cover'])

        gdf = EarthExplorerM2M.search_scenes(self.dataset_name, start_date, end_date, extent)
        self.search_res_gdv = GPDVector(gdf)
        self.search_res_gdv.remove_duplicates(['displayId'])

    def download_ls(self, des_dir):
        m2m = EarthExplorerM2M(des_dir)

        os.chdir(des_dir)
        downloaded_entity_ids = [n.split(".")[0] for n in glob.glob("*.tar")]
        res_df = self.search_res_gdv.gdf[['entityId']][~self.search_res_gdv.gdf.displayId.isin(downloaded_entity_ids)]
        req_entity_ids = res_df['entityId'].values.tolist()
        if len(req_entity_ids) > 0:
            m2m.download_datasets(self.dataset_name, req_entity_ids)
