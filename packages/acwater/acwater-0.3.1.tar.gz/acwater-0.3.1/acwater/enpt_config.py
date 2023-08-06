#!/usr/bin/env python
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

import os
import pkgutil

path_enptlib = os.path.dirname(pkgutil.get_loader("enpt").path)
path_acwater = os.path.dirname(pkgutil.get_loader("acwater").path)
path_polymer = os.path.abspath(os.path.join(os.path.dirname(pkgutil.get_loader("polymer").path), os.pardir))
path_options_default = os.path.join(path_enptlib, 'options', 'options_default.json')

config_for_testing_water = dict(
    path_l1b_enmap_image=os.path.abspath(
    os.path.join(path_acwater, '..', 'tests', 'data', 'ENMAP01-____L1B-DT000400126_20170218T110115Z_002_V000204_20200206T182719Z__rows700-730.zip')
    # os.path.join(path_acwater, '..', 'tests', 'data', 'L1B_Arcachon_3.zip')
    ),
    # path_dem=os.path.abspath(os.path.join(path_acwater, '..', 'tests', 'data', 'ASTGTM_Arcachon_DEM.tif')),
    log_level='DEBUG',
    output_dir=os.path.join(path_acwater,  '..', 'tests', 'data', 'test_outputs'),
    disable_progress_bars=False,
    is_dummy_dataformat=False,
    auto_download_ecmwf=True,
    average_elevation=0,
    deadpix_P_algorithm='spectral',
    deadpix_P_interp_spatial='linear',
    deadpix_P_interp_spectral='linear',
    enable_cloud_screening=False,
    enable_ice_retrieval=True,
    enable_keystone_correction=False,
    enable_vnir_swir_coreg=False,
    n_lines_to_append=None,
    ortho_resampAlg='nearest',
    run_deadpix_P=True,
    run_smile_P=False,
    scale_factor_boa_ref=10000,
    scale_factor_toa_ref=10000,
    enable_ac=True,
    mode_ac='combined',
    polymer_root=path_polymer,
    threads=-1,
    blocksize=100,
    vswir_overlap_algorithm='swir_only',
    CPUs=16
)

