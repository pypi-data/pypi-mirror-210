import os
import traceback
from io import BytesIO
import numpy as np
import rasterio
from PIL import Image
from rasterio.session import AWSSession

from rio_tiler.io import COGReader
from rio_tiler.colormap import cmap
from rio_tiler.models import ImageData

from digitalarztools.io.file_io import FileIO
from digitalarztools.raster.rio_raster import RioRaster
from rio_cogeo import cog_profiles, cog_translate

from digitalarztools.utils.logger import da_logger


class COGRaster:
    cog: COGReader
    file_path: str

    # def __init__(self, uuid: str, is_s3: bool = True):
    #     pass

    @classmethod
    def open_from_local(cls, file_path: str):
        cog_raster = cls()
        cog_raster.cog = COGReader(file_path)
        cog_raster.file_path = file_path
        return cog_raster

    @classmethod
    def open_from_s3(cls, s3_uri: str, session):
        cog_raster = cls()
        # s3_uri = S3Utils.get_cog_uri(f"{file_name}.tif")
        # cog_raster.cog = S3Utils().get_cog_rio_dataset(s3_uri)
        session = rasterio.Env(AWSSession(session))
        with session:
            cog_raster.cog = COGReader(s3_uri)
        cog_raster.file_path = s3_uri
        return cog_raster

    # @staticmethod
    # def upload_to_s3(src_path_name, des_path_uri, session: Session):
    #     try:
    #         # file_path, object_name = CommonUtils.separate_file_path_name(des_path_name)
    #         bucket_name, object_path = S3Utils.get_bucket_name_and_path(des_path_uri)
    #         response = session.client("s3").upload_file(src_path_name, bucket_name, object_path)
    #     except ClientError as e:
    #         da_logger.error(e)
    #         da_logger.error(traceback.print_exc())
    #         return False
    #     return True

    def get_file_path(self):
        return self.file_path

    def get_rio_raster(self):
        return RioRaster(self.cog.dataset)

    @classmethod
    def create_cog(cls, src_rio_raster: RioRaster, des_path: str,
                   profile: str = "deflate",
                   profile_options: dict = {},
                   **options):
        FileIO.mkdirs(des_path)
        with src_rio_raster.get_dataset() as src:
            """Convert image to COG."""
            output_profile = cog_profiles.get(profile)
            output_profile.update(dict(BIGTIFF="IF_SAFER"))
            output_profile.update(profile_options)

            # Dataset Open option (see gdalwarp `-oo` option)
            config = dict(
                GDAL_NUM_THREADS="ALL_CPUS",
                GDAL_TIFF_INTERNAL_MASK=True,
                GDAL_TIFF_OVR_BLOCKSIZE="128",
            )

            cog_translate(
                src,
                des_path,
                output_profile,
                overview_level=3,
                config=config,
                in_memory=False,
                quiet=True,
                **options,
            )
            print("cog created")
            return cls.open_from_local(des_path)

    @staticmethod
    def create_color_map(style):
        """
         style = {'labels': ['sandy loam', 'loam', 'clay loam', 'clay loam'],
             'values': ['30', '40', '50', '60'], 'max_val': 59.79513168334961,
             'min_val': 30.0, 'palette': ['#1a9641', '#c4e687', '#fec981', '#d7191c']}

        style = {"labels": ["<= 18.0109", "18.0109 - 32.0722", "32.0722 - 46.1335", "46.1335 - 60.1948", "> 60.1948"],
             "values": [18.01091274, 32.07221998, 46.13352722, 60.194834459999996, 67.29322814941406], "max_val": 67.29322814941406, "min_val": 2.9422078132629395,
             "palette": ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]}


        style = {"labels": ["", "Wheat", "Potato and Maize", "Potato", "Spring Maize", "Double Maize", "Fodder", "Orchards", "Sugarcane", "Others", "Trees and Plantation", "Builtup Area", "Fallow Land", "Water Bodies"],
             "palette": {"0": "#00000000", "1": "#92ff57", "2": "#a020f0", "3": "#ffffe0", "4": "#00c0ff", "5": "#7fff00", "6": "#ffff00", "7": "#008000", "8": "#ff8000", "9": "#9200ff", "10": "#7fffd4", "11": "#ff0000", "12": "#a0522d", "13": "#0000ff"}}
        :param style:
        :return:
        """
        palette = style['palette']
        custom_color = {}
        j = 0
        for p in palette:
            h = f"{palette[p] if isinstance(palette, dict) else p}FF".lstrip('#')
            custom_color[j] = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
            j = j + 1
        if "values" in style:
            values = style["values"]
            values = sorted(values, key=float)
            values[0] = style['min_val'] if values[0] > style['min_val'] else values[0]
            values.append(style['max_val'] if values[-1]< style['max_val'] else values[-1] + 1 )
            color_map = []
            for i in range(len(custom_color)):
                color_map.append(((values[i], values[i + 1]), custom_color[i]))
            return color_map
        else:
            # print("custom color", custom_color)
            cp = cmap.register({"cc": custom_color})
            return cp.get("cc")

    def read_tile_as_png(self, x: int, y: int, z: int, color_map: dict, tile_size=256):
        try:
            tile: ImageData = self.cog.tile(x, y, z, tilesize=tile_size)
            # tile.rescale(
            #     in_range=((0, 25),),
            #     out_range=((0, 255),)
            # )
            # if not color_map:
            #     return BytesIO(tile.render(False, img_format="GTIFF"))
            # else:
            return BytesIO(tile.render(True, colormap=color_map, img_format='PNG'))
        except Exception as e:
            # da_logger.error(traceback.print_exc())
            return self.create_empty_image(tile_size, tile_size)
            # pass

    @staticmethod
    def create_alpha_band(size_x, size_y):
        return np.zeros([size_x, size_y], dtype=np.uint8)

    def create_empty_image(self, size_x, size_y):
        blank_image = np.zeros([size_x, size_y, 4], dtype=np.uint8)
        # np_array.fill(255)  # or img[:] = 255
        # blank_image[:, :, 3] = 0
        return self.create_image(blank_image)

    @staticmethod
    def create_image(np_array, format="PNG", f_name=None, is_data_file=False):
        img = Image.fromarray(np_array)
        # if f_name and is_data_file:
        #     fp = os.path.join('media/temp', f_name)
        #     FileIO.mkdirs(fp)
        #     img.save(fp, format)

        buffer = BytesIO()
        img.save(buffer, format=format)  # Enregistre l'image dans le buffer
        # return "data:image/PNG;base64," + base64.b64encode(buffer.getvalue()).decode()
        return buffer  # .getvalue()

    def get_pixel_value_at_long_lat(self, long: float, lat: float):
        try:
            pixel_val = self.cog.point(long, lat)
            return pixel_val
        except Exception as e:
            # DataLogger.log_error_message(e)
            pass
