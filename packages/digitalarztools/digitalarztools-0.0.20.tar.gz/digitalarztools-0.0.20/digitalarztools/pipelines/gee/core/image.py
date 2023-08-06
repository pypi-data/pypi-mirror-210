import os
import shutil
import traceback

import ee
import numpy as np
from ee.batch import Export

from digitalarztools.io.file_io import FileIO
from digitalarztools.io.url_io import UrlIO
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.raster.rio_process import RioProcess


class GEEImage:
    image: ee.Image

    def __init__(self, img: ee.Image):
        self.image = img

    def get_gee_image(self) -> ee.Image:
        return self.image

    def get_band(self, band_name) -> 'GEEImage':
        # nir = self.image.select('B5')
        return GEEImage(self.image.select(band_name))

    def get_image_bands(self):
        meta = self.image.getInfo()
        return meta['bands']

    def get_image_bands_info(self):
        band_names = self.image.bandNames()
        band_info = band_names.getInfo()
        # print('Band names:', band_info)
        return band_info

    def get_image_metadata(self) -> dict:
        # print(self.image.getInfo())
        properties = self.image.propertyNames()
        print('Metadata properties:',
              properties.getInfo())  # ee.List of metadata properties
        return self.image.getInfo()

    def get_projection(self, is_info=True):
        # Get projection information from band 1.
        band_name = self.image.bandNames().getInfo()[0]
        # for b_name in band_names:
        #     b1_proj = self.image.select(b_name).projection()
        #     print('{} projection:'.format(b_name), b1_proj.getInfo())  # ee.Projection object

        projection = self.image.select(band_name).projection()
        return projection.getInfo() if is_info else projection

    def get_geo_transform(self, is_info=True):
        projection = self.get_projection(False)
        transform = projection.transform
        return transform.getInfo() if is_info else transform

    def get_crs(self, is_info=True):
        projection = self.get_projection(False)
        crs = projection.crs
        return crs.getInfo() if is_info else crs

    def get_scale(self, b_name=None):
        # Get scale (in meters) information from band 1.
        if b_name is None:
            band_names = self.image.bandNames().getInfo()
            res = {}
            for b_name in band_names:
                b1_scale = self.image.select(b_name).projection().nominalScale()
                # print('{} scale:'.format(b_name), b1_scale.getInfo())  # ee.Number
                res[b_name] = b1_scale.getInfo()
            return res
        else:
            b1_scale = self.image.select(b_name).projection().nominalScale()
            return b1_scale.getInfo()

    def get_cloude_cover(self):
        # Get a specific metadata property.
        cloudiness = self.image.get('CLOUD_COVER')
        print('CLOUD_COVER:', cloudiness.getInfo())  # ee.Number

    def get_pixel_value(self, lon, lat):
        p = ee.Geometry.Point([lon, lat], 'EPSG:4326')
        band_names = self.image.bandNames().getInfo()
        pixel_info = []
        for b_name in band_names:
            data = self.image.select(b_name).reduceRegion(ee.Reducer.first(), p, 10).get(b_name)
            info = {"band": b_name, "value": ee.Number(data)}
            pixel_info.append(info)

    def get_map_id_dict(self, vis_params):
        map_id_dict = self.image.getMapId(vis_params)
        # print(map_id_dict)
        # print(map_id_dict['tile_fetcher'].url_format)
        return map_id_dict

    def get_map_id(self, vis_params):
        map_id_dict = self.image.getMapId(vis_params)
        res = {
            'mapid': map_id_dict['mapid'],
            'token': map_id_dict['token'],
            'url_format': map_id_dict['tile_fetcher'].url_format,
            'image': map_id_dict['image'].getInfo()
        }
        return res

    def get_url_template(self, vis_params):
        map_id_dict = self.image.getMapId(vis_params)
        return map_id_dict['tile_fetcher'].url_format

    def get_download_url(self, img_name, aoi: ee.Geometry.Polygon, out_bands=None, scale=None):
        if not out_bands:
            out_bands = self.get_image_bands()
        url = self.image.getDownloadURL({
            'image': self.image.serialize(),
            'region': aoi,
            'bands': out_bands,
            'name': img_name,
            'scale': scale,
            'format': 'GEO_TIFF'
        })
        return url

    def download_image(self, file_path, img_region: GEERegion, scale=30,
                       bands=None, bit_depth=32):
        if not bands:
            bands = self.get_image_bands()
        dir_name = os.path.dirname(file_path)

        img_name, img_ext = FileIO.get_file_name_ext(os.path.basename(file_path))
        download_dir_name = os.path.join(dir_name, img_name)
        FileIO.mkdirs(download_dir_name)
        # final_file_name = os.path.join(dir_name, f'{img_name}.tif')
        # if not os.path.exists(download_dir_name):
        #     os.makedirs(download_dir_name)
        # regions = img_region.get_tiles(len(bands), scale,bit_depth=32)
        # print("regions", regions)
        # print("downloading", index)
        # for region, index in regions:
        # region = img_region
        for region, index in img_region.get_tiles(len(bands), scale, bit_depth=bit_depth):
            print(region, index)
            aoi = region.get_aoi()
            # print("aoi", aoi)
            url = self.get_download_url(img_name, aoi=aoi, scale=scale, out_bands=bands)
            # downloaded_obj = requests.get(url, allow_redirects=True)
            # # index = [1, 1]
            temp_file_path = os.path.join(download_dir_name, f"r{index[0]}c{index[1]}.tif")
            # # print("file_path", file_path)
            # with open(file_path, "wb") as file:
            #     file.write(downloaded_obj.content)
            res = UrlIO.download_url(url, temp_file_path)
        if res:
            try:
                raster = RioProcess.mosaic_images(download_dir_name)
                raster.save_to_file(file_path)
                shutil.rmtree(download_dir_name)
                print('Image downloaded as ', file_path)
            except:
                traceback.print_exc()
                res = False
        return res

    def gee_image_2_numpy(self, image, aoi: ee.Geometry.Polygon):
        if image.args:
            # aoi = ee.Geometry.Polygon(
            #     [[[-110.82, 44.72],
            #       [-110.82, 44.71],
            #       [-110.81, 44.71],
            #       [-110.81, 44.72]]], None, False)
            # aoi = ee.Geometry.Polygon(aoi, None, False)
            band_arrs = image.sampleRectangle(region=aoi)

            band_names = image.bandNames()

            band_count = band_names.img_size().getInfo()
            bands = ()
            for i in range(band_count):
                name = band_names.getString(i).getInfo()
                print('Band name: ', name)
                band_arr = band_arrs.get(name)
                np_arr = np.array(band_arr.getInfo())
                print("np_arr", np_arr.shape)
                # Expand the dimensions of the images so they can be concatenated into 3-D.
                np_arr_expanded = np.expand_dims(np_arr, 2)
                print("np_arr_expanded", np_arr_expanded.shape)
                bands = bands + (np_arr_expanded,)

            # rgb_img = np.concatenate(bands, 2)
            # print(rgb_img.shape)
            # rgb_img_test = (255 * ((rgb_img - 100) / 3500)).astype('uint8')
            # plt.imshow(rgb_img_test)
            # plt.show()
        print("Done...")
        # except Exception as e:
        #     print(str(e))

    def export_output(self, name: str, bucket_name: str, region: ee.Geometry.Polygon, description: str = ''):
        # res = Export.image.toDrive(**{
        #     "image": self.output_image,
        #     "description": 'test',
        #     "folder": 'gee_python',
        #     "fileNamePrefix": name,
        #     "scale": 30,
        #     # "maxPixels": 1e13,
        #     "region": self.aoi.bounds().getInfo()['coordinates']
        # })
        # self.gee_image_2_numpy(self.output_image)
        res = Export.image.toCloudStorage(
            image=self.image,
            description=description,
            bucket=bucket_name,
            fileNamePrefix=name,
            scale=30,
            region=region
        )
        res.start()
        while res.status()['state'] not in ['FAILED', 'COMPLETED']:
            print(res.status())
        res_status = res.status()
        if res_status['state'] == 'FAILED':
            print("error:", res_status['error_message'])
        return res_status
