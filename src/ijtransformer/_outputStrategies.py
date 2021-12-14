import abc
import os

import skimage.io
import skimage.transform as sktransform
import pathlib as pl
from ijtransformer.imageCollection import ImageCollection
import numpy as np


class OutputStrategy(abc.ABC):
    @abc.abstractmethod
    def execute(self, transform: sktransform.ProjectiveTransform, fixed: ImageCollection, moving: ImageCollection):
        ...


class SaveWarpedImagesOutputStrategy(OutputStrategy):
    def __init__(self, outputPath: os.PathLike):
        self._path = pl.Path(outputPath)
        if not self._path.exists():
            self._path.mkdir()

    def execute(self, transform: sktransform.ProjectiveTransform, fixed: ImageCollection, moving: ImageCollection):
        for i, im in enumerate(moving.getAllImages()):
            warped = sktransform.warp(im, transform)
            skimage.io.imsave(self._path / f"{i}.tif", warped)


class SaveMatrixOutputStrategy(OutputStrategy):
    def __init__(self, outputPath: os.PathLike, overwrite: bool = False):
        self._path = pl.Path(outputPath)
        assert self._path.suffix == '.csv', "Output file name must be a `.csv`"
        if not overwrite and self._path.exists():
            raise OSError(f"File {self._path} already exists. Please use `overwrite` = True.")

    def execute(self, transform: sktransform.ProjectiveTransform, fixed: ImageCollection, moving: ImageCollection):
        np.savetxt(self._path, transform.params, delimiter=',')

