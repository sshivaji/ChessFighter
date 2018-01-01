"""
Docstring.
"""
import chess
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTableView
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import QAbstractTableModel, QModelIndex
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from utilities import BidirectionalListener

CHESSDB_EXEC = '../external/parser'
MILLIONBASE_PGN = '../bases/millionbase.pgn'


class DatabaseWidget(QDockWidget, BidirectionalListener):
    """
    Docstring.
    """
    def __init__(self, title, parent_widget, parent, db=None):
        """
        Docstring.
        """
        super(DatabaseWidget, self).__init__(title, parent_widget)

        self.parent = parent
        self.setMinimumSize(300, 150)
        self.view = QTableView()
        self.view.setSortingEnabled(True)
        self.view.clicked.connect(self.cell_was_clicked)
        self.tableData = DatabaseModel(db)

        self.view.setModel(self.tableData)
        self.setWidget(self.view)

    def cell_was_clicked(self, clickedIndex):
        row = clickedIndex.row()
        model = clickedIndex.model()
        # print("load game offset {}".format(model.results[row][-1]))
        offset = int(model.results[row][-1])
        # print(self.tableData.chessDB.get_games([offset]))
        self.parent({"Action": "Load Game", "PGN": self.tableData.chessDB.get_games([offset]), "Origin": self.__class__})

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """
        if event["Origin"] is not self.__class__:
            if "Fen" in event:
                self.tableData.reset()
                fen = event["Fen"]
                self.tableData.populate_games(fen)
                self.tableData.more = True


class DatabaseModel(QAbstractTableModel):
    ROW_BATCH_COUNT = 50

    def __init__(self, db):
        super(DatabaseModel, self).__init__()
        self.headers = ["White", "WhiteElo", "Black", "BlackElo", "Result", "Event", "Site", "Date", "Round", "id"]

        self.rowsLoaded = DatabaseModel.ROW_BATCH_COUNT
        self.chessDB = db
        self.more = True
        self.reset()

    def reset(self):
        self.results = []
        self.skip = 0
        self.limit = DatabaseModel.ROW_BATCH_COUNT

    def populate_games(self, fen, skip=0, limit=ROW_BATCH_COUNT):
        results = self.get_games(fen, skip=skip, limit=limit)
        for i, r in enumerate(results["records"]):
            row = []
            for j, h in enumerate(self.headers):
                try:
                    value = str(r[h])
                except:
                    value = '*'
                row.append(value)
            # print("row: {}".format(row))
            self.addResult(row)
        # self.more = False

    def rowCount(self, index=QModelIndex()):
        if not self.results:
            return 0

        return len(self.results)

    def canFetchMore(self, index=QModelIndex()):
        if len(self.results) < DatabaseModel.ROW_BATCH_COUNT:
            return False
        return True

    def fetchMore(self, index=QModelIndex()):
        # reminder = len(self.results) - self.rowsLoaded
        # itemsToFetch = min(reminder, DatabaseModel.ROW_BATCH_COUNT)

        itemsToFetch = DatabaseModel.ROW_BATCH_COUNT
        self.skip += itemsToFetch
        print("Loading {0} more results, total loaded: {1}".format(itemsToFetch, self.skip))
        self.beginInsertRows(QModelIndex(), self.skip, self.skip + itemsToFetch)
        self.populate_games(self.fen, skip=self.skip, limit=itemsToFetch)

        # self.rowsLoaded += itemsToFetch
        self.endInsertRows()

    def addResult(self, result):
        self.beginResetModel()
        self.results.append(result)
        self.endResetModel()

    def columnCount(self, index=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        col = index.column()
        result = self.results[index.row()]
        if role == Qt.DisplayRole:
            return QVariant(result[col])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return QVariant(self.headers[section])
        return QVariant(int(section + 1))

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

                record = {'move': m['san'],
                          'pct': "{0:.2f}".format(
                            (m['wins'] + m['draws'] * 0.5) * 100.0 / (m['wins'] + m['draws'] + m['losses'])),
                          'freq': m['games'],
                          'wins': m['wins'],
                          'draws': m['draws'], 'losses': m['losses'], 'games': int(m['games']),
                          'pgn offsets': m['pgn offsets']}
                records.append(record)
            return records
        except:
            print("Error loading DB")
            return records

    def get_games(self, fen, skip=0, limit=ROW_BATCH_COUNT):
        self.fen = fen
        records = self.query_db(fen, skip=skip, limit=limit)
        # Reverse sort by the number of games and select the top 5 moves, for a balanced representation of the games
        records.sort(key=lambda x: x['games'], reverse=True)
        # For reporting purposes
        total_result_count = sum(r['games'] for r in records)
        filtered_records = records[:5]
        filtered_game_offsets = []
        # for r in records:
        #     total_result_count += r['games']
        for r in filtered_records:
            for skip in r['pgn offsets']:
                # print("offset: {0}".format(offset))
                if len(filtered_game_offsets) >= limit:
                    break
                filtered_game_offsets.append(skip)
                # else:
                #     break
                # total_result_count += 1

        # print("filtered_game_offset count : {0}".format(len(filtered_game_offsets)))
        headers = self.chessDB.get_game_headers(self.chessDB.get_games(filtered_game_offsets))
        for skip, h in zip(filtered_game_offsets, headers):
            # Should be sent as ID for front end accounting purposes, in an odd way, the offset is the game id,
            # as its the unique way to access the game
            h["id"] = skip
        results = {"records": headers, "queryRecordCount": total_result_count,
                   "totalRecordCount": total_result_count}
        return results
