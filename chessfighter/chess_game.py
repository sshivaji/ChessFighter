from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
        QFileDialog, QListWidget, QMainWindow, QMessageBox, QTextEdit)
import utilities
import chess


class ChessGameWidget(utilities.BidirectionalListener, QListWidget):
    def __init__(self, dock, parent):
        """
        Docstring.
        """
        super().__init__()
        self.parent = parent
        self.game = chess.pgn.Game()
        self.current_game = self.game

    def process_event(self, e):
        # print("event: {}".format(e))
        if e['Move']:
            move = e['Move']
        self.current_game = self.current_game.add_variation(move)
        self.addItem(str(move))