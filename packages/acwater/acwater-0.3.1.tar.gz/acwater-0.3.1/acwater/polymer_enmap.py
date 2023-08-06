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
""" The polymer_enmap module contains specifications and parameters of EnPT data for running polymer.

Detector parameters (e.g. wavelengths) are provided by the EnMAP Core Science Team.
Atmospheric parameters require ancillary data for
ozone (O2), nitrogen dioxide (NO2), and the extraterrestrial radiation (solar spectrum).

"""

import numpy as np

import pandas as pd
from os.path import join
from scipy.interpolate import interp1d

import os
import pkgutil
from pathlib import PurePath

try:
    dir_polymer = PurePath(os.path.dirname(pkgutil.get_loader("polymer").path)).parent
    dir_common = os.path.join(dir_polymer,'auxdata','common')
except:
    dir_common = PurePath(os.path.dirname(pkgutil.get_loader("enpt").path)).parent.parent
    aux = [aux for aux in os.listdir(dir_common) if aux.startswith('polymer')]
    aux = [aux for aux in aux if os.path.isdir(os.path.join(dir_common,aux,'auxdata','common'))][0]
    dir_polymer = os.path.join(dir_common,aux)
    dir_common = os.path.join(dir_polymer,'auxdata','common')

assert (os.path.isdir(dir_common))

# FIXME: review set up for the climatology
#  (e.g. K_OZ and K_NO2): investigate SCIATRAN and SeaDAS, currently uses SeaDAS as in hico

def filter_bands(bands, detector):
    # ------------------------------------------------------------
    # selection based on absorption features (H20, O3)
    # reference: https://amt.copernicus.org/articles/11/3205/2018/
    # ------------------------------------------------------------
    exact_bands_ = [550, 630, 690, 720, 760, 820, 940, 1060, 1100, 1270, 1380,
                   1400, 1580, 1600, 1870, 2000]  # strong absorption bands of O3 and NO2
    delta_wl = 1.5  # delta wavelength to search for be removed from bands_wavelength

    if detector == 'vnir':
        bands_wavelength = [x for x in bands if x < 1000]  # use only bands below 780 nm as hard-code previous version
    else:
        bands_wavelength = [x for x in bands if x < 1300]

    bands_to_remove = []  # create list for store actual bands to be removed

    for rb in exact_bands_:
        tmp = [x for x in bands_wavelength if x >= rb - delta_wl]
        bands_to_remove.extend([x for x in tmp if x <= rb + delta_wl])

    bands_to_use = [x for x in bands_wavelength if x not in bands_to_remove]

    # select band for cloud mask, !!Need to be check again if this is the right band
    band_cloudmask = [x for x in bands if x >= 863 - delta_wl]
    band_cloudmask = [x for x in band_cloudmask if x <= 863 + delta_wl]

    return bands_to_use, band_cloudmask[0]

def params_enmap(bands):

    band_wavelengths = bands

    # --------------------------------------------------------------------------------
    # detector calibration
    # set to one
    calib = {b: 1. for b in band_wavelengths}

    # --------------------------------------------------------------------------------
    # K_OZ:  Total ozone optical depth for 1000 DU

    # get ancillary data
    ozone_file = 'k_oz.csv'  # afglus atmospheric profile [350, 900 nm]
    k_oz_data = pd.read_csv(join(dir_common, ozone_file), comment="#")

    # interpolate to enmap bands
    k_oz = interp1d(k_oz_data.wavelength, k_oz_data.K_OZ, bounds_error=False, fill_value=0.)
    K_OZ_ENMAP = {b: k for b, k in zip(bands, k_oz(np.array(band_wavelengths)))}

    # --------------------------------------------------------------------------------
    # K_NO2: NO2 optical depth
    # get ancillary data,
    from polymer.hico import K_NO2_HICO  # same as K_OZ_HICO / SeaDAS

    # interpolate to enmap bands
    f_no2 = interp1d(list(K_NO2_HICO.keys()), list(K_NO2_HICO.values()), bounds_error=False, fill_value=0.)
    K_NO2_ENMAP = {b: k for b, k in zip(bands, f_no2(np.array(band_wavelengths)))}

    return K_NO2_ENMAP, K_OZ_ENMAP, calib


def solar_spectrum(bands):

    band_wavelengths = bands

    # --------------------------------------------------------------------------------
    # Solar spectrum

    try:
        # get ancillary data
        solar_spectrum_file = 'f0.txt'  # source <https://oceancolor.gsfc.nasa.gov/docs/rsr/f0.txt>
        solar_data = pd.read_csv(join(dir_common, solar_spectrum_file),
                                 delimiter=r"\s+|\t+|\s+\t+|\t+\s+", skiprows=15, header=None, engine='python')
        # interpolate to enmap bands
        F0 = interp1d(solar_data[0], solar_data[1])
        F0_ENMAP = np.array(F0(np.array(band_wavelengths)), dtype='float32')
    except:
        # get ancillary data
        solar_spectrum_file = 'SOLAR_SPECTRUM_WMO_86'  # source: polymer <http://download.hygeos.com/POLYMER/auxdata>
        solar_data = pd.read_csv(join(dir_common, solar_spectrum_file), sep=' ')
        # interpolate to enmap bands
        F0 = interp1d(solar_data['lambda(nm)'], solar_data['Sl(W.m-2.nm-1)'])
        F0_ENMAP = np.array(F0(np.array(band_wavelengths)) * 100., dtype='float32')

    return F0_ENMAP

