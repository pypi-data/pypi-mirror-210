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
""" The acwater module calls Polymer (Hygeos) using EnPT (GFZ/EnMAP) parameters.

"""

from polymer.main import run_atm_corr

from polymer.level2 import Level2

from acwater.polymer_enmap import params_enmap, filter_bands

from acwater.level1_enmap import Level1_ENMAP

from enpt.options.config import EnPTConfig

import numpy as np
import logging
from os.path import expanduser, isfile
import os

__author__ = 'Brenner Silva and Leonardo Alvarado'

def polymer_ac_enmap(enmap_l1b, level2='memory', config: EnPTConfig = None, detector='vnir'):
    """The polymer_ac_enmap function calls polymer using EnMAP data specific parameters

    :param enmap_l1b: the object of EnMAP level 1 data
    :param level2: the file name for the output data or 'memory", the latter is default for using with EnPT
    :param config: of EnPTConfig type must contain:
        * CPUs: number of CPUs, here combined with number of threads, if threads not given.
        * threads: number of threads for specifying number of threads.
        * blocksize: size in rows for each thread in multiprocessing
        * auto_download_ecmwf: for using reanalyses ERA5 data
    :param detector: "vnir" for visible to near infrared or "merge" to include shortwave infrared (swir) detector
    :return: level2 data object
    """

    print(detector)

    logger = enmap_l1b.logger or logging.getLogger(__name__)

    logger.info("Running polymer...")

    # use config of EnPT
    if config is not None:
        assert isinstance(config, EnPTConfig)
        blocksize = config.blocksize
        # threads number is combined with number of CPUs, but n threads can be larger if given
        threads = config.threads if int(
            config.threads) != -1 else -1 if config.CPUs is None else int(config.CPUs)

        # ancillary_source = 'reanalysis' if config.auto_download_ecmwf else 'climatology'
        #fixme: once climatology option is fixed, it can be triggered by config.auto_download_ecmwf, as in:
        # for now just give warning:
        ancillary_source = 'reanalysis'
        if not config.auto_download_ecmwf:
            logger.warning("Currently only tested with ERA5 data, i.e. set True for \"auto_download_ecmwf\"")
    else:
        blocksize = 100
        threads = -1
        ancillary_source = 'reanalysis'

    # check for key file, required in downloading ancillary data
    home = expanduser("~")
    if ancillary_source == 'reanalysis' and \
       not isfile(home + "/.cdsapirc") and \
       not ('CDSAPI_URL' in os.environ and 'CDSAPI_KEY' in os.environ):
        logger.error("Missing CDS API key, see ACwater Polymer instructions")
    elif ancillary_source == 'climatology' and not isfile(home + "/.netrc") and not isfile(home + "/.urs_cookies"):
        logger.error("Missing NASA Earthdata key file, see ACwater Polymer instructions")

    # check input for detector name
    assert detector in ['vnir', 'merge', 'vnswir']

    # select detector band
    if detector == 'vnir':

        bands_wavelength = enmap_l1b.meta.vnir.wvl_center.tolist() # create list of wavelength from center

        ibands_vnir = [bands_wavelength.index(b) for b in enmap_l1b.vnir.detector_meta.wvl_center]

        l1_enmap = Level1_ENMAP(enmap_l1b,
                                blocksize=blocksize,
                                bands_wavelength=bands_wavelength,
                                detector_name=detector,
                                ancillary=ancillary_source)

        # New implementation for flexible input wavelength bands from EnMAP (syntethic, comissioning, nominal)
        # previous version did not remove strong absorbers, but wavelength range is limited, it has been updated
        bands_to_use, band_cloudmask = filter_bands(bands = bands_wavelength,
                                                    detector = detector)

    elif detector == 'merge' or detector == 'vnswir':
        # vnir and swir

        bands_wavelength = sorted(enmap_l1b.meta.vnir.wvl_center.tolist() + enmap_l1b.meta.swir.wvl_center.tolist())

        ibands_vnir = [bands_wavelength.index(b) for b in enmap_l1b.vnir.detector_meta.wvl_center]
        ibands_swir = [bands_wavelength.index(b) for b in enmap_l1b.swir.detector_meta.wvl_center]

        from enpt.processors.orthorectification import VNIR_SWIR_Stacker

        # ------------------------------
        # # corregistration vnir to swir
        enmap_l1b.swir.data = enmap_l1b.transform_swir_to_vnir_raster(enmap_l1b.swir.data)

        data_geoarray = VNIR_SWIR_Stacker(vnir=enmap_l1b.vnir.data,
                                          swir=enmap_l1b.swir.data,
                                          vnir_wvls=enmap_l1b.meta.vnir.wvl_center,
                                          swir_wvls=enmap_l1b.meta.swir.wvl_center
                                          ).compute_stack(algorithm='order_by_wvl')

        # solution 1: use vnir object as data carrier
        enmap_l1b.vnir.data = data_geoarray
        # cannot delete, thus reduce size (issue with int8)
        enmap_l1b.swir.data[:] = enmap_l1b.swir.data[:].astype(dtype='float16')
        # instantiate class
        l1_enmap = Level1_ENMAP(enmap_l1b,
                                blocksize=blocksize,
                                bands_wavelength=bands_wavelength,
                                ancillary = ancillary_source)

        bands_to_use, band_cloudmask = filter_bands(bands=bands_wavelength,
                                                    detector=detector)

    else:
        raise NotImplementedError

    if level2 == 'memory':
        level2_object = Level2('memory')
    elif isinstance(level2, Level2):
        level2_object = level2
    else:
        # level2 is file name
        level2_object = Level2(filename=level2, fmt='netcdf4', overwrite=True)

    K_NO2, K_OZ, calib = params_enmap(bands_wavelength)

    product = run_atm_corr(l1_enmap,
                           level2=level2_object,
                           multiprocessing=threads,
                           # params for enmap, using 'GENERIC' as sensor attribute
                           bands_corr=bands_to_use,
                           bands_oc=bands_to_use,
                           bands_rw=bands_wavelength,
                           calib=calib,
                           K_OZ=K_OZ,
                           K_NO2=K_NO2,
                           band_cloudmask=band_cloudmask,
                           thres_Rcloud=0.2,
                           thres_Rcloud_std=0.04
                           )


    if detector == 'vnir':
        enmap_l2a_vnir = product.Rw[:, :, ibands_vnir]
        enmap_l2a_swir = np.ones(enmap_l1b.swir.data.shape, dtype=float) / config.scale_factor_boa_ref
    elif detector == 'merge' or detector == 'vnswir':
        enmap_l2a_vnir = product.Rw[:, :, ibands_vnir]
        enmap_l2a_swir = product.Rw[:, :, ibands_swir]
        enmap_l2a_swir = enmap_l1b.transform_vnir_to_swir_raster(enmap_l2a_swir)

    # Feature for other products can be returned separately as in:
    # return enmap_l2a_vnir, enmap_l2a_swir, product.logchl, product.logfb, product.bitmask, product.Rgli, product.Rnir
    # or combined in an additional output as in
    enmap_products = {'polymer_logchl' : product.logchl,
                    'polymer_logfb' : product.logfb,
                    'polymer_rgli' : product.Rgli ,
                    'polymer_rnir' : product.Rnir ,
                    'polymer_bitmask' : np.array(product.bitmask, dtype=np.int16) }

    return enmap_l2a_vnir, enmap_l2a_swir, enmap_products
