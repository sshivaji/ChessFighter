"""
Docstring.
"""
import chess

from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTextEdit

from utilities import BidirectionalListener


class ChessGameWidget(BidirectionalListener, QListWidget):
    """
    Docstring.
    """
    def __init__(self, dock, parent):
        """
        Docstring.
        """
        super(ChessGameWidget, self).__init__()

        self.parent = parent

        self.game = chess.pgn.Game()
        self.currentGame = self.game

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """

        if event["Origin"] is not self.__class__:
            if event["Move"]:
                move = event["Move"]
                self.currentGame = self.currentGame.add_variation(move)
                # print("move: {}".format(move))
                self.addItem(str(move))
