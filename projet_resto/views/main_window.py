# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:09:18 2026

@author: owena
"""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from views.page_accueil import PageAccueil
from views.page_carte import PageCarte       # on créera ça ensuite
from views.page_cuisine import PageCuisine   # idem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Restaurant")
        self.setMinimumSize(1000, 700)

        # QStackedWidget = pile de pages, une seule visible à la fois
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        # Création des pages
        self.page_accueil = PageAccueil(self)
        self.page_carte   = PageCarte(self)
        self.page_cuisine = PageCuisine(self)

        self.pages.addWidget(self.page_accueil)   # index 0
        self.pages.addWidget(self.page_carte)      # index 1
        self.pages.addWidget(self.page_cuisine)    # index 2

        self.pages.setCurrentIndex(0)  # on démarre sur l'accueil

    def aller_a(self, index: int):
        """Appelé par les boutons des pages pour naviguer."""
        self.pages.setCurrentIndex(index)