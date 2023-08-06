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

import argparse
from pathlib import Path
from hashlib import md5
import gdown
import json
import logging
import importlib.resources
import dicom2nifti
import sys
import shutil

from tcsa import PATHS
from .data_preparation import is_nifti, is_dicom

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
log = logging.getLogger(__name__)

log_conv = logging.getLogger('dicom2nifti')
log_conv.setLevel(logging.ERROR)

def create_parser() -> argparse.ArgumentParser:
    """
    Create the parser used in CLI.

    Return:
        (argparse.ArgumentParser): Parser with desired argument.
    """
    parser = argparse.ArgumentParser(
        prog='tcsa',
        description='Extract the CSA of temporalis muscle from T1w-contrast MRI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='only for POSIX system for now.'
    )
    parser.add_argument(
        "images",
        metavar="path_to_image(s)",
        nargs="?",
        type=Path,
        help="Path of image(s) to process, can be a folder or single image (.nii or .nii.gz)."
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="path_to_csv",
        nargs="?",
        type=Path,
        default=(Path.cwd() / 'temporalis_CSA.csv'),
        help="Path to save the csv file."
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Only keep input and output."
    )
    parser.add_argument(
        "--both-sides",
        action="store_true",
        help="segment both temporalis muscle."
    )
    # parser.add_argument(
    #     "-v",
    #     "--verbosity",
    #     action="count",
    #     default=0,
    #     help="Increase output verbosity (e.g., -vv is more than -v)."
    # )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Display version of tCSA."
    )

    parser.add_argument(
        "--dicom",
        action="store_true",
        help="Convert dicom directories to nifti."
    )
    return parser

def handle_dicom(args: argparse.Namespace, *, verbosity: bool = False) -> None:
    """
    Convert dicom directory in nifti for the pipeline.

    Pipeline work for nifti files,
    so we convert dicom into nifti files beforehand,
    the new nifti file is stored in a temp directory

    Args:
        args (argparse.Namespace): Arguments from CLI.
        verbosity (bool): Control the verbosity of dicom2nifti
    """
    if args.images.is_dir():
        dicom_files = list(args.images.iterdir())
        if len(dicom_files) == 0:
            log.warning("There is no files in your directory.")
            sys.exit()
        if is_dicom(dicom_files[0]):
            if verbosity:
                log_conv.setLevel(logging.INFO)
            log.info("Convering dicom to nifti...")
            temp_images = Path('temp_images').resolve()
            temp_images.mkdir(parents=True, exist_ok=True)
            dicom2nifti.convert_directory(args.images, temp_images,
                                          compression=False, reorient=True)
            args.images = temp_images
        else:
            log.warning("No dicom files found in the directory.")
            sys.exit()
    else:
        log.warning("Please put the dicom files in a directory.")
        sys.exit()

def handle_single_nifti(args: argparse.Namespace) -> None:
    """
    Make the pipeline work for single nifti file.

    Pipeline work for directories, so if there is only one image
    we create a temporary directory where we copy the image
    the temp directory will be our new input

    Args:
        args (argparse.Namespace): Arguments from CLI.
    """
    if is_nifti(args.images):
        temp_images = Path('temp_images').resolve()
        temp_images.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(args.images), str(temp_images / args.images.name))
        args.images = temp_images
    else:
        log.warning(f"{args.images.name} isn't a nifti file.")
        if is_dicom(args.images):
            log.warning(f"Please convert with --dicom in command line.")
        sys.exit()

def creating_directories() -> None:
    """
    Create the directories present in tcsa (__init__.py)
    """
    log.info("\nCreating the necessary directories...")
    for path in PATHS.values():
        path.mkdir(parents=True, exist_ok=True)

def get_hash(file: Path) -> str:
    """
    Get md5Hash of a file

    Args:
        file (Path): Path to file

    Return:
        str: md5Hash of file
    """
    md5_hash = md5()
    with open(str(file), 'rb') as f:
        for byte_block in iter(lambda: f.read(4096),b''):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def get_weights() -> None:
    """
    Check the weights and download them if necessary

    Raise:
        Exception: the weight downloaded is corrupted
    """
    # load configs containing the hash of the weight and there download link
    with importlib.resources.open_text("tcsa", "config.json") as config_file:
        config = json.load(config_file)
    HASHS, ID = config['HASHS'], config['ID']

    log.info("\nChecking if weights are present...")
    for weight, hash in HASHS.items():
        weight_path = PATHS['weights'] / weight
        if weight_path.exists():
            if get_hash(weight_path) == hash:
                log.info(f"{weight} is present and is up to date")
                continue
            else:
                log.info(f"{weight} is present but is corrupted/not up to date")
        else:
            log.info(f"{weight} is missing")
        log.info(f"{weight} will be downloaded")
        gdown.download(id=ID[weight], output=str(weight_path), quiet=False,
                       use_cookies=False, resume=False)
        if get_hash(weight_path) != hash:
            raise Exception("md5 checksum failed")

def run_prequisite() -> None:
    """
    Run all the prequisites (create directories and check weights).
    """
    creating_directories()
    get_weights()
