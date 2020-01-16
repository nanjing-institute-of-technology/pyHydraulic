import os
import sys
import inspect
from PyQt5.QtWidgets import *
from pyHydraulic.utils import loadStylesheet
from pyHydraulic.node_editor_window import NodeEditorWindow

def run():
    app = QApplication(sys.argv)
    wnd = NodeEditorWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
