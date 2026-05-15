# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:11:19 2026

@author: owena
"""
"""
views/page_cuisine.py
Page Cuisine : file d'attente publique + mode serveur protégé par mot de passe.

Mot de passe serveur : marinexowen

Dépendances :
    pip install PyQt5 qtawesome
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QDialog, QLineEdit, QSizePolicy,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont
import qtawesome as qta

# ── Constantes ────────────────────────────────────────────────────────────────
MOT_DE_PASSE   = "marinexowen"

COULEURS = {
    "fond":              "#FAFAF8",
    "surface":           "#FFFFFF",
    "bordure":           "#E8E6E0",
    "texte":             "#1A1A18",
    "texte_secondaire":  "#888780",
    "accent":            "#2C2C2A",
    "fond_serveur":      "#F5F4F0",

    # Statuts
    "attente_fond":   "#FEF3E2", "attente_texte":  "#8A5200",
    "encours_fond":   "#EEEDFE", "encours_texte":  "#4A41A7",
    "pret_fond":      "#E8F5EE", "pret_texte":     "#0A6647",
}

STATUTS = ["En attente", "En cours", "Prête"]

ICO_RETOUR  = "mdi.chevron-left"
ICO_LOCK    = "mdi.lock"
ICO_UNLOCK  = "mdi.lock-open"
ICO_CLOCK   = "mdi.clock-outline"
ICO_TABLE   = "mdi.table-chair"
ICO_PLUS    = "mdi.plus"
ICO_CHECK   = "mdi.check"
ICO_DELETE  = "mdi.close"
ICO_EYE     = "mdi.eye-off"


# ── Données de démonstration ──────────────────────────────────────────────────
# Remplacer par les vraies commandes de Marine quand commande.py sera prêt

def _commandes_demo():
    """
    Retourne une liste de dicts représentant des commandes en cours.
    Structure : { "table": int, "statut": str, "temps_estime": int (minutes) }

    À remplacer par : [cmd.to_dict() for cmd in cuisine.file_attente]
    """
    return [
        {"table": 3, "statut": "En cours",   "temps_estime": 8},
        {"table": 1, "statut": "En attente", "temps_estime": 15},
        {"table": 7, "statut": "Prête",      "temps_estime": 0},
    ]


# ── Dialog mot de passe ───────────────────────────────────────────────────────

class DialogMotDePasse(QDialog):
    """
    Fenêtre modale demandant le mot de passe serveur.
    Retourne QDialog.Accepted si le mot de passe est correct.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accès serveur")
        self.setFixedSize(300, 200)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._erreur = False
        self._build()
        self._apply_styles()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(10)

        titre = QLabel("Mode serveur")
        titre.setObjectName("modalTitre")
        titre.setAlignment(Qt.AlignCenter)

        sous_titre = QLabel("Entrez le code d'accès")
        sous_titre.setObjectName("modalSous")
        sous_titre.setAlignment(Qt.AlignCenter)

        self._champ = QLineEdit()
        self._champ.setObjectName("champMdp")
        self._champ.setEchoMode(QLineEdit.Password)
        self._champ.setAlignment(Qt.AlignCenter)
        self._champ.setPlaceholderText("••••••••••••")
        self._champ.returnPressed.connect(self._verifier)

        self._erreur_label = QLabel("")
        self._erreur_label.setObjectName("erreurLabel")
        self._erreur_label.setAlignment(Qt.AlignCenter)

        btn = QPushButton("Accéder")
        btn.setObjectName("btnConfirmer")
        btn.setFixedHeight(38)
        btn.clicked.connect(self._verifier)

        layout.addWidget(titre)
        layout.addWidget(sous_titre)
        layout.addSpacing(6)
        layout.addWidget(self._champ)
        layout.addWidget(self._erreur_label)
        layout.addWidget(btn)

    def _verifier(self):
        if self._champ.text() == MOT_DE_PASSE:
            self.accept()
        else:
            self._erreur_label.setText("Code incorrect")
            self._champ.clear()
            self._champ.setFocus()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {COULEURS['surface']};
                border: 1px solid {COULEURS['bordure']};
                border-radius: 14px;
            }}
            QLabel#modalTitre {{
                font-size: 16px; font-weight: 600;
                color: {COULEURS['texte']};
            }}
            QLabel#modalSous {{
                font-size: 12px; color: {COULEURS['texte_secondaire']};
            }}
            QLineEdit#champMdp {{
                padding: 10px 14px;
                border: 1px solid {COULEURS['bordure']};
                border-radius: 8px;
                font-size: 16px;
                letter-spacing: 4px;
                color: {COULEURS['texte']};
            }}
            QLineEdit#champMdp:focus {{
                border-color: {COULEURS['accent']};
            }}
            QLabel#erreurLabel {{
                font-size: 12px; color: #B53030;
            }}
            QPushButton#btnConfirmer {{
                background: {COULEURS['accent']};
                color: #FAFAF8;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton#btnConfirmer:hover {{
                background: #444440;
            }}
        """)


