"""
Docstring.
"""
import pgn
import chess
import itertools

from PyQt5.QtWidgets import QTextBrowser
from PyQt5 import QtGui
from utilities import BidirectionalListener

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3


class DisplayExporter(pgn.BaseVisitor):
    """
    Allows exporting a game in a viewer friendly screen format
    """

    def __init__(self, columns=80, headers=True, comments=True, variations=True):
        self.columns = columns
        self.headers = headers
        self.comments = comments
        self.variations = variations

        self.found_headers = False
        self.force_movenumber = True

        self.lines = []
        self.current_line = ""
        self.variation_depth = 0
        self.header_map = {}
        # pgn.Game.positions = {}

    def flush_current_line(self):
        if self.current_line:
            self.lines.append(self.current_line.rstrip())
        self.current_line = ""

    def write_token(self, token):
        if self.columns is not None and self.columns - len(self.current_line) < len(token):
            self.flush_current_line()
        if self.variation_depth == 0:
            self.current_line += "<span style =\" color:darkblue;\" font-weight=\"bold;\">"
        self.current_line += token
        if self.variation_depth == 0:
            self.current_line += "</span>"

    def write_line(self, line=""):
        self.flush_current_line()
        self.lines.append(line.rstrip())

    def end_game(self):
        self.write_line()

    def begin_headers(self):
        self.found_headers = False

    def visit_header(self, tagname, tagvalue):
        if self.headers:
            self.found_headers = True
            # self.write_line("{0} \"{1}\"<br>".format(tagname, tagvalue))
            self.header_map[tagname] = tagvalue

    def end_headers(self):
        if self.found_headers:
            self.write_line()
        # print(self.headers)
        #     print(self.header_map)
        #     self.write_token(str(self.header_map))
            for k,v in self.header_map.items():
                self.write_token("<span style =\" color:darkgreen;\" font-weight=\"bold;\">{0}:  {1}<br></span>".format(k,v))
            self.write_token("<br>")

        # Open file - File may not exist, File might be corrupt
        # Look for string in file - String may not exist
        # Based on string, do some action, action may fail

    def begin_variation(self):
        self.variation_depth += 1

        if self.variations:
            self.write_token("( ")
            self.force_movenumber = True

    def end_variation(self):
        self.variation_depth -= 1

        if self.variations:
            self.write_token(") ")
            self.force_movenumber = True

    def visit_comment(self, comment):
        if self.comments and (self.variations or not self.variation_depth):
            self.write_token("{ " + comment.replace("}", "").strip() + " } ")
            self.force_movenumber = True

    def visit_nag(self, nag):
        if self.comments and (self.variations or not self.variation_depth):
            self.write_token("$" + str(nag) + " ")

    def visit_move(self, board, move):
        if self.variations or not self.variation_depth:
            # Write the move number.
            if board.turn == chess.WHITE:
                self.write_token(str(board.fullmove_number) + ". ")
            elif self.force_movenumber:
                self.write_token(str(board.fullmove_number) + "... ")

            # tmp_board = board(board.fen(b))
            # tmp_board.make

            # tmp_board = board(F)
            # Write the SAN.
            # self.write_token("<a id =\"{}\">".format(move))

            tmp_board = board.copy()
            tmp_board.push(move)
            # pgn.Game.positions[str(tmp_board.fen())] = self

            self.write_token("<a href=\"{}\" id =\"{}\"> {} </a>".format(tmp_board.fen(), move, board.san(move) + " "))
            self.force_movenumber = False

    def visit_result(self, result):
        self.write_token(result + " ")

    def result(self):
        if self.current_line:
            return "\n".join(itertools.chain(self.lines, [self.current_line.rstrip()])).rstrip()
        else:
            return "\n".join(self.lines).rstrip()

    def __str__(self):
        return self.result()


