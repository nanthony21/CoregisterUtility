import imagej
import pathlib as pl
import scyjava

# https://imagej.net/develop/ij1-ij2-cheat-sheet
import skimage.data
from PyQt5.QtWidgets import QMessageBox, QApplication
from skimage.measure import ransac
from skimage.transform import SimilarityTransform, AffineTransform
import matplotlib.pyplot as plt
from skimage.feature import ORB, match_descriptors
if __name__ == '__main__':
    import numpy as np
    plt.ion()
    # ij = imagej.init(['sc.fiji:fiji', 'sc.fiji:bigwarp_fiji'], headless=False)
    ij = imagej.init(['net.imagej:imagej', 'net.imagej:imagej-legacy', 'sc.fiji:fiji', 'sc.fiji:bigwarp_fiji:7.0.4'], headless=False)
    # ij = imagej.init(['net.imagej:imagej', 'net.imagej:imagej-legacy', 'sc.fiji:fiji'], headless=False)
    # ij = imagej.init(r'C:\Program Files\Fiji.app', headless=False)
    ipClass = scyjava.jimport("ij.ImagePlus")


    ij.ui().showUI()

    astronaut1 = skimage.data.astronaut().mean(axis=2).astype(np.uint8)
    astronaut2 = skimage.transform.warp(astronaut1, AffineTransform(scale=0.7, rotation=.2, translation=(100, 100)).inverse)

    # ORB Detect
    detector1 = ORB()
    detector2 = ORB()
    detector1.detect_and_extract(astronaut1)
    detector2.detect_and_extract(astronaut2)
    matches = match_descriptors(detector1.descriptors, detector2.descriptors)

    src = detector1.keypoints[matches[:, 0]]
    dst = detector2.keypoints[matches[:, 1]]


    # # estimate affine transform model using all coordinates
    # model = SimilarityTransform()
    # model.estimate(src, dst)

    # robustly estimate affine transform model with RANSAC
    print(f"originally have {len(src)}")
    model_robust, inliers = ransac((src, dst), SimilarityTransform, min_samples=3,
                                   residual_threshold=2, max_trials=100)
    src = [i for i, inlier in zip(src, inliers) if inlier]
    dst = [i for i, inlier in zip(dst, inliers) if inlier]

    # Swap coords to account for the fact that they are originally (y,x) rather than (x,y)
    src = [(i[1], i[0]) for i in src]
    dst = [(i[1], i[0]) for i in dst]


    print(f"now have {len(src)}")

    pointPairs = list(zip(
        src,
        dst
    ))

    jo = ij.py.to_dataset(astronaut1)
    a0 = ij.convert().convert(jo, ipClass)
    jo = ij.py.to_dataset(astronaut2)
    a1 = ij.convert().convert(jo, ipClass)
    init = scyjava.jimport("bigwarp.BigWarpInit")
    bwData = init.initData()
    init.add(bwData, a0, 0, 0, True)
    init.add(bwData, a1, 1, 0, False)
    bwData.wrapUp()
    # Do I need the new RepeatingReleasedEventsFixer().install(); here?
    BWClass = scyjava.jimport("bigwarp.BigWarp")
    progWriter = scyjava.jimport("bdv.ij.util.ProgressWriterIJ")()
    BW = BWClass(bwData, "Big WWWWW", progWriter)
    BW.setTransformType("Similarity")  # Allows for scale, translation, and rotation. No shear or perspective

    #Convert point pairs to landmarks in bigwarp
    model = BW.getLandmarkPanel().getTableModel()
    for row, pair in enumerate(pointPairs):
        for i in range(2):
            model.setPoint(row, i % 2 == 0, pair[i], None)

    app = QApplication([])
    QMessageBox.information(None, 'Waiting...', "Click ok when done.")

    bwTransform = BW.getBwTransform()

    def j2pAffine(affine: 'java class "net.imglib2.realtransform.AffineTransform3D"'):
        arr = np.array(affine.getRowPackedCopy()).reshape((3, 4))  # a 3 transform 3x3 plus a 3x1 translation vector
        arr = arr[(0, 0, 0, 1, 1, 1), (0, 1, 3, 0, 1, 3)].reshape((2, 3))  # Convert to a 2d array.
        arr = np.vstack([arr, [0, 0, 1]])
        s = SimilarityTransform(matrix=arr)
        return s

    af3d = bwTransform.affine3d()
    sTransform = j2pAffine(bwTransform.affine3d())
    iTransform = SimilarityTransform(sTransform._inv_matrix)
    print(iTransform.scale, iTransform.rotation, iTransform.translation)

    plugin = scyjava.jimport("bdv.ij.BigWarpImagePlusPlugIn")
    plugin = plugin()
    plugin.run("")

    plugs = ij.plugin().getPlugins()
    for i in range(plugs.size()):
        print(plugs.get(i))


    macro = """
       run("Big Warp", "moving_image=my-moving-img-title.tif target_image=my-target-image-title.tif moving=[] moving_0=[] target=[] target_0=[] landmarks=[]"); 
    """
    args = {

    }
    ij.py.run_macro(macro)
    ij.py
    # path = pl.Path(r'\\backmanlabnas.myqnapcloud.com\Public\Nick_Aya_CellSurface\confocal images\sp5_05132021-2_05142021\confocal\deconvolvedHuygens_default')
    # image = ij.scifio().datasetIO().open(str(path / 'images_Series001.png'))
    #
    # ij.ui().show(image)
    #
    # for p in ij.command().getPlugins():
    #     print(p)
    a = 1