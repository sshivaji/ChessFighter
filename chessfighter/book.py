"""
Docstring.
"""
import chess
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtGui, QtCore
from utilities import BidirectionalListener
import utilities

MOVE_COLUMN = "move"

CHESSDB_EXEC = '../external/parser'
MILLIONBASE_PGN = '../bases/millionbase.pgn'


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

    def cell_was_clicked(self, row, column):
        item = self.item(row, column)

        if column == self.headers.index(MOVE_COLUMN):
            pieceEvent = {"SAN": item.text(), "Origin": self.__class__}
            self.parent(pieceEvent)

    def query_db(self, fen, limit=100, skip=0):
        records = []
        # selecting DB happens now
        try:
            self.chessDB.open(MILLIONBASE_PGN)
            results = self.chessDB.find(fen, limit=limit, skip=skip)
            board = chess.Board(fen)
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
            if "Fen" in event:
                #Process
                fen = event["Fen"]
                print("Book_Fen: {}".format(event["Fen"]))
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

