import math
from time import time

import numpy as np
import scipy
from scipy.spatial import KDTree
from digitalarztools.utils.logger import da_logger


class BandProcess:
    def __init__(self, data: np.ndarray):
        self.data = data

    @staticmethod
    def gap_filling(data: np.ndarray, NoDataValue, method=1) -> np.ndarray:
        """
        This function fills the no data gaps in a numpy array

        Keyword arguments:
        dataset -- numpy array
        NoDataValue -- Value that must be filled
        """
        try:
            # fill the no data values
            if NoDataValue is np.nan:
                mask = ~(np.isnan(data))
            else:
                mask = ~(data == NoDataValue)
            xx, yy = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))
            xym = np.vstack((np.ravel(xx[mask]), np.ravel(yy[mask]))).T
            data0 = np.ravel(data[:, :][mask])
            data_end = None
            if method == 1:
                interp0 = scipy.interpolate.NearestNDInterpolator(xym, data0)
                data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape(xx.shape)

            if method == 2:
                interp0 = scipy.interpolate.LinearNDInterpolator(xym, data0)
                data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape(xx.shape)

            return data_end
        except Exception as e:
            da_logger.warning(f"Failed in gap filling due to: {str(e)}")
            return data

    @staticmethod
    def create_buffor(Data_In: np.ndarray, Buffer_area=2):
        """
        This function creates a 3D array which is used to apply the moving window
        :param Data_In:
        :param Buffer_area:
        :return:
        """
        # A block of 2 times Buffer_area + 1 will be 1 if there is the pixel in the middle is 1
        Data_Out = np.empty((len(Data_In), len(Data_In[1])))
        Data_Out[:, :] = Data_In
        for ypixel in range(0, Buffer_area + 1):

            for xpixel in range(1, Buffer_area + 1):

                if ypixel == 0:
                    for xpixel in range(1, Buffer_area + 1):
                        Data_Out[:, 0:-xpixel] += Data_In[:, xpixel:]
                        Data_Out[:, xpixel:] += Data_In[:, :-xpixel]

                    for ypixel in range(1, Buffer_area + 1):
                        Data_Out[ypixel:, :] += Data_In[:-ypixel, :]
                        Data_Out[0:-ypixel, :] += Data_In[ypixel:, :]

                else:
                    Data_Out[0:-xpixel, ypixel:] += Data_In[xpixel:, :-ypixel]
                    Data_Out[xpixel:, ypixel:] += Data_In[:-xpixel, :-ypixel]
                    Data_Out[0:-xpixel, 0:-ypixel] += Data_In[xpixel:, ypixel:]
                    Data_Out[xpixel:, 0:-ypixel] += Data_In[:-xpixel, ypixel:]

        Data_Out[Data_Out > 0.1] = 1
        Data_Out[Data_Out <= 0.1] = 0

        return (Data_Out)

    @staticmethod
    def get_summary_data(data: np.ndarray, nodata=None):
        data = data.astype(np.float64)
        data[data == nodata] = np.nan
        mean_val = np.nanmean(data)
        min_val = np.nanmin(data)
        max_val = np.nanmax(data)
        std_val = np.nanstd(data)
        q25_val = np.nanquantile(data, 0.25)
        median_val = np.nanquantile(data, 0.5)
        q75_val = np.nanquantile(data, 0.75)
        return {"mean": mean_val, "median": median_val, "std": std_val, "min": min_val,
                "q25": q25_val, "q75": q75_val, "max": max_val}

    @classmethod
    def get_value_area_data(cls, data: np.ndarray, no_data, spatial_res, values=[]):
        value_count = cls.get_value_count_data(data, no_data, values)
        value_area = {}
        for k in value_count:
            value_area[k] = value_count[k] * spatial_res[0] * spatial_res[0]
        return value_area

    @staticmethod
    def get_value_count_data(data: np.ndarray, no_data, values=[], res_in_meter: tuple = (1, 1)) -> dict:
        """
        :param data: np.ndarray  like data = raster.get_data_array(band_no)
        :param no_data: no_data = raster.get_nodata_value()
        :param res_in_meter: tuple having raster resolution in x and y
        :param values:
        :return: value and count if res is provide than area in meter
        """
        if no_data is not None and 'float' in str(data.dtype):
            data[data == no_data] = np.nan
        # data[data == no_data] = np.nan
        if len(values) == 0:
            if "float" in str(data.dtype):
                data[data == no_data] = np.nan
                min_value = math.ceil(np.nanquantile(data, 0.25))
                max_value = math.ceil(np.nanquantile(data, 0.75))
                prev_val = None
                for v in range(min_value, max_value):
                    if v in [min_value, max_value]:
                        values.append((v,))
                    else:
                        values.append((prev_val, v))
                    prev_val = v

            else:
                values = np.unique(data)
        else:
            if "float" in str(data.dtype) and not isinstance(values[0], tuple):
                val = [float(v) for v in values]
                values = []
                for i in range(len(val)):
                    if i == 0 or i == len(val) - 1:
                        values.append((val[i],))
                    else:
                        values.append((val[i - 1], val[i]))

        output = {}
        for idx, v in enumerate(values):
            if isinstance(v, tuple):
                if len(v) == 1 and idx == 0:
                    count = np.count_nonzero(data <= v[0])
                    key = f"<= {v[0]}"
                elif len(v) == 1 and idx != 0:
                    count = np.count_nonzero(data >= v[0])
                    key = f">= {v[0]}"
                else:
                    count = np.count_nonzero((data > v[0]) & (data <= v[1]))
                    key = " - ".join(map(str, v))
                # output[key] = count * (res_in_meter[0] * res_in_meter[1])
                # output.append({"value": " - ".join(map(str, v)), "count": count })
            else:
                v = float(v) if isinstance(v, str) else v
                count = np.count_nonzero(data == v)
                key = str(v)
            output[key] = count * (res_in_meter[0] * res_in_meter[1])
                # output.append({"value": str(v), "count": count})
        return output

    @staticmethod
    def get_boolean_raster(data: np.ndarray, pixel_value: list):
        con = None
        for v in pixel_value:
            con = data == v if con is None else np.logical_or(con, data == v)
        res = np.where(con, 1, 0)
        res = res.astype(np.uint8)
        return res

    @staticmethod
    def create_distance_raster(data: np.ndarray, pixel_value, pixel_size_in_km=1):
        boolean_data = BandProcess.get_boolean_raster(data, pixel_value)
        dist_array = np.empty(boolean_data.shape, dtype=float)
        try:
            print("calculating distance raster")
            tree = KDTree(data=np.array(np.where(boolean_data == 1)).T, leafsize=64)
            t_start = time()
            for cur_index, val in np.ndenumerate(boolean_data):
                min_dist, min_index = tree.query([cur_index])
                if len(min_dist) > 0 and len(min_index) > 0:
                    min_dist = min_dist[0]
                    min_index = tree.data[min_index[0]]
                    # dist = math.sqrt(math.pow((cur_index[0] - min_index[0]),2)+math.pow((cur_index[1] - min_index[1]),2))
                    # print(min_dist, dist)
                    # if self.affine is not None:
                    #     if cur_index[1] == min_index[1]:
                    #         # columns are same meaning nearest is either vertical or self.
                    #         # no correction needed, just convert to km
                    #         dd_min_dist = min_dist * self.pixel_size
                    #         km_min_dist = dd_min_dist * 111.321
                    #
                    #     else:
                    #         km_min_dist = calc_haversine_distance(
                    #             convert_index_to_coords(cur_index, self.affine),
                    #             convert_index_to_coords(min_index, self.affine),
                    #         )
                    #
                    #     val = km_min_dist * 1000
                    #
                    # else:
                    # val = min_dist
                    dist_array[cur_index[0]][cur_index[1]] = min_dist * pixel_size_in_km
            e_time = time()
            print("Distance calc run time: {0} seconds".format(round(time() - t_start, 4)))
        except Exception as e:
            print(str(e))
        return dist_array

    @staticmethod
    def stretch_data(normalize_data: np.ndarray, stretch_range=[0, 255]):
        """
        stretch normalize data between stretch range. in future the stretch will based on dtype range
        :param normalize_data: use min_max, logarithmic, and exponential normalization
        :param stretch_range: list of min and max range
        :return:
        """
        max_stretch_val = stretch_range[1] - stretch_range[0]
        data = stretch_range[0] + (normalize_data * max_stretch_val)

        return data

    @staticmethod
    def logarithmic_normalization(data: np.ndarray, no_data: float, is_inverse: bool = False):
        """
        Normalize data between 0 and 1 using logarithmic stretch
        :param data:
        :param no_data:
        :param is_inverse:
        :return:
        """
        if 'float' not in str(data.dtype):
            data = data.astype(np.float32)
        if no_data is not None:
            data[data == no_data] = np.nan

        # data[data == no_data] = 0
        # data[data <= 30] = 0

        max_val = np.nanmax(data)
        # min_val = np.nanmin(data)
        c = 1 / np.log(1 + max_val)
        data = c * np.log(1 + data)
        if is_inverse:
            data = 1 - data
        # stetch between specified range
        # max_stretch_val = stretch_range[1] - stretch_range[0]
        # data = stretch_range[0] + (data * max_stretch_val)

        if no_data is not None:
            data = np.nan_to_num(data, nan=no_data)
        # if dtype is not None:
        #     data = data.astype(dtype)
        return data

    @staticmethod
    def min_max_normalization(data: np.ndarray, no_data, is_inverse: bool = False) -> np.ndarray:
        """
         Normalize data between 0 and 1 using min-max stretch
        :param data:
        :param no_data:
        :param is_inverse:
        :return:
        """
        if 'float' not in str(data.dtype):
            data = data.astype(np.float32)
        if no_data is not None:
            data[data == no_data] = np.nan
        min_val = np.nanmin(data)
        max_val = np.nanmax(data)
        # stretch from zero to 1
        data = (data - min_val) / (max_val - min_val)
        if is_inverse:
            data = 1 - data

        # stetch between specified range
        # max_stretch_val = stretch_range[1] - stretch_range[0]
        # data = stretch_range[0] + (data * max_stretch_val)

        if no_data is not None:
            data = np.nan_to_num(data, nan=no_data)
        # if dtype is not None:
        #     data = data.astype(dtype)
        return data
