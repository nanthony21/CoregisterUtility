from __future__ import annotations

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QFrame, QHBoxLayout

from coregister_utility._featureMatchers import MatcherFactory, FeatureMatcher
from coregister_utility._ui.BigWarpWrapper import BigWarpWrapper


class ControlFrameController:
    """
    The controller for the ControllerFrame widget

    Args:
        bwWrapper: The object we use to communicate with BigWarp
    """
    def __init__(self, bwWrapper: BigWarpWrapper, frame: ControlFrame):
        self._wrapper = bwWrapper
        self._ui = frame
        self._ui.clearButton.released.connect(lambda: self._wrapper.clearPoints())

        for button in self._ui.matcherButtons:
            name = button.text()
            matcher = MatcherFactory.getMatcher(name)
            button.released.connect(lambda m=matcher: self._applyMatcherPoints(m))

    def _applyMatcherPoints(self, matcher: FeatureMatcher):
        """

        Args:
            matcher: The feature matcher object to set points on the BigWarp images for.
        """
        fixed, moving = matcher.match(self._wrapper.getFixedImage(), self._wrapper.getMovingImage())
        self._wrapper.setPoints(fixed, moving)


class ControlFrame(QWidget):
    """
    The widget that has buttons to perform feature matching on the images.
    """
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
    """
    This is the top level Python widget that will pop up as a window.
    """
    def __init__(self):
        super().__init__(parent=None)

        self._cFrame = ControlFrame(self)
        self._okButton = QPushButton("Done")

        l = QGridLayout()
        l.addWidget(self._cFrame)
        l.addWidget(self._okButton)
        self.setLayout(l)


class MainController(QObject):
    """
    This is the controller for the Main Python Widget.

    Args:
        bwWrapper: The object that helps us control the BigWarp plugin for ImageJ
    """
    aboutToClose = pyqtSignal()

    def __init__(self, bwWrapper: BigWarpWrapper, parent=None):
        super(MainController, self).__init__(parent=parent)
        self._ui = MainWidg()
        self._bwWrapper = bwWrapper
        self._ui._okButton.released.connect(self.close)
        self._controller = ControlFrameController(bwWrapper, self._ui._cFrame)

    def show(self):
        """
        Show the user interface.
        """
        self._ui.show()

    def close(self):
        """
        Close the user interface and clean up other resources.
        """
        self._ui.close()
        self.aboutToClose.emit()
