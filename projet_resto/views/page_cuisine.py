"""
views/page_cuisine.py — branchée sur les classes de Marine

Branchements :
    StatutCommande          → vrais statuts (EN_ATTENTE, EN_PREPARATION, PRET, SERVI)
    Commande.changer_statut()  → transitions validées par Marine
    ObservateurCuisine      → reçoit les nouvelles commandes automatiquement
    ObservateurServeur      → reçoit les commandes prêtes
    Commande.duree_preparation() → temps réel depuis la création
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QDialog, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QTimer
import qtawesome as qta

from models.statuts import StatutCommande
from models.commande import Commande
from utils.observer import ObservateurCuisine, ObservateurServeur

MOT_DE_PASSE = "marinexowen"

C = {
    "fond": "#FAFAF8", "surface": "#FFFFFF", "bordure": "#E8E6E0",
    "texte": "#1A1A18", "sec": "#888780", "accent": "#2C2C2A",
    "fond_srv": "#F5F4F0",
    StatutCommande.EN_ATTENTE:    ("#FEF3E2", "#8A5200",  "#E8A020"),
    StatutCommande.EN_PREPARATION:("#EEEDFE", "#4A41A7",  "#4A41A7"),
    StatutCommande.PRET:          ("#E8F5EE", "#0A6647",  "#0A6647"),
    StatutCommande.SERVI:         ("#F0F0F0", "#555555",  "#888780"),
}

# Progression visuelle par statut
PROGRESSION = {
    StatutCommande.EN_ATTENTE:     15,
    StatutCommande.EN_PREPARATION: 60,
    StatutCommande.PRET:          100,
    StatutCommande.SERVI:         100,
}


# ── Dialog mot de passe ───────────────────────────────────────────────────────
class DialogMotDePasse(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accès serveur")
        self.setFixedSize(300, 190)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(10)
        titre = QLabel("Mode serveur"); titre.setObjectName("modalTitre"); titre.setAlignment(Qt.AlignCenter)
        sous = QLabel("Entrez le code d'accès"); sous.setObjectName("modalSous"); sous.setAlignment(Qt.AlignCenter)
        self._champ = QLineEdit(); self._champ.setObjectName("champMdp")
        self._champ.setEchoMode(QLineEdit.Password); self._champ.setAlignment(Qt.AlignCenter)
        self._champ.setPlaceholderText("••••••••••••"); self._champ.returnPressed.connect(self._verifier)
        self._err = QLabel(""); self._err.setObjectName("erreurLabel"); self._err.setAlignment(Qt.AlignCenter)
        btn = QPushButton("Accéder"); btn.setObjectName("btnConfirmer")
        btn.setFixedHeight(38); btn.clicked.connect(self._verifier)
        layout.addWidget(titre); layout.addWidget(sous); layout.addSpacing(6)
        layout.addWidget(self._champ); layout.addWidget(self._err); layout.addWidget(btn)
        self.setStyleSheet(f"""
            QDialog {{ background:#FFFFFF; border:1px solid #E8E6E0; border-radius:14px; }}
            QLabel#modalTitre {{ font-size:16px; font-weight:600; color:#1A1A18; }}
            QLabel#modalSous  {{ font-size:12px; color:#888780; }}
            QLabel#erreurLabel {{ font-size:12px; color:#B53030; }}
            QLineEdit#champMdp {{ padding:10px; border:1px solid #E8E6E0; border-radius:8px;
                font-size:16px; letter-spacing:4px; color:#1A1A18; }}
            QLineEdit#champMdp:focus {{ border-color:#2C2C2A; }}
            QPushButton#btnConfirmer {{ background:#2C2C2A; color:#FAFAF8; border:none;
                border-radius:8px; font-size:13px; font-weight:500; }}
            QPushButton#btnConfirmer:hover {{ background:#444440; }}
        """)

    def _verifier(self):
        if self._champ.text() == MOT_DE_PASSE:
            self.accept()
        else:
            self._err.setText("Code incorrect")
            self._champ.clear(); self._champ.setFocus()


# ── Carte d'une commande ──────────────────────────────────────────────────────
class CarteCommande(QFrame):
    """
    Affiche une vraie Commande de Marine.
    En mode serveur, affiche un bouton pour faire avancer le statut.
    """
    def __init__(self, commande: Commande, on_statut_change=None):
        super().__init__()
        self._commande = commande
        self._on_change = on_statut_change
        self.setObjectName("carteCommande")
        self.setFixedHeight(84)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(14)

        statut = self._commande.statut
        fond, texte_c, ico_c = C.get(statut, ("#EEE", "#333", "#888"))

        # Badge table
        bg = "#0A6647" if statut == StatutCommande.PRET else "#2C2C2A"
        badge = QLabel(f"T\n{self._commande.table.numero}")
        badge.setFixedSize(40, 40)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"background:{bg}; color:#FAFAF8; border-radius:10px;"
            f" font-size:12px; font-weight:600;"
        )

        # Infos
        infos = QVBoxLayout(); infos.setSpacing(3); infos.setContentsMargins(0,0,0,0)
        nom = QLabel(f"Table {self._commande.table.numero} — {self._commande.nombre_articles()} article(s)")
        nom.setObjectName("cmdTableNom")

        # Temps réel depuis création (Commande.duree_preparation())
        duree = self._commande.duree_preparation()
        if statut == StatutCommande.PRET:
            temps_txt = "Prête à servir !"
        elif duree == 0:
            temps_txt = "À l'instant"
        else:
            temps_txt = f"Depuis {duree} min"

        temps_row = QHBoxLayout(); temps_row.setSpacing(5); temps_row.setContentsMargins(0,0,0,0)
        ic = QLabel(); ic.setPixmap(qta.icon("mdi.clock-outline", color=C["sec"]).pixmap(12,12))
        tl = QLabel(temps_txt); tl.setObjectName("cmdTemps")
        temps_row.addWidget(ic); temps_row.addWidget(tl); temps_row.addStretch()

        # Barre de progression
        bar = QFrame(); bar.setObjectName("progressBar"); bar.setFixedHeight(3)
        fill = QFrame(bar); fill.setFixedHeight(3)
        pct = PROGRESSION.get(statut, 0)
        fill.setStyleSheet(f"background:{ico_c}; border-radius:2px;")
        fill.setFixedWidth(int(160 * pct / 100))

        infos.addWidget(nom)
        infos.addLayout(temps_row)
        infos.addWidget(bar)

        # Badge statut
        statut_lbl = QLabel(statut.value)
        statut_lbl.setAlignment(Qt.AlignCenter)
        statut_lbl.setFixedWidth(110)
        statut_lbl.setStyleSheet(
            f"background:{fond}; color:{texte_c}; border-radius:12px;"
            f" padding:4px 8px; font-size:11px; font-weight:500;"
        )

        layout.addWidget(badge)
        layout.addLayout(infos, stretch=1)
        layout.addWidget(statut_lbl)

        # Bouton avancer (mode serveur uniquement)
        if self._on_change:
            transitions = statut.transitions_autorisees()
            if transitions:
                prochain = transitions[0]
                btn = QPushButton(f"→ {prochain.value.split()[0]}")
                btn.setObjectName("btnAvancer")
                btn.setFixedHeight(28)
                btn.clicked.connect(
                    lambda: self._on_change(self._commande, prochain)
                )
                layout.addWidget(btn)


# ── Panneau serveur ───────────────────────────────────────────────────────────
class PanneauServeur(QWidget):
    def __init__(self, on_deconnecter):
        super().__init__()
        self._on_deco = on_deconnecter
        self.setObjectName("panneauServeur")
        self.setFixedWidth(220)
        self._build()
        self._apply_styles()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        titre_row = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("mdi.lock-open", color=C["texte"]).pixmap(16,16))
        titre = QLabel("Mode serveur actif"); titre.setObjectName("serveurTitre")
        titre_row.addWidget(ic); titre_row.addWidget(titre); titre_row.addStretch()
        layout.addLayout(titre_row)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("separateur")
        layout.addWidget(sep)

        info = QLabel("Utilisez les boutons\n→ sur chaque commande\npour avancer son statut.")
        info.setObjectName("serveurInfo")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()

        btn_deco = QPushButton("  Se déconnecter")
        btn_deco.setObjectName("btnDeco")
        btn_deco.setIcon(qta.icon("mdi.lock", color=C["sec"]))
        btn_deco.setIconSize(QSize(13,13))
        btn_deco.clicked.connect(self._on_deco)
        layout.addWidget(btn_deco)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget#panneauServeur {{ background:{C['fond_srv']}; border-left:1px solid {C['bordure']}; }}
            QLabel#serveurTitre {{ font-size:13px; font-weight:600; color:{C['texte']}; }}
            QLabel#serveurInfo  {{ font-size:12px; color:{C['sec']}; line-height:1.5; }}
            QFrame#separateur {{ color:{C['bordure']}; max-height:1px; }}
            QPushButton#btnDeco {{ background:transparent; border:1px solid {C['bordure']};
                border-radius:8px; font-size:12px; color:{C['sec']}; padding:8px; }}
            QPushButton#btnDeco:hover {{ background:#ECEAE3; }}
            QPushButton#btnAvancer {{ background:#EEEDFE; color:#4A41A7; border:none;
                border-radius:6px; font-size:11px; font-weight:500; padding:2px 10px; }}
            QPushButton#btnAvancer:hover {{ background:#DDDCFC; }}
        """)


