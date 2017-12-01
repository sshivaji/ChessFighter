"""
Docstring.
"""
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QStatusBar

from board import Chessboard


class MainWindow(QMainWindow):
    """
    Docstring.
    """
    def __init__(self):
        """
        Docstring.
        """
        super().__init__()

        self.setWindowTitle("Chess Fighter 1.0")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 200)

        self.board = Chessboard()
        self.setCentralWidget(self.board)

        self.menuBar = QMenuBar()

        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setTitle("File")

        self.actionOpenPGNFile = QAction()
        self.actionOpenPGNFile.setText("Open PGN File...")
        self.menuFile.addAction(self.actionOpenPGNFile)

        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setTitle("Help")

        self.actionAboutChessFighter = QAction()
        self.actionAboutChessFighter.setText("About Chess Fighter...")
        self.menuHelp.addAction(self.actionAboutChessFighter)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.setMenuBar(self.menuBar)

        self.statusBar = QStatusBar()
        self.statusBar.showMessage("Play a game of chess.")
        self.setStatusBar(self.statusBar)
