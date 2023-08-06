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
#

"""

This script runs Polymer using formatted text/ASCII-file

"""
# todo: cli

# from polymer.ancillary_era5 import Ancillary_ERA5

from polymer.main import run_atm_corr

from polymer.level1 import Level1

from polymer.level2 import Level2

from polymer.level1_ascii import Level1_ASCII

def example_ascii():
    """
    Process an ASCII file (here for SCIATRAN-simulated ENMAP)
    using custom calibration coefficients
    returns in-memory level2 (do not write file)
    """
    filename = 'extraction_reshape.csv'
    import os
    assert os.path.isfile(filename)

    headers_custom = {
        'TOA': lambda i, b: 'TOAR_{:03d}'.format(i + 1),
        'RHO_WN': lambda i, b: 'RHO_WN_{:03d}'.format(i + 1),
        'E_DOWN': lambda i, b: 'E_DOWN_{:03d}'.format(i + 1),  # must be calculated (see params.py) based on lambda0
        # 'LAMBDA0': lambda i, b: 'LAMBDA0_{:03d}'.format(i + 1), #  request from enmap.py WAV_ENMAP
        'LAT': 'latitude',
        'LON': 'longitude',
        'DATETIME': 'date',
        'DETECTOR_INDEX': 'detector',
        'OZONE': 'ozone',
        'WIND': 'wind_speed',
        'SURFACE_PRESSURE': 'pressure',
        'ALTITUDE': 'altitude',
        'SZA': 'solar_zenith',
        'VZA': 'viewing',
        'RAA': 'azimuth',
    }
    # id, latitude, longitude, date, ozone, pressure, solar_zenith, viewing_angles, azimuth_angles, wind_speed, detector, altitude

    # l1_ascii = Level1_ASCII(filename, square=1, sensor='ENMAP',
    #              headers=headers_custom,
    #              TOAR='radiance',
    #              # BANDS =
    #              # wind_module=False, relative_azimuth=False,
    #              sep=r"[ \t]*,[ \t]*", skiprows=0
    #              )

    l2 = run_atm_corr(Level1_ASCII(filename, square=1, sensor='ENMAP',
                                   headers=headers_custom,
                                   TOAR='radiance',
                                   # BANDS =
                                   # wind_module=False, relative_azimuth=False,
                                   sep=r"[ \t]*,[ \t]*", skiprows=0
                                   ),
                      Level2('memory'),
                      force_initialization=True,
                      # calib={
                      #    412: 1.01, 443: 0.99,
                      #    490: 1.0 , 510: 1.0,
                      #    560: 1.0 , 620: 1.0,
                      #    665: 1.0 , 681: 1.0,
                      #    709: 1.0 , 754: 1.0,
                      #    760: 1.0 , 779: 1.0,
                      #    865: 1.0 , 885: 1.0,
                      #    900: 1.0 ,
                      #    }
                      calib=None
                      # or calib=None to set all coefficients to 1
                      # (default calibration: use per-sensor defaults as defined in
                      #  param.py)
                      )

    # read input for comparison
    import pandas as pd
    l1 = pd.read_csv(filename,
                     sep=r"[ \t]*,[ \t]*", skiprows=0
                     )
    from acwater.polymer_enmap import BANDS_ENMAP, F0_ENMAP, WAV_ENMAP
    bands_label = 'RHO_WN'  # 'TOA'
    l1.bands = dict([(b, headers_custom[bands_label](i, b)) for (i, b) in enumerate(BANDS_ENMAP)])

    bands_label = 'E_DOWN'  # 'TOA'
    l1.bands_ed = dict([(b, headers_custom[bands_label](i, b)) for (i, b) in enumerate(BANDS_ENMAP)])

    # ploting
    import matplotlib.pyplot as plt

    for i, v in enumerate(l2.Rw[:, 0, 0]):
        #     # plt.plot(l2.bands, l2.Rw[i,0,:])  # plot spectrum of pixel at (0,0)
        #     # plt.plot(list(l1.bands.keys()), l1[l1.bands.values()].iloc[i, :])  # plot spectrum of pixel at (0,0)
        a = l2.bands
        b = l2.Rw[i, 0, :]

        m = list(l1.bands.keys())
        n = l1[l1.bands.values()].iloc[i, :]
        p = l1[l1.bands_ed.values()].iloc[i, :]

        fig, ax = plt.subplots()
        ax.plot(a, b, 'k--', label='polymer - Rw')
        # ax.plot(m, n, 'k', label='sciatran - Water leaving')
        import numpy as np
        ax.plot(m, np.array(n) / np.array(p), 'k:', label='sciatran - Wl / Edn')

        ax.legend(loc='upper right', shadow=True, fontsize='x-large')

    plt.show()

    # i=0
    #
    # a = l2.bands
    # b = l2.Rw[i,0,:]
    #
    # m = list(l1.bands.keys())
    # n = l1[l1.bands.values()].iloc[i, :]
    # p = l1[l1.bands_ed.values()].iloc[i, :]
    #
    # fig, ax = plt.subplots()
    # ax.plot(a, b, 'k--', label='polymer - Rw')
    # # ax.plot(m, n, 'k', label='sciatran - Water leaving')
    # import numpy as np
    # ax.plot(m, np.array(n)/np.array(p), 'k:', label='sciatran - Wl / Edn')
    #
    # legend = ax.legend(loc='upper right', shadow=True, fontsize='x-large')
    # plt.show()


if __name__ == "__main__":
    example_ascii()
