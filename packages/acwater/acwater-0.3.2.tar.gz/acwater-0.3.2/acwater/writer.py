# -*- coding: utf-8 -*-
#
# Atmospheric correction of EnMAP hyperspectral data for water surfaces
# acwater.py is a wrapper for Polymer algorithm (Hygeos) to run in EnPT (GFZ-Potsdam)
# Polymer was further adapted to process EnMAP L1B satellite data.
#
# Copyright (C) 2020  by Alfred Wegener Institute (AWI), Helmholtz Centre for Polar and Marine Research
# Astrid Bracher (AWI Bremerhaven, abracher@awi.de),
# Mariana Soppa (AWI Bremerhaven, msoppa@awi.de),
# Leonardo Alvarado (AWI Bremerhaven, leonardo.alvarado@awi.de), and
# Brenner Silva (AWI Bremerhaven)
#
# This software was developed at the Alfred-Wegener-Institute, Bremerhaven, supported by the DLR Space Administration
# with funds of the German Federal Ministry of Economic Affairs and Energy
# (on the basis of a decision by the German Bundestag: 50 EE 1529, 50 EE 1923 and 50 EE 1915)
# and contributions from GFZ, Potsdam.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# Please note that for proposed application of this software, specific terms do apply to the required software:
# EnPT is free software (GPLv3), with one exception ('tqdm', https://github.com/tqdm/tqdm/blob/master/LICENCE)
# polymer is distributed under its own licence (https://www.hygeos.com/polymer/licence)
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
This motule implements a Writer class for dumping EnMAP as netcdf.
"""
#todo: writer is not compatible with current read from file.nc,
# since now detectors value are included in detectors group, which includes lat lon for each detector

import logging
import os

from netCDF4 import Dataset

from enpt.model.images import EnMAPL1Product_SensorGeo
from enpt.options.config import EnPTConfig


class L1B_Writer(object):
    """Writer for EnMAP Level-1B products."""

    def __init__(self,
                 config: EnPTConfig = None,
                 logger: logging.Logger = None):
        """Write out an instance of L1B_Reader.

        :param config:  instance of EnPTConfig class
        :param logger:  instance of logging.Logger (NOTE: This logger is only used to log messages within L1B_Reader.
                                                          It is not appended to the read L1B EnMAP object).
        """

        self.cfg = config
        self.logger = logger or logging.getLogger(__name__)

    def write_data(self,
                   data_obj: EnMAPL1Product_SensorGeo,
                   out_dir,
                   out_file,
                   fmt: str = 'NETCDF4') -> bool:
        """Write out an instance of L1B_Reader (L1B EnMAP data)

                :param out_dir: output directory
                :param fmt: format
                :return: true if succeded or false if fails
                """

        self.logger.info("Writing Data : " + os.path.join(out_dir, out_file) + ", format " + fmt)

        # new netcdf file
        rootgrp = Dataset(os.path.join(out_dir, out_file), "w", format=fmt)

        # create dimensions
        rootgrp.createDimension("samples", None)
        rootgrp.createDimension("scan_lines", None)
        rootgrp.createDimension("bands", None)

        # create groups
        navigation = rootgrp.createGroup("navigation")
        products = rootgrp.createGroup("products")
        scan_line_attributes = rootgrp.createGroup("scan_line_attributes")
        metadata = rootgrp.createGroup("metadata")

        # products
        for detector_name in ['vnir','swir']:
            detector = getattr(data_obj,detector_name)
            data_type = 'f8'
            # multi
            detector_group = products.createGroup(detector_name)
            var = detector_group.createVariable(detector_name,data_type,("scan_lines","samples","bands",))
            # vnir-only
            # var = products.createVariable(detector_name,data_type,("scan_lines","samples","bands",))
            var[:] = detector.data.arr

            # attributes
            var.wavelength_units = 'nanometers'
            var.long_name = ''

            aux=detector.detector_meta.offsets
            try:
                var.add_offset = [x if x is not None else 0.0 for x in aux]
            except TypeError:
                var.add_offset = aux if aux else 0.0
            aux=detector.detector_meta.gains
            try:
                var.scale_factor = [x if x is not None else 1.0 for x in aux]
            except TypeError:
                var.scale_factor = aux if aux else 1.0

            var.units = detector.detector_meta.unit
            var.wavelengths = detector.detector_meta.wvl_center
            var.fwhm = detector.detector_meta.fwhm


            #----------------------------------------------------------------------
            # navigation
            # FIXME: why longitudes is a 2d-array while lons is 3d??
            var_name = 'longitudes'
            data_type = 'f8'
            # multi
            var = detector_group.createVariable(var_name, data_type, ("scan_lines","samples",))
            # vnir-only
            # var = navigation.createVariable(var_name, data_type, ("scan_lines","samples",))
            #FIXME: gets only first array (assumes perfect bands co-registration)
            var[:] = detector.detector_meta.lons[:,:,0] \
                if len(detector.detector_meta.lons.shape) == 3 \
                else detector.detector_meta.lons[:,:]
            var_name = 'latitudes'
            data_type = 'f8'
            # multi
            var = detector_group.createVariable(var_name, data_type, ("scan_lines", "samples",))
            #vnir only
            # var = navigation.createVariable(var_name, data_type, ("scan_lines","samples",))
            var[:] = detector.detector_meta.lats[:,:,0] \
                if len(detector.detector_meta.lats.shape) == 3 \
                else detector.detector_meta.lats[:,:]

        # FIXME: why is sensor zenith 2d-array while geom_zenith is 1 scalar? same for solar zenith, sensor_azimuth,
        var_name = 'sensor_zenith'
        data_type = 'f8'
        var = navigation.createVariable(var_name, data_type, ("scan_lines","samples",))
        var[:] = data_obj.meta.geom_view_zenith
        var.units = 'degrees'
        var.valid_max = 180.0
        var.valid_min = -180.0

        var_name = 'solar_zenith'
        data_type = 'f8'
        var = navigation.createVariable(var_name, data_type, ("scan_lines", "samples",))
        var[:] = data_obj.meta.geom_sun_zenith
        # FIXME: check for convention, could min/max values lies between -180 and 180?
        var.units = 'degrees'
        var.valid_max = 90.0
        var.valid_min = 0.0

        var_name = 'sensor_azimuth'
        data_type = 'f8'
        var = navigation.createVariable(var_name, data_type, ("scan_lines", "samples",))
        var[:] = data_obj.meta.geom_view_azimuth

        var_name = 'solar_azimuth'
        data_type = 'f8'
        var = navigation.createVariable(var_name, data_type, ("scan_lines", "samples",))
        var[:] = data_obj.meta.geom_sun_azimuth

        # scan_line_attributes
        var_name = 'scan_quality_flags'
        data_type = 'u8'
        var = scan_line_attributes.createVariable(var_name, data_type, ("scan_lines","samples",))

        #----------------------------------------------------------------------
        # metadata
        # datetime without microseconds
        metadata.observation_datetime = str(data_obj.meta.observation_datetime).split('.')[0]

        rootgrp.close()

