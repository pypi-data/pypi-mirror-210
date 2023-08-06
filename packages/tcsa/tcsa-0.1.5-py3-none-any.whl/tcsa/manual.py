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


# /!\ only for specific use, not intended for the default usage of the package

# make segmenting new images easier
# 0) run prequisites if necessary
# 1) run manual_pipeline()
# 2) run prepare_segmentation(dataset="name_of_dataset")
# 3) make segmentation with itksnap and save them with same name but append _seg
# 4) run convert_segmentation()

from pathlib import Path

import shutil
import numpy as np
import pandas as pd
import imageio
import nibabel as nib

from tcsa import PATHS
from .prequisite import run_prequisite
from .pipeline import manual_pipeline, select_slice_patients


def prepare_segmentation(input_path: Path = PATHS['temporalis'],
                         output_path: Path = PATHS['main'] / 'segmentation',
                         *, dataset: str = 'Unknown') -> None:
    """
    Take input from the middle of the pipeline (just after the slice selection),
    proceed to copy the correct slice in png and nifti format in a new directory
    called 'segmentation' (output_path) and renaming it as an integer.
    Keep a record of the original patient name (patient_names),
    and the slice number (slices_nb), and the new integer name (file_nb)
    and proceed to save it in a csv file with the name of the dataset

    Args:
        input_path (Path): Path to were the right slice is stored
        output_path (Path): Path to were the images used for manual segmentation
                            will be stored
    Kwargs:
        dataset (str): Name of the dataset, that will be used for the csv filename
    """
    patient_names = []
    slices_nb = []
    file_nb = []
    output_path_png = output_path / 'png'
    output_path_nii = output_path / 'nifti'
    output_path_png.mkdir(parents=True, exist_ok=True)
    output_path_nii.mkdir(parents=True, exist_ok=True)
    for i, patient in enumerate(input_path.iterdir()):
        patient_names.append(patient.name)
        png_path = list((patient / 'original').iterdir())[0]
        slices_nb.append(int(png_path.stem))
        file_nb.append(i)
        nifti_path = PATHS['slices'] / patient.name / 'preprocessed' / f'{png_path.stem}.nii.gz'
        shutil.copy(str(png_path), str(output_path_png / f'{i}.png'))
        shutil.copy(str(nifti_path), str(output_path_nii / f'{i}.nii.gz'))
    segmentation = {
        'Patient': patient_names,
        'Slice_nb': slices_nb,
        'Filename': file_nb
    }
    segmentation_df = pd.DataFrame(segmentation)
    segmentation_df.to_csv(output_path / f'{dataset}.csv')

def convert_segmentation(input_path: Path = PATHS['main'] / 'segmentation') -> None:
    """
    Convert manualy segmented nifti slice into a png file

    Args:
        input_path (Path): root directory where the segmentation are stored
    """
    for segmentation in (input_path / 'nifti').glob('*_seg.nii.gz'):
        img = nib.load(segmentation).get_fdata()
        img = np.flipud(np.rot90(img[:,:]))
        filename = segmentation.name[: -len(''.join(segmentation.suffixes))]
        output_path = input_path / 'png' / f'{filename}.png'
        imageio.imsave(str(output_path), img)

# run_prequisite()
# manual_pipeline()
# prepare_segmentation(dataset='UKBB')
# convert_segmentation()
