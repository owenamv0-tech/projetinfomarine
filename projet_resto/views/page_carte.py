"""
views/page_carte.py — branchée sur les classes de Marine

Branchements :
    Carte.get_tous_les_articles()   → affichage de la carte
    Commande.ajouter_ligne()        → ajout d'un article
    Commande.supprimer_ligne()      → suppression
    Commande.total()                → total en temps réel
    Commande.changer_statut()       → envoi en cuisine (notifie ObservateurCuisine)
    Table.ouvrir_commande()         → crée la commande
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
import qtawesome as qta

from models.carte import Carte
from models.article_carte import Entree, PlatPrincipal, Dessert, Boisson
from models.commande import Commande
from models.statuts import StatutCommande, StatutTable
from models.table import Table
from models.personnel import Serveur
from models.ingredient import Ingredient

# ── Palette ──────────────────────────────────────────────────────────────────
C = {
    "fond": "#FAFAF8", "surface": "#FFFFFF", "bordure": "#E8E6E0",
    "texte": "#1A1A18", "sec": "#888780", "accent": "#2C2C2A",
    "Entrée":  ("#E8F5EE", "#0A6647"), "Plat":    ("#EEEDFE", "#4A41A7"),
    "Dessert": ("#FEF3E2", "#8A5200"), "Boisson": ("#E3F0FB", "#1457A0"),
}
ICONES = {"Entrée": "mdi.food-apple", "Plat": "mdi.food",
          "Dessert": "mdi.cupcake",   "Boisson": "mdi.cup"}

# Serveur et tables par défaut
_SERVEUR = Serveur(1, "Dupont", "Alice")
_TABLES  = {i: Table(i, 4) for i in range(1, 11)}


def _carte_demo() -> Carte:
    """Carte de démonstration. Remplacer par Carte.from_json() plus tard."""
    carte = Carte()
    carte.ajouter_article(Entree(1, "Salade aux noix",
        "Salade verte, noix torréfiées, vinaigrette", 7.50, 5,
        [Ingredient("Noix", 30, "g", allergene=True)]))
    carte.ajouter_article(Entree(2, "Soupe à l'oignon",
        "Gratinée maison, croûtons dorés", 6.00, 10,
        [Ingredient("Gluten", 5, "g", allergene=True)], servie_chaude=True))
    carte.ajouter_article(PlatPrincipal(3, "Magret de canard",
        "Poêlé, sauce cèpes, pommes sarladaises", 22.00, 20,
        [Ingredient("Gluten", 10, "g", allergene=True)], "Gratin dauphinois"))
    carte.ajouter_article(PlatPrincipal(4, "Saumon grillé",
        "Beurre citron-aneth", 18.50, 15, [], "Riz basmati"))
    carte.ajouter_article(Dessert(5, "Moelleux au chocolat",
        "Fondant tiède, glace vanille", 6.50, 15,
        [Ingredient("Œufs", 2, "unité", allergene=True)]))
    carte.ajouter_article(Dessert(6, "Tarte tatin",
        "Pommes caramélisées, crème fraîche", 5.50, 10, [], fait_maison=True))
    carte.ajouter_article(Boisson(7, "Eau minérale", "50 cl", 2.50, 50))
    carte.ajouter_article(Boisson(8, "Bordeaux rouge",
        "15 cl, tanins élégants", 8.00, 15,
        est_alcoolisee=True, temperature_service="ambiante"))
    return carte


# ── Widget article ────────────────────────────────────────────────────────────
class CarteArticleWidget(QFrame):
    def __init__(self, article, on_ajouter):
        super().__init__()
        self.article = article
        self.setObjectName("articleRow")
        self.setFixedHeight(76)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(14)

        fond, ico_c = C.get(article.get_type(), ("#EEE", "#333"))
        ico_lbl = QLabel()
        ico_lbl.setFixedSize(36, 36)
        ico_lbl.setAlignment(Qt.AlignCenter)
        ico_lbl.setStyleSheet(f"background:{fond}; border-radius:18px;")
        ico_lbl.setPixmap(qta.icon(ICONES.get(article.get_type(), "mdi.food"),
            color=ico_c).pixmap(QSize(16, 16)))

        infos = QVBoxLayout()
        infos.setSpacing(1)
        infos.setContentsMargins(0, 0, 0, 0)
        nom_lbl = QLabel(article.nom); nom_lbl.setObjectName("articleNom")
        desc_lbl = QLabel(article.description); desc_lbl.setObjectName("articleDesc")
        desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        infos.addWidget(nom_lbl)
        infos.addWidget(desc_lbl)

        meta = QHBoxLayout(); meta.setSpacing(8); meta.setContentsMargins(0,0,0,0)
        temps = article.get_temps_preparation()
        if temps > 0:
            ic = QLabel(); ic.setPixmap(qta.icon("mdi.clock-outline", color=C["sec"]).pixmap(11,11))
            meta.addWidget(ic)
            meta.addWidget(QLabel(f"{temps} min").__class__(f"{temps} min"))
            tl = QLabel(f"{temps} min"); tl.setObjectName("articleDesc")
            meta.addWidget(ic); meta.addWidget(tl)
        allergenes = article.get_allergenes()
        if allergenes:
            ia = QLabel(); ia.setPixmap(qta.icon("mdi.alert-circle-outline", color="#C0392B").pixmap(11,11))
            al = QLabel(", ".join(allergenes)); al.setObjectName("allergene")
            meta.addWidget(ia); meta.addWidget(al)
        meta.addStretch()
        infos.addLayout(meta)

        prix_lbl = QLabel(f"{article.prix:.2f} €")
        prix_lbl.setObjectName("articlePrix")
        prix_lbl.setFixedWidth(65)
        prix_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn = QPushButton()
        btn.setObjectName("btnAjouter")
        btn.setFixedSize(32, 32)
        btn.setIcon(qta.icon("mdi.plus", color="#FAFAF8"))
        btn.setIconSize(QSize(14, 14))
        btn.clicked.connect(lambda: on_ajouter(article))

        if not article.est_disponible():
            self.setEnabled(False)
            self.setObjectName("articleRowIndispo")

        layout.addWidget(ico_lbl)
        layout.addLayout(infos, stretch=1)
        layout.addWidget(prix_lbl)
        layout.addWidget(btn)


# ── Ligne récap commande ──────────────────────────────────────────────────────
class LigneCommandeWidget(QWidget):
    def __init__(self, ligne, on_supprimer):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)
        texte = f"{ligne.quantite}× {ligne.article.nom}" if ligne.quantite > 1 else ligne.article.nom
        nom = QLabel(texte); nom.setObjectName("cmdNom")
        nom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        prix = QLabel(f"{ligne.sous_total():.2f} €"); prix.setObjectName("cmdPrix")
        prix.setFixedWidth(55); prix.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        btn = QPushButton(); btn.setObjectName("btnSupprimer")
        btn.setFixedSize(22, 22)
        btn.setIcon(qta.icon("mdi.close", color="#BBBBBB")); btn.setIconSize(QSize(10, 10))
        btn.clicked.connect(on_supprimer)
        layout.addWidget(nom); layout.addWidget(prix); layout.addWidget(btn)


# ── Panneau commande ──────────────────────────────────────────────────────────
class CommandeWidget(QWidget):
    def __init__(self, obs_cuisine=None):
        super().__init__()
        self._obs_cuisine = obs_cuisine
        self._num_table = 1
        self._commande: Commande = None
        self._ouvrir_commande()
        self._build()

    def _ouvrir_commande(self):
        table = _TABLES[self._num_table]
        
        if table.statut == StatutTable.LIBRE:
            self._commande = table.ouvrir_commande(_SERVEUR)
        else:
            # Si la table est occupée, on récupère la commande en cours
            self._commande = table.commande_active
            
        # On gère l'abonnement en évitant les doublons (Marine lève une erreur sinon)
        if self._obs_cuisine:
            try:
                self._commande.abonner(self._obs_cuisine)
            except ValueError:
                pass # L'observateur est déjà abonné, on ne fait rien

    def _build(self):
        self.setObjectName("panneauCommande")
        self.setFixedWidth(270)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(0)

        titre = QLabel("Commande"); titre.setObjectName("cmdTitre")
        layout.addWidget(titre)
        layout.addSpacing(16)

        # Sélecteur table
        tr = QHBoxLayout(); tr.setSpacing(6)
        ic = QLabel(); ic.setPixmap(qta.icon("mdi.table-chair", color=C["sec"]).pixmap(14,14))
        lt = QLabel("Table"); lt.setObjectName("cmdLabel")
        self._tdisplay = QLabel(str(self._num_table)); self._tdisplay.setObjectName("tableNum")
        self._tdisplay.setFixedWidth(24); self._tdisplay.setAlignment(Qt.AlignCenter)
        bm = QPushButton("−"); bm.setObjectName("btnTable"); bm.setFixedSize(26,26)
        bp = QPushButton("+"); bp.setObjectName("btnTable"); bp.setFixedSize(26,26)
        bm.clicked.connect(self._table_moins); bp.clicked.connect(self._table_plus)
        tr.addWidget(ic); tr.addWidget(lt); tr.addStretch()
        tr.addWidget(bm); tr.addWidget(self._tdisplay); tr.addWidget(bp)
        layout.addLayout(tr)
        layout.addSpacing(16); self._sep(layout); layout.addSpacing(12)

        # Liste
        self._liste_layout = QVBoxLayout(); self._liste_layout.setSpacing(0)
        self._liste_layout.addStretch()
        sc = QWidget(); sc.setLayout(self._liste_layout)
        scroll = QScrollArea(); scroll.setWidget(sc); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame); scroll.setStyleSheet("background:transparent;")
        layout.addWidget(scroll, stretch=1)

        layout.addSpacing(12); self._sep(layout); layout.addSpacing(12)

        # Total
        tr2 = QHBoxLayout()
        lt2 = QLabel("Total"); lt2.setObjectName("cmdLabel")
        self._total_lbl = QLabel("0,00 €"); self._total_lbl.setObjectName("totalLabel")
        tr2.addWidget(lt2); tr2.addStretch(); tr2.addWidget(self._total_lbl)
        layout.addLayout(tr2); layout.addSpacing(14)

        btn_val = QPushButton("  Envoyer en cuisine")
        btn_val.setObjectName("btnValider")
        btn_val.setIcon(qta.icon("mdi.check-circle", color="#FAFAF8"))
        btn_val.setIconSize(QSize(16,16)); btn_val.setFixedHeight(42)
        btn_val.clicked.connect(self._valider)
        layout.addWidget(btn_val)

    def ajouter_article(self, article):
        try:
            for ligne in self._commande.lignes:
                if ligne.article.id_article == article.id_article:
                    ligne.quantite += 1
                    self._rafraichir(); return
            self._commande.ajouter_ligne(article)
            self._rafraichir()
        except ValueError as e:
            QMessageBox.warning(self, "Impossible", str(e))

    def _supprimer(self, id_article):
        try:
            self._commande.supprimer_ligne(id_article)
            self._rafraichir()
        except ValueError:
            pass

    def _rafraichir(self):
        while self._liste_layout.count() > 1:
            item = self._liste_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for ligne in self._commande.lignes:
            w = LigneCommandeWidget(ligne,
                lambda _, aid=ligne.article.id_article: self._supprimer(aid))
            self._liste_layout.insertWidget(self._liste_layout.count()-1, w)
        self._total_lbl.setText(f"{self._commande.total():.2f} €")

    def _valider(self):
        if not self._commande.lignes: return
        
        try:
            # Si le statut n'est pas "EN_ATTENTE", on le change (ce qui notifie la cuisine automatiquement)
            if self._commande.statut != StatutCommande.EN_ATTENTE:
                self._commande.changer_statut(StatutCommande.EN_ATTENTE)
            # Si elle est DÉJÀ en attente, on force juste la notification
            else:
                self._commande.notifier()
                
            QMessageBox.information(self, "Envoyée !",
                f"Table {self._num_table} · {self._commande.nombre_articles()} article(s) "
                f"· {self._commande.total():.2f} €\nCommande envoyée en cuisine.")
            
            self._ouvrir_commande() 
            self._rafraichir()
            
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def _changer_table(self, n):
        self._num_table = n
        self._tdisplay.setText(str(n))
        self._ouvrir_commande(); self._rafraichir()

    def _table_moins(self):
        if self._num_table > 1: self._changer_table(self._num_table - 1)

    def _table_plus(self):
        if self._num_table < 10: self._changer_table(self._num_table + 1)

    @staticmethod
    def _sep(layout):
        f = QFrame(); f.setFrameShape(QFrame.HLine); f.setObjectName("separateur")
        layout.addWidget(f)


# ── Page Carte ────────────────────────────────────────────────────────────────
class PageCarte(QWidget):
    def __init__(self, main_window, obs_cuisine=None):
        super().__init__()
        self.main = main_window
        self._carte = _carte_demo()
        self._commande_widget = CommandeWidget(obs_cuisine)
        self._build()
        self._apply_styles()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Navbar
        nb = QHBoxLayout(); nb.setContentsMargins(20,14,20,14)
        btn_r = QPushButton("  Accueil"); btn_r.setObjectName("btnRetour")
        btn_r.setIcon(qta.icon("mdi.chevron-left", color=C["sec"])); btn_r.setIconSize(QSize(13,13))
        btn_r.clicked.connect(lambda: self.main.aller_a(0))
        tp = QLabel("La Carte"); tp.setObjectName("pageTitre")
        sp = QWidget(); sp.setFixedWidth(90)
        nb.addWidget(btn_r); nb.addStretch(); nb.addWidget(tp); nb.addStretch(); nb.addWidget(sp)
        root.addLayout(nb)
        s = QFrame(); s.setFrameShape(QFrame.HLine); s.setObjectName("separateur"); root.addWidget(s)

        # Corps
        corps = QHBoxLayout(); corps.setContentsMargins(0,0,0,0); corps.setSpacing(0)

        # Carte scrollable — utilise Carte.get_tous_les_articles()
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content); cl.setContentsMargins(20,16,20,24); cl.setSpacing(4)
        type_courant = None
        for article in self._carte.get_tous_les_articles():
            if article.get_type() != type_courant:
                type_courant = article.get_type()
                if cl.count() > 0: cl.addSpacing(12)
                sec = QLabel(type_courant.upper() + "S"); sec.setObjectName("sectionTitre")
                cl.addWidget(sec); cl.addSpacing(4)
            cl.addWidget(CarteArticleWidget(article, self._commande_widget.ajouter_article))
        cl.addStretch()
        scroll.setWidget(content)

        vs = QFrame(); vs.setFrameShape(QFrame.VLine); vs.setObjectName("separateur")
        corps.addWidget(scroll, stretch=1); corps.addWidget(vs); corps.addWidget(self._commande_widget)
        root.addLayout(corps)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ background:{C['fond']}; font-family:"Segoe UI","SF Pro Display",sans-serif; }}
            QPushButton#btnRetour {{ background:transparent; border:none; color:{C['sec']}; font-size:13px; padding:4px 8px; }}
            QPushButton#btnRetour:hover {{ color:{C['texte']}; }}
            QLabel#pageTitre {{ font-size:17px; font-weight:600; color:{C['texte']}; }}
            QFrame#separateur {{ color:{C['bordure']}; background:{C['bordure']}; max-height:1px; max-width:1px; }}
            QLabel#sectionTitre {{ font-size:11px; font-weight:600; color:{C['sec']}; letter-spacing:2px; }}
            QFrame#articleRow {{ background:{C['surface']}; border:1px solid {C['bordure']}; border-radius:10px; }}
            QFrame#articleRow:hover {{ border-color:#C8C6BF; background:#F7F6F2; }}
            QFrame#articleRowIndispo {{ background:#F5F5F3; border:1px solid {C['bordure']}; border-radius:10px; }}
            QLabel#articleNom {{ font-size:14px; font-weight:500; color:{C['texte']}; }}
            QLabel#articleDesc {{ font-size:12px; color:{C['sec']}; }}
            QLabel#allergene {{ font-size:11px; color:#B53030; }}
            QLabel#articlePrix {{ font-size:14px; font-weight:500; color:{C['texte']}; }}
            QPushButton#btnAjouter {{ background:{C['accent']}; border:none; border-radius:8px; }}
            QPushButton#btnAjouter:hover {{ background:#444440; }}
            QWidget#panneauCommande {{ background:{C['surface']}; border-left:1px solid {C['bordure']}; }}
            QLabel#cmdTitre {{ font-size:16px; font-weight:600; color:{C['texte']}; }}
            QLabel#cmdLabel {{ font-size:13px; color:{C['sec']}; }}
            QLabel#tableNum {{ font-size:14px; font-weight:600; color:{C['texte']}; }}
            QPushButton#btnTable {{ background:#F1EFE8; border:none; border-radius:6px; font-size:15px; color:{C['texte']}; }}
            QPushButton#btnTable:hover {{ background:#E5E3DC; }}
            QLabel#cmdNom {{ font-size:13px; color:{C['texte']}; }}
            QLabel#cmdPrix {{ font-size:13px; color:{C['sec']}; }}
            QPushButton#btnSupprimer {{ background:transparent; border:none; border-radius:4px; }}
            QPushButton#btnSupprimer:hover {{ background:#FCEBEB; }}
            QLabel#totalLabel {{ font-size:20px; font-weight:600; color:{C['texte']}; }}
            QPushButton#btnValider {{ background:{C['accent']}; color:#FAFAF8; border:none; border-radius:10px; font-size:14px; font-weight:500; }}
            QPushButton#btnValider:hover {{ background:#444440; }}
        """)
