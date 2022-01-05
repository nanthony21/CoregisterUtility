import abc
import os

import skimage.io
import skimage.transform as sktransform
import pathlib as pl
from coregister_utility._image_collections import AbstractImageCollection
import numpy as np


class OutputStrategy(abc.ABC):
    """
    Abstract representation of a final output for the Coregister Utility application.
    """
    @abc.abstractmethod
    def execute(self, transform: sktransform.ProjectiveTransform, fixed: AbstractImageCollection, moving: AbstractImageCollection):
        """
        This method will be run at the end of the application life-cycle.

        Args:
            transform: The scikit-image transform object representing the transformation.
            fixed: The collection of images that are considered "Fixed" in-place by the application
            moving:  The collection of images that are considered to be "Moving". The transform will be applied to these images.
        """
        ...


class SaveWarpedImagesOutputStrategy(OutputStrategy):
    """
    OutputStrategy implementation that will save the images after transformation to an output path.

    Args:
        outputPath: The path to save the images to.
    """
    def __init__(self, outputPath: os.PathLike):
        self._path = pl.Path(outputPath)
        if not self._path.exists():
            self._path.mkdir()

    def execute(self, transform: sktransform.ProjectiveTransform, fixed: AbstractImageCollection, moving: AbstractImageCollection):
        for i, im in enumerate(moving.getAllImages()):
            warped = sktransform.warp(im, transform)
            skimage.io.imsave(self._path / f"{i}.tif", warped)


class SaveMatrixOutputStrategy(OutputStrategy):
    """
    An OutputStrategy that will save the transform as a 3x3 transformation matrix in CSV format.

    Args:
        outputPath: The path to save the CSV to.
        overwrite: If true then an existing CSV of the same name will be replaced. Otherwise, an error will be thrown.
    """
    def __init__(self, outputPath: os.PathLike, overwrite: bool = False):
        self._path = pl.Path(outputPath)
        assert self._path.suffix == '.csv', "Output file name must be a `.csv`"
        if not overwrite and self._path.exists():
            raise OSError(f"File {self._path} already exists. Please use `overwrite` = True.")

    def execute(self, transform: sktransform.ProjectiveTransform, fixed: AbstractImageCollection, moving: AbstractImageCollection):
        np.savetxt(self._path, transform.params, delimiter=',')

