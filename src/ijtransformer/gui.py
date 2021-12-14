from __future__ import annotations

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QApplication, QHBoxLayout, QFrame
from skimage.transform import SimilarityTransform

from ijtransformer.BigWarpWrapper import BigWarpWrapper
from ijtransformer._featureMatchers import MatcherFactory, FeatureMatcher
from ijtransformer._outputStrategies import OutputStrategy
from ijtransformer.imageCollection import ImageCollection
import typing as t_


class ControlFrameController:
    def __init__(self, bwWrapper: BigWarpWrapper, frame: ControlFrame):
        self._wrapper = bwWrapper
        self._ui = frame
        self._ui.clearButton.released.connect(lambda: self._wrapper.clearPoints())

        for button in self._ui.matcherButtons:
            name = button.text()
            matcher = MatcherFactory.getMatcher(name)
            button.released.connect(lambda m=matcher: self._applyMatcherPoints(m))

    def show(self):
        self._ui.show()

    def _applyMatcherPoints(self, matcher: FeatureMatcher):
        fixed, moving = matcher.match(self._wrapper.getFixedIms(), self._wrapper.getMovingIms())
        self._wrapper.setPoints(fixed, moving)


class ControlFrame(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.matcherButtons = []
        for name in MatcherFactory.getMatcherNames():
            self.matcherButtons.append(QPushButton(name))

        self.clearButton = QPushButton("Clear Points")

        l = QGridLayout()
        l.addWidget(QLabel("Feature Detection"))
        matcherWidg = QFrame()
        matcherWidg.setFrameShape(QFrame.Box)
        matcherWidg.setLayout(QHBoxLayout())

        for b in self.matcherButtons:
            matcherWidg.layout().addWidget(b)
        l.addWidget(matcherWidg)
        l.addWidget(self.clearButton)
        self.setLayout(l)


class MainWidg(QWidget):
    def __init__(self):
        super().__init__(parent=None)

        self._cFrame = ControlFrame(self)
        self._okButton = QPushButton("Done")

        l = QGridLayout()
        l.addWidget(self._cFrame)
        l.addWidget(self._okButton)
        self.setLayout(l)


class MainController(QObject):
    aboutToClose = pyqtSignal()

    def __init__(self, bwWrapper: BigWarpWrapper, widg: MainWidg, parent=None):
        super(MainController, self).__init__(parent=parent)
        self._ui = widg
        self._bwWrapper = bwWrapper
        self._ui._okButton.released.connect(self.close)
        self._controller = ControlFrameController(bwWrapper, self._ui._cFrame)

    def show(self):
        self._ui.show()

    def close(self):
        self._bwWrapper.close()
        self._ui.close()
        self.aboutToClose.emit()


class App(QApplication):
    def __init__(self, fixedIms: ImageCollection, movingIms: ImageCollection, outputStrategy: t_.Sequence[OutputStrategy] = None):
        super(App, self).__init__([])

        self._outputs = outputStrategy
        self._fixedIms = fixedIms
        self._movingIms = movingIms
        self._bwWrapper = BigWarpWrapper(fixedIms.getDisplayImage(), movingIms.getDisplayImage())
        self._controller = MainController(self._bwWrapper, MainWidg(), parent=self)
        self._controller.aboutToClose.connect(self._executeOutputs)
        self._controller.show()

    # def getBigWarpWrapper(self):
    #     return self._bwWrapper

    def getTransform(self) -> SimilarityTransform:
        return self._bwWrapper.getTransform()

    def _executeOutputs(self):
        for out in self._outputs:
            out.execute(self.getTransform(), self._fixedIms, self._movingIms)

