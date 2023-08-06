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
import os
from shutil import rmtree
from tqdm import tqdm
import sys

import numpy as np
import nibabel as nib
import ants
import imageio

from tcsa import PATHS

# suppress warning about losy conversion for imageio
import logging
logger = logging.getLogger('imageio')
logger.setLevel(logging.ERROR)

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
log = logging.getLogger(__name__)

def is_nifti(path_to_image: Path) -> bool:
    """
    Check if the file is a nifti image.

    Take into account compressed nifti files

    Args:
        path_to_image (Path): Path to the file.
    Return:
        bool: return true if the file is a nifti file
    """
    extensions = ''.join(path_to_image.suffixes)
    return True if extensions in ('.nii', '.nii.gz') else False

def is_dicom(path_to_image: Path) -> bool:
    """
    Check if the file is a dicom image.

    Args:
        path_to_image (Path): Path to the file.
    Return:
        bool: return true if the file is a dicom file
    """
    extensions = ''.join(path_to_image.suffixes)
    return True if extensions in ('.dcm', '.DCM') else False

def valid_format(path_to_image: Path) -> bool:
    """
    Handle the different file format.

    Check if it's a nifti file, a dicom file,
    and provide information on what to do.

    Args:
        path_to_image (Path): Path to the file.
    Return:
        bool: return true if the file is a nifti file
    """
    if is_nifti(path_to_image):
        return True
    else:
        if is_dicom(path_to_image):
            log.warning(f'{path_to_image.name}: Please convert with --dicom in command line.')
        else:
            log.warning(f'{path_to_image.name}: Unknown file format.')
        return False

def slicing(path_to_images: Path,
            path_to_slices_folder: Path = PATHS['slices'],
            *, window: list = [0.25, 0.5]) -> None:
    """
    Slice the nifti file in path_to_images.

    Slice the images present in 'path_to_images',
    and output them in 'path_to_slices_folder' and are stored the following way:
    path_to_slices_folder:
    └─── original:
        ├─── patient_name:
        │   ├─── nbslice.extensions (nii or nii.gz)
        │   └─── ....
        └─── patient_name:
            ├─── nbslice.extensions
            └─── ....

    Args:
        path_to_images (Path): Path to the images (only Nifti images will work)
        path_to_slices_folder (Path): Ouput path of the slices
        window (list): only take into account a certain percentage of slices
                        (help reduce false eyeball segmentation)
    """
    if path_to_images.name == 'temp_images':
        log.info("\nSlicing image into 2D slices...")
    else:
        log.info("\nSlicing images into 2D slices...")
    for patient in path_to_images.iterdir():
        if not valid_format(patient):
            continue
        extensions = ''.join(patient.suffixes)
        patient_name = patient.name[: -len(extensions)]

        patient_directory = path_to_slices_folder / patient_name / 'original'
        patient_directory.mkdir(parents=True, exist_ok=True)

        img = nib.load(patient)
        nb_slices = img.shape[2]
        img = img.get_fdata()
        if len(img.shape) == 4:
            log.warning(f"{patient.name} contain multiple components (4D, or dicom). Only the first one will be kept")
            img = img[:,:,:,0]
        # img_cropped = img[..., nb_slices // 4:nb_slices // 2]
        for i in tqdm(
                range(round(nb_slices*window[0]), round(nb_slices*window[1])),
                desc=f"Slicing {patient.name}"
        ):
            imageio.imsave(str(patient_directory / f'{i}{extensions}'),
                                                           np.rot90(img[:,:,i]))
            # nib.save(img.slicer[..., i:i+1],
            #         path_to_slices_folder / f'{filename}_{i}{extensions}')



def preprocessing(path_to_slices_folder: Path = PATHS['slices'],
                  *, verbose: bool = False,
                  delete_og_slices: bool = False) -> None:
    """
    Preprocess nifti slices.

    Perform z-score normalization, bias field correction, resample, set spacing
    on slices and proceed to save them.

    Args:
        path_to_slices_folder (Path): Path to the root directory of the slices,
                                     contening ALL the slices (refer to README)
    Kwargs:
        verbose (bool): Make z-score verbose or not
        delete (bool): Delete unused slices (original and normalized)
    """
    nb_patients = len(list(path_to_slices_folder.iterdir()))
    if nb_patients == 0:
        log.warning("No slice found.")
        sys.exit()
    log.info("\nNormalizing slices ...")
    for patient in path_to_slices_folder.iterdir():
        slices_path = patient / 'original'
        normalized_path = patient / 'normalized'
        normalized_path.mkdir(parents=True, exist_ok=True)
        for slice in tqdm(
            slices_path.iterdir(),
            desc=f"Normalizing slices for {patient.name}",
            total=len(list(slices_path.iterdir()))
        ):
            normalization_query = (f"zscore-normalize '{str(slice)}'"
                                f" -o '{str(normalized_path / slice.name)}'")
            if verbose: normalization_query += ' -v'
            os.system(normalization_query)

    log.info("\nPreprocessing slices ...")
    for patient in path_to_slices_folder.iterdir():
        slices_path = patient / 'original'
        normalized_path = patient / 'normalized'
        preprocessed_path = patient / 'preprocessed'
        preprocessed_path.mkdir(parents=True, exist_ok=True)
        for slice in tqdm(
                        normalized_path.iterdir(),
                        desc=f"Preprocessing slices for {patient.name}",
                        total=len(list(normalized_path.iterdir()))
        ):
            img = nib.load(slice).get_fdata() # add [:,:,0] if the slice is still considered 3D, 2 main reasons possible:
                                              # you didn't use provided slicing method, or you used 4D images (3D and time)
            img = ants.from_numpy(img, origin = (0,0))
            img_n4 = ants.n4_bias_field_correction(img)
            img_res = ants.resample_image(img_n4, (256,256), True, 1)
            img_res.set_spacing((1,1))

            extensions = ''.join(slice.suffixes)
            filename = slice.name[: -len(extensions)]
            output_filename = f'{filename}{extensions}'
            output_path = preprocessed_path / output_filename
            ants.image_write(img_res, str(output_path))

        if delete_og_slices:
            rmtree(str(slices_path), ignore_errors=True)
            rmtree(str(normalized_path), ignore_errors=True)


def converting_to_png(path_to_slices: Path = PATHS['slices'],
                      path_to_test_folder: Path = PATHS['eyeballs']) -> None:
    """
    Convert nifti images to png to be fed to the neural network.

    Args:
        path_to_slices (Path): path that contains the nifti slices to convert
        path_to_test_foler (Path): ouput path that contains png of slices
    """
    log.info("\nConverting images to PNG....")
    for patient in path_to_slices.iterdir():
        preprocessed_path = patient / 'preprocessed'
        for slice in tqdm(
                        preprocessed_path.iterdir(),
                        desc=f"Converting to PNG for {patient.name}",
                        total=len(list(preprocessed_path.iterdir()))
        ):
            img = nib.load(slice).get_fdata()
            img = np.rot90(img[:,:], 3)
            filename = slice.name[: -len(''.join(slice.suffixes))]
            output_directory = path_to_test_folder / patient.name / 'original'
            output_directory.mkdir(parents=True, exist_ok=True)
            output_path = output_directory / f'{filename}.png'
            # additional line to work with new imageio version (2.29.0)
            img_upd = img.astype('uint8')
            # end of new code
            imageio.imsave(str(output_path), img_upd)
