"""
Docstring.
"""
from utilities import CustomQDockWidget

from PyQt5.QtCore import QFile
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTextStream, QProcess
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from PyQt5.QtGui import QKeySequence
from PyQt5.QtPrintSupport import QPrintDialog
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QApplication, QDialog, QTabWidget
from PyQt5.QtWidgets import QWidget, QToolBar, QSizePolicy, QVBoxLayout, QMessageBox, QMainWindow, QAction
from PyQt5.QtWidgets import QTextEdit, QDialog

from board import Chessboard
from book import OpeningBookWidget
from chessgame import ChessGameWidget, ChessGameWithVariationPicker

from database import DatabaseWidget
from engine import EngineWidget
from external import chess_db

import qtawesome as qta
import os
from functools import partial

QString = type("")

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
        self.process_list = []
        # self.showFullScreen()
        self.setGeometry(100, 100, 1000, 1000)
        # self.setMinimumSize(400, 200)

        self.chessDB = chess_db.Parser(CHESSDB_EXEC)
        self.boardDock = CustomQDockWidget("Board", self)
        self.board = Chessboard(self.sendEvent)

        self.createActions()
        self.createToolBars()
        self.createMenus()
        self.createDockWindows()
        self.createStatusBar()

        board_widget = QWidget()
        layout = QVBoxLayout()
        # layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.board)

        # spacer widget for left
        # left_spacer = QWidget()
        # left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # spacer widget for right
        # you can't add the same widget to both left and right. you need two different widgets.
        # right_spacer = QWidget()
        # right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        # layout.addWidget(self.board_controls)
        board_widget.setLayout(layout)

        self.boardDock.setWidget(board_widget)
        self.setCentralWidget(self.boardDock)

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

    def openBook(self):
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  "Choose a filename",
                                                  ".",
                                                  "CTG (*.ctg *.PGN)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self,
                                "Chess Fighter Error",
                                "Can't open the file {}:\n{}.".format(filename,
                                                                       file.errorString()))
            return

        self.statusBar().showMessage("Opened Book: {}".format(filename), 2000)
        for l in self.bidirectionalListeners:
            event = {"Book_File": filename, "Origin": self.__class__}
            # self.parent(event)
            l()(event)

    def openDatabase(self):
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  "Choose a filename",
                                                  ".",
                                                  "PGN (*.pgn)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self,
                                "Chess Fighter Error",
                                "Can't open the file {}:\n{}.".format(filename, file.errorString()))
            return

        self.statusBar().showMessage("Opened: {}".format(filename), 2000)

        # Check to see if indexes are already build for DB:

        fname, ext = os.path.splitext(filename)

        if not os.path.exists(fname+'.scout') or not os.path.exists(fname + '.bin') or not os.path.exists(fname + '.headers.json'):
            # Add the UI components (here we use a QTextEdit to display the stdout from the process)
            self.dialog = QTextEdit()
            self.dialog.setWindowTitle("Opening Database...")
            self.dialog.progress = QTextEdit()

            self.dialog.show()

        if not os.path.exists(fname+'.scout'):
            print("Creating Scout DB")
            command = "{0}/external/scoutfish".format(os.getcwd())
            args = ["make", "{}".format(filename)]

            # Add the process and start it
            self.setupProcess(command, args, filename)

        if not os.path.exists(fname + '.bin'):
            print("Creating .bin DB")
            command = "{0}/external/parser".format(os.getcwd())
            args = ["book", "{}".format(filename), "full"]

            self.setupProcess(command, args, filename)
        else:
            # Switch to this databse
            for l in self.bidirectionalListeners:
                event = {"DB_File": filename, "Origin": self.__class__}
                # self.parent(event)
                l()(event)
                event = {"Book_File": filename, "Origin": self.__class__}
                # self.parent(event)
                l()(event)

        if not os.path.exists(fname + '.headers.json'):
            print("Creating JSON headers")
            command = "{0}/external/pgnextractor".format(os.getcwd())
            args = ["headers", "{}".format(filename), "full"]

            self.setupProcess(command, args, filename)

    def setupProcess(self, command, args, filename):
        process = QProcess()
        # Set the channels
        process.setProcessChannelMode(QProcess.MergedChannels)
        # Connect the signal readyReadStandardOutput to the slot of the widget
        # process.readyReadStandardOutput.connect(lambda: self.readStdOutput(process))
        process.readyReadStandardOutput.connect(partial(self.readStdOutput, command, process, filename))

        # Run the process with a given command
        process.start(command, args)
        self.process_list.append(process)

    def __del__(self):
        if self.process_list:
            for process in self.process_list:
                # If QApplication is closed attempt to kill the process
                process.terminate()
                # Wait for Xms and then elevate the situation to terminate
                if not process.waitForFinished(10000):
                    process.kill()

    @pyqtSlot()
    def readStdOutput(self, command, p, filename):
        # Every time the process has something to output we attach it to the QTextEdit
        # print("command: {}".format(command))
        text = QString(p.readAllStandardOutput())
        self.dialog.append(text)
        self.dialog.append("\n")
        if p in self.process_list:
            del self.process_list[self.process_list.index(p)]

        if command.endswith("parser"):
            # change DB
            for l in self.bidirectionalListeners:
                event = {"DB_File": filename, "Origin": self.__class__}
                # self.parent(event)
                l()(event)
                event = {"Book_File": filename, "Origin": self.__class__}
                # self.parent(event)
                l()(event)

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

    def goToStart(self):
        for l in self.bidirectionalListeners:
            event = {"Action": "Go_To_Start", "Origin": self.__class__}
            # self.parent(event)
            l()(event)

    def goToEnd(self):
        for l in self.bidirectionalListeners:
            event = {"Action": "Go_To_End", "Origin": self.__class__}
            # self.parent(event)
            l()(event)

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

    def forward(self):
        # print("forward")
        for l in self.bidirectionalListeners:
            event = {"Action": "Forward", "Origin": self.__class__}
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
        self.newLetterAction = QAction(qta.icon('fa.file'),
                                       "&New Game",
                                       self,
                                       shortcut=QKeySequence.New,
                                       statusTip="Start a new game.")

        self.openDatabaseAction = QAction(qta.icon('fa.database'),
                                       "&Open Database",
                                       self,
                                       shortcut=QKeySequence.Open,
                                       statusTip="Open Database",
                                          triggered=self.openDatabase)

        self.openBookAction = QAction(qta.icon('fa.book'),
                                          "&Open Book",
                                          self,
                                          statusTip="Open Book",
                                          triggered=self.openBook)

        self.saveAction = QAction(qta.icon('fa.save'),
                                  "&Save...",
                                  self,
                                  shortcut=QKeySequence.Save,
                                  statusTip="Save the current game.",
                                  triggered=self.save)

        self.printAction = QAction(qta.icon('fa.print'),
                                   "&Print...",
                                   self,
                                   shortcut=QKeySequence.Print,
                                   statusTip="Print the current game.",
                                   triggered=self.printing)

        self.undoAction = QAction(qta.icon('fa.step-backward'),
                                  "&Undo",
                                  self,
                                  shortcut="Left",
                                  statusTip="Previous move (Left Arrow)",
                                  triggered=self.undo)

        self.goToStartAction = QAction(qta.icon('fa.fast-backward'),
                                  "&Start",
                                  self,
                                  shortcut="Home",
                                  statusTip="Go to the beginning (Home)",
                                  triggered=self.goToStart)

        self.goToEndAction = QAction(qta.icon('fa.fast-forward'),
                                       "&End",
                                       self,
                                       shortcut="End",
                                       statusTip="Go to the end (End)",
                                       triggered=self.goToEnd)

        self.forwardAction = QAction(qta.icon('fa.step-forward'),
                                  "&Forward",
                                  self,
                                  shortcut="Right",
                                  statusTip="Next move (Right Arrow)",
                                  triggered=self.forward)

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
        self.fileMenu.addAction(self.openDatabaseAction)
        self.fileMenu.addAction(self.openBookAction)

        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.printAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)


        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.forwardAction)


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
        self.fileToolBar.addAction(self.openDatabaseAction)
        self.fileToolBar.addAction(self.openBookAction)

        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.printAction)

        self.editToolbar = self.addToolBar("Edit")

        self.editToolbar.addAction(self.goToStartAction)
        self.editToolbar.addAction(self.undoAction)
        self.editToolbar.addAction(self.forwardAction)
        self.editToolbar.addAction(self.goToEndAction)
        self.engineToolbar = self.addToolBar("Engine")


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
        dock = CustomQDockWidget("Game", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.gamePane = ChessGameWithVariationPicker(parent=self.sendEvent,
                                                     dock=dock)

        dock.setWidget(self.gamePane)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = CustomQDockWidget("", self)
        self.outputPane = OpeningBookWidget(parent=self.sendEvent, dock=dock, db=self.chessDB)

        self.tab_widget = QTabWidget()
        self.engine_widget = EngineWidget("Engine", parent=self.sendEvent, db=self.chessDB)

        self.tab_widget.addTab(self.outputPane, "Book")
        self.tab_widget.addTab(self.engine_widget, "Engine")

        dock.setWidget(self.tab_widget)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = DatabaseWidget("Database", self, parent=self.sendEvent, db=self.chessDB)
        # self.DBPane = DatabaseWidget(parent=self.sendEvent, dock=dock, db=self.chessDB)
        self.DBPane = dock

        # dock.setWidget(self.DBPane)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        self.bidirectionalListeners = [self.gamePane.registerListener,
                                       self.board.registerListener,  self.DBPane.registerListener, self.outputPane.registerListener, self.engine_widget.registerListener]

        for l in self.bidirectionalListeners:
            event = {"Action": "Game Start", "Fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "Origin": self.__class__}
            # self.parent(event)
            l()(event)
