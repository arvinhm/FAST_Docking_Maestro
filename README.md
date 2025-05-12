First, create sequences.txt file with all peptide sequences you need

python split.py # change the number of parts to 500 or more if your pc can handle that (96 cores)

python run.py # change parts as you need (500)

python peptide_prep.py

python confgen.py to generate conformers

merge all conformaers in one giant file using python merge.py

split merged files to whatever you want based on your CPU I prefer using 500

use 500 files as direct subjobs for vws function in Maestro
