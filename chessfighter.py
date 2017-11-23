#! /usr/bin/env python

"""
This module is the execution point of the chess GUI application named
Chess Fighter.
"""

import sys

import chess
import chess.svg

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget


class MainWindow(QWidget):
    """
    Creates a surface for the chessboard.
    """
    def __init__(self):
        """
        Initializes the chessboard.
        """
        super().__init__()

        self.setWindowTitle("Chess GUI")
        self.setGeometry(300, 300, 800, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 600, 600)

        self.boardSize = min(self.widgetSvg.width(),
                             self.widgetSvg.height())
        self.margin = 0.05 * self.boardSize
        self.squareSize = (self.boardSize - 2 * self.margin) / 8
        self.pieceToMove = [None, None]

        self.square = -10
        self.moveFromSquare = -10
        self.moveToSquare = -10

        self.board = chess.Board()
        self.drawBoard()

    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        """
        Handles left mouse clicks and enables moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        if event.x() <= self.boardSize and event.y() <= self.boardSize:

            if event.buttons() == Qt.LeftButton:

                if self.margin < event.x() < self.boardSize - self.margin and self.margin < event.y() < self.boardSize - self.margin:
                    file = int((event.x() - self.margin) / self.squareSize)
                    rank = 7 - int((event.y() - self.margin) / self.squareSize)
                    self.square = chess.square(file, rank)
                    piece = self.board.piece_at(self.square)

                    fileCharacter = chr(file + 97)
                    rankNumber = str(rank + 1)
                    ply = "{}{}".format(fileCharacter,
                                        rankNumber)

                    if self.pieceToMove[0]:
                        move = chess.Move.from_uci("{}{}".format(self.pieceToMove[1],
                                                                 ply))

                        if move in self.board.legal_moves:
                            self.board.push(move)

                            self.moveFromSquare = move.from_square
                            self.moveToSquare = move.to_square

                            piece = None
                            ply = None

                    self.pieceToMove = [piece, ply]
                    self.drawBoard()

    def drawBoard(self):
        """
        Draws a chessboard with the starting position and then redraws
        it for every new move. Also draws a circle for a clicked square
        and an arrow to indicate the move that was last made.
        """
        check = self.board.king(self.board.turn) if self.board.is_check() else None
        boardSvg = chess.svg.board(board=self.board,
                                   arrows=[(self.square, self.square),
                                           (self.moveFromSquare, self.moveToSquare)],
                                   check=check)
        boardSvgEncoded = boardSvg.encode("utf-8")
        drawBoardSvg = self.widgetSvg.load(boardSvgEncoded)

        return drawBoardSvg


if __name__ == "__main__":
    chessTitan = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    chessTitan.exec()
