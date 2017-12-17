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
            if "Move" in event:
                move = event["Move"]
                self.currentGame = self.currentGame.add_variation(move)
                self.updatePgn()
            elif "Action" in event:
                if event["Action"] == "Undo":
                    self.undo()

    def updatePgn(self):
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        pgn_string = self.game.accept(exporter)
        # print("pgn: {}".format(pgn_string))
        self.setText(pgn_string)
        self.moveCursor(QtGui.QTextCursor.End)

    def undo(self):
        if self.currentGame.parent:
            self.currentGame = self.currentGame.parent
            self.updatePgn()
