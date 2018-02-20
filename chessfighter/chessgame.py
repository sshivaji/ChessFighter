"""
Docstring.
"""
import chess

from PyQt5.QtWidgets import QTextBrowser
from PyQt5 import QtGui
from utilities import BidirectionalListener

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3


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
            elif "SAN" in event:
                san = event["SAN"]
                move = self.currentGame.board().parse_san(san)
                print("move: {}".format(move))
                self.currentGame = self.currentGame.add_variation(move)
                self.updatePgn()
                self.parent({"Fen": self.currentGame.board().fen(), "Origin": self.__class__})
            elif "Action" in event:
                if event["Action"] == "Undo":
                    # print("got Undo")
                    self.undo()
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

                elif event["Action"] == "Refresh":
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

                elif event["Action"] == "Load Game":
                    pgn = StringIO(event["PGN"][0])
                    self.game = chess.pgn.read_game(pgn)
                    self.updatePgn()
                    self.currentGame = self.game

                elif event["Action"] == "Forward":
                    self.forward()
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

            elif "Book_File" in event:
                print("Got Book_File event!")
                board = self.currentGame.board()
                self.parent({"Fen": board.fen(), "Origin": self.__class__})


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

    def forward(self):
        if self.currentGame.variations:
            self.currentGame = self.currentGame.variations[0]
            self.updatePgn()
