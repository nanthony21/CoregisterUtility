import imagej
import scyjava
import typing as t_

from skimage.transform import SimilarityTransform

import numpy as np

Point2d = t_.Tuple[float, float]

ij = imagej.init(['net.imagej:imagej', 'net.imagej:imagej-legacy', 'sc.fiji:fiji', 'sc.fiji:bigwarp_fiji:7.0.5'], headless=False)
ImagePlusClass = scyjava.jimport("ij.ImagePlus")
BigWarpInitClass = scyjava.jimport("bigwarp.BigWarpInit")
BWClass = scyjava.jimport("bigwarp.BigWarp")
ProgressWriterClass = scyjava.jimport("bdv.ij.util.ProgressWriterIJ")


class BigWarpWrapper:
    """
    Run the BigWarp plugin for ImageJ with these two images compared to eachother.

    Args:
        fixedIm: image to compare to. Will not be transformed
        movingIm: image to warp.
    """
    def __init__(self, fixedIm: np.ndarray, movingIm: np.ndarray):
        imPlus1 = ij.convert().convert(ij.py.to_dataset(fixedIm), ImagePlusClass)
        imPlus2 = ij.convert().convert(ij.py.to_dataset(movingIm), ImagePlusClass)

        bwData = BigWarpInitClass.initData()
        BigWarpInitClass.add(bwData, imPlus2, 0, 0, True)  # Signature: ( BigWarpData bwdata, ImagePlus ip, int setupId, int numTimepoints, boolean isMoving )
        BigWarpInitClass.add(bwData, imPlus1, 1, 0, False)
        bwData.wrapUp()
        progWriter = ProgressWriterClass()
        self._bigWarp = BWClass(bwData, "Big WWWWW", progWriter)
        self._bigWarp.setTransformType("Similarity")  # Allows for scale, translation, and rotation. No shear or perspective

        self._fixedIms = fixedIm
        self._movingIms = movingIm

    def clearPoints(self):
        """
        Removes all points from the list of points in BigWarp
        """
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        model.clear()

    def setPoints(self, fixedPoints: t_.Sequence[Point2d], movingPoints: t_.Sequence[Point2d]):
        """
        Add these point pairs in addition to any pre-existing points

        Args:
            fixedPoints: The 2d points for the `fixed` image
            movingPoints: The 2d points for the `moving` image
        """
        assert len(movingPoints) == len(fixedPoints)
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        startRow = model.getRowCount()
        for row, pointPair in enumerate(zip(movingPoints, fixedPoints)):
            for i in range(2):
                model.setPoint(startRow + row, i % 2 == 0, pointPair[i], None)

    def getTransform(self) -> SimilarityTransform:
        """

        Returns: The current BigWarp transform in the form of a Scikit-Image SimilarityTransform.

        """
        def j2pAffine(affine: 'java class "net.imglib2.realtransform.AffineTransform3D"') -> SimilarityTransform:
            """
            Converts the Java `AffineTransform3D` class to a Python Scikit-Image `SimilarityTransform` class.

            Args:
                affine: The instance of the Java transform to convert.

            Returns:

            """
            arr = np.array(affine.getRowPackedCopy()).reshape((3, 4))  # a 3 transform 3x3 plus a 3x1 translation vector
            arr = arr[(0, 0, 0, 1, 1, 1), (0, 1, 3, 0, 1, 3)].reshape((2, 3))  # Convert to a 2d array.
            arr = np.vstack([arr, [0, 0, 1]])
            s = SimilarityTransform(matrix=arr)
            return s

        af3d = self._bigWarp.getBwTransform().affine3d()
        return j2pAffine(af3d)

    def __del__(self):
        """Make sure to close BigWarp when this object is destroyed. """
        self.close()

    def close(self):
        """
        Close BigWarp in ImageJ
        """
        self._bigWarp.closeAll()

    def getFixedImage(self) -> np.ndarray:
        return self._fixedIms

    def getMovingImage(self) -> np.ndarray:
        return self._movingIms