# ── Carte d'une commande ──────────────────────────────────────────────────────

class CarteCommande(QFrame):
    """
    Widget représentant une commande dans la file d'attente.

    MODIFIER ICI pour ajouter des infos (liste des plats, client, etc.)
    quand commande.py de Marine sera disponible.
    """

    STATUT_STYLES = {
        "En attente": ("attente_fond", "attente_texte", "#E8A020"),
        "En cours":   ("encours_fond", "encours_texte", "#4A41A7"),
        "Prête":      ("pret_fond",    "pret_texte",    "#0A6647"),
    }

    def __init__(self, commande: dict, on_statut_change=None):
        """
        commande : dict avec clés "table", "statut", "temps_estime"
        on_statut_change : callback(table, nouveau_statut) — None si vue client
        """
        super().__init__()
        self._commande = commande
        self._on_statut_change = on_statut_change
        self._build()

    def _build(self):
        self.setObjectName("carteCommande")
        self.setFixedHeight(80)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(14)

        statut = self._commande["statut"]
        fond_key, texte_key, ico_color = self.STATUT_STYLES.get(
            statut, ("fond", "texte", "#888780")
        )

        # ── Badge table ──
        table_badge = QLabel(f"T\n{self._commande['table']}")
        table_badge.setFixedSize(40, 40)
        table_badge.setAlignment(Qt.AlignCenter)
        bg = COULEURS["pret_texte"] if statut == "Prête" else COULEURS["accent"]
        table_badge.setStyleSheet(
            f"background:{bg}; color:#FAFAF8; border-radius:10px;"
            f" font-size:12px; font-weight:600; line-height:1.2;"
        )

        # ── Infos centre ──
        infos = QVBoxLayout()
        infos.setSpacing(4)
        infos.setContentsMargins(0, 0, 0, 0)

        nom = QLabel(f"Table {self._commande['table']}")
        nom.setObjectName("cmdTableNom")

        if statut == "Prête":
            temps_txt = "Commande prête !"
        else:
            temps_txt = f"Temps estimé : {self._commande['temps_estime']} min"

        temps_row = QHBoxLayout()
        temps_row.setSpacing(5)
        ico_temps = QLabel()
        ico_temps.setPixmap(
            qta.icon(ICO_CLOCK, color=COULEURS["texte_secondaire"]).pixmap(QSize(12, 12))
        )
        temps_lbl = QLabel(temps_txt)
        temps_lbl.setObjectName("cmdTemps")
        temps_row.addWidget(ico_temps)
        temps_row.addWidget(temps_lbl)
        temps_row.addStretch()

        # Barre de progression
        progress = QFrame()
        progress.setObjectName("progressBar")
        progress.setFixedHeight(3)
        progress_fill = QFrame(progress)
        progress_fill.setFixedHeight(3)
        pct = {"En attente": 15, "En cours": 60, "Prête": 100}.get(statut, 0)
        progress_fill.setStyleSheet(
            f"background:{ico_color}; border-radius:2px;"
        )
        progress_fill.setFixedWidth(int(180 * pct / 100))

        infos.addWidget(nom)
        infos.addLayout(temps_row)
        infos.addWidget(progress)

        # ── Badge statut ──
        statut_badge = QLabel(statut)
        statut_badge.setAlignment(Qt.AlignCenter)
        statut_badge.setFixedWidth(90)
        statut_badge.setStyleSheet(
            f"background:{COULEURS[fond_key]}; color:{COULEURS[texte_key]};"
            f" border-radius:12px; padding:4px 10px;"
            f" font-size:11px; font-weight:500;"
        )

        layout.addWidget(table_badge)
        layout.addLayout(infos, stretch=1)
        layout.addWidget(statut_badge)

        # ── Boutons serveur (visibles seulement si on_statut_change fourni) ──
        if self._on_statut_change:
            self._build_actions_serveur(layout, statut)

    def _build_actions_serveur(self, layout, statut):
        """Boutons pour faire avancer le statut d'une commande."""
        actions = QVBoxLayout()
        actions.setSpacing(4)

        statut_idx = STATUTS.index(statut) if statut in STATUTS else 0

        if statut_idx < len(STATUTS) - 1:
            prochain = STATUTS[statut_idx + 1]
            btn_avancer = QPushButton(f"→ {prochain}")
            btn_avancer.setObjectName("btnAvancer")
            btn_avancer.setFixedHeight(26)
            btn_avancer.clicked.connect(
                lambda: self._on_statut_change(self._commande["table"], prochain)
            )
            actions.addWidget(btn_avancer)

        layout.addLayout(actions)


