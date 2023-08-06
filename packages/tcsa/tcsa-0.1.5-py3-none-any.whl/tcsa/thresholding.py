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

import numpy as np
from pathlib import Path
import cv2
import shutil
import pandas as pd

from tcsa import PATHS

import logging
FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
log = logging.getLogger(__name__)


def select_slice(input_path: Path, output_path: Path,
                        *, nifti: bool = False,
                        delete_eyeballs: bool = False) -> None:
    """
    Select the slice at the right eyeball level

    First convert the segmentation.png present in input_path / original
    in a binary image and count the number of white pixel
    (corresponding to the area of the segmented eyeballs).
    Then calculate the 97th percentile of all the area for one patient and take
    the first slice greater than the 97th percentile and output the original png
    in output_path / original
    Possible to also get the nifti slice.

    Args:
        input_path (Path): Path to the png slice of the patient
        output_path (Path): Path for the png slice of the patient at the right level
    Kwargs:
        nifti (bool): if set to true also output the nifti slice
        delete (bool): delete all slices (eyeball png and nifti slices)
    """
    areas_list = []
    ordered_slices = sorted(input_path.iterdir(), key=lambda x: int(x.stem))
    for segmentation in ordered_slices:
        img = cv2.imread(str(segmentation))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        area = cv2.countNonZero(thresh)
        areas_list.append(area)
    area_97 = np.percentile(areas_list, 97)
    for i, area in enumerate(areas_list):
        if area >= area_97:
            eyeball_pictures = input_path.parent / 'original'
            eyeball = sorted(eyeball_pictures.iterdir(), key=lambda x: int(x.stem))[i]
            output_path /= 'original'
            output_path.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(eyeball), str(output_path / eyeball.name))
            if nifti:
                patient_name = input_path.parent.name
                nifti_slice = PATHS['slices'] / patient_name / 'preprocessed' / f'{eyeball.stem}.nii.gz'
                shutil.copy(str(nifti_slice), str(output_path / nifti_slice.name))
            break
    if delete_eyeballs:
        shutil.rmtree(str(PATHS['slices']), ignore_errors=True)
        shutil.rmtree(str(PATHS['eyeballs']), ignore_errors=True)

def temporalis_csa(input_path: Path = PATHS['temporalis'],
                    output_path: Path = PATHS['main'] / 'temporalis_csa.csv',
                    *, both_sides: bool, delete_all: bool = False) -> None:
    """
    Calculate the temporalis csa and output it in a csv

    Binarize the temporalis segmentation contained in input_path/patient/segmenttion,
    and count the white pixel (corresponding to the temporalis CSA).
    Input all the information in a csv of composed of the following coloumns:
        - patients_name: extracted from the directory name
        - slices_nb: extracted from the filename minus the extension
        - *_areas_temporalis: extracted from this function
    Output it in a csv file with the desired name

    Args:
        input_path (Path): Root path where the segmentation of all patients are stored
        output_path (Path): Path to where the csv will be saved
        csv_name (str): String of the desired output filename
    Kwargs:
        both_sides (bool): If you want to input both temporalis CSA
                            (need to segment both sides beforehand)
        delete (bool): Delete all the files except the csv
    """
    patients_name, slices_nb, l_areas_temporalis, r_areas_temporalis = ([], [], [], [])
    for patient in input_path.iterdir():
        patients_name.append(patient.name)
        segmentation_path = patient / 'segmentation'
        segmentations = list(segmentation_path.iterdir())
        nb_segmentations = len(segmentations)
        # both_sides = True if nb_segmentations == 2 else False
        if nb_segmentations == 3:
            # this case happen if you run once with both sides and after with
            # just one side or the other way around
            # the end result will be nb.png, l_nb.png, r_nb.png present in the fodler
            # we will use the fact that a number will always be before a letter
            # if we refer to the ASCII table
            if both_sides:
                segmentations[0].unlink()
            else:
                segmentations[1].unlink()
                segmentations[2].unlink()
        if both_sides:
            slices_nb.append(int(segmentations[1].stem[len('l_'):]))
        else:
            slices_nb.append(int(segmentations[0].stem))
        for segmentation in segmentation_path.iterdir():
            img = cv2.imread(str(segmentation))
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            if both_sides:
                if segmentation.stem.startswith('l_'):
                    l_areas_temporalis.append(cv2.countNonZero(thresh))
                elif segmentation.stem.startswith('r_'):
                    r_areas_temporalis.append(cv2.countNonZero(thresh))
            else:
                l_areas_temporalis.append(cv2.countNonZero(thresh))
                r_areas_temporalis.append('')

    if delete_all:
        shutil.rmtree(str(PATHS['slices']), ignore_errors=True)
        shutil.rmtree(str(PATHS['eyeballs']), ignore_errors=True)
        shutil.rmtree(str(PATHS['temporalis']), ignore_errors=True)
    temporalis = {
        'Patient': patients_name,
        'Slice_nb': slices_nb,
        'Temporalis_CSA_left (in px)': l_areas_temporalis,
        'Temporalis_CSA_right (in px)': r_areas_temporalis
    }
    # if both_sides:
    #     temporalis['Temporalis_CSA_right (in px)'] = r_areas_temporalis
    temporalis_df = pd.DataFrame(temporalis)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporalis_df.to_csv(output_path)
    log.info(f"\nCreated {output_path.name}")
