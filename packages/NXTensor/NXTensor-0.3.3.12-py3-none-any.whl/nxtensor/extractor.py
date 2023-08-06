#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 14:50:20 2020

@license : CeCILL-2.1
@author: sebastien@gardoll.fr
"""

from typing import Dict, List, Mapping, Tuple, Type

from nxtensor.exceptions import ConfigurationError
from nxtensor.square_extractor import SquareRegionExtractionVisitor, RegionExtractionVisitor
from nxtensor.extraction import ExtractionShape
from nxtensor.variable import VariableVisitor, SingleLevelVariable, MultiLevelVariable, ComputedVariable, Variable, \
    VariableNetcdfFilePathVisitor
from nxtensor.core.types import VariableId, LabelId, MetaDataBlock, Period

import nxtensor.core.xarray_extractions as xtract
import nxtensor.utils.time_utils as tu

import xarray as xr
import numpy as np


class ExtractionVisitor(VariableVisitor):

    __EXTRACTOR_FACTORY: Mapping[ExtractionShape, Type[RegionExtractionVisitor]] = \
        {ExtractionShape.SQUARE: SquareRegionExtractionVisitor}

    @staticmethod
    def __create_extractor(shape: ExtractionShape) -> Type[RegionExtractionVisitor]:
        try:
            return ExtractionVisitor.__EXTRACTOR_FACTORY[shape]
        except KeyError:
            msg = f"> [ERROR] unknown extraction shape '{shape}'"
            raise ConfigurationError(msg)

    def __init__(self, period: Period, extraction_metadata_blocks: List[Tuple[LabelId, MetaDataBlock]],
                 half_lat_frame: int,
                 half_lon_frame: int, has_to_round_coordinates: bool, dask_scheduler: str = 'single-threaded',
                 shape: ExtractionShape = ExtractionShape.SQUARE):
        self.__period: Period = period
        self.__extraction_metadata_blocks: List[Tuple[LabelId, MetaDataBlock]] = extraction_metadata_blocks
        self.__half_lat_frame: int = half_lat_frame
        self.__half_lon_frame: int = half_lon_frame
        self.__has_to_round_coordinates = has_to_round_coordinates
        self.__dask_scheduler: str = dask_scheduler
        self.__shape: ExtractionShape = shape
        self.result: List[Tuple[LabelId, np.ndarray, MetaDataBlock]] = list()

    def __core_extraction(self, var: Variable, datasets: Mapping[VariableId, xr.Dataset]) -> None:

        for label_id, extraction_metadata_block in self.__extraction_metadata_blocks:
            extracted_regions: List[xr.DataArray] = list()
            # The order of extraction_data_list must be deterministic so as all the channel
            # match their extracted region line by line.
            for extraction_data in extraction_metadata_block:
                extractor = ExtractionVisitor.__create_extractor(self.__shape)(
                                                           datasets=datasets,
                                                           extraction_data=extraction_data,
                                                           half_lat_frame=self.__half_lat_frame,
                                                           half_lon_frame=self.__half_lon_frame,
                                                           has_to_round_coordinates=self.__has_to_round_coordinates,
                                                           dask_scheduler=self.__dask_scheduler)
                var.accept(extractor)
                extracted_regions.append(extractor.get_result())

            data = np.stack(extracted_regions)
            self.result.append((label_id, data, extraction_metadata_block))

        [dataset.close() for dataset in datasets.values()]

    def visit_single_level_variable(self, var: SingleLevelVariable) -> None:
        time_dict = tu.from_time_list_to_dict(self.__period)
        netcdf_file_path = var.compute_netcdf_file_path(time_dict)
        datasets = {var.str_id: xtract.open_netcdf(netcdf_file_path)}
        self.__core_extraction(var, datasets)

    def visit_multi_level_variable(self, var: MultiLevelVariable) -> None:
        self.visit_single_level_variable(var)

    def visit_computed_variable(self, var: ComputedVariable) -> None:
        time_dict = tu.from_time_list_to_dict(self.__period)
        visitor = VariableNetcdfFilePathVisitor(time_dict)
        var.accept(visitor)
        datasets: Dict[VariableId, xr.Dataset] = dict()
        for var_id, netcdf_file_path in visitor.result.items():
            datasets[var_id] = xtract.open_netcdf(netcdf_file_path)
        self.__core_extraction(var, datasets)

    def get_result(self) -> List[Tuple[LabelId, np.ndarray, MetaDataBlock]]:
        return self.result
