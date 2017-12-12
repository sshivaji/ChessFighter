"""
Docstring.
"""
import chess
import chess.svg
import chess.pgn
import utilities

from PyQt5.QtCore import pyqtSlot, QRect, QSize, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget

class Chessboard(utilities.BidirectionalListener, QWidget):
    """
    Docstring.
    """
    def __init__(self, parent):
        """
        Docstring.
        """
        super().__init__()
        self.parent = parent
        self.svgWidget = QSvgWidget(parent=self)
        self.svgWidget.setGeometry(10, 10, 400, 400)

        self.pieceToMove = [None, None]
        self.square = -10
        self.moveFromSquare = -10
        self.moveToSquare = -10
        self.chessboard = chess.Board()
        self.drawChessboard()
        self.svgWidget.mouseReleaseEvent = self.boardMousePressEvent
        self.margin = 0

    def register_listener(self):
        return self.process_event

    def process_event(self, e):
        print("event: {}".format(e))

    def boardMousePressEvent(self, event):
        """
        Handles left mouse clicks and enables moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        board_width = self.svgWidget.width()/8
        board_height = self.svgWidget.height()/8

        file = int((event.x() - self.margin) / board_width)
        rank = 7 - int((event.y() - self.margin) / board_height)
        if rank < 0:
            rank = 0

        if file < 0:
            file = 0

        if file > 7:
            file = 7

        if rank > 7:
            rank = 7

        self.square = chess.square(file, rank)
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
                # self.current_game = self.current_game.add_variation(move)
                # print('Move: {0}'.format(move))
                evt = {"Move": move}

                self.parent(evt)

                self.moveFromSquare = move.from_square
                self.moveToSquare = move.to_square

                piece = None
                ply = None
                # print("MADE move: {}".format(move))

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
                                             check=check, coordinates=False)
        self.svgChessboardEncoded = self.svgChessboard.encode("utf-8")
        self.svgWidget.load(self.svgChessboardEncoded)

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(10, 10)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.svgWidget.resize(new_size*0.95)


