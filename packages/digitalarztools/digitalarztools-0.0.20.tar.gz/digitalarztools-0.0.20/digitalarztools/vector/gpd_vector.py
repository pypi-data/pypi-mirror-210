import json
import os.path

import fiona
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from pyproj import CRS
from rasterio.features import rasterize
from shapely import wkt


class GPDVector():
    gdf: gpd.GeoDataFrame
    orig_crs: CRS

    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        self.orig_crs = self.gdf.crs

    @classmethod
    def from_kml(cls, fp):
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
        gdf = gpd.read_file(fp, driver='KML')
        return cls(gdf)

    @classmethod
    def from_xy(cls, src, sheet_name='Sheet1', x_col='X', y_col='Y', crs='epsg:4326') -> 'GPDVector':
        """
        Create GeoDataFrame from xy value in an excel file
        :param src:
        :param sheet_name:
        :param x_col:
        :param y_col:
        :param crs:
        :return:
        """
        if os.path.exists(src):
            df = pd.read_excel(src, sheet_name=sheet_name)
            geom = gpd.points_from_xy(df[x_col], df[y_col])
            gdf = gpd.GeoDataFrame(df, geometry=geom, crs=crs)
            return cls(gdf)
        else:
            raise Exception(f"Excel file doesn't exist at {src}")

    @classmethod
    def from_excel(cls, src, sheet_name='Sheet1', crs='epsg:4326') -> 'GPDVector':
        if os.path.exists(src):
            df = pd.read_excel(src, sheet_name=sheet_name)
            df['geometry'] = df['geometry'].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df, geometry=df['geometry'], crs=crs)
            return cls(gdf)
        else:
            raise Exception(f"Excel file doesn't exist at {src}")

    @classmethod
    def from_shp(cls, src) -> 'GPDVector':
        gdf = gpd.read_file(src)
        return cls(gdf)

    @classmethod
    def from_df(cls, df, geom_col='geometry', crs='epsg:4326') -> 'GPDVector':
        gdf = gpd.GeoDataFrame(df, geometry=df[geom_col], crs=crs)
        return cls(gdf)

    @classmethod
    def from_gpkg(cls, src, layer) -> 'GPDVector':
        gdf = gpd.read_file(src, layer=layer)
        return cls(gdf)

    def to_gpkg(self, des, layer):
        self.gdf.to_file(des, layer=layer, driver="GPKG")

    def to_excel(self, des, sheet_name="Sheet1", mode='a'):
        """
        :param des: destination file
        :param sheet_name:
        :param mode: either w (write) or a (append) default w
        :return:
        """
        cols = self.gdf.select_dtypes(include=['datetime64[ns, UTC]']).columns
        for col in cols:
            self.gdf[col] = self.gdf[col].dt.tz_localize(None)

        mode = mode if os.path.exists(des) else 'w'
        sheet_exists = 'replace' if os.path.exists(des) else None
        with pd.ExcelWriter(des, engine="openpyxl", mode=mode, if_sheet_exists=sheet_exists) as writer:
            self.gdf.to_excel(writer, sheet_name=sheet_name, index_label="index")

    def to_file(self, des):
        self.gdf.to_file(des)

    def get_srs(self) -> str:
        return self.gdf.crs.srs

    def get_crs(self):
        return self.gdf.crs

    def to_crs(self, crs=None, epsg=None):
        """
        :param crs:
        :param epsg:
        :return:
        """
        if crs is not None:
            self.gdf = self.gdf.to_crs(crs)
        if epsg is not None:
            self.gdf = self.gdf.to_crs(epsg=epsg)

    # def to_raster(self, ref_raster: 'RioRaster', value_col='id'):
    #     # out_arr = np.zeros((rows,cols))
    #     # shapes = ((geom, value) for geom, value in zip(self.gdf.geometry, self.gdf[value_col]))
    #     # rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
    #     shapes = self.get_geometry_list(value_col)
    #     data = rasterize(shapes, out_shape=img_resolution, transform=transform)

    def to_crs_original(self):
        if str(self.gdf.crs) != str(self.orig_crs):
            self.gdf = self.gdf.to_crs(crs=self.orig_crs)

    def inplace_result(self, gdf, inplace) -> 'GPDVector':
        if inplace:
            self.gdf = gdf
            return self
        else:
            return GPDVector(gdf)

    def extract_sub_data(self, col_name: str, col_vals: list, inplace=False) -> 'GPDVector':
        """
        :param col_name: column name
        :param col_vals: column value as a list
        :param inplace: 
        :return: 
        """
        if isinstance(col_vals, list):
            res = []
            for v in col_vals:
                res.append(self.gdf[self.gdf[col_name] == v])

            gdf = gpd.GeoDataFrame(pd.concat(res, ignore_index=True), crs=self.get_crs())
        else:
            gdf = self.gdf[self.gdf[col_name] == col_vals]
        return self.inplace_result(gdf, inplace)

    def select_columns(self, cols, inplace=True):
        gdf = self.gdf[cols]
        return self.inplace_result(gdf, inplace)

    def add_id_col(self):
        """
        add id column in the dataframe
        """
        self.gdf["id"] = self.gdf.index + 1

    def add_area_col(self, unit='sq.km'):
        """
        :param unit: values sq.km, sq.m
        :return:
        """
        gdf = self.gdf.to_crs(epsg='3857') if self.gdf.crs.is_geographic else self.gdf
        if unit == "sq.km":
            self.gdf['area'] = round(gdf.geometry.area / (1000 * 1000), 4)
        else:
            self.gdf['area'] = round(gdf.geometry.area, 4)

    def head(self, n=5):
        print(self.gdf.head(n=n))

    def tail(self, n=5):
        print(self.gdf.tail(n=n))

    def get_geometry(self, col_name, col_val):
        res = self.gdf[self.gdf[col_name] == col_val]['geometry']
        if not res.empty:
            return res.values[0]

    def get_gdf(self):
        return self.gdf

    def get_geometry_list(self, attr_name=None) -> list:
        if attr_name:
            # return [(row['geometry'], row[attr_name]) for index, row in self.gdf.iterrows()]
            return list(zip(self.gdf['geometry'], self.gdf[attr_name]))
        else:
            return self.gdf.geometry.tolist()

    def spatial_join(self, input_gdf: gpd.GeoDataFrame, predicate='intersects', how="inner") -> 'GPDVector':
        # inp, res = self.gdf.geometry.sindex.query_bulk(input_gdf.geometry, predicate=predicate)
        # res_df = pd.DataFrame({
        #     'self_index': res,
        #     'inp_index': inp
        # })
        # return res_df
        if str(input_gdf.crs) != str(self.get_crs()):
            input_gdf = input_gdf.to_crs(self.get_crs())
        join_result = self.gdf.sjoin(input_gdf, how="inner", predicate=predicate)
        return GPDVector(join_result)

    def to_goejson(self):
        geojson = json.loads(self.gdf.to_json())
        return geojson

    def apply_buffer(self, distance_in_meter: int, inplace=False) -> 'GPDVector':
        """
        :param distance_in_meter: buffer distance in radiuse
        :param inplace:
        :return: GPDVector
        """
        gdf = self.gdf.to_crs(epsg=3857)
        gdf = gdf.buffer(distance_in_meter)
        gdf = gdf.to_crs(epsg=4326)
        return self.inplace_result(gdf, inplace)

    def get_unary_union(self):
        """
        combine all geometry as a single geometry
        :return: shapely geometry
        """
        if self.get_rows_count() > 1:
            return self.gdf.geometry.unary_union()
        else:
            return self.gdf.geometry.values[0]

    def get_rows_count(self) -> int:
        """
        :return: rows count
        """
        return self.gdf.shape[0]

    def get_cols_count(self) -> int:
        """
        :return: no of columns
        """
        return self.gdf.shape[1]

    def get_cols_list(self) -> list:
        """
        :return: column name list
        """
        return self.gdf.columns.tolist()

    def get_col_values(self, col_name) -> list:
        return self.gdf[col_name].values.tolist()

    def drop_duplicate_geometry(self):
        """
        :return:
        """
        self.gdf = self.gdf.drop_duplicates()

    def calculate_total_area(self):
        gdf = self.gdf.to_crs(epsg=3857)
        return gdf.area.sum()

    def remove_duplicates(self, col_name=None):
        if col_name is None:
            self.gdf = self.gdf.drop_duplicates(keep='first')
        else:
            self.gdf = self.gdf[~self.gdf.set_index(col_name).index.duplicated()]

    def is_empty(self):
        return self.gdf.empty

    def check_dates_available(self, col_name, start_date, end_date):
        res = self.gdf[self.gdf[col_name].between(start_date, end_date)]
        return res

    @classmethod
    def extent_2_envelop(cls, min_x, min_y, max_x, max_y, crs) -> 'GPDVector':
        wkt = f"Polygon(({min_x} {max_y}, {max_x} {max_y}, {max_x} {min_y}, {min_x} {min_y}, {min_x} {max_y} ))"
        env = shapely.wkt.loads(wkt)

        return cls(gpd.GeoDataFrame({'geometry': env}, index=[0], crs=crs))
