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

This script converts SCIATRAN output into Polymer readable ASCII-format

"""
# todo: cli

import zipfile
from glob import glob
import shutil

# import os

# FIXME: only horizontal as ascii for reading in polymer
# False for R
horizontal = True

path_to_zip_file = "*DATA_OUT.zip"
path_to_zip_file = 'sx_*.zip'
directory_to_extract_to = "./"

files = sorted(glob(path_to_zip_file))
print(files)
ifile = 0
out_table = []
out = []
head = []
icount = 1
bool_next = False
zenith_0_to_90 = True

for ifile in range(0, len(files)):

    print(ifile)
    print(files[ifile])

    # unzip and read settings file
    data_directory = directory_to_extract_to + files[ifile].split('.')[0] + "/"
    zip_ref = zipfile.ZipFile(files[ifile], 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()
    file_pars = data_directory + "DATA_OUT/SCE_INP-PARS.OUT"

    # load setting file in read_pars variable
    read_pars = []
    with open(file_pars) as f:
        for line in f:
            read_pars.append(line.strip())

    # initialize meta data table
    meta_data = []
    meta_data.append(str(icount))
    head.append("id")

    # extract lines from setting data in read_pars
    s1 = "*** RTM Mode"
    if s1 in read_pars:
        i = read_pars.index(s1)
        mode = read_pars[i + 1].split(' ')[1]
        meta_data.append(mode)
        s1 = s1.split('*** ')[-1]
        head.append(s1)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Inelastic processes wihtin water"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split('--> ')[-1]
        meta_data.append(s2)
        s1 = s1.split('*** ')[-1]
        head.append(s1)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** File name for chlorophyll concentration"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split('wt_')[1].split('_chl')[0]
        meta_data.append(s2)
        s1 = s1.split('*** ')[-1]
        head.append(s1)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Parameters of specific absorption coefficient"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split()[2]
        meta_data.append(s2)
        s1 = s1.split('*** ')[-1]
        head.append(s1)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Concentrations of fulvic and humic acids"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split('--> ')[-1].split('/')[-1].split('\'')[0]  #
        meta_data.append(s2)
        s2 = read_pars[i + 2].split('--> ')[-1].split('/')[-1].split('\'')[0]  #
        meta_data.append(s2)
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        head.append(s1 + "_1")
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        head.append(s1 + "_1")
        meta_data.append(s1)
        meta_data.append(s1)

    s1 = "*** Hydrosol angular scattering"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]  # .split(' ')[0]
        s1 = s1.split('*** ')[-1].split(' ')[0]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** File names for scattering function/matrix (hydrosols)"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1].split('_ism')[1].split('.dat')[0]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Standard profile scenario file name"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split('/')[-1]  # .split('_chl')[0]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        head.append(s1 + "_1")
        s3 = s2.split('mon')[-1].split('lat')[0]
        meta_data.append(s3)
        s3 = s2.split('lat')[-1][:2]
        if s2.split('lat')[-1][2] == "s":
            s3 = "-" + s3
        meta_data.append(s3)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)
        head.append(s1 + "_1")
        meta_data.append(s1)

    s1 = "*** Flat or wind-roughed ocean surface"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split('--> ')[-1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Mean square slope and wind speed"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1]  # .split('_chl')[0]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        s2.strip()
        s3 = s2.split(' ')
        while '' in s3:
            s3.remove('')
        meta_data.append(s3[3])
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Season"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Boundary layer aerosol type"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Boundary layer visibility"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Boundary layer humidity"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Tropospheric humidity"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Tropospheric visibility"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Stratospheric aerosol loading"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Stratospheric aerosol type"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Mesospheric aerosol loading"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Aerosol OT at reference wavelength"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[2]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** WMO aerosol type"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Profile of extinction coefficient (WMO)"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1].split(',')[0]
        if (s2 != "0.0"):
            s2 = "1.0"
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Coupling"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Number of streams"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Altitude grid file name"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split('/')[-1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Viewing angles"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    s1 = "*** Solar zenith angles"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    # file name
    s1 = '*** ' + files[ifile].split('.')[0]
    s1 = s1.split('*** ')[-1]
    head.append("file")
    meta_data.append(s1)

    "*** Hydrosol angular scattering"
    "*** Scattering function representation for hydrosols"

    # FIXME: make header once
    # this line redefines header and meta_data excluding previous

    # header for level1_ascii
    # initialize meta data table
    meta_data = []
    meta_data.append(str(icount))
    head = []
    head.append("id")
    # LAT
    # LON
    s1 = "*** Latitude & longitude"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(',')[-2].split('--> ')[-1]
        s1 = s1.split('*** ')[-1].split(' & ')
        head.append(s1[0].lower())
        meta_data.append(s2)
        s2 = read_pars[i + 1].split(',')[-1]
        head.append(s1[1].lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1].split(' & ')
        head.append(s1[0])
        meta_data.append(s1)
        head.append(s1[1])
        meta_data.append(s2)

    # TIME
    s1 = "*** Date"
    if s1 in read_pars:
        i = read_pars.index(s1)
        # s2 = read_pars[i + 2].split('.')[-1] + '-' + read_pars[i + 2].split('.')[-2] + '-' + \
        #      read_pars[i + 2].split('.')[-3].split(' ')[-1]
        #
        s2 = read_pars[i + 2].split('.')[-1] + '' + read_pars[i + 2].split('.')[-2] + '' + \
             read_pars[i + 2].split('.')[-3].split(' ')[-1] + 'T120000Z'
        s1 = s1.split('*** ')[-1]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    # FIXME: current ozone and pressure are from climatology, not fixed values as the total ozone or scaling pressure

    # OZONE_ECMWF
    s1 = "*** Ozone total column"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        s1 = s1.split('*** ')[-1].split()[0]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    # PRESS_ECMWF
    s1 = "*** Pressure profile scaling"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        s1 = s1.split('*** ')[-1].split()[0]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    # SUN_ZENITH
    s1 = "*** Solar zenith angles"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        if zenith_0_to_90:
            s2 = str(90. - float(s2))
        s1 = s1.split('*** ')[-1].split()
        s1 = s1[0] + '_' + s1[1]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    # VIEW_ZENITH
    s1 = "*** Viewing angles"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        s1 = s1.split('*** ')[-1].split()
        s1 = s1[0]  # + '_' + s1[1]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        s1 = ""
        meta_data.append(s1)

    # DELTA_AZIMUTH
    s1 = "*** Azimuth angles"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split(' ')[-1]
        s1 = s1.split('*** ')[-1].split()
        s1 = s1[0]  # + '_' + s1[1]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        s1 = ""
        meta_data.append(s1)

    # WINDM
    s1 = "*** Mean square slope and wind speed"
    if s1 in read_pars:
        i = read_pars.index(s1)
        s2 = read_pars[i + 1].split()[-1]
        s1 = s1.split('*** ')[-1].split()
        s1 = s1[-2] + '_' + s1[-1]
        head.append(s1.lower())
        meta_data.append(s2)
    else:
        s1 = s1.split('*** ')[-1]
        head.append(s1)
        meta_data.append(s1)

    # FIXME: what does detector means?
    # DETECTOR
    s1 = "detector"
    head.append(s1)
    # s2="999"
    # meta_data.append(s2)
    meta_data.append(str(icount))

    # ALTITUDE
    s1 = "altitude"
    head.append(s1)
    if mode == 'flux':
        s2 = "0"
        meta_data.append(s2)
    if mode == 'int':
        if bool_next:
            bool_next = False
            s2 = "0"
            meta_data.append(s2)
        else:
            # ALTITUDE
            s1 = "*** User-defined output altitude"
            if s1 in read_pars:
                i = read_pars.index(s1)
                s2 = read_pars[i + 1].split()[-1]
                meta_data.append(s2)
                bool_next = True
            else:
                s1 = ""
                meta_data.append(s1)

    # ---------------------------------------------------------
    # wavelength
    if ifile == 0:

        row_table = 0

        file_name = "intensity"
        file_data = data_directory + "DATA_OUT/" + file_name + ".dat"

        wavelength = []
        for line in open(file_data):
            li = line.strip()
            if not li.startswith("#"):
                wavelength.append(line.rstrip().split()[0])

        # FIXME:when to use out? when to use out_table?
        # create header line with wavelengths
        blank = head.copy()
        blank.append("wavelength")
        blank.extend(wavelength)
        out = [blank.copy()]
        wl_out = wavelength.copy()  # out[0][len(head.copy()+"wavelength"):len(out[0])]

        # create header line without wavelengths
        # assumes: 'intensity' = 'TOAR'; water_leaving = RHO_WN; flux = E_DOWN;
        blank = head.copy()
        blank.extend(['TOAR_{:03d}'.format(i + 1) for i, w in enumerate(wavelength)])
        blank.extend(['RHO_WN_{:03d}'.format(i + 1) for i, w in enumerate(wavelength)])
        blank.extend(['E_DOWN_{:03d}'.format(i + 1) for i, w in enumerate(wavelength)])
        out_table = [blank.copy()]

        COLS_E_DOWN = [i for i, s in enumerate(out_table[0]) if 'E_DOWN' in s]
        E_DOWN_BEG = COLS_E_DOWN[0]
        E_DOWN_END = COLS_E_DOWN[-1]
        COLS_RHO_WN = [i for i, s in enumerate(out_table[0]) if 'RHO_WN' in s]
        RHO_WN_BEG = COLS_RHO_WN[0]
        RHO_WN_END = COLS_RHO_WN[-1]
        COLS_TOAR = [i for i, s in enumerate(out_table[0]) if 'TOAR' in s]
        TOAR_BEG = COLS_TOAR[0]
        TOAR_END = COLS_TOAR[-1]

        NROWS = len(out_table[0])

        print('nrows:' + str(NROWS))
        print('TOAR_END:' + str(TOAR_END))
        print('RHO_WN_END:' + str(RHO_WN_END))
        print('E_DOWN_END:' + str(E_DOWN_END))

        row_table += 1
        out_table.append(list([0] * NROWS).copy())
        # print(out_table[0].__len__())
        # print(out_table[1].__len__())

        # print('len row out_table 0:' + str(len(out_table[0])))
        # print('len row out_table:'+str(len(out_table[row_table])))
        pass
    else:

        # print(files[ifile])
        if ifile % 2 == 0:
            # flux is the second file,
            # every two files finish a row
            row_table += 1
            out_table.append(list([0] * NROWS).copy())
            # print(out_table[0].__len__())
            # print(out_table[1].__len__())

        # print('len row out_table 0:'+str(len(out_table[0])))
        # print('len row out_table:'+str(len(out_table[row_table])))

    # ---------------------------------------------------------
    # flux

    if mode == 'flux':
        file_name = "total_flux_dn"
        # file_name="total_flux_up"
        file_data = data_directory + "DATA_OUT/" + file_name + ".dat"
        num = []
        altitude = []
        wavelength = []
        intensity = []
        # read output_map.inf
        file_map = "output_map.inf"
        file_map = data_directory + "DATA_OUT/" + file_map
        for line in open(file_map):
            li = line.strip()
            if not li.startswith("#"):
                num.append(line.rstrip().split()[0])
                # solzen.append(line.rstrip().split()[2])
                altitude.append(line.rstrip().split()[2])
        # print altitude
        col = altitude.index('0.0000')
        # col=altitude.index('99.0000')
        # col=104
        for line in open(file_data):
            li = line.strip()
            if not li.startswith("#"):
                wavelength.append(line.rstrip().split()[0])
                intensity.append(line.rstrip().split()[col])

        #
        if len(set(wl_out).difference(wavelength)) != 0:
            print("not same wavelengths")

        meta_data[0] = str(icount)
        icount = icount + 1
        # meta_data.append(str(icount))
        # head.append("id")
        b = meta_data + [file_name] + intensity
        out.append(b)

        # out_table[row_table][0:len(meta_data)]=meta_data.copy()
        out_table[row_table][E_DOWN_BEG:E_DOWN_END + 1] = intensity.copy()
        # print(str(out_table[0][E_DOWN_BEG-1:E_DOWN_BEG+1])+' '+str(out_table[0][E_DOWN_END-1:E_DOWN_END+2]))
        # print(str(out_table[1][E_DOWN_BEG-1:E_DOWN_BEG+1])+' '+str(out_table[1][E_DOWN_END-1:E_DOWN_END+2]))
        # print(out_table[0].__len__())
        # print(out_table[1].__len__())

    # ---------------------------------------------------------
    # intensity

    if mode == 'int':
        file_name = "intensity"
        file_data = data_directory + "DATA_OUT/" + file_name + ".dat"
        wavelength = []
        intensity = []
        for line in open(file_data):
            li = line.strip()
            if not li.startswith("#"):
                wavelength.append(line.rstrip().split()[0])
                intensity.append(line.rstrip().split()[1])
                # if line.rstrip().split()[0] in wl_out[-2:]:
                #     print(intensity.__len__())

        #
        if len(set(wl_out).difference(wavelength)) != 0:
            print("not same wavelengths")

        meta_data[0] = str(icount)
        icount = icount + 1
        b = meta_data + [file_name] + intensity
        out.append(b)

        out_table[row_table][0:len(meta_data)] = meta_data.copy()
        out_table[row_table][TOAR_BEG:TOAR_END + 1] = intensity.copy()

        # ---------------------------------------------------------
        # water leaving

        # if files[ifile].find("up") == -1:
        file_name = "water_leaving"
        file_data = data_directory + "DATA_OUT/" + file_name + ".dat"

        wavelength = []
        intensity = []
        for line in open(file_data):
            li = line.strip()
            if not li.startswith("#"):
                wavelength.append(line.rstrip().split()[0])
                intensity.append(line.rstrip().split()[1])

        #
        if len(set(wl_out).difference(wavelength)) != 0:
            print("not same wavelengths")

        meta_data[0] = str(icount)
        icount = icount + 1
        b = meta_data + [file_name] + intensity
        out.append(b)
        # out[1].extend(b)

        # out_table[row_table][0:len(meta_data)]=meta_data.copy()
        out_table[row_table][RHO_WN_BEG:RHO_WN_END + 1] = intensity.copy()

    shutil.rmtree(data_directory)

# import pandas as pd
#
# df = pd.DataFrame.from_records(out_table)
# df_transposed = df.T
# out_filename = 'ascii_df.csv'
# df.to_csv(out_filename, index=False, header=None)
#

# outname = 'file_t.csv'
# if not horizontal:
#     # zip(*out)
#     out = map(list, zip(*out))
#     outname = 'file.csv'
#     out_table = map(list, zip(*out_table))

import csv

# write it
# out_filename='test_' +outname
# with open(out_filename, 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     [writer.writerow(r) for r in out]

# out_filename = 'ascii_' + outname
out_filename = 'extraction.csv'
with open(out_filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    [writer.writerow(r) for r in out_table]

import os

print(os.getcwd())
print(out_filename)
