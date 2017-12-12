"""
Docstring.
"""
import chess
import chess.svg

from PyQt5.QtCore import pyqtSlot, QRect, QSize, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget

class Chessboard(QWidget):
    """
    Docstring.
    """
    def __init__(self):
        """
        Docstring.
        """
        super().__init__()

        self.chessboard = chess.Board()
        self.drawChessboard()

    @pyqtSlot(QSvgWidget)
    def mouseReleaseEvent(self, event):
        """
        Docstring.
        """
        pass

    def drawChessboard(self):
        """
        Docstring.
        """
        self.svgChessboard = chess.svg.board(board=self.chessboard, coordinates=False)
        self.svgChessboardEncoded = self.svgChessboard.encode("utf-8")
        self.svgWidget = QSvgWidget(parent=self)
        self.svgWidget.setGeometry(10, 10, 400, 400)

        return self.svgWidget.load(self.svgChessboardEncoded)

    def resizeEvent(self, event):
        # super().__init__()
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(10, 10)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.svgWidget.resize(new_size*0.95)


