import imagej
import scyjava
import typing as t_
from src.ijtransformer.imageCollection import ImageCollection

Point2d = t_.Tuple[float, float]

ij = imagej.init(['net.imagej:imagej', 'net.imagej:imagej-legacy', 'sc.fiji:fiji', 'sc.fiji:bigwarp_fiji:7.0.4'], headless=False)
ImagePlusClass = scyjava.jimport("ij.ImagePlus")
BigWarpInitClass = scyjava.jimport("bigwarp.BigWarpInit")
BWClass = scyjava.jimport("bigwarp.BigWarp")
ProgressWriterClass = scyjava.jimport("bdv.ij.util.ProgressWriterIJ")

class BigWarpWrapper:
    def __init__(self, fixedIms: ImageCollection, movingIms: ImageCollection):

        imPlus1 = ij.convert().convert(ij.py.to_dataset(fixedIms.getDisplayImage(), ImagePlusClass))
        imPlus2 = ij.convert().convert(ij.py.to_dataset(movingIms.getDisplayImage(), ImagePlusClass))

        bwData = BigWarpInitClass.initData()
        BigWarpInitClass.add(bwData, imPlus1, 0, 0, True)
        BigWarpInitClass.add(bwData, imPlus2, 1, 0, False)
        bwData.wrapUp()
        # Do I need the new RepeatingReleasedEventsFixer().install(); here?
        progWriter = ProgressWriterClass()
        self._bigWarp = BWClass(bwData, "Big WWWWW", progWriter)
        self._bigWarp.setTransformType("Similarity")  # Allows for scale, translation, and rotation. No shear or perspective

        # Convert point pairs to landmarks in bigwarp
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        # for row, pair in enumerate(pointPairs):
        #     for i in range(2):
        #         model.setPoint(row, i % 2 == 0, pair[i], None)

    def clearPoints(self):
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        model.clear()

    def setPoints(self, movingPoints: t_.Sequence[Point2d], fixedPoints: t_.Sequence[Point2d]):
        assert len(movingPoints) == len(fixedPoints)
        model = self._bigWarp.getLandmarkPanel().getTableModel()
        for row, pointPair in enumerate(zip(movingPoints, fixedPoints)):
            for i in range(2):
                model.setPoint(row, i % 2 == 0, pointPair[i], None)

    def close(self):
        self._bigWarp.closeAll()
