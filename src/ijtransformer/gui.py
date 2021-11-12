from __future__ import annotations
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QApplication

from ijtransformer.BigWarpWrapper import BigWarpWrapper
from ijtransformer._featureMatchers import ORBFeatureMatcher
from ijtransformer.imageCollection import ImageCollection


class ControlFrameController:
    def __init__(self, bwWrapper: BigWarpWrapper, frame: ControlFrame):
        self._wrapper = bwWrapper
        self._ui = frame
        self._ui.clearButton.released.connect(lambda: self._wrapper.clearPoints())
        self._ui.orbButton.released.connect(self._applyOrbPoints)

    def show(self):
        self._ui.show()

    def _applyOrbPoints(self):
        src, dst = ORBFeatureMatcher().match(self._wrapper.getFixedIms(), self._wrapper.getMovingIms())
        self._wrapper.setPoints(src, dst)


class ControlFrame(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.orbButton = QPushButton("ORB")

        self.clearButton = QPushButton("Clear Points")

        l = QGridLayout()
        l.addWidget(QLabel("Feature Detection"))
        l.addWidget(self.orbButton)
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


class MainController:
    def __init__(self, bwWrapper: BigWarpWrapper, widg: MainWidg):
        self._ui = widg
        self._bwWrapper = bwWrapper
        self._ui._okButton.released.connect(self.close)
        self._controller = ControlFrameController(bwWrapper, self._ui._cFrame)

    def show(self):
        self._ui.show()

    def close(self):
        self._bwWrapper.close()
        self._ui.close()


class App(QApplication):
    def __init__(self, fixedIms: ImageCollection, movingIms: ImageCollection):
        super(App, self).__init__([])

        self._bwWrapper = BigWarpWrapper(fixedIms, movingIms)
        self._controller = MainController(self._bwWrapper, MainWidg())
        self._controller.show()

    def getBigWarpWrapper(self):
        return self._bwWrapper