# ── Page Cuisine ──────────────────────────────────────────────────────────────
class PageCuisine(QWidget):
    """
    Expose un ObservateurCuisine public (self.obs_cuisine) que
    MainWindow passe à PageCarte pour brancher les notifications.
    """

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        # Observateurs de Marine
        self.obs_cuisine = ObservateurCuisine()
        self.obs_serveur = ObservateurServeur()
        self._mode_serveur = False
        self._build()
        self._apply_styles()

        # Timer : rafraîchit la file toutes les 30 s (durées en temps réel)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rafraichir_file)
        self._timer.start(30_000)

    def get_toutes_commandes(self):
        """
        Agrège toutes les commandes connues des deux observateurs,
        sans doublon, triées par horodatage de création.
        """
        vues = {}
        for cmd in self.obs_cuisine.nouvelles_commandes:
            vues[cmd.id_commande] = cmd
        for cmd in self.obs_serveur.commandes_pretes:
            vues[cmd.id_commande] = cmd
        return sorted(vues.values(), key=lambda c: c.horodatage_creation)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Navbar
        nb = QHBoxLayout(); nb.setContentsMargins(20,14,20,14)
        btn_r = QPushButton("  Accueil"); btn_r.setObjectName("btnRetour")
        btn_r.setIcon(qta.icon("mdi.chevron-left", color=C["sec"])); btn_r.setIconSize(QSize(13,13))
        btn_r.clicked.connect(lambda: self.main.aller_a(0))
        tp = QLabel("Cuisine"); tp.setObjectName("pageTitre")
        self._btn_srv = QPushButton("  Mode serveur")
        self._btn_srv.setObjectName("btnServeur")
        self._btn_srv.setIcon(qta.icon("mdi.lock", color=C["texte"])); self._btn_srv.setIconSize(QSize(13,13))
        self._btn_srv.clicked.connect(self._toggle_serveur)
        nb.addWidget(btn_r); nb.addStretch(); nb.addWidget(tp); nb.addStretch(); nb.addWidget(self._btn_srv)
        root.addLayout(nb)
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("separateur"); root.addWidget(sep)

        # Corps
        self._corps = QHBoxLayout(); self._corps.setContentsMargins(0,0,0,0); self._corps.setSpacing(0)

        self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True); self._scroll.setFrameShape(QFrame.NoFrame)
        self._rafraichir_file()
        self._corps.addWidget(self._scroll, stretch=1)

        self._panneau_srv = PanneauServeur(self._deconnecter)
        self._panneau_srv.setVisible(False)
        self._corps.addWidget(self._panneau_srv)
        root.addLayout(self._corps)

    def _rafraichir_file(self):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20,16,20,20); layout.setSpacing(8)

        sec = QLabel("FILE D'ATTENTE"); sec.setObjectName("sectionTitre")
        layout.addWidget(sec); layout.addSpacing(4)

        commandes = self.get_toutes_commandes()
        on_change = self._changer_statut if self._mode_serveur else None

        if commandes:
            for cmd in commandes:
                layout.addWidget(CarteCommande(cmd, on_change))
        else:
            vide = QLabel("Aucune commande en cours")
            vide.setObjectName("videLabel"); vide.setAlignment(Qt.AlignCenter)
            layout.addWidget(vide)

        layout.addStretch()
        self._scroll.setWidget(content)

    def _changer_statut(self, commande: Commande, nouveau: StatutCommande):
        """
        Fait avancer le statut via Commande.changer_statut() de Marine.
        Marine gère les transitions invalides (lève ValueError).
        """
        try:
            commande.changer_statut(nouveau)
            # Si la commande est PRET, ObservateurServeur la capte automatiquement
            self._rafraichir_file()
        except ValueError as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Transition invalide", str(e))

    def _toggle_serveur(self):
        if self._mode_serveur:
            self._deconnecter()
        else:
            dlg = DialogMotDePasse(self)
            if dlg.exec_() == QDialog.Accepted:
                self._mode_serveur = True
                self._panneau_srv.setVisible(True)
                self._btn_srv.setText("  Serveur connecté")
                self._btn_srv.setIcon(qta.icon("mdi.lock-open", color="#0A6647"))
                self._rafraichir_file()

    def _deconnecter(self):
        self._mode_serveur = False
        self._panneau_srv.setVisible(False)
        self._btn_srv.setText("  Mode serveur")
        self._btn_srv.setIcon(qta.icon("mdi.lock", color=C["texte"]))
        self._rafraichir_file()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ background:{C['fond']}; font-family:"Segoe UI","SF Pro Display",sans-serif; }}
            QPushButton#btnRetour {{ background:transparent; border:none; color:{C['sec']}; font-size:13px; padding:4px 8px; }}
            QPushButton#btnRetour:hover {{ color:{C['texte']}; }}
            QLabel#pageTitre {{ font-size:17px; font-weight:600; color:{C['texte']}; }}
            QPushButton#btnServeur {{ background:{C['surface']}; border:1px solid {C['bordure']};
                border-radius:8px; font-size:12px; font-weight:500; color:{C['texte']}; padding:6px 14px; }}
            QPushButton#btnServeur:hover {{ background:#F1EFE8; }}
            QFrame#separateur {{ color:{C['bordure']}; background:{C['bordure']}; max-height:1px; max-width:1px; }}
            QLabel#sectionTitre {{ font-size:11px; font-weight:600; color:{C['sec']}; letter-spacing:2px; }}
            QLabel#videLabel {{ font-size:14px; color:{C['sec']}; }}
            QFrame#carteCommande {{ background:{C['surface']}; border:1px solid {C['bordure']}; border-radius:10px; }}
            QFrame#carteCommande:hover {{ background:#F7F6F2; border-color:#C8C6BF; }}
            QLabel#cmdTableNom {{ font-size:14px; font-weight:500; color:{C['texte']}; }}
            QLabel#cmdTemps    {{ font-size:12px; color:{C['sec']}; }}
            QFrame#progressBar {{ background:{C['bordure']}; border-radius:2px; }}
        """)
