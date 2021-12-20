from __future__ import annotations

from PyQt5.QtWidgets import QApplication
from skimage.transform import SimilarityTransform

from coregister_utility._ui.BigWarpWrapper import BigWarpWrapper
from coregister_utility._outputStrategies import OutputStrategy
from coregister_utility._image_collections import AbstractImageCollection
import typing as t_

from coregister_utility._ui.mainUI import MainWidg, MainController


class CoregisterUtilityApp(QApplication):
    def __init__(self, fixedIms: AbstractImageCollection, movingIms: AbstractImageCollection, outputStrategy: t_.Sequence[OutputStrategy] = None):
        super(CoregisterUtilityApp, self).__init__([])

        self._outputs = outputStrategy
        self._fixedIms = fixedIms
        self._movingIms = movingIms
        self._bwWrapper = BigWarpWrapper(fixedIms.getDisplayImage(), movingIms.getDisplayImage())
        self._controller = MainController(self._bwWrapper, MainWidg(), parent=self)
        self._controller.aboutToClose.connect(self._executeOutputs)
        self._controller.show()

    @staticmethod
    def run(fixedIms: AbstractImageCollection, movingIms: AbstractImageCollection, outputStrategy: t_.Sequence[OutputStrategy] = None) -> CoregisterUtilityApp:
        app = CoregisterUtilityApp(fixedIms, movingIms, outputStrategy=outputStrategy)
        app.exec()
        return app

    def getTransform(self) -> SimilarityTransform:
        return self._bwWrapper.getTransform()

    def _executeOutputs(self):
        for out in self._outputs:
            out.execute(self.getTransform(), self._fixedIms, self._movingIms)

