# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:11:02 2026

@author: owena
"""

"""
views/page_carte.py
Page Carte : affichage des articles + suivi de commande en temps réel.

Dépendances :
    pip install PyQt5 qtawesome
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
import qtawesome as qta

# ── Imports des classes de Marine ──────────────────────────────────────────
from models.article_carte import Entree, PlatPrincipal, Dessert, Boisson
from models.ingredient import Ingredient


# ── Palette de couleurs (modifier ici pour changer le thème) ───────────────
COULEURS = {
    "fond":          "#FAFAF8",
    "surface":       "#FFFFFF",
    "bordure":       "#E8E6E0",
    "texte":         "#1A1A18",
    "texte_secondaire": "#888780",
    "accent":        "#2C2C2A",

    # Couleurs par type d'article  (fond badge, couleur texte, couleur icône)
    "Entrée":   ("#E8F5EE", "#0A6647", "#0A6647"),
    "Plat":     ("#EEEDFE", "#4A41A7", "#4A41A7"),
    "Dessert":  ("#FEF3E2", "#8A5200", "#8A5200"),
    "Boisson":  ("#E3F0FB", "#1457A0", "#1457A0"),
}

# Icônes qtawesome par type (Font Awesome 5 Solid)
ICONES = {
    "Entrée":  "fa5s.leaf",
    "Plat":    "fa5s.utensils",
    "Dessert": "fa5s.ice-cream",
    "Boisson": "fa5s.wine-glass-alt",
}

# Icônes de navigation
ICO_RETOUR   = "fa5s.arrow-left"
ICO_AJOUTER  = "fa5s.plus"
ICO_SUPPR    = "fa5s.times"
ICO_VALIDER  = "fa5s.check"
ICO_ALLERGENE = "fa5s.exclamation-triangle"
ICO_TABLE    = "fa5s.chair"


# ── Données de démonstration ────────────────────────────────────────────────
# À remplacer par un vrai chargement (fichier JSON, BDD…) quand vous serez prêts

def _carte_demo():
    return [
        Entree(1, "Salade aux noix",
               "Salade verte, noix torréfiées, vinaigrette miel-moutarde",
               7.50, 5, [Ingredient("Noix", 30, "g", allergene=True)]),
        Entree(2, "Soupe à l'oignon",
               "Soupe gratinée maison, croûtons dorés",
               6.00, 10, [Ingredient("Gluten", 5, "g", allergene=True)],
               servie_chaude=True),
        PlatPrincipal(3, "Magret de canard",
                      "Magret poêlé, sauce aux cèpes, pommes sarladaises",
                      22.00, 20,
                      [Ingredient("Gluten", 10, "g", allergene=True)],
                      "Gratin dauphinois"),
        PlatPrincipal(4, "Saumon grillé",
                      "Pavé de saumon, beurre citron-aneth",
                      18.50, 15, [], "Riz basmati"),
        Dessert(5, "Moelleux au chocolat",
                "Fondant tiède, cœur coulant, boule de glace vanille",
                6.50, 15,
                [Ingredient("Œufs", 2, "unité", allergene=True),
                 Ingredient("Lait", 10, "cl", allergene=True)]),
        Dessert(6, "Tarte tatin",
                "Tarte aux pommes caramélisées, crème fraîche",
                5.50, 10, [], fait_maison=True),
        Boisson(7, "Eau minérale", "Eau plate ou gazeuse", 2.50, 50),
        Boisson(8, "Bordeaux rouge",
                "Appellation contrôlée, tanins élégants",
                8.00, 15, est_alcoolisee=True, temperature_service="ambiante"),
    ]


# ── Widget d'un article de la carte ─────────────────────────────────────────