# ── Panneau serveur (droite, déverrouillé) ────────────────────────────────────

class PanneauServeur(QWidget):
    """
    Panneau visible uniquement en mode serveur.
    Permet d'ajouter manuellement une commande à la file.

    MODIFIER ICI pour brancher commande.py de Marine.
    """

    def __init__(self, on_ajouter_commande):
        super().__init__()
        self._on_ajouter = on_ajouter_commande
        self._num_table = 1
        self._build()
        self._apply_styles()

    def _build(self):
        self.setObjectName("panneauServeur")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        # Titre
        titre_row = QHBoxLayout()
        ico = QLabel()
        ico.setPixmap(qta.icon(ICO_UNLOCK, color=COULEURS["texte"]).pixmap(QSize(16, 16)))
        titre = QLabel("Mode serveur")
        titre.setObjectName("serveurTitre")
        titre_row.addWidget(ico)
        titre_row.addWidget(titre)
        titre_row.addStretch()
        layout.addLayout(titre_row)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separateur")
        layout.addWidget(sep)

        # Sélection de table
        layout.addWidget(QLabel("Nouvelle commande").setObjectName("serveurLabel") or QLabel("Nouvelle commande"))
        lbl = QLabel("Nouvelle commande")
        lbl.setObjectName("serveurLabel")
        layout.addWidget(lbl)

        table_row = QHBoxLayout()
        lbl_t = QLabel("Table :")
        lbl_t.setObjectName("serveurLabel")
        self._table_display = QLabel("1")
        self._table_display.setObjectName("tableNum")
        self._table_display.setFixedWidth(28)
        self._table_display.setAlignment(Qt.AlignCenter)
        btn_m = QPushButton("−"); btn_m.setObjectName("btnTable"); btn_m.setFixedSize(28, 28)
        btn_p = QPushButton("+"); btn_p.setObjectName("btnTable"); btn_p.setFixedSize(28, 28)
        btn_m.clicked.connect(self._table_moins)
        btn_p.clicked.connect(self._table_plus)
        table_row.addWidget(lbl_t)
        table_row.addStretch()
        table_row.addWidget(btn_m)
        table_row.addWidget(self._table_display)
        table_row.addWidget(btn_p)
        layout.addLayout(table_row)

        # Bouton envoyer en cuisine
        btn_envoyer = QPushButton("  Envoyer en cuisine")
        btn_envoyer.setObjectName("btnEnvoyer")
        btn_envoyer.setIcon(qta.icon(ICO_CHECK, color="#FAFAF8"))
        btn_envoyer.setIconSize(QSize(14, 14))
        btn_envoyer.setFixedHeight(40)
        btn_envoyer.clicked.connect(self._envoyer)
        layout.addWidget(btn_envoyer)

        layout.addStretch()

        # Bouton se déconnecter
        btn_deco = QPushButton("  Se déconnecter")
        btn_deco.setObjectName("btnDeco")
        btn_deco.setIcon(qta.icon(ICO_LOCK, color=COULEURS["texte_secondaire"]))
        btn_deco.setIconSize(QSize(13, 13))
        btn_deco.clicked.connect(self._deconnecter)
        layout.addWidget(btn_deco)

        self._btn_deco = btn_deco

    def set_on_deconnecter(self, callback):
        self._btn_deco.clicked.disconnect()
        self._btn_deco.clicked.connect(callback)

    def _table_moins(self):
        if self._num_table > 1:
            self._num_table -= 1
            self._table_display.setText(str(self._num_table))

    def _table_plus(self):
        self._num_table += 1
        self._table_display.setText(str(self._num_table))

    def _envoyer(self):
        # ── Brancher Commande de Marine ici ──
        # from models.commande import Commande
        # cmd = Commande(self._num_table)
        # cuisine.ajouter(cmd)
        self._on_ajouter({
            "table": self._num_table,
            "statut": "En attente",
            "temps_estime": 20,
        })

    def _deconnecter(self):
        pass  # surchargé via set_on_deconnecter()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget#panneauServeur {{
                background: {COULEURS['fond_serveur']};
                border-left: 1px solid {COULEURS['bordure']};
            }}
            QLabel#serveurTitre {{
                font-size: 14px; font-weight: 600; color: {COULEURS['texte']};
            }}
            QLabel#serveurLabel {{
                font-size: 12px; color: {COULEURS['texte_secondaire']};
            }}
            QLabel#tableNum {{
                font-size: 14px; font-weight: 600; color: {COULEURS['texte']};
            }}
            QPushButton#btnTable {{
                background: #FFFFFF; border: 1px solid {COULEURS['bordure']};
                border-radius: 6px; font-size: 15px; color: {COULEURS['texte']};
            }}
            QPushButton#btnTable:hover {{ background: #E5E3DC; }}
            QPushButton#btnEnvoyer {{
                background: {COULEURS['accent']}; color: #FAFAF8;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 500;
            }}
            QPushButton#btnEnvoyer:hover {{ background: #444440; }}
            QPushButton#btnAvancer {{
                background: {COULEURS['encours_fond']};
                color: {COULEURS['encours_texte']};
                border: none; border-radius: 6px;
                font-size: 11px; font-weight: 500; padding: 2px 8px;
            }}
            QPushButton#btnAvancer:hover {{ background: #DDDCFC; }}
            QPushButton#btnDeco {{
                background: transparent;
                border: 1px solid {COULEURS['bordure']};
                border-radius: 8px; font-size: 12px;
                color: {COULEURS['texte_secondaire']}; padding: 8px;
            }}
            QPushButton#btnDeco:hover {{ background: #ECEAE3; }}
            QFrame#separateur {{ color: {COULEURS['bordure']}; max-height:1px; }}
        """)


# ── Page Cuisine principale ───────────────────────────────────────────────────

class PageCuisine(QWidget):
    """
    Page Cuisine.

    - Gauche  : file d'attente (visible par tous)
    - Droite  : panneau serveur (déverrouillé par mot de passe)

    MODIFIER ICI pour brancher les vraies commandes de Marine :
        → remplacer _carte_demo() par un appel à Cuisine.file_attente
        → brancher _changer_statut() sur Cuisine.changer_statut()
    """

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self._commandes = _commandes_demo()
        self._mode_serveur = False
        self._build()
        self._apply_styles()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar
        navbar = QHBoxLayout()
        navbar.setContentsMargins(20, 14, 20, 14)

        btn_retour = QPushButton("  Accueil")
        btn_retour.setObjectName("btnRetour")
        btn_retour.setIcon(qta.icon(ICO_RETOUR, color=COULEURS["texte_secondaire"]))
        btn_retour.setIconSize(QSize(13, 13))
        btn_retour.clicked.connect(lambda: self.main.aller_a(0))

        titre_page = QLabel("Cuisine")
        titre_page.setObjectName("pageTitre")

        self._btn_serveur = QPushButton("  Mode serveur")
        self._btn_serveur.setObjectName("btnServeur")
        self._btn_serveur.setIcon(qta.icon(ICO_LOCK, color=COULEURS["texte"]))
        self._btn_serveur.setIconSize(QSize(13, 13))
        self._btn_serveur.clicked.connect(self._toggle_serveur)

        navbar.addWidget(btn_retour)
        navbar.addStretch()
        navbar.addWidget(titre_page)
        navbar.addStretch()
        navbar.addWidget(self._btn_serveur)
        root.addLayout(navbar)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("separateur")
        root.addWidget(sep)

        # Corps
        self._corps = QHBoxLayout()
        self._corps.setContentsMargins(0, 0, 0, 0)
        self._corps.setSpacing(0)

        # Panneau file d'attente (gauche)
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        self._rafraichir_file()

        self._corps.addWidget(self._scroll_area, stretch=1)

        # Panneau serveur (droite, caché par défaut)
        self._panneau_serveur = PanneauServeur(self._ajouter_commande)
        self._panneau_serveur.set_on_deconnecter(self._deconnecter)
        self._panneau_serveur.setVisible(False)
        self._corps.addWidget(self._panneau_serveur)

        root.addLayout(self._corps)

    def _rafraichir_file(self):
        """Recrée la liste des cartes de commandes."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(8)

        section = QLabel("FILE D'ATTENTE")
        section.setObjectName("sectionTitre")
        layout.addWidget(section)
        layout.addSpacing(4)

        on_change = self._changer_statut if self._mode_serveur else None

        for cmd in self._commandes:
            carte = CarteCommande(cmd, on_change)
            layout.addWidget(carte)

        if not self._commandes:
            vide = QLabel("Aucune commande en cours")
            vide.setObjectName("videLabel")
            vide.setAlignment(Qt.AlignCenter)
            layout.addWidget(vide)

        layout.addStretch()
        self._scroll_area.setWidget(content)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _toggle_serveur(self):
        if self._mode_serveur:
            self._deconnecter()
        else:
            dialog = DialogMotDePasse(self)
            if dialog.exec_() == QDialog.Accepted:
                self._mode_serveur = True
                self._panneau_serveur.setVisible(True)
                self._btn_serveur.setText("  Mode serveur actif")
                self._btn_serveur.setIcon(
                    qta.icon(ICO_UNLOCK, color="#0A6647")
                )
                self._rafraichir_file()

    def _deconnecter(self):
        self._mode_serveur = False
        self._panneau_serveur.setVisible(False)
        self._btn_serveur.setText("  Mode serveur")
        self._btn_serveur.setIcon(
            qta.icon(ICO_LOCK, color=COULEURS["texte"])
        )
        self._rafraichir_file()

    def _changer_statut(self, num_table: int, nouveau_statut: str):
        """Appelé par les boutons serveur sur chaque CarteCommande."""
        for cmd in self._commandes:
            if cmd["table"] == num_table:
                cmd["statut"] = nouveau_statut
                if nouveau_statut == "Prête":
                    cmd["temps_estime"] = 0
                break
        self._rafraichir_file()

    def _ajouter_commande(self, commande: dict):
        """Ajoute une nouvelle commande à la file."""
        self._commandes.append(commande)
        self._rafraichir_file()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _apply_styles(self):
        c = COULEURS
        self.setStyleSheet(f"""
            QWidget {{ background: {c['fond']}; font-family: "Segoe UI", "SF Pro Display", sans-serif; }}

            QPushButton#btnRetour {{
                background: transparent; border: none;
                color: {c['texte_secondaire']}; font-size: 13px; padding: 4px 8px;
            }}
            QPushButton#btnRetour:hover {{ color: {c['texte']}; }}

            QLabel#pageTitre {{
                font-size: 17px; font-weight: 600; color: {c['texte']};
            }}
            QPushButton#btnServeur {{
                background: {c['surface']}; border: 1px solid {c['bordure']};
                border-radius: 8px; font-size: 12px; font-weight: 500;
                color: {c['texte']}; padding: 6px 14px;
            }}
            QPushButton#btnServeur:hover {{ background: #F1EFE8; }}

            QFrame#separateur {{ color: {c['bordure']}; background: {c['bordure']}; max-height:1px; max-width:1px; }}

            QLabel#sectionTitre {{
                font-size: 11px; font-weight: 600;
                color: {c['texte_secondaire']}; letter-spacing: 2px;
            }}
            QLabel#videLabel {{ font-size: 14px; color: {c['texte_secondaire']}; }}

            QFrame#carteCommande {{
                background: {c['surface']};
                border: 1px solid {c['bordure']};
                border-radius: 10px;
            }}
            QFrame#carteCommande:hover {{ background: #F7F6F2; border-color: #C8C6BF; }}

            QLabel#cmdTableNom {{ font-size: 14px; font-weight: 500; color: {c['texte']}; }}
            QLabel#cmdTemps    {{ font-size: 12px; color: {c['texte_secondaire']}; }}

            QFrame#progressBar {{
                background: {c['bordure']}; border-radius: 2px;
            }}
        """)