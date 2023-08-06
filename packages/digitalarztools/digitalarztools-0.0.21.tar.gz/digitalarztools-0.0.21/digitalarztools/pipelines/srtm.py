"""
Download SRTM from https://srtm.csi.cgiar.org/srtmdata/
exmample: http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/srtm_51_06.zip
"""
import os
import ssl
import traceback

import numpy as np
import urllib
import sys
import socket

from digitalarztools.io.file_io import FileIO
from digitalarztools.raster.rio_process import RioProcess
from digitalarztools.raster.rio_raster import RioRaster
from digitalarztools.utils.logger import da_logger



class SRTMUtils:
    def extract_srtm_data(self, bounds: dict, des_folder: str) -> RioRaster:
        lat_lim = [bounds['miny'], bounds['maxy']]
        lon_lim = [bounds['minx'], bounds['maxx']]
        names, range_lon, range_lat = self.find_document_names(lat_lim, lon_lim)
        # srtm_folder = os.path.join(MEDIA_DIR, 'srtm_data')
        temp_folder = os.path.join(des_folder, 'temp')
        extracted_folder = os.path.join(temp_folder, 'extracted')

        for name in names:
            try:
                if not os.path.exists(temp_folder):
                    os.makedirs(temp_folder)
                output_file, file_name = self.download_data(name, temp_folder)

                # extract zip data
                FileIO.extract_zip_file(output_file, extracted_folder)

                # The input is the file name and in which directory the data must be stored
                # file_name_tiff = file_name.replace(".zip", ".tif")
                # output_tiff = os.path.join(extracted_folder, file_name_tiff)
                # print(output_tiff)
            except Exception as e:
                print("error", name)
                traceback.print_exc()
        rio_raster = RioProcess.mosaic_images(extracted_folder)

        FileIO.delete_folder(extracted_folder)
        return rio_raster

    @staticmethod
    def find_document_names(lat_lim, lon_lim):
        """
        This function will translate the latitude and longitude limits into
        the filenames that must be downloaded from the hydroshed webpage

        Keyword Arguments:
        latlim -- [ymin, ymax] (values must be between -60 and 60)
        lonlim -- [xmin, xmax] (values must be between -180 and 180)
        """
        # find tiles that must be downloaded
        start_lat = np.floor((60 - lat_lim[1]) / 5) + 1
        start_lon = np.floor((180 + lon_lim[0]) / 5) + 1
        end_lat = np.ceil((60 - lat_lim[0]) / 5.0) + 1
        end_lon = np.ceil((180 + lon_lim[1]) / 5.0) + 1
        step_size = 1
        range_lon = np.arange(start_lon, end_lon + step_size, step_size)
        range_lat = np.arange(start_lat, end_lat + step_size, step_size)

        name = []

        # make the names of the files that must be downloaded
        for lon_name in range_lon:
            for lat_name in range_lat:
                name.append(str("srtm_%02d_%02d.zip" % (lon_name, lat_name)))

        return name, range_lon, range_lat

    @classmethod
    def download_data(cls, name_file, output_folder_trash):
        """
        This function downloads the DEM data from the HydroShed website

        Keyword Arguments:
        nameFile -- name, name of the file that must be downloaded
        output_folder_trash -- Dir, directory where the downloaded data must be
                               stored
        """

        # download data from the internet
        url = f"http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/{name_file}"
        # print(url)

        socket.setdefaulttimeout(300)
        file_name = url.split('/')[-1]
        output_file = os.path.join(output_folder_trash, file_name)
        if not os.path.exists(output_file):
            ssl._create_default_https_context = ssl._create_unverified_context
            if sys.version_info[0] == 3:
                urllib.request.urlretrieve(url, output_file)
            if sys.version_info[0] == 2:
                urllib.urlretrieve(url, output_file)
            pass
        else:
            da_logger.critical(f"{output_file} already exist")
        return output_file, file_name
