
import pandas as pd
import numpy as np

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

This script reshapes output from build-ascii into Polymer readable format for example_ascii

"""

# todo: cli

from acwater import polymer_enmap as enmap


filename='extraction.csv'
filename_out='extraction_reshape.csv'

sep=r"[ \t]*,[ \t]*"

data = pd.read_csv(filename,sep=sep)

meta_cols=list(range(12))

wavelength_grid_from = np.linspace(340, 1100, 761,retstep = False)
wavelength_grid_to = enmap.WAV_ENMAP
# grid_cols_out = [i for i, s in enumerate(wavelength_grid_to)]

data_meta = data[data.columns[meta_cols]].copy()

label_list=['TOAR_', 'RHO_WN_', 'E_DOWN_']
for label in label_list:

    grid_cols = [i for i, s in enumerate(data.columns) if label in s]

    # index=0

    # data_out = wavelength_grid_to.copy()
    data_out_bands = [str(int(round(b,0))) for b in wavelength_grid_to]
    data_out=pd.DataFrame(columns=data_out_bands)

    index=0
    for data_grid_from in data.iloc[:,grid_cols].values.astype(float):
        data_grid_to = np.interp(wavelength_grid_to, wavelength_grid_from, data_grid_from)
        data_grid_to = dict((b, [d]) for b,d in zip(data_out_bands,data_grid_to))
        data_grid_to = pd.DataFrame(data_grid_to)
        data_out=data_out.append(data_grid_to)

    meta_len = len(data_meta.columns)
    for c in data_out_bands:
        data_meta[c]=list(data_out[c])

    new_columns=list(range(meta_len, len(data_meta.columns)))

    new_columns_names = [label + '{:03d}'.format(i+1) for i in range(len(list(data_grid_to)))]
    # data_meta.columns[]=lambda i, b: label +'{:03d}'.format(i + 1)
    data_grid_to = dict((d, b) for d, b in zip(list(data_meta.columns[new_columns]), new_columns_names))
    data_meta=data_meta.rename(columns=data_grid_to)


data_meta.to_csv(filename_out, index=False, header=True)

pass
