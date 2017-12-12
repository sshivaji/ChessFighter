#!/usr/bin/env python

from PyQt5.QtCore import QDate, QFile, Qt, QTextStream
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QTextCharFormat,
        QTextCursor, QTextTableFormat)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
        QFileDialog, QListWidget, QMainWindow, QMessageBox, QTextEdit)

from board import Chessboard
from chess_game import ChessGameWidget
import copy
import queue
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Chess Fighter 1.0")
        self.setGeometry(100, 100, 800, 700)
        self.setMinimumSize(400, 200)

        self.board_dock = QDockWidget("Board", self)
        self.board = Chessboard(self.send_event)
        self.board_dock.setWidget(self.board)
        self.setCentralWidget(self.board_dock)

        self.createActions()
        self.createMenus()
        # self.createToolBars()
        self.createStatusBar()
        self.createDockWindows()

        self.event_q = queue.Queue()
        self.setWindowTitle("Chess Fighter")

    def print_(self):
        document = self.textEdit.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                "Choose a file name", '.', "PGN (*.pgn)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "ChessFighter",
                    "Cannot write file %s:\n%s." % (filename, file.errorString()))
            return

        out = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.textEdit.toHtml()
        QApplication.restoreOverrideCursor()

        self.statusBar().showMessage("Saved '%s'" % filename, 2000)

    def undo(self):
        document = self.textEdit.document()
        document.undo()

    def about(self):
        QMessageBox.about(self, "About Chess Fighter",
                "Chess GUI")

    def createActions(self):
        self.newLetterAct = QAction(QIcon(':/images/new.png'), "&New Game",
                self, shortcut=QKeySequence.New,
                statusTip="Start a New Game")

        self.saveAct = QAction(QIcon(':/images/save.png'), "&Save...", self,
                shortcut=QKeySequence.Save,
                statusTip="Save current Game", triggered=self.save)

        self.printAct = QAction(QIcon(':/images/print.png'), "&Print...", self,
                shortcut=QKeySequence.Print,
                statusTip="Print the current Game",
                triggered=self.print_)

        self.undoAct = QAction(QIcon(':/images/undo.png'), "&Undo", self,
                shortcut=QKeySequence.Undo,
                statusTip="Undo last move", triggered=self.undo)

        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newLetterAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)

        self.viewMenu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newLetterAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.printAct)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.undoAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def send_event(self, e):
        for l in self.bidi_listeners:
            l()(e)

    def createDockWindows(self):
        dock = QDockWidget("Game", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.gamePane = ChessGameWidget(dock, self.send_event)

        self.bidi_listeners = [self.gamePane.register_listener, self.board.register_listener]

        dock.setWidget(self.gamePane)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = QDockWidget("Engine", self)
        self.outputPane = QListWidget(dock)

        dock.setWidget(self.outputPane)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = QDockWidget("Database", self)
        self.outputPane = QListWidget(dock)

        dock.setWidget(self.outputPane)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
