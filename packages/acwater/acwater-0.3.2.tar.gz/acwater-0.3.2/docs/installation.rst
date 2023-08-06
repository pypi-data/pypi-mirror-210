.. _installation:

Installation
=============

The installation process for **ACwater** involves cloning and installing the module and its
dependencies using a Python package manager. The objective is to install EnPT, Polymer,
and ACwater in the same environment.

=================
User
=================

Linux Debian/Ubuntu
=================

=========================================================================================================

**Installing ACwater/EnPT as standalone package (no GUI)**

1. Install **EnPT** using mamba forge as decribed in https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html

2. Using the previously created enpt conda environment (as described above), first install some dependencies:

.. code:: console

    mamba activate enpt
    mamba install -c conda-forge cdsapi cython ecmwf-api-client gdal netcdf4 pygrib pyhdf xarray

3. Then register at the HYGEOS support forum, download polymer from there, unpack it and run the following commands from the unpacked root directory of polymer:

.. code:: console

    make
    make auxdata_common
    make ancillary
    mkdir -p ANCILLARY/ERA5/
    pip install -e .

Ancillary data
=================

The **ERA5 reanalysis data** is the default option for ancillary data in ACwater Polymer.
Please register at the `CDS registration page`_ and install the `CDS API key`_
by creating a key file with your registration data, as follows:

.. _CDS registration page: https://cds.climate.copernicus.eu
.. _CDS API key: https://cds.climate.copernicus.eu/api-how-to

.. code:: console

    CDS_API_KEY="copy your key here"
    touch $HOME/.cdsapirc
    echo "url: https://cds.climate.copernicus.eu/api/v2" >> $HOME/.cdsapirc
    echo "key: $CDS_API_KEY" >> $HOME/.cdsapirc

.. _`Polymer server`: http://download.hygeos.com/POLYMER/auxdata

4. Install **ACwater**

.. code:: console

    pip install acwater>=0.3.0
    
============================================================================================================

**Installing ACwater/EnPT along with the EnMAP-Box (a QGIS plugin) which provides a GUI for EnPT**

**Install** QGIS as in `QGIS instructions`_

.. _QGIS instructions: https://www.qgis.org/en/site/forusers/alldownloads.html#debian-ubuntu

.. code:: console

    sudo apt install gnupg software-properties-common
    wget -qO - https://qgis.org/downloads/qgis-2020.gpg.key | sudo gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import
    sudo chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg
    sudo add-apt-repository "deb https://qgis.org/debian `lsb_release -c -s` main"
    sudo apt update
    sudo apt install qgis qgis-plugin-grass

**Install** python package manager pip.

.. code:: console

    sudo apt update
    sudo apt install python3-pip

**Install** EnMap-box requirements and the `EnMap-box plugin`_

.. code:: console

    pip3 install -r https://bitbucket.org/hu-geomatics/enmap-box/raw/develop/requirements.txt

.. _EnMap-box plugin: https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html#install-or-update-the-enmap-box


**Install** EnMap-Box using the Plugin manager


Install Conda
===========================================

Current suggested installation is using a virtual environment, here with the environment
and package manager `miniconda`_.

.. code:: console

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

.. _miniconda: https://docs.conda.io/en/latest/miniconda.html

where the first line download the installing script and the second line executes the script.

When needed start conda by:

.. code:: console

    source miniconda3/bin/activate

The next step is to create the environment, activate it and install EnPT.

.. code:: console

    conda create -c conda-forge --name enpt python=3
    conda activate enpt
    conda install -c conda-forge enpt

Polymer (by HYGEOS)
===========================================

**Obtain** polymer by first subscribing to the `Polymer forum`_.
Then, download and decompress the polymer package.

.. code:: console

    tar -xvf polymer-v4.13.tar.gz
    cd polymer-v4.13

.. _Polymer forum: https://forum.hygeos.com

**Install** the python dependencies executing the shell script that comes with the
polymer software *install-anaconda-deps.sh* or,
**best** for ACwater Polymer, install the essential packages as bellow:

.. code:: console

    pip3 install cython xarray cdsapi

**Compile** polymer using the command 'make', which creates a 'build' folder for the
compiled libraries. Polymer uses 'cython' and thus requires a C/C++ compiler
previously installed.

.. code:: console

    sed -i '9s/python /python3 /' makefile
    sudo apt update
    sudo apt install build-essential
    make

where the first line edits the makefile to make sure python 3 is used.
The second and third lines install the C/C++ compiler and library and
the last line compiles polymer.

**Install** Polymer using the package manager:

.. code:: console

    pip3 install -e .

Ancillary data
===========================================

**Download** parameterization data via the command bellow. Basically, the
necessary data (190 Mb) are downloaded from the `Polymer server`_ and stored in
the local polymer directory. Be sure to be in the polymer directory, e.g. *polymer*.

.. code:: console

    make auxdata_common

Polymer downloads **ancillary data** in runtime.
Use following lines to create a directory for ancillary data (reanalysis and climatology):

.. code:: console

    mkdir -p ANCILLARY/ERA5/ ANCILLARY/METEO/

The **ERA5 reanalysis data** is the default option for ancillary data in ACwater Polymer.
Please register at the `CDS registration page`_ and install the `CDS API key`_
by creating a key file with your registration data, as follows:

.. _CDS registration page: https://cds.climate.copernicus.eu
.. _CDS API key: https://cds.climate.copernicus.eu/api-how-to

.. code:: console

    CDS_API_KEY="copy your key here"
    touch $HOME/.cdsapirc
    echo "url: https://cds.climate.copernicus.eu/api/v2" >> $HOME/.cdsapirc
    echo "key: $CDS_API_KEY" >> $HOME/.cdsapirc

.. _`Polymer server`: http://download.hygeos.com/POLYMER/auxdata


ACwater Polymer
===========================================

**Clone** and **install** the source code of the wrapper module ACwater for running Polymer with the EnPT.

.. code:: console

    git clone https://gitlab.awi.de/phytooptics/acwater.git
    cd acwater
    pip3 install .


=================
Notes
=================

On package dependencies you should get a running installation when following the dependencies on the tree top:

.. list-table:: Tree top dependencies
   :widths: 25 25 25
   :header-rows: 1

   * - package
     - version
     - install
   * - cdsapi
     - 0.5.1
     - pip
   * - Cython
     - 0.29.22
     - pip
   * - enpt
     - 0.17.2
     - conda
   * - h5py
     - 3.1.0
     - conda
   * - xarray
     - 0.17.0
     - pip

Full Installation into a conda environment
===========================================

Alternatively you can use the `EnPT environment file`_ for a full installation, including EnMAP-box, EnPT, ACwater Polymer and the QGIS as frontend, as explained in `EnPT instructions`_ . The following command line should also do the update to the installation above.

.. code:: console

  conda env update -n enpt -f https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT/raw/master/tests/gitlab_CI_docker/context/environment_enpt_full.yml


.. _EnPT environment file: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT/raw/master/tests/gitlab_CI_docker/context/environment_enpt_full.yml

.. _EnPT instructions: https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html#installing-enpt-along-with-qgis-and-the-enmap-box-backend-gui
