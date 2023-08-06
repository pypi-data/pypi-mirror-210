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
#
# Please note that for proposed application of this software, specific terms do apply to the software dependencies:
# - Polymer is distributed under its own licence (https://www.hygeos.com/polymer/licence)
# - EnPT is free software (GPLv3), with dependencies (https://gitext.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT/-/blob/master/LICENSE)
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""The module level1_enmap contains the class that enables running the Polymer algorithm in the EnPT processing chain.

"""

from __future__ import print_function, division, absolute_import

from acwater.polymer_enmap import solar_spectrum #, get_bands_dict #, BANDS_ENMAP

from polymer.ancillary import Ancillary_NASA
from polymer.ancillary_era5 import Ancillary_ERA5
from polymer.block import Block
from polymer.common import L2FLAGS
from polymer.level1_nasa import filled
from polymer.utils import raiseflag

from polymer.gsw import GSW

from collections import OrderedDict
from datetime import datetime
import logging
import numpy as np

import os
import pkgutil
from pathlib import PurePath

try:
    from enpt.model.images.images_sensorgeo import EnMAPL1Product_SensorGeo
    from geoarray import GeoArray # GeoArray is required in EnPT
except:
    raise NotImplementedError('EnPT is required!')

try:
    dir_polymer = PurePath(os.path.dirname(pkgutil.get_loader("polymer").path)).parent
    dir_common = os.path.join(dir_polymer,'auxdata','common')
except:
    dir_common = PurePath(os.path.dirname(pkgutil.get_loader("enpt").path)).parent.parent
    aux = [aux for aux in os.listdir(dir_common) if aux.startswith('polymer')]
    aux = [aux for aux in aux if os.path.isdir(os.path.join(dir_common,aux,'auxdata','common'))][0]
    dir_polymer = os.path.join(dir_common,aux)
    dir_common = os.path.join(dir_polymer,'auxdata','common')

class Level1_ENMAP(object):
    """ The class for level 1 EnMAP data enables integrating Polymer processing into EnPT by
    giving the data object of EnPT as input to construct the Polymer object.

        Initialization using EnPT data object

        :param data_obj: EnPT Level 1 data object
        :param blocksize: block size for multiprocessing
        :param sline: lines to skip at begin of data array
        :param eline: lines to skip at end of data array
        :param scol: columns to skip at begin of data array
        :param ecol: columns to skip at end of data array
        :param ancillary: object for ancillyry data, defaults to ERA5 reanalysis data
        :param landmask: 'EnMAP_L1B' or 'GSW' or A GSW instance (see gsw.py), Example: landmask=GSW(directory='/path/to/gsw_data/')
        :param logger: logger object
        :param detector_name: EnMAP detector name, there are two ("vnir" for visible and near infrared, "swir" for short wave infrared), however only vnir is currently implemented

    """

    def __init__(self,
                 data_obj, # detector_meta=None, platform_meta=None,
                 blocksize=100,
                 sline=0, eline=-1, scol=0, ecol=-1,
                 ancillary='reanalysis',
                 landmask='EnMAP_L1B',
                 logger: logging.Logger = None,
                 detector_name='vnir',
                 bands_wavelength = None
                 ):

        self.sensor = 'GENERIC'  # create string for sensor name

        if hasattr(data_obj, 'logger'):
            self.logger = data_obj.logger or logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger(__name__)

        # if applicable use different mask for vnir and merge vnir+swir, for now, use mask of vnir
        if landmask == 'GSW':
            self.landmask = GSW(data_obj.cfg.output_dir)
        elif landmask == 'EnMAP_L1B':
            assert isinstance(data_obj.vnir.mask_landwater[:], (np.ndarray))
            self.landmask_data = data_obj.vnir.mask_landwater[:]
            self.landmask = landmask

        self.detector_name = detector_name

        assert detector_name in ['vnir', 'swir']

        self.detector_data = getattr(data_obj, self.detector_name).data
        self.detector_meta = getattr(data_obj, self.detector_name).detector_meta

        self.bands_enmap = bands_wavelength
        if not self.bands_enmap:
            self.bands_enmap = self.detector_meta.wvl_center

        self.f0_enmap = solar_spectrum(self.bands_enmap)

        self.platform_meta = data_obj.meta

        self.filename = data_obj.cfg.path_l1b_enmap_image.split('.')[0]

        # > detector.data: GeoArray
        self.totalheight, self.totalwidth, self.nlam = self.detector_data.shape  # ints for total size

        # defaults to polymer root for ancillary data
        # dir_ancillary = PurePath(os.path.dirname(pkgutil.get_loader("polymer").path)).parent
        if ancillary == 'reanalysis':
            # defaults option
            dir_ancillary = dir_polymer / 'ANCILLARY' / 'ERA5'
            self.ancillary = Ancillary_ERA5(directory=dir_ancillary)
        elif ancillary == 'climatology':
            dir_ancillary = dir_polymer / 'ANCILLARY' / 'METEO'
            self.ancillary = Ancillary_NASA(directory=dir_ancillary)
        else:
            self.ancillary = ancillary

        self.blocksize = blocksize  # int for blocksize
        self.sline = sline  # int for skip
        self.scol = scol  # int for skip

        if eline < 0:
            self.height = self.totalheight  # int for slice
            self.height -= sline
            self.height += eline + 1
        else:
            self.height = eline - sline

        if ecol < 0:
            self.width = self.totalwidth  # int for slice
            self.width -= scol
            self.width += ecol + 1
        else:
            self.width = ecol - scol

        self.shape = (self.height, self.width)  # ints for shape

        if logger:
            logger.info('Initializing ENMAP product of size', self.shape)
        else:
            print('Initializing ENMAP product of size', self.shape)

        self.datetime = self.get_time()  # data acquisition/satellite overpass

        self.init_landmask()

        # initialize ancillary data

        self.ancillary_files = OrderedDict()  # ancillary dict for filenames
        if self.ancillary is not None:
            self.init_ancillary()

    def init_ancillary(self):
        self.ozone = self.ancillary.get('ozone', self.datetime)  # ancillary objects
        self.wind_speed = self.ancillary.get('wind_speed', self.datetime)
        self.surf_press = self.ancillary.get('surf_press', self.datetime)
        self.ancillary_files.update(self.ozone.filename)
        self.ancillary_files.update(self.wind_speed.filename)
        self.ancillary_files.update(self.surf_press.filename)

    def init_landmask(self):
        # > detector.detector_meta.lats: array lat/long
        # GSW case
        if hasattr(self.landmask, 'get'):
            lat = filled(self.detector_meta.lats[:, :, 0])  # array lat
            lon = filled(self.detector_meta.lons[:, :, 0])  # array lon
            self.landmask_data = self.landmask.get(lat, lon)
            self.logger.info('Landmask is GSW')
        # EnMAP L1B case
        elif self.landmask == 'EnMAP_L1B':
            self.landmask_data = self.landmask_data != 2 # 2 is for water
            self.logger.info('Landmask is EnMAP L1B')

    def get_time(self):
        # > data_obj.meta.observation_datetime
        beg_date = str(self.platform_meta.observation_datetime)
        beg_date = beg_date.strip().split(".")[0]  # exclude microseconds
        return datetime.strptime(beg_date, '%Y-%m-%d %H:%M:%S')

    def read_block(self, size, offset, bands):
        nbands = len(bands)  # number of bands
        size3 = size + (nbands,)  #
        (ysize, xsize) = size  # tuple for size
        (yoffset, xoffset) = offset  # tuple offset
        SY = slice(offset[0] + self.sline, offset[0] + self.sline + size[0])  # slice? Y coordinates in data
        SX = slice(offset[1] + self.scol, offset[1] + self.scol + size[1])  # X coordinates in data

        block = Block(offset=offset, size=size, bands=bands)  # Block object
        block.jday = self.datetime.timetuple().tm_yday  # julian day
        block.month = self.datetime.timetuple().tm_mon  # month

        # fixme: how to handle the third dimension? For now it assumes perfect bands co-registration
        if len(self.detector_meta.lats.shape) == 3:
            block.latitude = filled(self.detector_meta.lats[:, :, 0][SY, SX])
            block.longitude = filled(self.detector_meta.lons[:, :, 0][SY, SX])
        else:
            block.latitude = filled(self.detector_meta.lats[:, :][SY, SX])
            block.longitude = filled(self.detector_meta.lons[:, :][SY, SX])

        # using 2D array for geometry
        # parameters are filled from a single value based on block size instead of extracting them using eh SY, SX coordinates
        # uses a lighter dtype, single float32, not double, required in blocks processing
        block.sza = filled(np.full(size, self.platform_meta.geom_sun_zenith, dtype='float32'))
        block.vza = filled(np.full(size, self.platform_meta.geom_view_zenith, dtype='float32'))
        block.saa = filled(np.full(size, self.platform_meta.geom_sun_azimuth, dtype='float32'))
        block.vaa = filled(np.full(size, self.platform_meta.geom_view_azimuth, dtype='float32'))

        # read bitmask
        block.bitmask = np.zeros(size, dtype='uint16')

        # -----------------------------------------------------------------
        # get corresponding bands
        ibands = np.array([self.bands_enmap.index(b) for b in bands])  # bands values

        # initialize block
        block.Ltoa = np.zeros(size3) + np.NaN # block variable np array
        block.Ltoa[:] = filled(self.detector_data.arr[SY, SX, ibands])
        # block.Ltoa = filled(self.detector_data.arr[SY, SX, ibands])

        # # arrays contain TOARad
        # > detector.detector_meta.unitcode:str = "TOARad"
        # > detector.detector_meta.unit = 'mW m^-2 sr^-1 nm^-1'
        if self.detector_meta.unitcode == "TOARad" and self.detector_meta.unit == 'mW m^-2 sr^-1 nm^-1':
            pass
            # no need to rescale, directly assign TOARad to Ltoa
        else:
            # > detector.detector_meta.offsets
            # > detector.detector_meta.gains
            # # assumes array contains DNs and apply gains and offset
            aux = self.detector_meta.offsets
            try:
                intercept = [x if x is not None else 0.0 for x in aux]
            except TypeError:
                intercept = aux if aux else 0.0
            aux = self.detector_meta.gains
            try:
                slope = [x if x is not None else 1.0 for x in aux]
            except TypeError:
                slope = aux if aux else 1.0

            # assign TOARad to Ltoa
            block.Ltoa = block.Ltoa * slope + intercept

            self.detector_meta.unit = 'mW m^-2 sr^-1 nm^-1'
            self.detector_meta.unitcode = "TOARad"

        # # after  DNs are converted to radiance, EnMAP TOA should have following units
        assert self.detector_meta.unit == 'mW m^-2 sr^-1 nm^-1'
        assert self.detector_meta.unitcode == "TOARad"

        block.Ltoa /= 10 # convert mW/m^2/sr/nm -> mW/cm^2/um/sr

        # load solar irradiance spectrum
        block.F0 = np.zeros(size3) + np.NaN
        block.F0[:,:,:] = self.f0_enmap[None,None,ibands]
        # block.F0 = np.full(size3, F0_ENMAP[None, None, ibands])

        # wavelength - bands and central wavelengths
        block.wavelen = np.zeros(size3, dtype='float32') + np.NaN
        block.wavelen[:, :, :] = np.array(self.bands_enmap, dtype='float32')[None, None, ibands]
        # block.wavelen = np.full(size3, WAV_ENMAP[None, None, ibands])

        block.cwavelen = np.array(self.bands_enmap, dtype='float32')[ibands]

        # ancillary data of atmosphere
        block.ozone = np.zeros(size, dtype='float32')
        block.ozone[:] = self.ozone[block.latitude, block.longitude]
        block.wind_speed = np.zeros(size, dtype='float32')
        block.wind_speed[:] = self.wind_speed[block.latitude, block.longitude]
        block.surf_press = np.zeros(size, dtype='float32')
        block.surf_press[:] = self.surf_press[block.latitude, block.longitude]

        block.altitude = np.zeros(size, dtype='float32')

        if self.landmask is not None:
            raiseflag(block.bitmask, L2FLAGS['LAND'],
                      self.landmask_data[
                      yoffset + self.sline:yoffset + self.sline + ysize,
                      xoffset + self.scol:xoffset + self.scol + xsize,
                      ])

        return block

    def blocks(self, bands_read):
        nblocks = int(np.ceil(float(self.height) / self.blocksize))

        # python generator
        for iblock in range(nblocks):
            # determine block size and go through top-down row-wise
            xsize = self.width
            if iblock == nblocks - 1:
                ysize = self.height - (nblocks - 1) * self.blocksize
            else:
                ysize = self.blocksize
            size = (ysize, xsize)

            # determine the block offset
            xoffset = 0
            yoffset = iblock * self.blocksize
            offset = (yoffset, xoffset)

            yield self.read_block(size, offset, bands_read)

    def attributes(self, date_format=None):
        attr = OrderedDict()
        attr['datetime'] = self.datetime.strftime(date_format) if date_format else self.datetime
        return attr

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
