import imagej
import scyjava
import typing as t_

from skimage.transform import SimilarityTransform

from src.ijtransformer.imageCollection import ImageCollection
import numpy as np

Point2d = t_.Tuple[float, float]

ij = imagej.init(['net.imagej:imagej', 'net.imagej:imagej-legacy', 'sc.fiji:fiji', 'sc.fiji:bigwarp_fiji:7.0.4'], headless=False)
ImagePlusClass = scyjava.jimport("ij.ImagePlus")
BigWarpInitClass = scyjava.jimport("bigwarp.BigWarpInit")
BWClass = scyjava.jimport("bigwarp.BigWarp")
ProgressWriterClass = scyjava.jimport("bdv.ij.util.ProgressWriterIJ")


class BigWarpWrapper:
    def __init__(self, fixedIms: ImageCollection, movingIms: ImageCollection):

        imPlus1 = ij.convert().convert(ij.py.to_dataset(fixedIms.getDisplayImage()), ImagePlusClass)
        imPlus2 = ij.convert().convert(ij.py.to_dataset(movingIms.getDisplayImage()), ImagePlusClass)

        bwData = BigWarpInitClass.initData()
        BigWarpInitClass.add(bwData, imPlus1, 0, 0, True)
        BigWarpInitClass.add(bwData, imPlus2, 1, 0, False)
        bwData.wrapUp()
        # Do I need the new RepeatingReleasedEventsFixer().install(); here?
        progWriter = ProgressWriterClass()
        self._bigWarp = BWClass(bwData, "Big WWWWW", progWriter)
        self._bigWarp.setTransformType("Similarity")  # Allows for scale, translation, and rotation. No shear or perspective

        self._fixedIms = fixedIms
        self._movingIms = movingIms

    def clearPoints(self):
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        model.clear()

    def setPoints(self, movingPoints: t_.Sequence[Point2d], fixedPoints: t_.Sequence[Point2d]):
        assert len(movingPoints) == len(fixedPoints)
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        for row, pointPair in enumerate(zip(movingPoints, fixedPoints)):
            for i in range(2):
                model.setPoint(row, i % 2 == 0, pointPair[i], None)

    def getTransform(self) -> SimilarityTransform:
        def j2pAffine(affine: 'java class "net.imglib2.realtransform.AffineTransform3D"') -> SimilarityTransform:
            arr = np.array(affine.getRowPackedCopy()).reshape((3, 4))  # a 3 transform 3x3 plus a 3x1 translation vector
            arr = arr[(0, 0, 0, 1, 1, 1), (0, 1, 3, 0, 1, 3)].reshape((2, 3))  # Convert to a 2d array.
            arr = np.vstack([arr, [0, 0, 1]])
            s = SimilarityTransform(matrix=arr)
            return s

        af3d = self._bigWarp.getBwTransform().affine3d()
        return j2pAffine(af3d)

    def __del__(self):
        self.close()

    def close(self):
        self._bigWarp.closeAll()

    def getFixedIms(self) -> ImageCollection:
        return self._fixedIms

    def getMovingIms(self) -> ImageCollection:
        return self._movingIms
