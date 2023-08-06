from datetime import datetime
from typing import Union

import numpy as np
import requests
from bs4 import BeautifulSoup

from digitalarztools.pipelines.gee.core.auth import GEEAuth
from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.utils.logger import da_logger
from digitalarztools.vector.gpd_vector import GPDVector


class CHIRP:
    @staticmethod
    def get_last_available_date():
        """
        :return: chirps and chirp end dates
        """
        url = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        Years = []
        for link in soup.findAll('a'):
            link_str = str(link.get('href'))
            if link_str[0] == "1" or link_str[0] == "2":
                Years.append(int(link_str[:-1]))

        files = []
        for Year in Years[-5:]:
            url = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/%d" % Year
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.findAll('a')[-5:]:
                link_str = str(link.get('href'))
                # print(link_str)
                if link_str.startswith("chirps") and (link_str.endswith(".tif") or link_str.endswith(".tif.gz")):
                    files.append(link_str)

        chirps_end_dates_tif = [datetime.strptime(k, "chirps-v2.0.%Y.%m.%d.tif").toordinal() for k in files if
                                k.endswith(".tif")]
        chirps_end_dates_tif_gz = [datetime.strptime(k, "chirps-v2.0.%Y.%m.%d.tif.gz").toordinal() for k in
                                   files if k.endswith(".tif.gz")]
        chirps_end_dates = chirps_end_dates_tif_gz + chirps_end_dates_tif
        chirps_end_date = datetime.fromordinal(np.max(chirps_end_dates))

        url = "https://data.chc.ucsb.edu/products/CHIRP/daily"
        r = requests.get(url)

        soup = BeautifulSoup(r.text, "html.parser")

        Years = []
        for link in soup.findAll('a'):
            link_str = str(link.get('href'))
            if link_str[0] == "1" or link_str[0] == "2":
                Years.append(int(link_str[:-1]))

        files = []
        for Year in Years[-5:]:

            url = "https://data.chc.ucsb.edu/products/CHIRP/daily/%d" % Year
            r = requests.get(url)

            soup = BeautifulSoup(r.text, "html.parser")

            for link in soup.findAll('a')[-5:]:
                link_str = str(link.get('href'))
                if link_str.startswith("chirp") and (link_str.endswith(".tif") or link_str.endswith(".tif.gz")):
                    files.append(link_str)

        chirp_end_dates_tif = [datetime.strptime(k, "chirp.%Y.%m.%d.tif").toordinal() for k in files if
                               k.endswith(".tif")]
        chirp_end_dates_tif_gz = [datetime.strptime(k, "chirp.%Y.%m.%d.tif.gz").toordinal() for k in files if
                                  k.endswith(".tif.gz")]
        chirp_end_dates = chirp_end_dates_tif_gz + chirp_end_dates_tif
        chirp_end_date = datetime.fromordinal(np.max(chirp_end_dates))

        return chirps_end_date, chirp_end_date

