"""
Docstring.
"""
import sys

from PyQt5.QtCore import QFile
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTextStream
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence
from PyQt5.QtPrintSupport import QPrintDialog
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget



from board import Chessboard
from book import OpeningBookWidget
from chessgame import ChessGameWidget

from database import DatabaseWidget
from external import chess_db


CHESSDB_EXEC = '../external/parser'

class MainWindow(QMainWindow):
    """
    Docstring.
    """
    def __init__(self):
        """
        Docstring.
        """
        super(MainWindow, self).__init__()

        self.setWindowTitle("Chess Fighter 1.0")
        # self.showFullScreen()
        # self.setGeometry(100, 100, 1000, 1000)
        # self.setMinimumSize(400, 200)

        self.chessDB = chess_db.Parser(CHESSDB_EXEC)
        self.boardDock = QDockWidget("Board", self)
        self.board = Chessboard(self.sendEvent)

        board_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.board)
        board_widget.setLayout(layout)

        self.boardDock.setWidget(board_widget)
        self.setCentralWidget(self.boardDock)

        self.createActions()
        self.createToolBars()
        self.createMenus()
        self.createDockWindows()
        self.createStatusBar()


    def printing(self):
        """
        Docstring.
        """
        document = self.gamePane.document()
        printer = QPrinter()

        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QDialog.Accepted:
            return

        document.print(printer)

        self.statusBar().showMessage("Ready.", 2000)

    def save(self):
        """
        Docstring.
        """
        filename, _ = QFileDialog.getSaveFileName(self,
                                               "Choose a filename",
                                               ".",
                                               "PGN (*.pgn)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self,
                                "Chess Fighter Error",
                                "Can't write the file {}:\n{}.".format(filename,
                                                                       file.errorString()))
            return

        out = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.gamePane.toHtml()
        QApplication.restoreOverrideCursor()

        self.statusBar().showMessage("Saved: {}".format(filename), 2000)

    def undo(self):
        """
        Docstring.
        """
        # document = self.gamePane
        # document.undo()

        for l in self.bidirectionalListeners:
            event = {"Action": "Undo", "Origin": self.__class__}
            # self.parent(event)
            l()(event)


    def aboutChessFighter(self):
        """
        Docstring.
        """
        QMessageBox.about(self,
                          "About Chess Fighter",
                          "This is a chess GUI.")

    def createActions(self):
        """
        Docstring.
        """
        self.newLetterAction = QAction(QIcon("images/new.svg"),
                                       "&New Game",
                                       self,
                                       shortcut=QKeySequence.New,
                                       statusTip="Start a new game.")

        self.saveAction = QAction(QIcon("images/save.svg"),
                                  "&Save...",
                                  self,
                                  shortcut=QKeySequence.Save,
                                  statusTip="Save the current game.",
                                  triggered=self.save)

        self.printAction = QAction(QIcon("images/print.svg"),
                                   "&Print...",
                                   self,
                                   shortcut=QKeySequence.Print,
                                   statusTip="Print the current game.",
                                   triggered=self.printing)

        self.undoAction = QAction(QIcon("images/undo.svg"),
                                  "&Undo",
                                  self,
                                  shortcut=QKeySequence.Undo,
                                  statusTip="Undo the last move.",
                                  triggered=self.undo)

        self.quitAction = QAction("&Quit",
                                  self,
                                  shortcut="Ctrl + Q",
                                  statusTip="Quit Chess Fighter.",
                                  triggered=self.close)

        self.aboutChessFighterAction = QAction("&About",
                                               self,
                                               statusTip="Show info about Chess Fighter.",
                                               triggered=self.aboutChessFighter)

        self.aboutQtAction = QAction("About &Qt",
                                     self,
                                     statusTip="Show info about Qt library.",
                                     triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        """
        Docstring.
        """
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newLetterAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.printAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAction)

        self.viewMenu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutChessFighterAction)
        self.helpMenu.addAction(self.aboutQtAction)

    def createToolBars(self):
        """
        Docstring.
        """
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newLetterAction)
        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.printAction)

        self.editToolbar = self.addToolBar("Edit")
        self.editToolbar.addAction(self.undoAction)

    def createStatusBar(self):
        """
        Docstring.
        """
        self.statusBar().showMessage("Ready.")

    def sendEvent(self, event):
        """
        Docstring.
        """
        for listener in self.bidirectionalListeners:
            listener()(event)

    def createDockWindows(self):
        """
        Docstring.
        """
        dock = QDockWidget("Game", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.gamePane = ChessGameWidget(parent=self.sendEvent,
                                        dock=dock)

        dock.setWidget(self.gamePane)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = QDockWidget("Engine", self)
        self.outputPane = OpeningBookWidget(parent=self.sendEvent, dock=dock, db=self.chessDB)

        dock.setWidget(self.outputPane)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = DatabaseWidget("Database", self, parent=self.sendEvent, db=self.chessDB)
        # self.DBPane = DatabaseWidget(parent=self.sendEvent, dock=dock, db=self.chessDB)
        self.DBPane = dock

        # dock.setWidget(self.DBPane)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        self.bidirectionalListeners = [self.gamePane.registerListener,
                                       self.board.registerListener, self.outputPane.registerListener, self.DBPane.registerListener]

        for l in self.bidirectionalListeners:
            event = {"Action": "Game Start", "Fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "Origin": self.__class__}
            # self.parent(event)
            l()(event)
