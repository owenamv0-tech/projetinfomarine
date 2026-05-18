# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:09:52 2026

@author: owena
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont



class PageAccueil(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        # --- Logo (cercle avec icône texte) ---
        self.logo = QLabel("🍽")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setFixedSize(90, 90)
        self.logo.setObjectName("logo")

        # --- Nom du restaurant ---
        self.titre = QLabel("Le Brestois")
        self.titre.setAlignment(Qt.AlignCenter)
        self.titre.setObjectName("titre")

        # --- Sous-titre ---
        self.sous_titre = QLabel("GESTION DE RESTAURANT")
        self.sous_titre.setAlignment(Qt.AlignCenter)
        self.sous_titre.setObjectName("sousTitre")

        # --- Boutons de navigation ---
        self.btn_carte   = self._make_btn("🗒  Carte",   1)
        self.btn_cuisine = self._make_btn("👨‍🍳  Cuisine", 2)
        self.btn_stats   = self._make_btn("📊  Stats",   3)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.addWidget(self.btn_carte)
        btn_layout.addWidget(self.btn_cuisine)
        btn_layout.addWidget(self.btn_stats)

        # --- Assemblage ---
        layout.addStretch()
        layout.addWidget(self.logo, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.titre)
        layout.addSpacing(6)
        layout.addWidget(self.sous_titre)
        layout.addSpacing(48)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def _make_btn(self, texte: str, page_index: int) -> QPushButton:
        btn = QPushButton(texte)
        btn.setFixedSize(140, 80)
        btn.setObjectName("navBtn")
        # Signal → slot : clic connecté à la navigation
        btn.clicked.connect(lambda: self.main.aller_a(page_index))
        return btn

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAF8;
            }
            QLabel#logo {
                background-color: #2C2C2A;
                color: white;
                font-size: 36px;
                border-radius: 45px;
            }
            QLabel#titre {
                font-size: 28px;
                font-weight: 500;
                color: #2C2C2A;
                letter-spacing: 2px;
            }
            QLabel#sousTitre {
                font-size: 12px;
                color: #888780;
                letter-spacing: 4px;
            }
            QPushButton#navBtn {
                background-color: #FFFFFF;
                color: #2C2C2A;
                border: 1px solid #D3D1C7;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton#navBtn:hover {
                background-color: #F1EFE8;
                border-color: #B4B2A9;
            }
            QPushButton#navBtn:pressed {
                background-color: #2C2C2A;
                color: #FAFAF8;
            }
        """)
