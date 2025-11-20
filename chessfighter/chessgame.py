"""
Docstring.
"""
import pgn
import chess
import itertools

from PyQt5.QtWidgets import QTextBrowser, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from utilities import BidirectionalListener
import utilities as util

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3


class DisplayExporter(pgn.BaseVisitor):
    """
    Allows exporting a game in a viewer friendly screen format
    """

    def __init__(self, columns=80, headers=True, comments=True, variations=True, currentGame=None):
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
        self.currentGame = currentGame
        # pgn.Game.positions = {}

    def flush_current_line(self):
        if self.current_line:
            self.lines.append(self.current_line.rstrip())
        self.current_line = ""

    def write_token(self, token):
        if self.columns is not None and self.columns - len(self.current_line) < len(token):
            self.flush_current_line()

        # Style based on variation depth
        if self.variation_depth == 0:
            # Main line: dark blue and bold
            self.current_line += "<span style=\"color:darkblue; font-weight:bold;\">"
        elif self.variation_depth == 1:
            # First level variation: dark gray and italic
            self.current_line += "<span style=\"color:#666; font-style:italic; font-size:95%;\">"
        else:
            # Deeper variations: lighter gray and smaller
            self.current_line += "<span style=\"color:#999; font-style:italic; font-size:90%;\">"

        self.current_line += token
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
            # Add line break and indentation for better readability
            if self.variation_depth == 1:
                self.write_line()
                self.current_line = "&nbsp;&nbsp;&nbsp;&nbsp;"  # Indentation
            self.write_token("( ")
            self.force_movenumber = True

    def end_variation(self):
        self.variation_depth -= 1

        if self.variations:
            self.write_token(") ")
            self.force_movenumber = True
            # Add line break after first-level variations
            if self.variation_depth == 0:
                self.write_line()

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
            if tmp_board.fen() == self.currentGame.board().fen():
                # self.write_line("<br>")
                self.write_token(
                    "<a href=\"{}\" style=\" background-color: #FFFF00; text-decoration:none;\" id =\"{}\"> {} </a>".format(tmp_board.fen(), move,
                                                                                                 util.figurizine(
                                                                                                     board.san(
                                                                                                         move)) + " "))
                # self.write_line("<br>")

            else:
                self.write_token("<a href=\"{}\" style=\" text-decoration:none;\" id =\"{}\"> {} </a>".format(tmp_board.fen(), move,
                                                                         util.figurizine(board.san(move)) + " "))
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
        # self.setDefaultStyleSheet("a{ text-decoration: none; }")
        # print(dir(self))
        self.setAcceptRichText(True)
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
        self.exporter = DisplayExporter(headers=True, variations=True, comments=True, currentGame=self.currentGame)
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

    def get_current_variations(self):
        """Get list of available variations at current position"""
        return self.currentGame.variations if self.currentGame else []


class ChessGameWithVariationPicker(QWidget, BidirectionalListener):
    """
    Wrapper widget that adds a variation picker UI to the chess game widget
    """
    def __init__(self, dock, parent):
        super(ChessGameWithVariationPicker, self).__init__()
        self.parent_callback = parent

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Variation picker panel (initially hidden)
        self.variation_panel = QWidget()
        variation_layout = QHBoxLayout()
        variation_layout.setContentsMargins(5, 5, 5, 5)

        self.variation_label = QLabel("Variations:")
        self.variation_combo = QComboBox()
        self.variation_combo.currentIndexChanged.connect(self.on_variation_selected)

        self.show_main_btn = QPushButton("Main Line")
        self.show_main_btn.clicked.connect(self.select_main_line)
        self.show_main_btn.setMaximumWidth(80)

        variation_layout.addWidget(self.variation_label)
        variation_layout.addWidget(self.variation_combo, 1)
        variation_layout.addWidget(self.show_main_btn)

        self.variation_panel.setLayout(variation_layout)
        self.variation_panel.setVisible(False)

        # Chess game widget
        self.game_widget = ChessGameWidget(dock, self.forward_event)

        # Add to main layout
        main_layout.addWidget(self.variation_panel)
        main_layout.addWidget(self.game_widget, 1)

        self.setLayout(main_layout)

    def forward_event(self, event):
        """Forward events from game widget to parent and update variation picker"""
        self.update_variation_picker()
        self.parent_callback(event)

    def update_variation_picker(self):
        """Update the variation picker based on current position"""
        variations = self.game_widget.get_current_variations()

        if len(variations) > 1:
            # Multiple variations available - show picker
            self.variation_combo.blockSignals(True)
            self.variation_combo.clear()

            for i, var in enumerate(variations):
                move = var.move
                board = self.game_widget.currentGame.board()
                san = util.figurizine(board.san(move))
                self.variation_combo.addItem(f"Variation {i+1}: {san}")

            self.variation_combo.blockSignals(False)
            self.variation_panel.setVisible(True)
        else:
            # No variations or only one - hide picker
            self.variation_panel.setVisible(False)

    def on_variation_selected(self, index):
        """Handle variation selection from combo box"""
        if index >= 0:
            variations = self.game_widget.get_current_variations()
            if index < len(variations):
                self.game_widget.currentGame = variations[index]
                self.game_widget.updatePgn()
                board = self.game_widget.currentGame.board()
                self.parent_callback({"Fen": board.fen(), "Origin": ChessGameWidget})

    def select_main_line(self):
        """Select the main line (first variation)"""
        variations = self.game_widget.get_current_variations()
        if variations:
            self.variation_combo.setCurrentIndex(0)
            self.on_variation_selected(0)

    def processEvent(self, event):
        """Forward events to the game widget"""
        self.game_widget.processEvent(event)
        self.update_variation_picker()


