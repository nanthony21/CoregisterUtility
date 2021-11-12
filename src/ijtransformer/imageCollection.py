import numpy as np
import typing as t_


class ImageCollection:
    def __init__(self, displayImage: np.ndarray, packagedImages: t_.Sequence[np.ndarray] = None):
        self._displayImage = displayImage
        self._packagedImages = packagedImages

        # Check if dimensions match
        if self._packagedImages is not None:
            for im in self._packagedImages:
                assert self._displayImage.shape == im.shape

    def getDisplayImage(self) -> np.ndarray:
        return self._displayImage

    def getPackagedImages(self) -> t_.Sequence[np.ndarray]:
        return self._packagedImages
