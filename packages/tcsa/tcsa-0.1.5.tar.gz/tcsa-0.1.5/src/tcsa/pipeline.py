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


from pathlib import Path

from tcsa import PATHS
from .prequisite import run_prequisite
from .data_preparation import (slicing, preprocessing, converting_to_png)

from .model import unet
from .data import (testGenerator, saveResult)
from .thresholding import (select_slice, temporalis_csa)
import cv2

import logging
FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
log = logging.getLogger(__name__)

def segment_eyeballs() -> None:
    """
    Segment the eyeballs from the png slices present in eyeballs/patient/original,
    and save the result in eyeballs/patient/segmentation as png.
    """
    model = unet(PATHS['weights'] / 'unet_eyeball.hdf5')
    log.info("\nSegmenting eyeballs ...")
    for patient in (PATHS['eyeballs']).iterdir():
        slices_path = patient / 'original'
        testGene = testGenerator(slices_path)
        number_of_test_images = len(list(slices_path.iterdir()))
        names = [file.name for file in slices_path.iterdir()]
        log.info(f'Segmenting eyeball for {patient.name}...')
        results = model.predict_generator(testGene,number_of_test_images,verbose=1)
        saveResult(patient / 'segmentation', results, names)

def select_slice_patients(*, delete_eyeballs: bool = False) -> None:
    """
    Iterate throught all the patients, and run select_slice for each patient.

    Kwargs:
        delete_eyeballs (bool): pass to select_slice,
                                delete all slices (eyeball png and nifti slices)
    """
    for patient in (PATHS['eyeballs']).iterdir():
        segmentation_path = patient / 'segmentation'
        select_slice(segmentation_path,
            PATHS['temporalis'] / patient.name, delete_eyeballs=delete_eyeballs)

def segment_temporalis(*, both_sides: bool = False) -> None:
    """
    Segment the temporalis from the png slice present in temporalis/patient/original
    and save the result in temporalis/patient/segmentation as png

    Kwargs:
        both_sides (bool): if set to true will segment both sides
                           (the other sides will be flipped)
    """
    model = unet(PATHS['weights'] / 'unet_temporalis.hdf5')
    log.info("\nSegmenting temporalis ...")
    for patient in PATHS['temporalis'].iterdir():
        slice_path = patient / 'original'
        if both_sides: right_side(slice_path)
        testGene = testGenerator(slice_path)
        number_of_test_images = 1 if not both_sides else 2
        names = [file.name for file in slice_path.iterdir()]
        log.info(f'Segmenting temporalis for {patient.name}...')
        results = model.predict_generator(testGene,number_of_test_images,verbose=1)
        saveResult(patient / 'segmentation', results, names)

def right_side(input_path: Path) -> None:
    """
    flip the image and create a copy to be able to segment both sides.
    the original one will be renamned l_nbslice.png and the flipped r_nbslice.png

    Args:
        input_path (Path): path provided by segment_temporalis, it's the path
                           to temporalis/patient/original
    """
    for slice in input_path.iterdir():
        if slice.name.startswith(('l_', 'r_')): return
        img = cv2.imread(str(slice))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_flipped = cv2.flip(gray, 1)
        cv2.imwrite(str(slice.parent / f'r_{slice.name}'), gray_flipped)
        slice.rename(slice.parent / f'l_{slice.name}')


def full_pipeline(input_path: Path, output_path: Path,
                  delete: bool = False, both_sides: bool = True) -> None:
    """
    Run the full pipeline.

    1) Prequisite: creates directories, and check weights for model
    2) Slicing: get the slices from the mri
    3) Preprocess: preprocess the slices
    4) Convert to PNG: needed for the neural network
    5) Segment eyeballs
    6) Select slice: select the slice at the eye level
    7) Segment temporalis: can segment both sides if needed
    8) Output: create a csv file with the patient name, the slice, and the CSA

    Args:
        input_path (Path): Path to the directory where the images are stored
        output_path (Path): Path to where the csv file will be saved,
                            (can be the directory with or without the filename)
        delete (bool): Delete all intermediate directories and files,
                       only keep the csv, images in input_path and weights
        both_sides (bool): Segment both sides, only left side by default
    """
    run_prequisite()

    nb_patients = len(list(input_path.iterdir()))
    log.info(f"\nYou have {nb_patients} image{'s' if nb_patients > 1 else ''}")

    slicing(input_path)
    preprocessing(delete_og_slices=False)
    converting_to_png()

    segment_eyeballs()
    select_slice_patients(delete_eyeballs=False)
    segment_temporalis(both_sides=both_sides)

    temporalis_csa(output_path=output_path, both_sides=both_sides, delete_all=delete)

def manual_pipeline() -> None:
    """
    Run only the necessary part of the pipeline to make manual segmentation
    /!\ Only for specific use
    """
    slicing()
    preprocessing(delete_og_slices=False)
    converting_to_png()

    segment_eyeballs()
    select_slice_patients(delete_eyeballs=False)
