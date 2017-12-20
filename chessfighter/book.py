"""
Docstring.
"""
import chess
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtGui
from external import chess_db
from utilities import BidirectionalListener

CHESSDB_EXEC = '../external/parser'
MILLIONBASE_PGN = '../bases/millionbase.pgn'

class OpeningBookWidget(BidirectionalListener, QTableWidget):
    """
    Docstring.
    """
    def __init__(self, dock, parent):
        """
        Docstring.
        """
        super(OpeningBookWidget, self).__init__()
        self.parent = parent
        self.chessDB = chess_db.Parser(CHESSDB_EXEC)

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
                    (m['wins'] + m['draws'] * 0.5) * 100.0 / (m['wins'] + m['draws'] + m['losses'])), 'freq': m['games'],
                          'wins': m['wins'],
                          'draws': m['draws'], 'losses': m['losses'], 'games': int(m['games']),
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
                print("Fen: {}".format(event["Fen"]))
                results = self.query_db(fen, limit=1)
                # print("results: {}".format(results))
                self.setRowCount(5)
                self.setColumnCount(5)

                headers = ["move", "freq", "pct", "draws", "games"]
                self.setHorizontalHeaderLabels(headers)

                for i, r in enumerate(results):
                    for j, h in enumerate(headers):
                        # print(r[h])
                        self.setItem(i, j, QTableWidgetItem(str(r[h])))
                    if i>3:
                        break

