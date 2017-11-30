#! /usr/bin/env python

"""
Docstring.
"""
import sys

from PyQt5.QtWidgets import QApplication

from window import MainWindow


class Run(object):
    """
    Docstring.
    """
    def application(self):
        """
        Docstring.
        """
        chessFighter = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        chessFighter.exec()


if __name__ == "__main__":
    run = Run()
    run.application()
