"""
Docstring.
"""
from queue import Queue

try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except Exception:
    CPUINFO_AVAILABLE = False

import chess.uci
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QSpinBox, QComboBox, QPushButton
from PyQt5 import QtGui, QtCore
from utilities import BidirectionalListener
import platform
import utilities
import json
import os
from external.ctg_reader import CTGReader

MOVE_COLUMN = "move"

CHESSDB_EXEC = '../external/parser'
MILLIONBASE_PGN = '../bases/millionbase.pgn'
CHESS_CTG_READER = '../external/ctg_reader'


class EngineWidget(BidirectionalListener, QWidget):
    """
    Docstring.
    """

    engine_output = QtCore.pyqtSignal(dict)

    def __init__(self, dock, parent, db=None):
        """
        Docstring.
        """
        super(EngineWidget, self).__init__()
        self.engine = None
        self.engine_output.connect(self.engine_analysis_update)

        self.textbox = QLabel(self)
        self.textbox.setText("Lines:")

        self.lines_box = QSpinBox(self)
        # self.lines_box.resize(1,1)
        self.lines_box.setMinimum(1)
        self.lines_box.setMaximum(9)
        self.lines_box.setSingleStep(1)
        self.lines_box.valueChanged.connect(self.engine_analysis_lines)
        self.engine_activated = False
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        layout = QVBoxLayout()

        row_layout= QHBoxLayout()
        row_layout.addWidget(self.textbox)
        row_layout.addWidget(self.lines_box)

        comboBox = QComboBox(self)
        comboBox.addItem(os.path.basename(self.detect_default_engine()))
        comboBox.addItem("Slowfish")
        comboBox.activated[str].connect(self.engine_choice)

        # comboBox.move(50, 250)

        # comboBox.activated[str].connect(self.style_choice)
        self.start_eng_btn = QPushButton("Start")
        self.start_eng_btn.clicked.connect(self.engine_action)

        row_layout.addWidget(comboBox)
        row_layout.addWidget(self.start_eng_btn)

        self.engine_pane = QTextEdit()

        layout.addLayout(row_layout)
        layout.addWidget(self.engine_pane)

        # layout.
        # addWidget(self.board_controls)
        self.setLayout(layout)

    def detect_platform(self):
        system = platform.system()
        if system == 'Darwin':
            system = 'Mac'
        return system

    def detect_default_engine(self):
        system = self.detect_platform()

        if CPUINFO_AVAILABLE:
            try:
                cpu = cpuinfo.get_cpu_info()
                bits = cpu['bits']
                flags = cpu['flags']

                if 'bmi2' in flags:
                    cpu_string = 'bmi2'
                elif 'popcnt' in flags:
                    cpu_string = 'popcnt'
                else:
                    cpu_string = ''
            except Exception:
                # Fallback if cpuinfo fails
                bits = 64 if platform.machine() in ['x86_64', 'AMD64', 'arm64', 'aarch64'] else 32
                cpu_string = ''
        else:
            # Fallback when cpuinfo is not available
            bits = 64 if platform.machine() in ['x86_64', 'AMD64', 'arm64', 'aarch64'] else 32
            cpu_string = ''

        exec_path = ''

        if system == 'Mac' or system == 'Linux':
            if not cpu_string:
                cpu_string = 64
            exec_path = "./engines/{}/stockfish-9-{}".format(system, cpu_string)

        if system == 'Windows':
            if cpu_string:
                cpu_string = '_' + cpu_string
            exec_path = "./engines/{}/stockfish_9_x{}{}.exe".format(system, bits, cpu_string)

        return exec_path

    @QtCore.pyqtSlot(int)
    def engine_analysis_lines(self):
        # print("got value: {}".format(self.lines_box.value()))
        if self.engine:
            self.engine.stop()
            self.engine.setoption({"MultiPV": self.lines_box.value()})
            self.engine.go(infinite=True, async_callback=True)

    @QtCore.pyqtSlot(dict)
    def engine_analysis_update(self, value):
        # print(value)
        text = "<span style=\" color:darkblue;\" font-weight=\"bold;\" >"
        try:
            for index in value["score"]:
                if value["score"][index].cp is not None:
                    text += str(value["score"][index].cp/100)
                if value["depth"]:
                    text += "/{}".format(value["depth"])
                    text += "</span>"
                board = chess.Board(self.fen)
                text += "  "
                moves = board.variation_san(value["pv"][index])
                moves = utilities.figurizine(moves)
                text += moves
                text += "<br><br>"
            # text += "</span>"

            self.engine_pane.setText(text)
        except KeyError:
            print("Waiting for engine to get score and depth..")

    def engine_choice(self, txt):
        print("got engine: {}".format(txt))

    def engine_action(self):
        self.engine_activated = not self.engine_activated

        # time.sleep(3)
        if self.engine_activated:
            self.start_eng_btn.setText("Stop")

            class EngineHandler(chess.uci.InfoHandler):
                def post_info(self):
                    super(EngineHandler, self).post_info()
                    # q.put(self.info)
                    self.parent.engine_output.emit(self.info)
                    # self.parent.engine_analysis_update()
                    # print(self.info)

            eh = EngineHandler()
            eh.parent = self
            # eh.buffer = Queue()
            # Start engine
            self.engine = chess.uci.popen_engine(self.detect_default_engine())
            self.engine.uci()
            # print (engine.name)
            board = chess.Board(self.fen)
            self.engine.position(board)
            self.engine.setoption({"MultiPV": self.lines_box.value()})

            self.engine.go(infinite=True, async_callback=True)
            if not self.engine.info_handlers:
                self.engine.info_handlers.append(eh)

        else:
            self.start_eng_btn.setText("Start")

            # Stop Engine
            self.engine.stop()

        # print("engine_activated: {}".format(self.engine_activated))

    def engine_refresh(self, fen):
        if self.engine and self.engine_activated:
            self.engine.stop()
            board = chess.Board(fen)
            self.engine.position(board)
            self.engine.go(infinite=True, async_callback=True)

    def processEvent(self, event):
        """
        Docstring.
        Processes an event, ignores events coming from this class
        """
        if event["Origin"] is not self.__class__:
            # print("Book: {}".format(event))

            if "Engine_Select" in event:
                # print("event: {}".format(event))
                self.engine = event["Engine_Select"]

            if "Fen" in event:
                # print("engine_fen event: {}".format(event))
                self.fen = event["Fen"]
                self.engine_refresh(self.fen)


