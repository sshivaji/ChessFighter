"""
Docstring.
"""
import chess
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtGui
from utilities import BidirectionalListener

CHESSDB_EXEC = '../external/parser'
MILLIONBASE_PGN = '../bases/millionbase.pgn'


class DatabaseWidget(BidirectionalListener, QTableWidget):
    """
    Docstring.
    """
    def __init__(self, dock, parent, db=None):
        """
        Docstring.
        """
        super(DatabaseWidget, self).__init__()
        self.parent = parent
        self.chessDB = db
        self.setMinimumSize(300, 150)
        self.setSortingEnabled(True)


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

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """
        if event["Origin"] is not self.__class__:
            # print("Book: {}".format(event))
            if "Fen" in event:
                fen = event["Fen"]
                results = self.get_games(fen)

                headers = ["White", "WhiteElo", "Black", "BlackElo", "Result", "Event", "Site", "Date", "Round"]
                self.setColumnCount(len(headers))
                self.setRowCount(len(results["records"]))

                self.setHorizontalHeaderLabels(headers)
                self.verticalHeader().setVisible(False)
                # self.setVerticalHeaderLabels(None)

                for i, r in enumerate(results["records"]):
                    # print("row:")
                    # print(r)
                    for j, h in enumerate(headers):
                        # print(r[h])
                        try:
                            value = str(r[h])
                        except:
                            value = '*'
                        self.setItem(i, j, QTableWidgetItem(value))
                    # if i>3:
                    #     break

    def get_games(self, fen, offset=0, perPage=20):
        # offset = 0
        # perPage = 20
        # perPage = 20 & page = 2 & offset = 20
        # perPage = self.get_argument("perPage", default=10)
        # perPage = int(perPage)
        # # page = self.get_argument("page", default=1)
        # offset = self.get_argument("offset", default=0)
        # offset = int(offset)
        #
        # print("perPage: {0}, offset: {1}".format(perPage, offset))
        # convert to skip and limit logic
        # offset = skip
        # limit = perPage
        records = self.query_db(fen, skip=offset, limit=perPage)
        # Reverse sort by the number of games and select the top 5, for a balanced representation of the games
        records.sort(key=lambda x: x['games'], reverse=True)
        # For reporting purposes
        total_result_count = sum(r['games'] for r in records)
        filtered_records = records[:5]
        filtered_game_offsets = []
        # Limit number of games to 10 for now
        # for r in records:
        #     total_result_count += r['games']
        for r in filtered_records:
            for offset in r['pgn offsets']:
                # print("offset: {0}".format(offset))
                if len(filtered_game_offsets) >= perPage:
                    break
                filtered_game_offsets.append(offset)
                # else:
                #     break
                # total_result_count += 1

        # print("filtered_game_offset count : {0}".format(len(filtered_game_offsets)))
        headers = self.chessDB.get_game_headers(self.chessDB.get_games(filtered_game_offsets))
        # print("offsets: ")
        # print(filtered_game_offsets)
        # print("headers: ")
        # for h in headers:
        #     print(h)
        # print("headers: {0}".format(headers))
        # tag the offset to each header
        for offset, h in zip(filtered_game_offsets, headers):
            # Should be sent as ID for front end accounting purposes, in an odd way, the offset is the game id,
            # as its the unique way to access the game
            h["id"] = offset
        results = {"records": headers, "queryRecordCount": total_result_count,
                   "totalRecordCount": total_result_count}
        return results

