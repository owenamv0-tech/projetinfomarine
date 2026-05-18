"""
Module db_manager.py
Centralise tous les accès à la base de données SQLite du restaurant.

Le reste du code ne communique jamais directement avec SQLite :
tout passe par cette classe (pattern Repository).

Schéma de la base :
    articles        → tous les articles de la carte
    ingredients     → ingrédients liés à chaque article
    menus           → menus à prix fixe (références aux articles)
    commandes       → commandes passées
    lignes_commande → articles commandés dans chaque commande
    stock           → quantités disponibles en cuisine

Auteur : Marine
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from models.ingredient import Ingredient
from models.article_carte import (ArticleCarte, Entree, PlatPrincipal,
                                   Dessert, Boisson)
from models.menu import Menu
from models.carte import Carte
from models.commande import Commande, LigneCommande
from models.stock import Stock, StockIngredient
from models.statuts import StatutCommande


class DBManager:
    """
    Gestionnaire de la base de données SQLite du restaurant.

    Fournit des méthodes de haut niveau pour sauvegarder et charger
    les objets métier (articles, menus, commandes, stock) sans que
    le reste du code ait à connaître les détails SQL.

    Attributs:
        chemin_db (str)                 : Chemin vers le fichier .db.
                                          Utiliser ':memory:' pour les tests.
        _connexion (sqlite3.Connection) : Connexion SQLite active.
    """

    def __init__(self, chemin_db: str = "restaurant.db") -> None:
        """
        Initialise la connexion SQLite et crée les tables si nécessaire.

        Args:
            chemin_db (str): Chemin du fichier de base de données.
                             Défaut: 'restaurant.db' dans le répertoire courant.
                             Utiliser ':memory:' pour une BDD temporaire en mémoire.
        """
        self.chemin_db = chemin_db
        self._connexion = sqlite3.connect(chemin_db)
        self._connexion.row_factory = sqlite3.Row   # accès par nom de colonne
        self._connexion.execute("PRAGMA foreign_keys = ON")
        self.initialiser()

    # -----------------------------------------------------------------------
    # Initialisation du schéma
    # -----------------------------------------------------------------------

    def initialiser(self) -> None:
        """
        Crée toutes les tables de la base si elles n'existent pas encore.
        Peut être appelé plusieurs fois sans risque (IF NOT EXISTS).
        """
        curseur = self._connexion.cursor()

        curseur.executescript("""
            CREATE TABLE IF NOT EXISTS articles (
                id_article          INTEGER PRIMARY KEY,
                type                TEXT    NOT NULL,
                nom                 TEXT    NOT NULL,
                description         TEXT    NOT NULL,
                prix                REAL    NOT NULL,
                disponible          INTEGER NOT NULL DEFAULT 1,
                temps_preparation   INTEGER NOT NULL DEFAULT 0,
                -- Entree
                servie_chaude       INTEGER,
                -- PlatPrincipal
                accompagnement      TEXT,
                -- Dessert
                fait_maison         INTEGER,
                -- Boisson
                volume_cl           REAL,
                est_alcoolisee      INTEGER,
                temperature_service TEXT
            );

            CREATE TABLE IF NOT EXISTS ingredients (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                id_article  INTEGER NOT NULL
                                REFERENCES articles(id_article)
                                ON DELETE CASCADE,
                nom         TEXT    NOT NULL,
                quantite    REAL    NOT NULL,
                unite       TEXT    NOT NULL,
                allergene   INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS menus (
                id_menu     INTEGER PRIMARY KEY,
                nom         TEXT    NOT NULL,
                prix        REAL    NOT NULL,
                disponible  INTEGER NOT NULL DEFAULT 1,
                id_plat     INTEGER NOT NULL
                                REFERENCES articles(id_article),
                id_entree   INTEGER REFERENCES articles(id_article),
                id_dessert  INTEGER REFERENCES articles(id_article),
                id_boisson  INTEGER REFERENCES articles(id_article)
            );

            CREATE TABLE IF NOT EXISTS commandes (
                id_commande         INTEGER PRIMARY KEY,
                numero_table        INTEGER NOT NULL,
                id_serveur          INTEGER NOT NULL,
                nom_serveur         TEXT    NOT NULL,
                prenom_serveur      TEXT    NOT NULL,
                statut              TEXT    NOT NULL,
                horodatage_creation TEXT    NOT NULL,
                horodatage_service  TEXT,
                total               REAL    NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS lignes_commande (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                id_commande     INTEGER NOT NULL
                                    REFERENCES commandes(id_commande)
                                    ON DELETE CASCADE,
                id_article      INTEGER NOT NULL,
                nom_article     TEXT    NOT NULL,
                quantite        INTEGER NOT NULL,
                commentaire     TEXT    NOT NULL DEFAULT '',
                sous_total      REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stock (
                nom_ingredient      TEXT    PRIMARY KEY,
                unite               TEXT    NOT NULL,
                allergene           INTEGER NOT NULL DEFAULT 0,
                quantite_disponible REAL    NOT NULL,
                seuil_alerte        REAL    NOT NULL DEFAULT 0
            );
        """)
        self._connexion.commit()

    # -----------------------------------------------------------------------
    # Articles
    # -----------------------------------------------------------------------

    def sauvegarder_article(self, article: ArticleCarte) -> None:
        """
        Insère ou remplace un article et ses ingrédients dans la base.

        Args:
            article (ArticleCarte): L'article à persister.
        """
        cur = self._connexion.cursor()

        cur.execute("""
            INSERT OR REPLACE INTO articles
                (id_article, type, nom, description, prix, disponible,
                 temps_preparation, servie_chaude, accompagnement,
                 fait_maison, volume_cl, est_alcoolisee, temperature_service)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.id_article,
            article.get_type(),
            article.nom,
            article.description,
            article.prix,
            int(article.disponible),
            article.get_temps_preparation(),
            int(article.servie_chaude)    if isinstance(article, Entree)        else None,
            article.accompagnement        if isinstance(article, PlatPrincipal) else None,
            int(article.fait_maison)      if isinstance(article, Dessert)       else None,
            article.volume_cl             if isinstance(article, Boisson)       else None,
            int(article.est_alcoolisee)   if isinstance(article, Boisson)       else None,
            article.temperature_service   if isinstance(article, Boisson)       else None,
        ))

        # Supprime les anciens ingrédients avant de les réinsérer
        cur.execute(
            "DELETE FROM ingredients WHERE id_article = ?",
            (article.id_article,)
        )
        for ing in article.get_ingredients():
            cur.execute("""
                INSERT INTO ingredients (id_article, nom, quantite, unite, allergene)
                VALUES (?, ?, ?, ?, ?)
            """, (article.id_article, ing.nom, ing.quantite,
                  ing.unite, int(ing.allergene)))

        self._connexion.commit()

    def charger_tous_les_articles(self) -> List[ArticleCarte]:
        """
        Charge tous les articles de la base et reconstruit les objets Python.

        Returns:
            List[ArticleCarte]: Liste de tous les articles.
        """
        cur = self._connexion.cursor()
        cur.execute("SELECT * FROM articles")
        rows = cur.fetchall()

        articles = []
        for row in rows:
            ingredients = self._charger_ingredients(row["id_article"])
            article = self._construire_article(row, ingredients)
            if article:
                articles.append(article)
        return articles

    def charger_article_par_id(self, id_article: int) -> Optional[ArticleCarte]:
        """
        Charge un article par son identifiant.

        Args:
            id_article (int): Identifiant de l'article.

        Returns:
            ArticleCarte | None: L'article trouvé, ou None.
        """
        cur = self._connexion.cursor()
        cur.execute("SELECT * FROM articles WHERE id_article = ?", (id_article,))
        row = cur.fetchone()
        if row is None:
            return None
        ingredients = self._charger_ingredients(id_article)
        return self._construire_article(row, ingredients)

    def _charger_ingredients(self, id_article: int) -> List[Ingredient]:
        """
        Charge les ingrédients d'un article depuis la base.

        Args:
            id_article (int): Identifiant de l'article parent.

        Returns:
            List[Ingredient]: Ingrédients de l'article.
        """
        cur = self._connexion.cursor()
        cur.execute(
            "SELECT * FROM ingredients WHERE id_article = ?",
            (id_article,)
        )
        return [
            Ingredient(
                nom=row["nom"],
                quantite=row["quantite"],
                unite=row["unite"],
                allergene=bool(row["allergene"])
            )
            for row in cur.fetchall()
        ]

    def _construire_article(self, row: sqlite3.Row,
                             ingredients: List[Ingredient]
                             ) -> Optional[ArticleCarte]:
        """
        Reconstruit l'objet Python correspondant à une ligne SQL.

        Args:
            row (sqlite3.Row)           : Ligne de la table articles.
            ingredients (List[Ingredient]): Ingrédients associés.

        Returns:
            ArticleCarte | None: L'objet reconstruit, ou None si type inconnu.
        """
        type_ = row["type"]
        kwargs = dict(
            id_article=row["id_article"],
            nom=row["nom"],
            description=row["description"],
            prix=row["prix"],
            disponible=bool(row["disponible"]),
        )

        if type_ == "Entrée":
            return Entree(
                **kwargs,
                temps_preparation=row["temps_preparation"],
                ingredients=ingredients,
                servie_chaude=bool(row["servie_chaude"] or 0),
            )
        if type_ == "Plat":
            return PlatPrincipal(
                **kwargs,
                temps_preparation=row["temps_preparation"],
                ingredients=ingredients,
                accompagnement=row["accompagnement"] or "",
            )
        if type_ == "Dessert":
            return Dessert(
                **kwargs,
                temps_preparation=row["temps_preparation"],
                ingredients=ingredients,
                fait_maison=bool(row["fait_maison"] or 0),
            )
        if type_ == "Boisson":
            return Boisson(
                **kwargs,
                volume_cl=row["volume_cl"],
                est_alcoolisee=bool(row["est_alcoolisee"] or 0),
                temperature_service=row["temperature_service"] or "fraîche",
            )
        return None

    # -----------------------------------------------------------------------
    # Menus
    # -----------------------------------------------------------------------

    def sauvegarder_menu(self, menu: Menu) -> None:
        """
        Insère ou remplace un menu dans la base.
        Les articles du menu doivent déjà être sauvegardés.

        Args:
            menu (Menu): Le menu à persister.
        """
        self._connexion.execute("""
            INSERT OR REPLACE INTO menus
                (id_menu, nom, prix, disponible,
                 id_plat, id_entree, id_dessert, id_boisson)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            menu.id_menu, menu.nom, menu.prix, int(menu.disponible),
            menu.plat.id_article,
            menu.entree.id_article  if menu.entree  else None,
            menu.dessert.id_article if menu.dessert else None,
            menu.boisson.id_article if menu.boisson else None,
        ))
        self._connexion.commit()

    def charger_tous_les_menus(self) -> List[Menu]:
        """
        Charge tous les menus en reconstruisant les références aux articles.

        Returns:
            List[Menu]: Liste de tous les menus.
        """
        cur = self._connexion.cursor()
        cur.execute("SELECT * FROM menus")
        menus = []
        for row in cur.fetchall():
            plat = self.charger_article_par_id(row["id_plat"])
            if not isinstance(plat, PlatPrincipal):
                continue
            entree  = self.charger_article_par_id(row["id_entree"])  \
                      if row["id_entree"]  else None
            dessert = self.charger_article_par_id(row["id_dessert"]) \
                      if row["id_dessert"] else None
            boisson = self.charger_article_par_id(row["id_boisson"]) \
                      if row["id_boisson"] else None
            menus.append(Menu(
                id_menu=row["id_menu"],
                nom=row["nom"],
                prix=row["prix"],
                plat=plat,
                entree=entree   if isinstance(entree,  Entree)  else None,
                dessert=dessert if isinstance(dessert, Dessert) else None,
                boisson=boisson if isinstance(boisson, Boisson) else None,
                disponible=bool(row["disponible"]),
            ))
        return menus

    # -----------------------------------------------------------------------
    # Commandes
    # -----------------------------------------------------------------------

    def sauvegarder_commande(self, commande: Commande) -> None:
        """
        Insère ou met à jour une commande et ses lignes dans la base.

        Args:
            commande (Commande): La commande à persister.
        """
        cur = self._connexion.cursor()

        cur.execute("""
            INSERT OR REPLACE INTO commandes
                (id_commande, numero_table, id_serveur, nom_serveur,
                 prenom_serveur, statut, horodatage_creation,
                 horodatage_service, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            commande.id_commande,
            commande.table.numero,
            commande.serveur.id_personnel,
            commande.serveur.nom,
            commande.serveur.prenom,
            commande.statut.value,
            commande.horodatage_creation.isoformat(),
            commande.horodatage_service.isoformat()
                if commande.horodatage_service else None,
            commande.total(),
        ))

        cur.execute(
            "DELETE FROM lignes_commande WHERE id_commande = ?",
            (commande.id_commande,)
        )
        for ligne in commande.lignes:
            cur.execute("""
                INSERT INTO lignes_commande
                    (id_commande, id_article, nom_article,
                     quantite, commentaire, sous_total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                commande.id_commande,
                ligne.article.id_article,
                ligne.article.nom,
                ligne.quantite,
                ligne.commentaire,
                ligne.sous_total(),
            ))

        self._connexion.commit()

    def charger_commandes_du_jour(self) -> List[dict]:
        """
        Charge toutes les commandes créées aujourd'hui.

        Retourne des dictionnaires (pas des objets Commande) car reconstruire
        les objets nécessiterait de charger les serveurs et tables depuis
        une autre source. Owen utilisera ces données pour l'affichage.

        Returns:
            List[dict]: Données brutes des commandes du jour.
        """
        aujourd_hui = datetime.now().strftime("%Y-%m-%d")
        cur = self._connexion.cursor()
        cur.execute("""
            SELECT * FROM commandes
            WHERE horodatage_creation LIKE ?
            ORDER BY horodatage_creation ASC
        """, (f"{aujourd_hui}%",))

        commandes = []
        for row in cur.fetchall():
            cur2 = self._connexion.cursor()
            cur2.execute(
                "SELECT * FROM lignes_commande WHERE id_commande = ?",
                (row["id_commande"],)
            )
            lignes = [dict(l) for l in cur2.fetchall()]
            commande_dict = dict(row)
            commande_dict["lignes"] = lignes
            commandes.append(commande_dict)

        return commandes

    def historique(self, date_debut: str, date_fin: str) -> List[dict]:
        """
        Retourne les commandes dont la date de création est comprise
        entre date_debut et date_fin (inclus).

        Args:
            date_debut (str): Date de début au format 'YYYY-MM-DD'.
            date_fin (str)  : Date de fin au format 'YYYY-MM-DD'.

        Returns:
            List[dict]: Données des commandes sur la période.
        """
        cur = self._connexion.cursor()
        cur.execute("""
            SELECT * FROM commandes
            WHERE DATE(horodatage_creation) BETWEEN ? AND ?
            ORDER BY horodatage_creation ASC
        """, (date_debut, date_fin))
        return [dict(row) for row in cur.fetchall()]

    def get_chiffre_affaires(self, date_debut: str, date_fin: str) -> float:
        """
        Calcule le chiffre d'affaires total sur une période donnée,
        en ne comptant que les commandes au statut PAYE.

        Args:
            date_debut (str): Date de début au format 'YYYY-MM-DD'.
            date_fin (str)  : Date de fin au format 'YYYY-MM-DD'.

        Returns:
            float: Somme des totaux des commandes payées sur la période.
        """
        cur = self._connexion.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM commandes
            WHERE statut = ?
              AND DATE(horodatage_creation) BETWEEN ? AND ?
        """, (StatutCommande.PAYE.value, date_debut, date_fin))
        return round(cur.fetchone()[0], 2)

    # -----------------------------------------------------------------------
    # Stock
    # -----------------------------------------------------------------------

    def sauvegarder_stock(self, stock: Stock) -> None:
        """
        Sauvegarde l'état complet du stock dans la base.
        Remplace toutes les lignes existantes.

        Args:
            stock (Stock): Le stock à persister.
        """
        cur = self._connexion.cursor()
        cur.execute("DELETE FROM stock")
        for si in stock.stock_ingredients.values():
            cur.execute("""
                INSERT INTO stock
                    (nom_ingredient, unite, allergene,
                     quantite_disponible, seuil_alerte)
                VALUES (?, ?, ?, ?, ?)
            """, (
                si.ingredient.nom,
                si.ingredient.unite,
                int(si.ingredient.allergene),
                si.quantite_disponible,
                si.seuil_alerte,
            ))
        self._connexion.commit()

    def charger_stock(self) -> Stock:
        """
        Reconstruit un objet Stock depuis la base.

        Returns:
            Stock: Stock chargé depuis la base de données.
        """
        cur = self._connexion.cursor()
        cur.execute("SELECT * FROM stock")
        stock = Stock()
        for row in cur.fetchall():
            ing = Ingredient(
                nom=row["nom_ingredient"],
                quantite=1.0,
                unite=row["unite"],
                allergene=bool(row["allergene"])
            )
            si = StockIngredient(
                ingredient=ing,
                quantite_disponible=row["quantite_disponible"],
                seuil_alerte=row["seuil_alerte"]
            )
            stock.stock_ingredients[row["nom_ingredient"].lower()] = si
        return stock

    # -----------------------------------------------------------------------
    # Utilitaires
    # -----------------------------------------------------------------------

    def fermer(self) -> None:
        """
        Ferme proprement la connexion à la base de données.
        À appeler en fin de programme ou dans un bloc finally.
        """
        self._connexion.close()

    def __enter__(self) -> "DBManager":
        """Permet l'utilisation avec le gestionnaire de contexte `with`."""
        return self

    def __exit__(self, *args) -> None:
        """Ferme la connexion automatiquement en sortie du bloc `with`."""
        self.fermer()
