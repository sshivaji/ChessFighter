"""
Docstring.
"""
import chess
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtGui, QtCore
from utilities import BidirectionalListener
import utilities
import json
from external.ctg_reader import CTGReader

MOVE_COLUMN = "move"

CHESSDB_EXEC = '../external/parser'
MILLIONBASE_PGN = '../bases/millionbase.pgn'

CHESS_CTG_READER = '../external/ctg_reader'


class OpeningBookWidget(BidirectionalListener, QTableWidget):
    """
    Docstring.
    """
    def __init__(self, dock, parent, db=None):
        """
        Docstring.
        """
        super(OpeningBookWidget, self).__init__()
        self.parent = parent
        self.chessDB = db
        self.setMinimumSize(500, 150)
        self.setSortingEnabled(True)
        self.cellClicked.connect(self.cell_was_clicked)
        self.headers = [MOVE_COLUMN, "freq", "pct", "draws", "games"]
        self.filename = MILLIONBASE_PGN

    def cell_was_clicked(self, row, column):
        item = self.item(row, column)

        if column == self.headers.index(MOVE_COLUMN):
            self.parent({"SAN": item.text(), "Origin": self.__class__})

    def query_ctg_db(self, fen, limit=100, skip=0):
        records = []
        # selecting DB happens now
        try:
            c = CTGReader(CHESS_CTG_READER)
            c.open(self.filename)
            results = c.find(fen)
            # self.chessDB.open(self.filename)
            # results = self.chessDB.find(fen, limit=limit, skip=skip)
            board = chess.Board(fen)
            # print(results)
            # print(results)
            for m in results['moves']:
                # print(m)
                # m = json.loads(m)
                # print(m)
                m['san'] = board.san(chess.Move.from_uci(m['move']))
                record = {'move': m['san'], 'pct': "{0:.2f}".format(
                    (m['wins'] + m['draws'] * 0.5) * 100.0 / (m['wins'] + m['draws'] + m['losses'])),
                          'freq': utilities.num_fmt(m['avg_games']),
                          'wins': utilities.num_fmt(m['wins']),
                          'draws': utilities.num_fmt(m['draws']),
                          'losses': utilities.num_fmt(m['losses']),
                          'games': utilities.num_fmt(m['avg_games'])}
                records.append(record)
            return records
        except:
            print("Error loading DB")
            # raise
            return records


    def query_db(self, fen, limit=100, skip=0):
        records = []
        # selecting DB happens now
        try:
            self.chessDB.open(self.filename)
            results = self.chessDB.find(fen, limit=limit, skip=skip)
            board = chess.Board(fen)
            print(results)
            for m in results['moves']:
                # print(m)
                m['san'] = board.san(chess.Move.from_uci(m['move']))
                record = {'move': m['san'], 'pct': "{0:.2f}".format(
                    (m['wins'] + m['draws'] * 0.5) * 100.0 / (m['wins'] + m['draws'] + m['losses'])),
                          'freq': utilities.num_fmt(m['games']),
                          'wins': utilities.num_fmt(m['wins']),
                          'draws': utilities.num_fmt(m['draws']),
                          'losses': utilities.num_fmt(m['losses']),
                          'games': utilities.num_fmt(m['games']),
                          'pgn offsets': m['pgn offsets']}
                records.append(record)
            return records
        except:
            print("Error loading DB")
            return records

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """
        if event["Origin"] is not self.__class__:
            # print("Book: {}".format(event))

            if "Book_File" in event:
                self.filename = event["Book_File"]

            if "Fen" in event:
                fen = event["Fen"]
                print("Book_Fen: {}".format(event["Fen"]))
                if self.filename.endswith('ctg'):
                    print("loading CTG FEN")
                    results = self.query_ctg_db(fen, limit=1)
                else:
                    # print("loading norm")
                    results = self.query_db(fen, limit=1)
                # print("results: {}".format(results))
                self.setRowCount(5)
                self.setColumnCount(5)
                self.clear()

                self.setHorizontalHeaderLabels(self.headers)

                for i, r in enumerate(results):
                    for j, h in enumerate(self.headers):
                        # print(r[h])
                        item = QTableWidgetItem(str(r[h]))
                        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        self.setItem(i, j, item)
                    if i>3:
                        break

