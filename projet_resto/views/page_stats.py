"""
views/page_stats.py — statistiques du service

Données affichées (calculées depuis les vraies commandes) :
    - Chiffre d'affaires total du service
    - Nombre de commandes traitées
    - Articles les plus commandés (top 5)
    - Temps de préparation moyen par type
    - Prix moyen par type (depuis Carte.get_prix_moyen_par_type())
    - Répartition des commandes par statut
"""
from collections import Counter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
import qtawesome as qta

from models.statuts import StatutCommande
from models.commande import Commande

C = {
    "fond": "#FAFAF8", "surface": "#FFFFFF", "bordure": "#E8E6E0",
    "texte": "#1A1A18", "sec": "#888780", "accent": "#2C2C2A",
}

COULEURS_STATUT = {
    StatutCommande.EN_ATTENTE:     "#E8A020",
    StatutCommande.EN_PREPARATION: "#4A41A7",
    StatutCommande.PRET:           "#0A6647",
    StatutCommande.SERVI:          "#888780",
    StatutCommande.PAYE:           "#1A1A18",
}


# ── Widgets de stats ──────────────────────────────────────────────────────────

class KpiCard(QFrame):
    """Grande carte avec une valeur chiffrée et un label."""
    def __init__(self, icone: str, valeur: str, label: str, couleur: str = "#2C2C2A"):
        super().__init__()
        self.setObjectName("kpiCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        ic = QLabel()
        ic.setAlignment(Qt.AlignCenter)
        ic.setPixmap(qta.icon(icone, color=couleur).pixmap(QSize(24, 24)))

        val = QLabel(valeur)
        val.setObjectName("kpiValeur")
        val.setAlignment(Qt.AlignCenter)
        val.setStyleSheet(f"color:{couleur};")

        lbl = QLabel(label)
        lbl.setObjectName("kpiLabel")
        lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(ic)
        layout.addWidget(val)
        layout.addWidget(lbl)


class BarreHorizontale(QWidget):
    """Barre de progression horizontale avec label et valeur."""
    def __init__(self, label: str, valeur: str, pct: float, couleur: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        top = QHBoxLayout()
        lbl = QLabel(label); lbl.setObjectName("barLabel")
        val = QLabel(valeur); val.setObjectName("barValeur")
        top.addWidget(lbl); top.addStretch(); top.addWidget(val)
        layout.addLayout(top)

        track = QFrame(); track.setObjectName("barTrack"); track.setFixedHeight(6)
        fill = QFrame(track)
        fill.setFixedHeight(6)
        fill.setStyleSheet(f"background:{couleur}; border-radius:3px;")
        fill.setFixedWidth(max(6, int(400 * min(pct, 1.0))))
        layout.addWidget(track)


# ── Page Stats ────────────────────────────────────────────────────────────────

class PageStats(QWidget):
    """
    Page Statistiques.

    Reçoit la liste des commandes depuis PageCuisine (via MainWindow)
    et calcule les indicateurs en temps réel à chaque affichage.

    MODIFIER get_commandes() dans MainWindow pour passer les vraies données.
    """

    def __init__(self, main_window, get_commandes=None):
        """
        get_commandes : callable() → List[Commande]
            Fonction appelée pour récupérer toutes les commandes du service.
            Si None, affiche des données de démonstration.
        """
        super().__init__()
        self.main = main_window
        self._get_commandes = get_commandes or (lambda: [])
        self._build()
        self._apply_styles()

    def showEvent(self, event):
        """Recalcule les stats à chaque fois qu'on navigue vers cette page."""
        super().showEvent(event)
        self._rafraichir()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # Navbar
        nb = QHBoxLayout(); nb.setContentsMargins(20, 14, 20, 14)
        btn_r = QPushButton("  Accueil"); btn_r.setObjectName("btnRetour")
        btn_r.setIcon(qta.icon("mdi.chevron-left", color=C["sec"])); btn_r.setIconSize(QSize(13, 13))
        btn_r.clicked.connect(lambda: self.main.aller_a(0))
        tp = QLabel("Statistiques"); tp.setObjectName("pageTitre")
        btn_refresh = QPushButton(); btn_refresh.setObjectName("btnRefresh")
        btn_refresh.setIcon(qta.icon("mdi.refresh", color=C["sec"])); btn_refresh.setIconSize(QSize(16, 16))
        btn_refresh.setFixedSize(36, 36); btn_refresh.setToolTip("Actualiser")
        btn_refresh.clicked.connect(self._rafraichir)
        sp = QWidget(); sp.setFixedWidth(54)
        nb.addWidget(btn_r); nb.addStretch(); nb.addWidget(tp); nb.addStretch()
        nb.addWidget(btn_refresh); nb.addWidget(sp)
        root.addLayout(nb)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("separateur")
        root.addWidget(sep)

        # Zone scrollable
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(24, 20, 24, 24)
        self._content_layout.setSpacing(24)
        scroll.setWidget(self._content)
        root.addWidget(scroll)

    def _rafraichir(self):
        """Vide et recrée toute la zone de contenu."""
        # Vider
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        commandes = self._get_commandes()
        self._build_kpis(commandes)
        self._build_top_articles(commandes)
        self._build_temps_prep(commandes)
        self._build_repartition(commandes)
        self._content_layout.addStretch()

    # ── Sections ─────────────────────────────────────────────────────────────

    def _build_kpis(self, commandes):
        """4 grandes cartes : CA, commandes, articles, ticket moyen."""
        self._section_titre("Vue d'ensemble")
        row = QHBoxLayout(); row.setSpacing(12)

        ca = sum(c.total() for c in commandes)
        nb_cmd = len(commandes)
        nb_art = sum(c.nombre_articles() for c in commandes)
        ticket = (ca / nb_cmd) if nb_cmd else 0

        row.addWidget(KpiCard("mdi.currency-eur",   f"{ca:.2f} €",   "Chiffre d'affaires", "#0A6647"))
        row.addWidget(KpiCard("mdi.receipt",         str(nb_cmd),     "Commandes",           "#4A41A7"))
        row.addWidget(KpiCard("mdi.food",             str(nb_art),     "Articles servis",     "#8A5200"))
        row.addWidget(KpiCard("mdi.chart-line",      f"{ticket:.2f} €","Ticket moyen",        "#1457A0"))

        container = QWidget(); container.setLayout(row)
        self._content_layout.addWidget(container)

    def _build_top_articles(self, commandes):
        """Top 5 des articles les plus commandés."""
        self._section_titre("Articles les plus commandés")
        compteur = Counter()
        for cmd in commandes:
            for ligne in cmd.lignes:
                compteur[ligne.article.nom] += ligne.quantite

        if not compteur:
            self._vide("Aucun article commandé pour l'instant")
            return

        max_qte = max(compteur.values())
        couleurs = ["#0A6647", "#4A41A7", "#8A5200", "#1457A0", "#888780"]

        for i, (nom, qte) in enumerate(compteur.most_common(5)):
            barre = BarreHorizontale(
                label=nom,
                valeur=f"{qte} commande{'s' if qte > 1 else ''}",
                pct=qte / max_qte,
                couleur=couleurs[i % len(couleurs)]
            )
            self._content_layout.addWidget(barre)

    def _build_temps_prep(self, commandes):
        """Temps moyen de traitement par type d'article."""
        self._section_titre("Temps de préparation moyen")
        temps_par_type: dict[str, list] = {}
        for cmd in commandes:
            for ligne in cmd.lignes:
                t = ligne.article.get_temps_preparation()
                if t > 0:
                    typ = ligne.article.get_type()
                    temps_par_type.setdefault(typ, []).append(t)

        if not temps_par_type:
            self._vide("Pas encore de données")
            return

        couleurs = {"Entrée": "#0A6647", "Plat": "#4A41A7",
                    "Dessert": "#8A5200", "Boisson": "#1457A0"}
        max_t = max(sum(v)/len(v) for v in temps_par_type.values())

        for typ, valeurs in sorted(temps_par_type.items()):
            moy = sum(valeurs) / len(valeurs)
            barre = BarreHorizontale(
                label=typ,
                valeur=f"{moy:.0f} min",
                pct=moy / max_t if max_t else 0,
                couleur=couleurs.get(typ, C["accent"])
            )
            self._content_layout.addWidget(barre)

    def _build_repartition(self, commandes):
        """Répartition des commandes par statut."""
        self._section_titre("Statut des commandes")
        if not commandes:
            self._vide("Aucune commande")
            return

        compteur = Counter(c.statut for c in commandes)
        total = len(commandes)

        for statut in StatutCommande:
            n = compteur.get(statut, 0)
            if n == 0:
                continue
            barre = BarreHorizontale(
                label=statut.value,
                valeur=f"{n} ({int(n/total*100)} %)",
                pct=n / total,
                couleur=COULEURS_STATUT.get(statut, C["accent"])
            )
            self._content_layout.addWidget(barre)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _section_titre(self, texte: str):
        lbl = QLabel(texte.upper())
        lbl.setObjectName("sectionTitre")
        self._content_layout.addWidget(lbl)

    def _vide(self, texte: str):
        lbl = QLabel(texte)
        lbl.setObjectName("videLabel")
        lbl.setAlignment(Qt.AlignCenter)
        self._content_layout.addWidget(lbl)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ background:{C['fond']}; font-family:"Segoe UI","SF Pro Display",sans-serif; }}
            QPushButton#btnRetour {{ background:transparent; border:none; color:{C['sec']}; font-size:13px; padding:4px 8px; }}
            QPushButton#btnRetour:hover {{ color:{C['texte']}; }}
            QPushButton#btnRefresh {{ background:transparent; border:1px solid {C['bordure']}; border-radius:8px; }}
            QPushButton#btnRefresh:hover {{ background:#F1EFE8; }}
            QLabel#pageTitre {{ font-size:17px; font-weight:600; color:{C['texte']}; }}
            QFrame#separateur {{ color:{C['bordure']}; background:{C['bordure']}; max-height:1px; max-width:1px; }}
            QLabel#sectionTitre {{ font-size:11px; font-weight:600; color:{C['sec']}; letter-spacing:2px; margin-top:4px; }}
            QLabel#videLabel {{ font-size:13px; color:{C['sec']}; padding:12px 0; }}

            QFrame#kpiCard {{ background:{C['surface']}; border:1px solid {C['bordure']}; border-radius:12px; min-width:140px; }}
            QLabel#kpiValeur {{ font-size:22px; font-weight:600; }}
            QLabel#kpiLabel  {{ font-size:12px; color:{C['sec']}; }}

            QLabel#barLabel  {{ font-size:13px; color:{C['texte']}; }}
            QLabel#barValeur {{ font-size:13px; color:{C['sec']}; }}
            QFrame#barTrack  {{ background:{C['bordure']}; border-radius:3px; }}
        """)
