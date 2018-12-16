import math
from PyQt5.QtWidgets import QDockWidget

"""
Docstring.
"""

FIGURINE_MAP = {
    "K": u'\u2654',
    "Q": u'\u2655',
    "R": u'\u2656',
    "B": u'\u2657',
    "N": u'\u2658'
}

INV_FIGURING_MAP = {v: k for k, v in FIGURINE_MAP.items()}


def figurizine(move, reverse=False):
    for letter in move:
        if reverse:
            if letter in INV_FIGURING_MAP:
                move = move.replace(letter, INV_FIGURING_MAP[letter])
        else:
            if letter in FIGURINE_MAP:
                move = move.replace(letter, FIGURINE_MAP[letter])
    return move

def num_fmt(num):
    i_offset = 15 # change this if you extend the symbols!!!
    prec = 3
    fmt = '.{p}g'.format(p=prec)
    symbols = ['Y', 'T', 'G', 'M', 'k', '', 'm', 'u', 'n']

    if num == 0:
        return num

    e = math.log10(abs(num))
    if e >= i_offset + 3:
        return '{:{fmt}}'.format(num, fmt=fmt)
    for i, sym in enumerate(symbols):
        e_thresh = i_offset - 3 * i
        if e >= e_thresh:
            return '{:{fmt}}{sym}'.format(num/10.**e_thresh, fmt=fmt, sym=sym)
    return '{:{fmt}}'.format(num, fmt=fmt)


class BidirectionalListener(object):
    """
    Docstring.
    """
    def __init__(self):
        """
        Docstring.
        """
        super(BidirectionalListener, self).__init__()

    def registerListener(self):
        return self.processEvent

    def processEvent(self, event):
        """
        Docstring.
        """
        # TODO: Override this.
        pass

    def sendEvent(self, event):
        """
        Docstring.
        """
        # TODO: Override this.
        pass


class CustomQDockWidget(QDockWidget):
    def __init__(self, name, parent):
        """
        Docstring.
        """
        super(CustomQDockWidget, self).__init__()
        self.setFeatures(QDockWidget.DockWidgetFloatable |
                             QDockWidget.DockWidgetMovable)
        self.setWindowTitle(name)