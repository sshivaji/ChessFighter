"""
Docstring.
"""
import chess


from PyQt5.QtWidgets import QTextBrowser
from PyQt5 import QtGui
from utilities import BidirectionalListener


class ChessGameWidget(BidirectionalListener, QTextBrowser):
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
        self.setReadOnly = False

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """

        if event["Origin"] is not self.__class__:
            if event["Move"]:
                move = event["Move"]
                self.currentGame = self.currentGame.add_variation(move)

                exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
                pgn_string = self.game.accept(exporter)
                self.setText(pgn_string)
                self.moveCursor(QtGui.QTextCursor.End)

