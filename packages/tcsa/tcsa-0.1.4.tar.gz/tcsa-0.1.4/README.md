# temporalis Cross Sectional Area (tCSA)

The temporalis Cross Sectional Area (tCSA) is a Python package for the segmentation of the temporalis muscle in T1-weighted contrast enhanced MRI and returns the cross-sectional area of the muscle.

Preferred input type is NIfTI files (.nii or .nii.gz), however, it is possible to work with DICOM files (.dcm) with the included converter in the package.

For now tCSA is only available on POSIX systems (Linux, and macOS) and require python == 3.7.


## Table of Contents


- [Installation](#installation)
- [Quick start](#quick-start)
    - [DICOM](#dicom)
- [Credits](#credits)
    - [Contributors](#contributors)
- [References](#references)

## Installation

To install the package, create a new virtual environment and run the following command:

`python -m pip install tcsa`

## Quick start

Once installed, tCSA can be run in the command line interface with `tcsa`.


`tcsa .path/to/images -o path/to/output/folder/temporalis.csv --both-sides --delete`


- `../images`: is the path to where the MRI are stored, it can be a directory or a single image
- `-o output/temporalis.csv`: optional, this is the path to where the csv file will be saved and can be ommited.The output file will be created automatically
- `--both-sides`: optional, if present will segment both sides of the temporalis muscle
- `--delete`: optional, if present will delete all intermediate files and only keep the original MRI, the downloaded weights, and the csv file
- all paths can be absolute or relative


### DICOM

To work with DICOM(.dcm) files you need to either convert them manually or use the argument `--dicom`.

Dicom files must be put in a folder. 

`tcsa path/to/folder/with/dicom/images --dicom`

Please be aware that if the DICOM file has multiple components, only the first one will be segmented and the others will be discarded.


## Credits

### Contributors

- M. Radvile, Data analyst, Computational Oncology lab, Imperial College London, United Kingdom
- A. Adrien, Visiting student, Computational Oncology lab, Imperial College London, United Kingdom
- W. James, Honorary Clinical Research Fellow, Computational Oncology lab, Imperial College London, United Kingdom
