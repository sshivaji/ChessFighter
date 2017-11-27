#! /usr/bin/env python

"""
This module is the execution point of the chess GUI application named
Chess Fighter.
"""

import sys

import chess
import chess.svg

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

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

        self.widgetSvg = QSvgWidget()
        # self.widgetSvg.setGeometry(0, 0, 600, 600)

        self.horizontalGroupBox = QGroupBox("Chess Fighter")
        layout = QGridLayout()

        self.widgetSvg.mouseReleaseEvent = self.boardMousePressEvent

        layout.addWidget(self.widgetSvg, 0, 0, 4, 4)
        layout.addWidget(QPushButton('Board Controls'), 5, 1)
        layout.addWidget(QPushButton('Database/Engine Tab'), 6, 1)
        layout.addWidget(QPushButton('Header'), 0, 4)
        layout.addWidget(QPushButton('Game PGN'), 1, 4)

        self.horizontalGroupBox.setLayout(layout)
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.margin = 0
        self.pieceToMove = [None, None]

        self.square = -10
        self.moveFromSquare = -10
        self.moveToSquare = -10

        self.board = chess.Board()
        self.drawBoard()

    def boardMousePressEvent(self, event):
        """
        Handles left mouse clicks and enables moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        board_width = self.widgetSvg.width()/8
        board_height = self.widgetSvg.height()/8

        file = int((event.x() - self.margin) / board_width)
        rank = 7 - int((event.y() - self.margin) / board_height)

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
                                   check=check, coordinates=False)
        boardSvgEncoded = boardSvg.encode("utf-8")
        self.widgetSvg.load(boardSvgEncoded)


def main():
    """Makes the script to be executed."""
    chessFighter = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    chessFighter.exec()


if __name__ == "__main__":
    main()
