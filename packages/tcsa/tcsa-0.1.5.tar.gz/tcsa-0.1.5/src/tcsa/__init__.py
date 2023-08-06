# Copyright (C) 2022 Imperial College London
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/.

from __future__ import annotations

import logging

__title__ = "tcsa"
__description__ = "temporalis segmentation pipeline to assess CSA of temporalis"
__url__ = "https://gitlab.com/computational.oncology/temporalis-segmentation-pipeline"
__author__ = """Computational Oncology"""
# __email__ = ""
__version__ = "0.1.5"
__license__ = "GPL 3"
__copyright__ = "Copyright 2022 Imperial College London"


logging.getLogger(__name__).addHandler(logging.NullHandler())

import requests
from packaging.version import parse, Version
import json

def get_version(url_pattern: str = 'https://pypi.org/pypi/tcsa/json') -> Version:
    """Returns version of tCSA on test.pypi.org using json.

    Args:
        url_pattern (str): url to the json of the package

    return:
        Version: latest version of the package
    """
    req = requests.get(url_pattern)
    version = parse('0')

    if req.encoding:
        if req.status_code == requests.codes.ok:
            j = json.loads(req.text.encode(req.encoding))
            releases = j.get('releases', [])

            for release in releases:
                ver = parse(release)
                if not ver.is_prerelease:
                    version = max(version, ver)

    return version

def welcome() -> None:
    """
    Print a welcome screen and check if the package need an update.
    """
    print(rf"""

                         Cross                             Area
______________________/\\\\\\\\\_____/\\\\\\\\\\\_______/\\\\\\\\\____
 ___________________/\\\////////____/\\\/////////\\\___/\\\\\\\\\\\\\__
  _____/\\\________/\\\/____________\//\\\______\///___/\\\/////////\\\_
   __/\\\\\\\\\\\__/\\\_______________\////\\\_________\/\\\_______\/\\\_
    _\////\\\////__\/\\\__________________\////\\\______\/\\\\\\\\\\\\\\\_
     ____\/\\\______\//\\\____________________\////\\\___\/\\\/////////\\\_
      ____\/\\\_/\\___\///\\\___________/\\\______\//\\\__\/\\\_______\/\\\_
       ____\//\\\\\______\////\\\\\\\\\_\///\\\\\\\\\\\/___\/\\\_______\/\\\_
        _____\/////__________\/////////____\///////////_____\///________\///__
           temporalis                        Sectional


                                    v{__version__}
                                License: GPL v3

                     *************************************
             Oncology Lab | Imperial College London | NHS Trust
                     *************************************

    """)
    latest = get_version('https://test.pypi.org/pypi/tcsa/json')
    if parse(__version__) < latest:
        print(rf"""
A new version of tCSA is available (v{str(latest)}).
You can update it by running:
$ pip install --upgrade tcsa
        """)
    else:
        print("You are using the latest version of tCSA.")


from pathlib import Path

##########################################################
##  Different paths necessary for the program to work:  ##
##  main:                                               ##
##  ├─── images: (your input folder)                    ##
##  │	 ├─── patient_name_01.nifti                     ##
##  │	 └─── ...                                       ##
##  ├─── slices: (folder for the slices)                ##
##  │    ├─── patient_name_01:                          ##
##  │    │    ├─── original:                            ##
##  │    │    │    ├─── nbslice.nifti                   ##
##  │    │    │    └─── ...                             ##
##  │    │    ├─── normalized:                          ##
##  │    │    │    ├─── nbslice.nifti                   ##
##  │    │    │    └─── ...                             ##
##  │    │    └─── preprocessed:                        ##
##  │    │    	   ├─── nbslice.nifti                   ##
##  │    │         └─── ...                             ##
##  │    └─── patient_name_...:                         ##
##  ├─── eyeballs:                                      ##
##  │    ├─── patient_name_01:                          ##
##  │    │    ├─── original:                            ##
##  │    │    │    ├─── nbslice.png                     ##
##  │    │    │    └─── ...                             ##
##  │    │    └─── segmentation:                        ##
##  │    │         ├─── nbslice.png                     ##
##  │    │         └─── ...                             ##
##  │    └─── patient_name_...:                         ##
##  ├─── temporalis:                                    ##
##  │    ├─── patient_name_01:                          ##
##  │    │    ├─── original:                            ##
##  │    │    │    ├─── nbslice.png                     ##
##  │    │    │    └─── ...                             ##
##  │    │    └─── segmentation:                        ##
##  │    │         ├─── nbslice.png                     ##
##  │    │         └─── ...                             ##
##  │    └─── patient_name_...:                         ##
##  └─── trained_weights:                               ##
##  	 ├─── unet_eyeball.hdf5                         ##
##  	 └─── unet_temporalis.hdf5                      ##
##########################################################

PATHS = {'main' : Path.cwd()}
# PATHS['images'] = PATHS['main'] / 'images'
PATHS['slices'] = PATHS['main'] / 'slices'
PATHS['eyeballs'] = PATHS['main'] / 'eyeballs'
PATHS['temporalis'] = PATHS['main'] / 'temporalis'
PATHS['weights'] = PATHS['main'] / 'trained_weights'
