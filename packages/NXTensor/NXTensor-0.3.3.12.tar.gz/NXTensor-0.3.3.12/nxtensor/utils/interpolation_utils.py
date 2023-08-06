#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 10:22:43 2020

@license : CeCILL-2.1
@author: Sébastien Gardoll
"""
from typing import Tuple

from scipy.interpolate import interp2d

import numpy as np

import nxtensor.utils.hdf5_utils as hu

from concurrent.futures import ThreadPoolExecutor


def interpolate_tensor(tensor: np.ndarray, src_x_resolution: float, src_y_resolution: float,
                       dest_x_size: int, dest_x_resolution: float, dest_y_size: int, dest_y_resolution: float,
                       method: str, is_channels_last: bool, nb_threads: int) -> np.ndarray:
    # Tensor must be of shape: (image, channel, x, y) or (image, x, y, channel) if is_channels_last is True.
    # The dimensions of the tensor can be swapped: see has_to_swap_channel.
    # The view of the tensor is channels first for the rest of the algorithm.
    if is_channels_last:
        tensor = tensor.swapaxes(1, 3).swapaxes(2, 3)
    src_x_size = tensor.shape[2]
    src_y_size = tensor.shape[3]
    nb_channels = tensor.shape[1]
    nb_images = tensor.shape[0]

    src_x_1d_grid, dest_x_1d_grid = __generate_coordinates(src_x_size, src_x_resolution, dest_x_size, dest_x_resolution)
    src_y_1d_grid, dest_y_1d_grid = __generate_coordinates(src_y_size, src_y_resolution, dest_y_size, dest_y_resolution)

    image_range = range(0, nb_images)
    if nb_threads > 1:
        result = np.ndarray(shape=(nb_images, nb_channels, dest_x_size, dest_y_size), dtype=float)
        static_parameters = (tensor, src_x_1d_grid, dest_x_1d_grid, src_y_1d_grid, dest_y_1d_grid,
                             method, is_channels_last, result)
        parameters_list = [(image_index, *static_parameters) for image_index in image_range]
        with ThreadPoolExecutor(max_workers=nb_threads) as executor:
            executor.map(__map_interpolated_image, parameters_list)
        if is_channels_last:
            result = result.swapaxes(1, 3).swapaxes(1, 2)
        return result
    else:
        interpolated_images = list()
        for image_index in image_range:
            interpolated_image = interpolate_image(image_index, tensor, src_x_1d_grid, dest_x_1d_grid, src_y_1d_grid,
                                                   dest_y_1d_grid, method, is_channels_last)
            interpolated_images.append(interpolated_image)
        return np.stack(interpolated_images)


def __map_interpolated_image(parameter_list):
    interpolate_image(*parameter_list)


def interpolate_image(image_index: int, tensor: np.ndarray, src_x_1d_grid: np.ndarray, dest_x_1d_grid: np.ndarray,
                      src_y_1d_grid: np.ndarray, dest_y_1d_grid: np.ndarray,
                      method: str, is_channel_last: bool, dest_buffer: np.ndarray = None) -> np.ndarray:
    img = tensor[image_index]
    interpolated_channels = None
    if dest_buffer is None:
        interpolated_channels = list()
    for channel_index in range(0, tensor.shape[1]):  # For each channel of an image.
        channel = img[channel_index]
        interpolated_channel = process_channel(channel, src_x_1d_grid, dest_x_1d_grid, src_y_1d_grid, dest_y_1d_grid,
                                               method)
        if dest_buffer is None:
            interpolated_channels.append(interpolated_channel)
        else:
            np.copyto(dst=dest_buffer[image_index][channel_index], src=interpolated_channel, casting='no')
    result = None
    if dest_buffer is None:
        if is_channel_last:
            result = np.stack(interpolated_channels, axis=2)
        else:
            result = np.stack(interpolated_channels)
    return result


def process_channel(channel: np.ndarray, src_x_1d_grid: np.ndarray, dest_x_1d_grid: np.ndarray,
                    src_y_1d_grid: np.ndarray, dest_y_1d_grid: np.ndarray, method: str) -> np.ndarray:
    interpolation_func = interp2d(x=src_x_1d_grid, y=src_y_1d_grid, z=channel, copy=False, kind=method, fill_value=None)
    interpolated_channel = interpolation_func(dest_x_1d_grid, dest_y_1d_grid)
    return interpolated_channel


def __generate_coordinates(src_size: int, src_resolution: float, dest_size: int, dest_resolution: float)\
        -> Tuple[np.ndarray, np.ndarray]:
    src_first_coordinate = 0
    src_last_coordinate = __compute_last_coordinate(src_size, src_resolution)
    dest_last_coordinate = __compute_last_coordinate(dest_size, dest_resolution)

    shift = src_last_coordinate - dest_last_coordinate
    if shift < 0:
        raise Exception(f"src {src_size}px @ {src_resolution} and dest {dest_size}px @ {dest_resolution} are not "
                        'compliant, src has not enough data')
    elif shift % 2 != 0.:
        raise Exception(f"src {src_size}px @ {src_resolution} and dest {dest_size}px @ {dest_resolution} are not "
                        "compliant, can't lead to square surface")
    offset = int(shift / 2)
    src_1d_grid = np.arange(src_first_coordinate, src_last_coordinate, src_resolution)
    dest_1d_grid = np.arange(src_first_coordinate+offset, src_last_coordinate-offset, dest_resolution)

    if src_1d_grid[-1] < dest_1d_grid[-1]:
        print("> [WARNING]: some points are outside of the grid (they will be extrapolated via nearest-neighbor"
              " extrapolation")

    return src_1d_grid, dest_1d_grid


def __compute_last_coordinate(size: int, resolution: float) -> int:
    last_coordinate = size * resolution

    if last_coordinate % 1 == 0:
        last_coordinate = int(last_coordinate)
    else:
        raise Exception(f"the size '{size}'px and the resolution '{resolution}' are not compliant, "
                        f"(the result of size * resolution must be an integer)")
    return last_coordinate


def __all_tests():

    import time
    import os.path as path
    import nxtensor.utils.time_utils as tu
    import nxtensor.utils.image_utils as iu

    tensor_file_path = '/home_local/sgardoll/tmp_cyclone/merra2/tensors/test_all_data.h5'
    tensor = hu.read_ndarray_from_hdf5(tensor_file_path)
    src_x_resolution = 0.5
    src_y_resolution = 0.625
    dest_x_size = 32
    dest_x_resolution = 0.25
    dest_y_size = 32
    dest_y_resolution = 0.25
    method = 'linear'
    nb_threads = 4
    is_channels_last = True
    variable_names = ('slp', 'tqv', 'u10m', 'v10m', 't200', 't500', 'u850', 'v850')
    image_index = 0

    print(f"> image at index {image_index} before interpolation with method '{method}'")
    iu.display_channels(tensor[image_index], variable_names, f"image {image_index} before interpolation", True)

    start = time.time()
    interpolated_tensor = interpolate_tensor(tensor, src_x_resolution, src_y_resolution, dest_x_size, dest_x_resolution,
                                             dest_y_size, dest_y_resolution, method, is_channels_last, nb_threads)
    tensor_parent_dir_path = path.dirname(tensor_file_path)
    tensor_filename = path.basename(tensor_file_path)

    interpolated_tensor_filename = \
        f'interpolated_{method}_{dest_x_size}px_{dest_y_size}px_at_{dest_y_resolution}_{tensor_filename}'
    interpolated_tensor_file_path = path.join(tensor_parent_dir_path, interpolated_tensor_filename)
    hu.write_ndarray_to_hdf5(interpolated_tensor_file_path, interpolated_tensor)
    stop = time.time()
    print(f'> elapsed time: {tu.display_duration(stop-start)}')

    print(f'> interpolated tensor shape: {interpolated_tensor.shape}')

    print(f'> has nan : {np.isnan(interpolated_tensor.flatten()).max()}')
    print(f'> sum: {interpolated_tensor.sum()}; mean: {interpolated_tensor.mean()}; std: {interpolated_tensor.std()}')
    print(f"> image at index {image_index} after interpolation with method '{method}'")
    iu.display_channels(interpolated_tensor[image_index], variable_names, f"image {image_index} after interpolation",
                        True)


if __name__ == '__main__':
    __all_tests()
