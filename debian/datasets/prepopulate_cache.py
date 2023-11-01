#!/usr/bin/python3

"""Place data from R into the statsmodels cache, as Debian does not allow Internet access during builds"""

import os
import subprocess
import glob
import pickle
import zlib

buildroot_directory = os.getcwd()
Rtmp_directory = buildroot_directory + '/build/Rtmp'
target_directory = buildroot_directory + '/build/datacache'
os.makedirs(target_directory)
os.makedirs(Rtmp_directory)

# R packages (datasets) used:
# car (Duncan, Moore) # now split off as carData
# COUNT (medpar) # not in Debian, use removed by use_available_data.patch
# geepack (dietox)
# HistData (Guerry) # not in Debian, but Guerry is and has the same dataset
# MASS (epil, Sitka)
# robustbase (starsCYG)
# vcd (Arthritis, VisualAcuity)

# duration.rst would use survival (flchain) but that example isn't run during build

# R-using examples use lme4, geepack, robustbase

subprocess.run(['R', 'CMD', 'BATCH', buildroot_directory + '/debian/datasets/Rdatasets.R'], cwd=Rtmp_directory, check=True)
subprocess.run([buildroot_directory + '/debian/datasets/rst.sh'], cwd=Rtmp_directory + '/doc', check=True)

for fname_in in glob.glob(Rtmp_directory + '/**/*', recursive=True):
    if os.path.isfile(fname_in):
        with open(fname_in,'rb') as fd:
            data = fd.read()
        fname_out = target_directory + '/raw.githubusercontent.com,vincentarelbundock,Rdatasets,master,' + os.path.relpath('-v2.'.join(fname_in.rsplit('.',1)), start=Rtmp_directory).replace('/',',') + '.zip'
        data2 = zlib.compress(data)
        with open(fname_out, 'wb') as fd:
            fd.write(data2)
