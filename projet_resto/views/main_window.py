# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:09:18 2026

@author: owena
"""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from views.page_accueil import PageAccueil
from views.page_carte   import PageCarte
from views.page_cuisine import PageCuisine
from views.page_stats   import PageStats

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Le Brestois")
        self.setMinimumSize(1100, 720)

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        # 1. Cuisine en premier — elle crée l'ObservateurCuisine
        self.page_cuisine = PageCuisine(self)

        # 2. Carte reçoit l'observateur → quand on valide une commande,
        #    la cuisine est notifiée automatiquement via le pattern Observer
        self.page_carte = PageCarte(self, obs_cuisine=self.page_cuisine.obs_cuisine)

        # 3. Stats reçoit une fonction qui lit les commandes depuis la cuisine
        self.page_stats = PageStats(self,
            get_commandes=self.page_cuisine.get_toutes_commandes)

        self.pages.addWidget(PageAccueil(self))    # 0
        self.pages.addWidget(self.page_carte)       # 1
        self.pages.addWidget(self.page_cuisine)     # 2
        self.pages.addWidget(self.page_stats)       # 3

    def aller_a(self, index: int):
        self.pages.setCurrentIndex(index)