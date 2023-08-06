# Copyright (c) 2019 zhixuhao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
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
import numpy as np
import skimage.io as io
import skimage.transform as trans
from skimage import img_as_ubyte


def testGenerator(full_path: Path, target_size: tuple = (256,256)) -> np.ndarray:
    """
    Generator to feed the images to the neural network.

    Args:
        full_path (Path): path to eyeballs/patient/original,
                          where preprocessed png are stored
        target_size (tuple): size of the final image

    Return:
        img (np.ndarray): numpy array of the png image with the desired property
    """
    for filename in full_path.iterdir():
        img = io.imread(str(filename), as_gray = True)
        img = img / 255.
        img = trans.resize(img,target_size)
        img = np.reshape(img,img.shape+(1,))
        img = np.reshape(img,(1,)+img.shape)
        yield img


def saveResult(output_path: Path, npyfile: np.ndarray, list_name: list) -> None:
    """
    Save the results of the model prediction as png in output_path.

    Args:
        output_path (Path): Path to where the png segmentation will be stored
        npyfile (np.ndarray): numpy array of the model prediction
        list_name (list): list containing strings of the desired output filename
    """
    for name in list_name:
        output_path.mkdir(parents=True, exist_ok=True)
        for i, item in enumerate(npyfile):
            if list_name.index(name) == i:
                img = item[:,:,0]
                io.imsave(str(output_path / name), img_as_ubyte(img),
                                                           check_contrast=False)