class ChessGameWidget(BidirectionalListener, QTextBrowser):
    """
    Docstring.
    """
    def __init__(self, dock, parent):
        """
        Docstring.
        """
        super(ChessGameWidget, self).__init__()

        self.parent = parent

        self.game = pgn.Game()
        self.currentGame = self.game
        self.setReadOnly = False
        # print(dir(QTextBrowser))
        self.anchorClicked.connect(self.anchor_was_clicked)
        self.setOpenLinks(False)

        # self.html = True

    def anchor_was_clicked(self, fen):
        # print(dir(fen))
        print("Anchor was clicked, fen : {}".format(fen.url()))
        # board = self.
        # fen = str(fen)
        self.go_to_fen(fen.url())

        # print(pgn.Game.positions[fen.url()])
        # print(self.exporter.positions[fen.url()])

    # self.currentGame.add_variation(move)
    def add_try_variation(self, move):
        for v in self.currentGame.variations:
            # print("variations: {}".format(v))
            # print("move: {}".format(move))
            # print("existing move: {}".format(v.move))

            if v.move == move:
                return v

        return self.currentGame.add_variation(move)

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """
        if event["Origin"] is not self.__class__:
            if "Move" in event:
                move = event["Move"]
                self.currentGame = self.add_try_variation(move)
                self.updatePgn()
            elif "SAN" in event:
                san = event["SAN"]
                move = self.currentGame.board().parse_san(san)
                print("move: {}".format(move))
                self.currentGame = self.add_try_variation(move)
                self.updatePgn()
                self.parent({"Fen": self.currentGame.board().fen(), "Origin": self.__class__})
            elif "Action" in event:
                if event["Action"] == "Go_To_Start":
                    # print("got Undo")
                    self.go_to_start()
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

                elif event["Action"] == "Go_To_End":
                    # print("got Undo")
                    self.go_to_end()
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

                elif event["Action"] == "Undo":
                    # print("got Undo")
                    self.undo()
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

                elif event["Action"] == "Refresh":
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

                elif event["Action"] == "Load Game":
                    pgn_game = StringIO(event["PGN"][0])
                    self.game = pgn.read_game(pgn_game)
                    self.updatePgn()
                    self.currentGame = self.game

                elif event["Action"] == "Forward":
                    self.forward()
                    board = self.currentGame.board()
                    self.parent({"Fen": board.fen(), "Origin": self.__class__})

            elif "Book_File" in event:
                print("Got Book_File event!")
                board = self.currentGame.board()
                self.parent({"Fen": board.fen(), "Origin": self.__class__})

    def updatePgn(self):
        self.exporter = DisplayExporter(headers=True, variations=True, comments=True)
        pgn_string = self.game.accept(self.exporter)
        # print("pgn after operation: {}".format(pgn_string))
        self.setHtml(pgn_string)
        self.moveCursor(QtGui.QTextCursor.End)

    def undo(self):
        if self.currentGame.parent:
            self.currentGame = self.currentGame.parent
            self.updatePgn()

    def forward(self):
        if self.currentGame.variations:
            self.currentGame = self.currentGame.variations[0]
            # print("type currentGame: {}".format(type(self.currentGame)))

            self.updatePgn()

    def go_to_start(self):
        while self.currentGame.parent:
            self.currentGame = self.currentGame.parent
        self.updatePgn()

    def go_to_fen(self, fen):
        # print(self.exporter.positions)
        # print("fen: {}".format(fen))
        # if fen in self.exporter.positions:
        # print("fen found: {}".format(pgn.Game.positions[fen]))

        self.currentGame = pgn.Game.positions[fen]
        # print("type currentGame: {}".format(type(self.currentGame)))
        board = self.currentGame.board()
        self.parent({"Fen": board.fen(), "Origin": self.__class__})

        self.updatePgn()

        # self.currentGame = self.

    def go_to_end(self):
        while self.currentGame.variations:
            self.currentGame = self.currentGame.variations[0]
        self.updatePgn()


