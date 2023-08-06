# ACwater


Atmospheric correction of EnMAP hyperspectral data for water surfaces.

**ACwater** implements a class to load an EnMAP object and
execute Polymer atmospheric correction for water surfaces. ACwater
requires *EnPT* for the EnMAP data processing and *Polymer* for the
atmospheric correction algorithm.

**Operating system** for installation is **Linux**, tested on Debian
GNU/Linux 9.9 (stretch) - Linux 4.9.0-9-amd64 x86_64.

**Requirements** are
[EnPT](https://gitext.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT) and
[Polymer](https://www.hygeos.com/polymer).

**Installation** of EnPT follows
[EnPT instructions](https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html).

## Installation

The [Instructions](https://gitlab.awi.de/phytooptics/acwater/-/blob/master/docs/installation.rst)
involve cloning the package and installing its dependencies using a Python package manager. Note that both ACwater and Polymer must be installed with EnPT in the same environment.

## How to use with command line

First, download an EnMAP Level 1B image from https://eoweb.dlr.de/egp/.

Please refer to the list of arguments that can be used in EnPT, which is available at https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/usage.html.

Here is an example of what the command might look like:

enpt --CPUs 4 --auto_download_ecmwf True --average_elevation 0 --blocksize 100 --deadpix_P_algorithm spectral --deadpix_P_interp_spatial linear --deadpix_P_interp_spectral linear --disable_progress_bars True --drop_bad_bands True --enable_ac True --mode_ac water  --polymer_additional_results True --ortho_resampAlg gauss --output_dir /your output dir/ --output_format GTiff --path_l1b_enmap_image /path to your EnMAP L1B zip file/ENMAP01-____L1B-DT0000002037_20220801T105350Z_026_V010111_20230223T123717Z.ZIP --polymer_root /Polymer path/polymer-v4.14 --run_deadpix_P True --scale_factor_boa_ref 10000 --scale_factor_toa_ref 10000 --target_epsg 4326 --threads -3 --vswir_overlap_algorithm vnir_only


## Features

-   Level 1 class for connecting EnPT and Polymer.

## License

This software is under [GNU General Public License
v3](https://gitlab.awi.de/phytooptics/acwater/-/blob/develop/LICENSE)

## Credits

Credits are with Phytooptics Group at AWI. This software was developed within the context of the EnMAP project supported by the DLR Space Administration with
funds of the German Federal Ministry of Economic Affairs and Energy (on the basis of a decision by the German
Bundestag: 50 EE 1923 and 50 EE 1915) and contributions from GFZ and Hygeos.

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr](https://github.com/audreyr/cookiecutter-pypackage) project
template.