class CarteArticleWidget(QFrame):
    """
    Ligne représentant un article dans le panneau carte.

    MODIFIER ICI pour :
    - changer l'apparence d'une ligne  → _build()
    - changer les couleurs / tailles   → COULEURS / ICONES en haut du fichier
    """

    def __init__(self, article, on_ajouter):
        super().__init__()
        self.article = article
        self._build(on_ajouter)

    def _build(self, on_ajouter):
        self.setObjectName("articleRow")
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(14)

        type_art = self.article.get_type()
        fond, texte_c, ico_c = COULEURS.get(type_art, ("#EEE", "#333", "#333"))

        # ── Icône type (cercle coloré) ──
        ico_container = QLabel()
        ico_container.setFixedSize(36, 36)
        ico_container.setAlignment(Qt.AlignCenter)
        ico_container.setStyleSheet(
            f"background:{fond}; border-radius:18px;"
        )
        ico = qta.icon(ICONES.get(type_art, "fa5s.circle"), color=ico_c)
        ico_container.setPixmap(ico.pixmap(QSize(16, 16)))

        # ── Nom + description ──
        infos = QVBoxLayout()
        infos.setSpacing(2)
        infos.setContentsMargins(0, 0, 0, 0)

        nom = QLabel(self.article.nom)
        nom.setObjectName("articleNom")

        desc = QLabel(self.article.description)
        desc.setObjectName("articleDesc")
        desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        infos.addWidget(nom)
        infos.addWidget(desc)

        # ── Allergènes ──
        allergenes = self.article.get_allergenes()
        if allergenes:
            alg_row = QHBoxLayout()
            alg_row.setSpacing(4)
            alg_row.setContentsMargins(0, 0, 0, 0)
            alg_ico = QLabel()
            alg_ico.setPixmap(
                qta.icon(ICO_ALLERGENE, color="#C0392B").pixmap(QSize(11, 11))
            )
            alg_txt = QLabel(", ".join(allergenes))
            alg_txt.setObjectName("allergene")
            alg_row.addWidget(alg_ico)
            alg_row.addWidget(alg_txt)
            alg_row.addStretch()
            infos.addLayout(alg_row)

        # ── Prix ──
        prix = QLabel(f"{self.article.prix:.2f} €")
        prix.setObjectName("articlePrix")
        prix.setFixedWidth(65)
        prix.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # ── Bouton ajouter ──
        btn = QPushButton()
        btn.setObjectName("btnAjouter")
        btn.setFixedSize(32, 32)
        btn.setIcon(qta.icon(ICO_AJOUTER, color="#FAFAF8"))
        btn.setIconSize(QSize(14, 14))
        btn.setToolTip("Ajouter à la commande")
        btn.clicked.connect(lambda: on_ajouter(self.article))

        # ── Indisponible ──
        if not self.article.est_disponible():
            self.setEnabled(False)
            self.setObjectName("articleRowIndispo")
            btn.setToolTip("Article indisponible")

        layout.addWidget(ico_container)
        layout.addLayout(infos, stretch=1)
        layout.addWidget(prix)
        layout.addWidget(btn)


# ── Panneau commande (droite) ────────────────────────────────────────────────

class LigneCommande(QWidget):
    """Une ligne dans le récapitulatif de commande."""

    def __init__(self, article, on_supprimer):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        nom = QLabel(article.nom)
        nom.setObjectName("cmdNom")
        nom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        prix = QLabel(f"{article.prix:.2f} €")
        prix.setObjectName("cmdPrix")
        prix.setFixedWidth(55)
        prix.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn_del = QPushButton()
        btn_del.setObjectName("btnSupprimer")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(qta.icon(ICO_SUPPR, color="#BBBBBB"))
        btn_del.setIconSize(QSize(10, 10))
        btn_del.clicked.connect(on_supprimer)

        layout.addWidget(nom)
        layout.addWidget(prix)
        layout.addWidget(btn_del)


