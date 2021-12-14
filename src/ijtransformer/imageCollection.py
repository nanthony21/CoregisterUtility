import numpy as np
import typing as t_


class ImageCollection:
    """
    Represents a set of images that all have the same localization. The `displayImage` will be the one shown in a GUI.

    Args:
        displayImage: The image to show to represent these images.
        packagedImages: The full set of images that are colocalized. Not including the displayImage.
    """
    def __init__(self, displayImage: np.ndarray, packagedImages: t_.Sequence[np.ndarray] = None):
        self._displayImage = displayImage
        self._packagedImages = tuple(packagedImages) if packagedImages is not None else None

        # Check if dimensions match
        if self._packagedImages is not None:
            for im in self._packagedImages:
                assert self._displayImage.shape == im.shape

    def getDisplayImage(self) -> np.ndarray:
        return self._displayImage

    def getPackagedImages(self) -> t_.Sequence[np.ndarray]:
        return self._packagedImages

    def getAllImages(self) -> t_.Sequence[np.ndarray]:
        return tuple((self.getDisplayImage(),) + tuple(self.getPackagedImages()))
