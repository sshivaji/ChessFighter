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
        self.headers = [MOVE_COLUMN, "pct", "score", "draws", "games"]
        self.filename = MILLIONBASE_PGN

    def cell_was_clicked(self, row, column):
        item = self.item(row, column)

        if column == self.headers.index(MOVE_COLUMN):
            self.parent({"SAN": utilities.figurizine(item.text(), reverse=True), "Origin": self.__class__})

    def query_ctg_db(self, fen, limit=100, skip=0):
        records = []
        # selecting DB happens now
        try:
            c = CTGReader(CHESS_CTG_READER)
            c.open(self.filename)
            results = c.find(fen)
            board = chess.Board(fen)
            for m in results['moves']:
                m['san'] = board.san(chess.Move.from_uci(m['move']))
                total = m['wins'] + m['draws'] + m['losses']

                record = {'move': utilities.figurizine(m['san']),
                          'score': utilities.num_fmt(m['wins'] - m['losses']),
                          'losses': utilities.num_fmt(m['losses']),
                          'games': utilities.num_fmt(total)}
                if total > 0:
                    record['pct'] = "{0:.1f}%".format((m['wins'] + m['draws'] * 0.5) * 100.0 / total)
                    record['draws'] = "{}%".format(utilities.num_fmt(m['draws'] / total * 100.0))

                else:
                    record['pct'] = 'N/A'
                    record['draws'] = 'N/A'

                records.append(record)
            return records
        except:
            print("Error loading DB")
            return records

    def query_db(self, fen, limit=100, skip=0):
        records = []
        # selecting DB happens now
        try:
            self.chessDB.open(self.filename)
            results = self.chessDB.find(fen, limit=limit, skip=skip)
            board = chess.Board(fen)
            # print(results)
            for m in results['moves']:
                m['san'] = board.san(chess.Move.from_uci(m['move']))
                total = m['wins'] + m['draws'] + m['losses']

                record = {'move': utilities.figurizine(m['san']),
                          'score': utilities.num_fmt(m['wins'] - m['losses']),
                          'losses': utilities.num_fmt(m['losses']),
                          'games': utilities.num_fmt(m['games']),
                          'pgn offsets': m['pgn offsets']}
                if total > 0:
                    record['pct']= "{0:.1f}%".format((m['wins'] + m['draws'] * 0.5) * 100.0 / total)
                    record['draws'] = "{}%".format(utilities.num_fmt(m['draws'] / total * 100.0))
                else:
                    record['pct'] = 'N/A'
                    record['draws'] = 'N/A'

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
                # print("event: {}".format(event))
                self.filename = event["Book_File"]

            if "Fen" or "Book_File" in event:
                print("event: {}".format(event))
                if "Fen" in event:
                    self.fen = event["Fen"]
                print("Book_Fen: {}".format(self.fen))
                # print("filename: {}".format(self.filename))
                if self.filename.endswith('ctg'):
                    print("loading CTG FEN")
                    results = self.query_ctg_db(self.fen, limit=1)
                else:
                    # print("loading norm")
                    results = self.query_db(self.fen, limit=1)
                # print("results: {}".format(results))
                self.setRowCount(10)
                self.setColumnCount(len(self.headers))
                self.clear()

                self.setHorizontalHeaderLabels(self.headers)

                for i, r in enumerate(results):
                    for j, h in enumerate(self.headers):
                        # print(r[h])
                        item = QTableWidgetItem(str(r[h]))
                        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        self.setItem(i, j, item)
                    if i > 10:
                        break