class CommandeWidget(QWidget):
    """
    Panneau droit : suivi de la commande en cours.

    MODIFIER ICI pour :
    - brancher Commande de Marine  → _valider()
    - changer le nombre de tables  → _table_plus() / _table_moins()
    """

    def __init__(self):
        super().__init__()
        self._articles = []
        self._num_table = 1
        self._build()

    def _build(self):
        self.setObjectName("panneauCommande")
        self.setFixedWidth(270)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(0)

        # ── Titre ──
        titre = QLabel("Commande")
        titre.setObjectName("cmdTitre")
        layout.addWidget(titre)
        layout.addSpacing(16)

        # ── Sélecteur de table ──
        table_row = QHBoxLayout()
        table_row.setSpacing(6)
        ico_table = QLabel()
        ico_table.setPixmap(
            qta.icon(ICO_TABLE, color=COULEURS["texte_secondaire"]).pixmap(QSize(14, 14))
        )
        lbl_table = QLabel("Table")
        lbl_table.setObjectName("cmdLabel")

        self._table_display = QLabel(str(self._num_table))
        self._table_display.setObjectName("tableNum")
        self._table_display.setFixedWidth(24)
        self._table_display.setAlignment(Qt.AlignCenter)

        btn_m = QPushButton("−")
        btn_p = QPushButton("+")
        for b in (btn_m, btn_p):
            b.setObjectName("btnTable")
            b.setFixedSize(26, 26)
        btn_m.clicked.connect(self._table_moins)
        btn_p.clicked.connect(self._table_plus)

        table_row.addWidget(ico_table)
        table_row.addWidget(lbl_table)
        table_row.addStretch()
        table_row.addWidget(btn_m)
        table_row.addWidget(self._table_display)
        table_row.addWidget(btn_p)
        layout.addLayout(table_row)
        layout.addSpacing(16)

        self._sep(layout)
        layout.addSpacing(12)

        # ── Liste scrollable des articles commandés ──
        self._liste_layout = QVBoxLayout()
        self._liste_layout.setSpacing(0)
        self._liste_layout.addStretch()

        scroll_content = QWidget()
        scroll_content.setLayout(self._liste_layout)
        scroll = QScrollArea()
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        layout.addWidget(scroll, stretch=1)

        layout.addSpacing(12)
        self._sep(layout)
        layout.addSpacing(12)

        # ── Total ──
        total_row = QHBoxLayout()
        lbl_total = QLabel("Total")
        lbl_total.setObjectName("cmdLabel")
        self._total_label = QLabel("0,00 €")
        self._total_label.setObjectName("totalLabel")
        total_row.addWidget(lbl_total)
        total_row.addStretch()
        total_row.addWidget(self._total_label)
        layout.addLayout(total_row)
        layout.addSpacing(14)

        # ── Bouton valider ──
        self._btn_valider = QPushButton("  Valider la commande")
        self._btn_valider.setObjectName("btnValider")
        self._btn_valider.setIcon(qta.icon(ICO_VALIDER, color="#FAFAF8"))
        self._btn_valider.setIconSize(QSize(14, 14))
        self._btn_valider.setFixedHeight(42)
        self._btn_valider.clicked.connect(self._valider)
        layout.addWidget(self._btn_valider)

    # ── API publique ──────────────────────────────────────────────────────────

    def ajouter_article(self, article):
        """Appelé depuis CarteArticleWidget quand on clique sur +."""
        self._articles.append(article)
        self._rafraichir()

    # ── Méthodes internes ─────────────────────────────────────────────────────

    def _supprimer(self, index):
        self._articles.pop(index)
        self._rafraichir()

    def _rafraichir(self):
        # Vider la liste (sauf le stretch en bas)
        while self._liste_layout.count() > 1:
            item = self._liste_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for i, article in enumerate(self._articles):
            ligne = LigneCommande(article, lambda _, idx=i: self._supprimer(idx))
            self._liste_layout.insertWidget(
                self._liste_layout.count() - 1, ligne
            )

        total = sum(a.prix for a in self._articles)
        self._total_label.setText(f"{total:.2f} €")

    def _valider(self):
        if not self._articles:
            return
        # ── Brancher Commande de Marine ici quand elle sera prête ──
        # from models.commande import Commande
        # cmd = Commande(self._num_table)
        # for a in self._articles:
        #     cmd.ajouter(a)
        # cmd.envoyer_cuisine()

        print(f"[Commande] Table {self._num_table} | "
              f"{len(self._articles)} articles | "
              f"Total : {sum(a.prix for a in self._articles):.2f} €")
        self._articles.clear()
        self._rafraichir()

    def _table_moins(self):
        if self._num_table > 1:
            self._num_table -= 1
            self._table_display.setText(str(self._num_table))

    def _table_plus(self):
        self._num_table += 1
        self._table_display.setText(str(self._num_table))

    @staticmethod
    def _sep(layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separateur")
        layout.addWidget(line)


# ── Page principale Carte ────────────────────────────────────────────────────

class PageCarte(QWidget):
    """
    Fenêtre Carte : panneau gauche (articles) + panneau droit (commande).

    STRUCTURE :
        _build()         → construit les widgets
        _apply_styles()  → tout le style QSS (couleurs, polices, marges)

    Pour changer l'apparence globale : modifier uniquement _apply_styles().
    Pour changer la structure        : modifier _build().
    """

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self._build()
        self._apply_styles()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Barre de navigation ──
        navbar = QHBoxLayout()
        navbar.setContentsMargins(20, 14, 20, 14)

        btn_retour = QPushButton("  Accueil")
        btn_retour.setObjectName("btnRetour")
        btn_retour.setIcon(qta.icon(ICO_RETOUR, color=COULEURS["texte_secondaire"]))
        btn_retour.setIconSize(QSize(13, 13))
        btn_retour.clicked.connect(lambda: self.main.aller_a(0))

        titre_page = QLabel("La Carte")
        titre_page.setObjectName("pageTitre")

        navbar.addWidget(btn_retour)
        navbar.addStretch()
        navbar.addWidget(titre_page)
        navbar.addStretch()
        # Espace symétrique à droite pour centrer le titre
        spacer = QWidget()
        spacer.setFixedWidth(btn_retour.sizeHint().width())
        navbar.addWidget(spacer)

        root.addLayout(navbar)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separateur")
        root.addWidget(sep)

        # ── Corps : carte gauche + commande droite ──
        corps = QHBoxLayout()
        corps.setContentsMargins(0, 0, 0, 0)
        corps.setSpacing(0)

        # Panneau commande (instancié en premier car les widgets carte s'y branchent)
        self._commande = CommandeWidget()

        # Panneau carte scrollable
        carte_scroll = QScrollArea()
        carte_scroll.setWidgetResizable(True)
        carte_scroll.setFrameShape(QFrame.NoFrame)

        carte_content = QWidget()
        carte_layout = QVBoxLayout(carte_content)
        carte_layout.setContentsMargins(20, 16, 20, 24)
        carte_layout.setSpacing(4)

        type_courant = None
        for article in _carte_demo():
            # En-tête de section à chaque changement de type
            if article.get_type() != type_courant:
                type_courant = article.get_type()
                if carte_layout.count() > 0:
                    carte_layout.addSpacing(12)
                section = QLabel(type_courant.upper() + "S")
                section.setObjectName("sectionTitre")
                carte_layout.addWidget(section)
                carte_layout.addSpacing(4)

            widget = CarteArticleWidget(
                article, self._commande.ajouter_article
            )
            carte_layout.addWidget(widget)

        carte_layout.addStretch()
        carte_scroll.setWidget(carte_content)

        corps.addWidget(carte_scroll, stretch=1)

        # Séparateur vertical
        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setObjectName("separateur")
        corps.addWidget(vsep)

        corps.addWidget(self._commande)
        root.addLayout(corps)

    def _apply_styles(self):
        """
        Tout le style visuel est ici.
        Modifier cette méthode pour changer couleurs, polices, arrondis, etc.
        """
        c = COULEURS
        self.setStyleSheet(f"""
            /* ── Fond général ── */
            QWidget {{
                background: {c['fond']};
                font-family: "Segoe UI", "SF Pro Display", sans-serif;
            }}

            /* ── Navbar ── */
            QPushButton#btnRetour {{
                background: transparent;
                border: none;
                color: {c['texte_secondaire']};
                font-size: 13px;
                padding: 4px 8px;
            }}
            QPushButton#btnRetour:hover {{ color: {c['texte']}; }}
            QLabel#pageTitre {{
                font-size: 17px;
                font-weight: 600;
                color: {c['texte']};
            }}

            /* ── Séparateurs ── */
            QFrame#separateur {{
                color: {c['bordure']};
                background: {c['bordure']};
                max-height: 1px;
                max-width: 1px;
            }}

            /* ── Section titre ── */
            QLabel#sectionTitre {{
                font-size: 11px;
                font-weight: 600;
                color: {c['texte_secondaire']};
                letter-spacing: 2px;
            }}

            /* ── Ligne article ── */
            QFrame#articleRow {{
                background: {c['surface']};
                border: 1px solid {c['bordure']};
                border-radius: 10px;
            }}
            QFrame#articleRow:hover {{
                border-color: #C8C6BF;
                background: #F7F6F2;
            }}
            QFrame#articleRowIndispo {{
                background: #F5F5F3;
                border: 1px solid {c['bordure']};
                border-radius: 10px;
                opacity: 0.5;
            }}
            QLabel#articleNom {{
                font-size: 14px;
                font-weight: 500;
                color: {c['texte']};
            }}
            QLabel#articleDesc {{
                font-size: 12px;
                color: {c['texte_secondaire']};
            }}
            QLabel#allergene {{
                font-size: 11px;
                color: #B53030;
            }}
            QLabel#articlePrix {{
                font-size: 14px;
                font-weight: 500;
                color: {c['texte']};
            }}
            QPushButton#btnAjouter {{
                background: {c['accent']};
                border: none;
                border-radius: 8px;
            }}
            QPushButton#btnAjouter:hover {{
                background: #444440;
            }}
            QPushButton#btnAjouter:disabled {{
                background: #CCCBC7;
            }}

            /* ── Panneau commande ── */
            QWidget#panneauCommande {{
                background: {c['surface']};
            }}
            QLabel#cmdTitre {{
                font-size: 16px;
                font-weight: 600;
                color: {c['texte']};
            }}
            QLabel#cmdLabel {{
                font-size: 13px;
                color: {c['texte_secondaire']};
            }}
            QLabel#tableNum {{
                font-size: 14px;
                font-weight: 600;
                color: {c['texte']};
            }}
            QPushButton#btnTable {{
                background: #F1EFE8;
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: 400;
                color: {c['texte']};
            }}
            QPushButton#btnTable:hover {{
                background: #E5E3DC;
            }}
            QLabel#cmdNom {{
                font-size: 13px;
                color: {c['texte']};
            }}
            QLabel#cmdPrix {{
                font-size: 13px;
                color: {c['texte_secondaire']};
            }}
            QPushButton#btnSupprimer {{
                background: transparent;
                border: none;
                border-radius: 4px;
            }}
            QPushButton#btnSupprimer:hover {{
                background: #FCEBEB;
            }}
            QLabel#totalLabel {{
                font-size: 20px;
                font-weight: 600;
                color: {c['texte']};
            }}
            QPushButton#btnValider {{
                background: {c['accent']};
                color: #FAFAF8;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton#btnValider:hover {{
                background: #444440;
            }}
        """)