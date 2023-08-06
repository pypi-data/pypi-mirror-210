import os

from digitalarztools.io.file_io import FileIO
from digitalarztools.raster.rio_raster import RioRaster
from test.test_config import BASE_DIR

if __name__ == '__main__':
    # file_name = 'srtm_49_06.zip'
    # zip_file = os.path.join(DATA_DIR, file_name)
    # output_folder = FileIO.extract_zip_file(zip_file)
    # tif_file = os.path.join(output_folder, file_name.replace('.zip', '.tif'))
    tif_file = os.path.join(BASE_DIR,'../../DHATreeCount/media/Adyala Land 2D Svy_dsm.tif')
    prj_path = os.path.join(BASE_DIR, '../../DHATreeCount/media/Adyala Land 2D Svy_dsm.prj')
    crs = FileIO.read_prj_file(prj_path)
    rio_raster = RioRaster(tif_file)
    rio_raster.set_crs(crs)
    print(rio_raster.get_raster_extent())
    print(rio_raster.get_crs())
    print("done")