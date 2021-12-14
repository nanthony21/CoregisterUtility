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

from ijtransformer.BigWarpWrapper import BigWarpWrapper
from ijtransformer.gui import ControlFrameController, App
from ijtransformer.imageCollection import ImageCollection
import numpy as np

if __name__ == '__main__':
    # ij.ui().showUI()

    astronaut1 = skimage.data.astronaut().mean(axis=2).astype(np.uint8)
    astronaut2 = skimage.transform.warp(astronaut1, AffineTransform(scale=0.7, rotation=.2, translation=(100, 100)).inverse)

    im1 = ImageCollection(astronaut1)
    im2 = ImageCollection(astronaut2)

    app = App(im1, im2)
    app.exec()
    sTransform = app.getTransform()

    iTransform = SimilarityTransform(sTransform._inv_matrix)
    print(iTransform.scale, iTransform.rotation, iTransform.translation)

    a = 1