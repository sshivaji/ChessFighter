#! /usr/bin/env python

"""
This module is the execution point of the chess GUI application named
Chess Fighter.
"""

import sys
from PyQt5 import QtGui, QtCore

import chess
import chess.pgn
import chess.svg

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QFrame, QLabel, QLayout,
        QTextBrowser, QWidget, QWidgetItem)
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout


class ItemWrapper(object):
    def __init__(self, i, p):
        self.item = i
        self.position = p


class BorderLayout(QLayout):
    West, North, South, East, Center = range(5)
    MinimumSize, SizeHint = range(2)

    def __init__(self, parent=None, margin=None, spacing=-1):
        super(BorderLayout, self).__init__(parent)

        if margin is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.list = []

    def __del__(self):
        l = self.takeAt(0)
        while l is not None:
            l = self.takeAt(0)

    def addItem(self, item):
        self.add(item, self.West)

    def addWidget(self, widget, position):
        self.add(QWidgetItem(widget), position)

    def expandingDirections(self):
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self):
        return False

    def count(self):
        return len(self.list)

    def itemAt(self, index):
        if index < len(self.list):
            return self.list[index].item

        return None

    def minimumSize(self):
        return self.calculateSize(self.MinimumSize)

    def setGeometry(self, rect):
        center = None
        eastWidth = 0
        westWidth = 0
        northHeight = 0
        southHeight = 0
        centerHeight = 0

        super(BorderLayout, self).setGeometry(rect)

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.North:
                item.setGeometry(QRect(rect.x(), northHeight,
                        rect.width(), item.sizeHint().height()))

                northHeight += item.geometry().height() + self.spacing()

            elif position == self.South:
                item.setGeometry(QRect(item.geometry().x(),
                        item.geometry().y(), rect.width(),
                        item.sizeHint().height()))

                southHeight += item.geometry().height() + self.spacing()

                item.setGeometry(QRect(rect.x(),
                        rect.y() + rect.height() - southHeight + self.spacing(),
                        item.geometry().width(), item.geometry().height()))

            elif position == self.Center:
                center = wrapper

        centerHeight = rect.height() - northHeight - southHeight

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.West:
                item.setGeometry(QRect(rect.x() + westWidth,
                        northHeight, item.sizeHint().width(), centerHeight))

                westWidth += item.geometry().width() + self.spacing()

            elif position == self.East:
                item.setGeometry(QRect(item.geometry().x(),
                        item.geometry().y(), item.sizeHint().width(),
                        centerHeight))

                eastWidth += item.geometry().width() + self.spacing()

                item.setGeometry(QRect(rect.x() + rect.width() - eastWidth + self.spacing(),
                        northHeight, item.geometry().width(),
                        item.geometry().height()))

        if center:
            center.item.setGeometry(QRect(westWidth, northHeight,
                    rect.width() - eastWidth - westWidth, centerHeight))

    def sizeHint(self):
        return self.calculateSize(self.SizeHint)

    def takeAt(self, index):
        if index >= 0 and index < len(self.list):
            layoutStruct = self.list.pop(index)
            return layoutStruct.item

        return None

    def add(self, item, position):
        self.list.append(ItemWrapper(item, position))

    def calculateSize(self, sizeType):
        totalSize = QSize()

        for wrapper in self.list:
            position = wrapper.position
            itemSize = QSize()

            if sizeType == self.MinimumSize:
                itemSize = wrapper.item.minimumSize()
            else: # sizeType == self.SizeHint
                itemSize = wrapper.item.sizeHint()

            if position in (self.North, self.South, self.Center):
                totalSize.setHeight(totalSize.height() + itemSize.height())

            if position in (self.West, self.East, self.Center):
                totalSize.setWidth(totalSize.width() + itemSize.width())

        return totalSize


class ChessBoardWidget(QSvgWidget):
    # Chessboard resize should always be a square
    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(10, 10)
        new_size.scale(event.size(), QtCore.Qt.KeepAspectRatio)
        self.resize(new_size)


class MainWindow(QWidget):
    """
    Creates a surface for the chessboard.
    """
    def __init__(self):
        """
        Initializes the chessboard.
        """
        super(MainWindow, self).__init__()
        self.widgetSvg = ChessBoardWidget()

        layout = BorderLayout()
        layout.addWidget(self.widgetSvg, BorderLayout.Center)

        # Because BorderLayout doesn't call its super-class addWidget() it
        # doesn't take ownership of the widgets until setLayout() is called.
        # Therefore we keep a local reference to each label to prevent it being
        # garbage collected too soon.

        label_n = self.createLabel("Controls")
        layout.addWidget(label_n, BorderLayout.North)

        self.game_pgn = QTextBrowser()
        layout.addWidget(self.game_pgn, BorderLayout.East)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        # self.tabs.resize(300, 300)
        # self.tabs.setTabBar(self.tab_bar)

        # Add tabs
        self.tabs.addTab(self.tab1, "Database")
        self.tabs.addTab(self.tab2, "Book")
        self.tabs.addTab(self.tab3, "Engine")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("Database")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)

        # self.label_database = self.createLabel("Database")
        layout.addWidget(self.tabs, BorderLayout.South)

        self.setLayout(layout)
        self.setWindowTitle("Chess Fighter")


        # Action Handlers
        self.widgetSvg.mouseReleaseEvent = self.boardMousePressEvent

        self.margin = 0

        self.pieceToMove = [None, None]
        self.square = -10
        self.moveFromSquare = -10
        self.moveToSquare = -10

        self.game = chess.pgn.Game()
        self.current_game = self.game
        self.board = chess.Board()
        self.drawBoard()

    def createLabel(self, text):
        label = QLabel(text)
        label.setFrameStyle(QFrame.Box | QFrame.Raised)

        return label

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
                self.current_game = self.current_game.add_variation(move)

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

        # New chess position, update other widgets
        self.updateWidgets()

    def updateWidgets(self):
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        pgn_string = self.game.accept(exporter)
        self.game_pgn.setText(pgn_string)
        self.game_pgn.moveCursor(QtGui.QTextCursor.End)


def main():
    """Makes the script to be executed."""
    chessFighter = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    chessFighter.exec()


if __name__ == "__main__":
    main()
