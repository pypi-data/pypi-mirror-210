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
import shutil
import sys

from tcsa import welcome, __version__
from .prequisite import create_parser, handle_dicom, handle_single_nifti
from .pipeline import full_pipeline

parser = create_parser()

if len(sys.argv)==1:
    parser.print_usage()
    sys.exit(0)

args = parser.parse_args()

if args.version:
    welcome()
    sys.exit(0)

args.images = args.images.resolve(strict=True) # check if the path exist
args.output = args.output.resolve(strict=False)

if args.dicom:
    handle_dicom(args, verbosity=False)

if args.images.is_file() and not args.dicom:
    handle_single_nifti(args)

def main() -> None:
    """
    Run the full script.
    """
    # welcome()
    full_pipeline(input_path=args.images, output_path=args.output, delete=args.delete, both_sides=args.both_sides)
    shutil.rmtree(str(Path('temp_images').resolve()), ignore_errors=True)
