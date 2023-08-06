import os
import time
import traceback
import urllib

import numpy as np

from digitalarztools.raster.band_process import BandProcess
from digitalarztools.raster.rio_raster import RioRaster
from digitalarztools.utils.logger import da_logger
from digitalarztools.utils.waitbar_console import WaitBarConsole


class SoilContent:
    @classmethod
    def get_clay_content(cls, des_dir, lat_lim, lon_lim, level='sl1', wait_bar=1):
        """
        Downloads SoilGrids data from ftp://ftp.soilgrids.org/data/recent/

        this data includes a Digital Elevation Model (DEM)
        The spatial resolution is 90m (3s) or 450m (15s)

        The following keyword arguments are needed:
        des_dir -- path to store data
        lat_lim -- [ymin, ymax]
        lon_lim -- [xmin, xmax]
        level -- 'sl1' (Default)
                 'sl2'
                 'sl3'
                 'sl4'
                 'sl5'
                 'sl6'
                 'sl7'
        wait_bar -- '1' if you want a waitbar (Default = 1)
        """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Clay_Content')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'ClayContentMassFraction_%s_SoilGrids_percentage.tif' % level)

        if not os.path.exists(fp_end):

            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text('\nDownload Clay Content soil map of %s from SoilGrids.org' % level)

                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "CLAY", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nClay Content soil map of {level} from SoilGrids.org already exists in {fp_end}")

    @classmethod
    def get_silt_content(cls, des_dir, lat_lim, lon_lim, level='sl1', wait_bar=1):
        """
        Downloads SoilGrids data from ftp://ftp.soilgrids.org/data/recent/

        The following keyword arguments are needed:
        Dir -- 'C:/file/to/path/'
        lat_lim -- [ymin, ymax]
        lon_lim -- [xmin, xmax]
        level -- 'sl1' (Default)
                 'sl2'
                 'sl3'
                 'sl4'
                 'sl5'
                 'sl6'
                 'sl7'
        wait_bar -- '1' if you want a waitbar (Default = 1)
        """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Silt_Content')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'SiltContentMassFraction_%s_SoilGrids_percentage.tif' % level)

        if not os.path.exists(fp_end):

            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text(
                    '\nDownload Silt Content Mass Fraction soil map of %s from SoilGrids.org' % level)
                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "SILT", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nSilt Content Mass Fraction soil map of {level} from SoilGrids.org already exists in {fp_end}")

    @staticmethod
    def download_data(output_folder, lat_lim, lon_lim, dataset, level=None):
        """
        This function downloads SoilGrids data from SoilGrids.org
        Keyword arguments:
        output_folder -- directory of the result
        lat_lim -- [ymin, ymax] (values must be between -50 and 50)
        lon_lim -- [xmin, xmax] (values must be between -180 and 180)
        level -- "sl1" .... "sl7"
        dataset -- ground dataset
        """

        dict_levels = dict()
        dict_levels["sl1"] = "0-5"
        dict_levels["sl2"] = "5-15"
        dict_levels["sl3"] = "15-30"
        dict_levels["sl4"] = "30-60"
        dict_levels["sl5"] = "60-100"
        dict_levels["sl6"] = "100-200"

        # if "conversion" in locals():
        #     del "conversion"

        # Define parameter depedent variables
        if dataset == "BULKDENSITY":
            name_end = os.path.join(output_folder, 'BulkDensity_%s_SoilGrids_kg-m-3.tif' % level)
            parameter = "bdod"
            conversion = 10  # cg/cm3 to kg/m3
            level_str = dict_levels[level]
        if dataset == "NITROGEN":
            name_end = os.path.join(output_folder, 'Nitrogen_%s_SoilGrids_g_kg-1.tif' % level)
            parameter = "nitrogen"
            level_str = dict_levels[level]
            conversion = 0.01  # cg/kg to g/kg
        if dataset == "SOC":
            name_end = os.path.join(output_folder, 'SoilOrganicCarbonContent_%s_SoilGrids_g_kg.tif' % level)
            parameter = "soc"
            level_str = dict_levels[level]
            conversion = 0.1  # dg/kg to g/kg
        if dataset == "SOD":
            name_end = os.path.join(output_folder, 'SoilOrganicCarbonDensity_%s_SoilGrids_g_dm3.tif' % level)
            parameter = "ocd"
            conversion = 1.0
            level_str = dict_levels[level]
        if dataset == "PH":
            name_end = os.path.join(output_folder, 'SoilPH_%s_SoilGrids_pH10.tif' % level)
            parameter = "phh2o"
            level_str = dict_levels[level]
            conversion = 1.0
        if dataset == "CLAY":
            name_end = os.path.join(output_folder, 'ClayContentMassFraction_%s_SoilGrids_percentage.tif' % level)
            parameter = "clay"
            level_str = dict_levels[level]
            conversion = 0.1  # g/kg to percentage
        if dataset == "SAND":
            name_end = os.path.join(output_folder, 'SandContentMassFraction_%s_SoilGrids_percentage.tif' % level)
            parameter = "sand"
            level_str = dict_levels[level]
            conversion = 0.1  # g/kg to percentage
        if dataset == "SILT":
            name_end = os.path.join(output_folder, 'SiltContentMassFraction_%s_SoilGrids_percentage.tif' % level)
            parameter = "silt"
            level_str = dict_levels[level]
            conversion = 0.1  # g/kg to percentage

        if not os.path.exists(name_end):

            # Download, extract, and converts all the files to tiff files
            try:

                url = "https://maps.isric.org/mapserv?map=/map/%s.map&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=%s_%scm_mean&FORMAT=image/tiff&SUBSET=long(%f,%f)&SUBSET=lat(%f,%f)&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/4326&OUTPUTCRS=http://www.opengis.net/def/crs/EPSG/0/4326" % (
                    parameter, parameter, level_str, lon_lim[0], lon_lim[1], lat_lim[0], lat_lim[1])
                # url = "http://85.214.241.121:8080/geoserver/ows?service=WCS&version=2.0.1&request=GetCoverage&CoverageId=%s_M_%s250m&subset=Long(%f,%f)&subset=Lat(%f,%f)" %(dataset, level_name, lonlim[0], lonlim[1], latlim[0], latlim[1])
                # print(url)
                urllib.request.urlretrieve(url, filename=name_end)

                if "conversion" in locals():
                    print("Conversion is applied of %s" % conversion)
                    # dest = gdal.Open(nameEnd)
                    raster = RioRaster(name_end)
                    # geo = dest.GetGeoTransform()
                    affine_transform = raster.get_geo_transform()
                    # proj = "WGS84"
                    proj = raster.get_crs()
                    # Array = dest.GetRasterBand(1).ReadAsArray()
                    data = raster.get_data_array(1)
                    # del raster
                    time.sleep(1)
                    data = np.float_(data) * conversion
                    nodata_value = 0

                    data = BandProcess.gap_filling(data, nodata_value)

                    # DC.Save_as_tiff(name_end, data, geo, proj)
                    RioRaster.write_to_file(name_end, data, raster.get_crs(), raster.get_geo_transform(), nodata_value)

            except:
                da_logger.error(traceback.print_stack())

        return None

    @classmethod
    def get_organic_carbon_content(cls, des_dir, lat_lim, lon_lim, level, wait_bar=1):
        """
            Downloads SoilGrids data from ftp://ftp.soilgrids.org/data/recent/

            The following keyword arguments are needed:
            des_dir -- destination directory
            lat_lim -- [ymin, ymax]
            lon_lim -- [xmin, xmax]
            level -- 'sl1' (Default)
                     'sl2'
                     'sl3'
                     'sl4'
                     'sl5'
                     'sl6'
                     'sl7'
            wait_bar -- '1' if you want a waitbar (Default = 1)
            """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Soil_Organic_Carbon_Content')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'SoilOrganicCarbonContent_%s_SoilGrids_g_kg.tif' % level)

        if not os.path.exists(fp_end):

            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text(
                    '\nDownload Soil Organic Carbon Content soil map of %s from SoilGrids.org' % level)
                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "SOC", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nSoil Organic Carbon Content soil map of {level} from SoilGrids.org already exists in {fp_end}")

    @classmethod
    def get_bulk_density(cls, des_dir, lat_lim, lon_lim, level, wait_bar=1):
        """
            Downloads data from SoilGrids (www.soilgrids.org)

            The following keyword arguments are needed:
            des_dir -- destination directory
            lat_lim -- [ymin, ymax]
            lon_lim -- [xmin, xmax]
            level -- 'sl1' (Default)
                     'sl2'
                     'sl3'
                     'sl4'
                     'sl5'
                     'sl6'
                     'sl7'
            wait_bar -- '1' if you want a waitbar (Default = 1)
            """

        # Create directory if not exists for the output
        output_folder = os.path.join(des_dir, 'SoilGrids', 'Bulk_Density')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output map and create this if not exists
        fp_end = os.path.join(output_folder, 'BulkDensity_%s_SoilGrids_kg-m-3.tif' % level)

        if not os.path.exists(fp_end):
            # Create Waitbar
            if wait_bar == 1:
                WaitBarConsole.print_bar_text('\nDownload Bulk Density soil map of %s from SoilGrids.org' % level)
                total_amount = 1
                amount = 0
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

            # Download and process the data
            cls.download_data(output_folder, lat_lim, lon_lim, "BULKDENSITY", level)

            if wait_bar == 1:
                amount = 1
                WaitBarConsole.print_wait_bar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

        else:
            if wait_bar == 1:
                da_logger.info(
                    f"\nBulk Density soil map of {level} from SoilGrids.org already exists in {fp_end}")
