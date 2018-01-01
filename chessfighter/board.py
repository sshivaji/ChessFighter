"""
Docstring.
"""
import chess
import chess.pgn
import chess.svg

from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget

from utilities import BidirectionalListener


class Chessboard(BidirectionalListener, QSvgWidget):
    """
    Docstring.
    """
    def __init__(self, parent):
        """
        Docstring.
        """
        super(Chessboard, self).__init__()
        self.parent = parent

        self.moveFromSquare = -10
        self.moveToSquare = -10
        self.square = -10

        self.margin = 0
        self.pieceToMove = [None, None]

        self.chessboard = chess.Board()
        self.drawChessboard()
        self.mouseReleaseEvent = self.mouseEvent

    def registerListener(self):
        """
        Docstring.
        """
        return self.processEvent

    def processEvent(self, event):
        """
        Processes an event, ignores events coming from this class
        """
        if event["Origin"] is not self.__class__:
            if "Fen" in event:
                self.chessboard = chess.Board(event["Fen"])
                self.drawChessboard()


                # if "Action" in event:
            #     if event["Action"] == "Undo":
            #         self.undo()
            # if "Move" in event and "Fen" not in event:
            #     pieceEvent = {"Move": chess.Move.from_uci(event["Move"]), "Fen": self.chessboard.fen(), "Origin": self.__class__}
            #     self.parent(pieceEvent)

    # def undo(self):
    #     self.chessboard.pop()
    #     self.drawChessboard()
    #     pieceEvent = {"Fen": self.chessboard.fen(), "Origin": self.__class__}
    #     self.parent(pieceEvent)

    def mouseEvent(self, event):
        """
        Docstring.
        """
        boardWidth = self.width() / 8
        boardHeight = self.height() / 8

        file = int((event.x() - self.margin) / boardWidth)
        rank = 7 - int((event.y() - self.margin) / boardHeight)

        if rank < 0:
            rank = 0

        if file < 0:
            file = 0

        if file > 7:
            file = 7

        if rank > 7:
            rank = 7

        self.square = chess.square(file,
                                   rank)
        piece = self.chessboard.piece_at(self.square)

        fileCharacter = chr(file + 97)
        rankNumber = str(rank + 1)
        ply = "{}{}".format(fileCharacter,
                            rankNumber)

        if self.pieceToMove[0]:
            move = chess.Move.from_uci("{}{}".format(self.pieceToMove[1],
                                                     ply))
            if move in self.chessboard.legal_moves:
                self.chessboard.push(move)

                pieceEvent = {"Move": move, "Fen": self.chessboard.fen(), "Origin": self.__class__}
                self.parent(pieceEvent)

                self.moveFromSquare = move.from_square
                self.moveToSquare = move.to_square

                piece = None
                ply = None

        self.pieceToMove = [piece, ply]
        self.drawChessboard()

    def drawChessboard(self):
        """
        Docstring.
        """
        check = self.chessboard.king(self.chessboard.turn) if self.chessboard.is_check() else None
        self.svgChessboard = chess.svg.board(board=self.chessboard,
                                             arrows=[(self.square, self.square),
                                                     (self.moveFromSquare, self.moveToSquare)],
                                             check=check,
                                             coordinates=False)
        self.svgChessboardEncoded = self.svgChessboard.encode("utf-8")
        self.load(self.svgChessboardEncoded)

    def resizeEvent(self, event):
        """
        Docstring.
        """
        newSize = QSize(10, 10)
        newSize.scale(event.size(), Qt.KeepAspectRatio)
        # print(newSize * 0.95)
        self.resize(newSize)
