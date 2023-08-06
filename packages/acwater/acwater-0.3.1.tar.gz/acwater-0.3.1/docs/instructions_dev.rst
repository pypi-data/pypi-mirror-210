

## get the code

# EnPT:
git clone https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT.git
- go to the branch under development
- install the code under development  <-
activate environment
cd EnPT
pip install .

# Polymer: https://forum.hygeos.com
if needed, download the zip and install polymer

# acwater:
git clone https://gitlab.awi.de/phytooptics/acwater.git
- for testing go to next step
- for further development go to the branch under development

# test
activate python environment (enpt)
call enpt
python EnPT/cli.py
python EnPT/cli.py  file.json
python EnPT/cli.py -param1 -param1 -param1 -param1 -param1 -param1 -param12

# sample data
../tests/data/ENMAP01-____L1B-DT000400126_20170218T110115Z_002_V000204_20200206T182719Z__rows700-730.zip

# visualization
using QGIS
