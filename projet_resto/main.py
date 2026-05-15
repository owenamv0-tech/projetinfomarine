# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:12:05 2026

@author: owena
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# ← Ces deux lignes règlent le problème de pixélisation sur écrans HD
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Police globale plus propre
    from PyQt5.QtGui import QFont
    app.setFont(QFont("Segoe UI", 10))  # Windows
    # app.setFont(QFont("SF Pro Display", 10))  # Mac
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())