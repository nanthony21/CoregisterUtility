from __future__ import annotations

from PyQt5.QtWidgets import QApplication
from skimage.transform import SimilarityTransform

from coregister_utility._ui.BigWarpWrapper import BigWarpWrapper
from coregister_utility._outputStrategies import OutputStrategy
from coregister_utility._image_collections import AbstractImageCollection
import typing as t_

from coregister_utility._ui.mainUI import MainController


class CoregisterUtilityApp(QApplication):
    """
    This is the top-level application that runs the whole procedure.

    Args:
        fixedIms: A collection of images to use as a reference for the transform
        movingIms: A collection of images to apply the calculated transform to.
        outputStrategy: A list of OutputStrategies which determine what type of data is output at the end of the process.
    """
    def __init__(self, fixedIms: AbstractImageCollection, movingIms: AbstractImageCollection, outputStrategy: t_.Sequence[OutputStrategy] = None):
        super(CoregisterUtilityApp, self).__init__([])

        self._outputs = outputStrategy
        self._fixedIms = fixedIms
        self._movingIms = movingIms
        self._bwWrapper = BigWarpWrapper(fixedIms.getDisplayImage(), movingIms.getDisplayImage())
        self._controller = MainController(self._bwWrapper, parent=self)
        self._controller.aboutToClose.connect(self._close)
        self._controller.show()

    @staticmethod
    def run(fixedIms: AbstractImageCollection, movingIms: AbstractImageCollection, outputStrategy: t_.Sequence[OutputStrategy] = None) -> CoregisterUtilityApp:
        """
        Use this method to run the application. It will block until the application is closed.

        Args:
            See the constructor for more information

        Returns:
            An instance of the application.
        """
        app = CoregisterUtilityApp(fixedIms, movingIms, outputStrategy=outputStrategy)
        app.exec()
        return app

    def getTransform(self) -> SimilarityTransform:
        """
        Returns:
            The transform that was calculated by BigWarp
        """
        return self._bwWrapper.getTransform()

    def _close(self):
        """
        Runs the various output strategies at the end of the process. This is connected to the application's "aboutToClose" event.
        """
        self._bwWrapper.close()
        # Execute the output strategies
        for out in self._outputs:
            out.execute(self.getTransform(), self._fixedIms, self._movingIms)

