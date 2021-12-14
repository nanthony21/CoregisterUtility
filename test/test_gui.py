import skimage
import skimage.data
from skimage.transform import AffineTransform

from ijtransformer._outputStrategies import SaveWarpedImagesOutputStrategy, SaveMatrixOutputStrategy
from ijtransformer.gui import App
from ijtransformer.imageCollection import ImageCollection
import numpy as np
import pathlib as pl


def test_gui():
    astronaut1 = skimage.data.astronaut().mean(axis=2).astype(np.uint8)
    tForm = AffineTransform(scale=0.7, rotation=.2, translation=(100, 100)).inverse
    astronaut2 = skimage.transform.warp(astronaut1, tForm)
    other = skimage.transform.warp(
        skimage.transform.resize(skimage.data.horse().astype(float), astronaut1.shape),
        tForm
    )

    fixedIms = ImageCollection(astronaut1)
    movingIms = ImageCollection(astronaut2, [other])

    outPath = pl.Path(__file__).parent / 'out'
    if not outPath.exists():
        outPath.mkdir()
    outputs = [
        SaveWarpedImagesOutputStrategy(outPath),
        SaveMatrixOutputStrategy(outPath / 'transform.csv', overwrite=True)
    ]

    app = App.run(fixedIms, movingIms, outputStrategy=outputs)
    sTransform = app.getTransform()

    iTransform = skimage.transform.SimilarityTransform(sTransform._inv_matrix)
    print(iTransform.scale, iTransform.rotation, iTransform.translation)