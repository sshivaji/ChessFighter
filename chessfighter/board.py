"""
Chessboard widget using chessground library in QWebEngineView.
"""
import chess
import chess.pgn
import json
import os

from PyQt5.QtCore import QUrl, pyqtSlot, QObject
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

from utilities import BidirectionalListener


class PyBridge(QObject):
    """
    Bridge object for JavaScript to Python communication.
    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    @pyqtSlot(str)
    def onMove(self, move_str):
        """Called from JavaScript when a move is made on the board."""
        self.parent.handleMoveFromJS(move_str)

    @pyqtSlot()
    def onBoardReady(self):
        """Called from JavaScript when the board is initialized."""
        print("Chessground board is ready")


class Chessboard(BidirectionalListener, QWebEngineView):
    """
    Chessboard widget using chessground library.
    """
    def __init__(self, parent):
        """
        Initialize the chessboard.
        """
        super(Chessboard, self).__init__()
        self.parent = parent

        self.moveFromSquare = -10
        self.moveToSquare = -10
        self.square = -10

        self.chessboard = chess.Board()

        # Set up web channel for JS-Python communication
        self.channel = QWebChannel()
        self.bridge = PyBridge(self)
        self.channel.registerObject('pybridge', self.bridge)
        self.page().setWebChannel(self.channel)

        # Enable web features
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        # Load the chessground HTML
        html_path = os.path.join(os.path.dirname(__file__), 'board_chessground.html')
        self.load(QUrl.fromLocalFile(html_path))

        # Wait for page to load before drawing
        self.loadFinished.connect(self.onLoadFinished)

    def onLoadFinished(self, ok):
        """Called when the web page finishes loading."""
        if ok:
            self.drawChessboard()

    def registerListener(self):
        """
        Register this widget as a listener.
        """
        return self.processEvent

    def processEvent(self, event):
        """
        Processes an event, ignores events coming from this class.
        """
        if event["Origin"] is not self.__class__:
            if "Fen" in event:
                self.chessboard = chess.Board(event["Fen"])
                self.drawChessboard(show_arrows=False)

    def handleMoveFromJS(self, move_str):
        """
        Handle a move made in the JavaScript chessground board.
        """
        try:
            # move_str is in format like "e2e4"
            move = chess.Move.from_uci(move_str)

            if move in self.chessboard.legal_moves:
                self.chessboard.push(move)

                pieceEvent = {
                    "Move": move,
                    "Fen": self.chessboard.fen(),
                    "Origin": self.__class__
                }
                self.parent(pieceEvent)

                self.moveFromSquare = move.from_square
                self.moveToSquare = move.to_square

                self.drawChessboard()
            else:
                # Move was not legal, reset the board position
                self.drawChessboard()
        except Exception as e:
            print(f"Error handling move: {e}")
            self.drawChessboard()

    def drawChessboard(self, show_arrows=True):
        """
        Update the chessboard display.
        """
        # Set the position
        fen = self.chessboard.fen()
        self.page().runJavaScript(f"window.setPosition('{fen}');")

        # Update legal moves
        legal_moves_map = {}
        for move in self.chessboard.legal_moves:
            orig = chess.square_name(move.from_square)
            dest = chess.square_name(move.to_square)

            if orig not in legal_moves_map:
                legal_moves_map[orig] = []
            legal_moves_map[orig].append(dest)

        legal_moves_json = json.dumps(legal_moves_map)
        self.page().runJavaScript(f"window.setMovable({legal_moves_json});")

        # Highlight last move and check
        if show_arrows and (self.moveFromSquare >= 0 and self.moveToSquare >= 0):
            from_square = chess.square_name(self.moveFromSquare)
            to_square = chess.square_name(self.moveToSquare)

            # Highlight check if in check
            if self.chessboard.is_check():
                king_square = chess.square_name(
                    self.chessboard.king(self.chessboard.turn)
                )
                self.page().runJavaScript(
                    f"window.highlightSquares(['{from_square}', '{to_square}', '{king_square}'], 'red');"
                )
            else:
                self.page().runJavaScript(
                    f"window.highlightSquares(['{from_square}', '{to_square}'], 'paleBlue');"
                )
        else:
            self.page().runJavaScript("window.clearHighlights();")

    def setOrientation(self, color):
        """
        Set the board orientation.

        Args:
            color: 'white' or 'black'
        """
        self.page().runJavaScript(f"window.setOrientation('{color}');")
