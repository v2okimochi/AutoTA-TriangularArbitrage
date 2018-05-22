# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
from GUI import GUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = GUI()
    sys.exit(app.exec())
