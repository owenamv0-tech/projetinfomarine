"""
Module test_db_manager.py
Tests unitaires pour la classe DBManager.

Tous les tests utilisent une base en mémoire (':memory:') pour être
rapides, indépendants et sans effet de bord sur le système de fichiers.

Auteur : Marine
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import datetime

from database.db_manager import DBManager
from models.ingredient import Ingredient
from models.article_carte import Entree, PlatPrincipal, Dessert, Boisson
from models.menu import Menu
from models.commande import Commande
from models.table import Table
from models.personnel import Serveur
from models.stock import Stock, StockIngredient
from models.statuts import StatutCommande


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def creer_entree() -> Entree:
    return Entree(1, "Soupe", "Soupe du jour", 5.0, 5,
                  [Ingredient("Légumes", 200, "g")], servie_chaude=True)

def creer_plat() -> PlatPrincipal:
    return PlatPrincipal(2, "Steak", "Steak frites", 15.0, 15,
                         [Ingredient("Boeuf", 200, "g", allergene=True)],
                         accompagnement="Frites")

def creer_dessert() -> Dessert:
    return Dessert(3, "Tarte", "Tarte pommes", 5.0, 10,
                   [Ingredient("Pomme", 100, "g")])

def creer_boisson() -> Boisson:
    return Boisson(4, "Eau", "Eau minérale", 2.0, 50,
                   est_alcoolisee=False, temperature_service="fraîche")

def creer_serveur() -> Serveur:
    return Serveur(1, "Dupont", "Alice")

def creer_commande_complete() -> Commande:
    """Crée une commande avec un plat, prête à être sauvegardée."""
    Table._compteur_commandes = 0
    serveur = creer_serveur()
    table = Table(1, 4)
    commande = table.ouvrir_commande(serveur)
    commande.ajouter_ligne(creer_plat(), 2, "bien cuit")
    commande.ajouter_ligne(creer_entree())
    return commande


# ===========================================================================
# Tests DBManager
# ===========================================================================

class TestDBManagerInit(unittest.TestCase):
    """Tests d'initialisation et de création des tables."""

    def setUp(self):
        self.db = DBManager(":memory:")

    def tearDown(self):
        self.db.fermer()

    def test_tables_creees(self):
        """Toutes les tables attendues doivent exister après initialisation."""
        cur = self.db._connexion.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        for attendue in ["articles", "ingredients", "menus",
                          "commandes", "lignes_commande", "stock"]:
            self.assertIn(attendue, tables)

    def test_initialiser_idempotent(self):
        """Appeler initialiser() plusieurs fois ne doit pas lever d'erreur."""
        self.db.initialiser()
        self.db.initialiser()

    def test_context_manager(self):
        """Le gestionnaire de contexte doit fermer la connexion proprement."""
        with DBManager(":memory:") as db:
            db.initialiser()


# ===========================================================================
# Tests Articles
# ===========================================================================

class TestDBManagerArticles(unittest.TestCase):
    """Tests de persistance des articles."""

    def setUp(self):
        self.db = DBManager(":memory:")

    def tearDown(self):
        self.db.fermer()

    # --- Entrée ------------------------------------------------------------

    def test_sauvegarder_charger_entree(self):
        """Une Entree sauvegardée doit être rechargée avec ses attributs."""
        entree = creer_entree()
        self.db.sauvegarder_article(entree)
        articles = self.db.charger_tous_les_articles()
        self.assertEqual(len(articles), 1)
        self.assertIsInstance(articles[0], Entree)
        self.assertEqual(articles[0].nom, "Soupe")
        self.assertEqual(articles[0].prix, 5.0)
        self.assertTrue(articles[0].servie_chaude)

    def test_sauvegarder_charger_ingredients(self):
        """Les ingrédients d'un article doivent être persistés et rechargés."""
        self.db.sauvegarder_article(creer_plat())
        articles = self.db.charger_tous_les_articles()
        self.assertEqual(len(articles[0].get_ingredients()), 1)
        self.assertEqual(articles[0].get_ingredients()[0].nom, "Boeuf")
        self.assertTrue(articles[0].get_ingredients()[0].allergene)

    # --- Plat Principal ----------------------------------------------------

    def test_sauvegarder_charger_plat(self):
        """Un PlatPrincipal doit être rechargé avec son accompagnement."""
        self.db.sauvegarder_article(creer_plat())
        article = self.db.charger_article_par_id(2)
        self.assertIsInstance(article, PlatPrincipal)
        self.assertEqual(article.accompagnement, "Frites")

    # --- Dessert -----------------------------------------------------------

    def test_sauvegarder_charger_dessert(self):
        """Un Dessert doit être rechargé avec son flag fait_maison."""
        self.db.sauvegarder_article(creer_dessert())
        article = self.db.charger_article_par_id(3)
        self.assertIsInstance(article, Dessert)
        self.assertTrue(article.fait_maison)

    # --- Boisson -----------------------------------------------------------

    def test_sauvegarder_charger_boisson(self):
        """Une Boisson doit être rechargée avec volume et température."""
        self.db.sauvegarder_article(creer_boisson())
        article = self.db.charger_article_par_id(4)
        self.assertIsInstance(article, Boisson)
        self.assertEqual(article.volume_cl, 50)
        self.assertEqual(article.temperature_service, "fraîche")

    # --- Plusieurs articles ------------------------------------------------

    def test_sauvegarder_plusieurs_articles(self):
        """Plusieurs articles de types différents doivent tous être chargés."""
        for a in [creer_entree(), creer_plat(), creer_dessert(), creer_boisson()]:
            self.db.sauvegarder_article(a)
        articles = self.db.charger_tous_les_articles()
        self.assertEqual(len(articles), 4)

    def test_charger_article_par_id_inexistant(self):
        """Charger un id inexistant doit retourner None."""
        self.assertIsNone(self.db.charger_article_par_id(999))

    def test_remplacer_article_existant(self):
        """Sauvegarder un article déjà présent doit le mettre à jour."""
        self.db.sauvegarder_article(creer_plat())
        plat_modifie = creer_plat()
        plat_modifie.prix = 18.0
        self.db.sauvegarder_article(plat_modifie)
        article = self.db.charger_article_par_id(2)
        self.assertEqual(article.prix, 18.0)
        self.assertEqual(len(self.db.charger_tous_les_articles()), 1)


# ===========================================================================
# Tests Menus
# ===========================================================================

class TestDBManagerMenus(unittest.TestCase):
    """Tests de persistance des menus."""

    def setUp(self):
        self.db = DBManager(":memory:")
        for a in [creer_entree(), creer_plat(), creer_dessert(), creer_boisson()]:
            self.db.sauvegarder_article(a)

    def tearDown(self):
        self.db.fermer()

    def test_sauvegarder_charger_menu_complet(self):
        """Un menu complet doit être rechargé avec tous ses articles."""
        menu = Menu(1, "Menu du jour", 20.0,
                    plat=creer_plat(), entree=creer_entree(),
                    dessert=creer_dessert(), boisson=creer_boisson())
        self.db.sauvegarder_menu(menu)
        menus = self.db.charger_tous_les_menus()
        self.assertEqual(len(menus), 1)
        self.assertEqual(menus[0].nom, "Menu du jour")
        self.assertIsNotNone(menus[0].entree)
        self.assertIsNotNone(menus[0].dessert)
        self.assertIsNotNone(menus[0].boisson)

    def test_sauvegarder_charger_menu_plat_seul(self):
        """Un menu avec seulement un plat doit avoir ses optionnels à None."""
        menu = Menu(2, "Plat seul", 12.0, plat=creer_plat())
        self.db.sauvegarder_menu(menu)
        menus = self.db.charger_tous_les_menus()
        self.assertIsNone(menus[0].entree)
        self.assertIsNone(menus[0].dessert)
        self.assertIsNone(menus[0].boisson)

    def test_prix_menu_preservé(self):
        """Le prix du menu doit être exactement celui sauvegardé."""
        menu = Menu(3, "Économique", 18.50, plat=creer_plat())
        self.db.sauvegarder_menu(menu)
        menus = self.db.charger_tous_les_menus()
        self.assertAlmostEqual(menus[0].prix, 18.50)


# ===========================================================================
# Tests Commandes
# ===========================================================================

class TestDBManagerCommandes(unittest.TestCase):
    """Tests de persistance des commandes."""

    def setUp(self):
        Table._compteur_commandes = 0
        self.db = DBManager(":memory:")
        self.commande = creer_commande_complete()

    def tearDown(self):
        self.db.fermer()

    def test_sauvegarder_charger_commande(self):
        """Une commande sauvegardée doit apparaître dans charger_commandes_du_jour."""
        self.db.sauvegarder_commande(self.commande)
        commandes = self.db.charger_commandes_du_jour()
        self.assertEqual(len(commandes), 1)
        self.assertEqual(commandes[0]["id_commande"], self.commande.id_commande)

    def test_lignes_sauvegardees(self):
        """Les lignes de la commande doivent être persistées."""
        self.db.sauvegarder_commande(self.commande)
        commandes = self.db.charger_commandes_du_jour()
        self.assertEqual(len(commandes[0]["lignes"]), 2)

    def test_total_sauvegarde(self):
        """Le total de la commande doit être correctement persisté."""
        self.db.sauvegarder_commande(self.commande)
        commandes = self.db.charger_commandes_du_jour()
        # 2 × 15 (steak) + 1 × 5 (soupe) = 35
        self.assertAlmostEqual(commandes[0]["total"], 35.0)

    def test_mettre_a_jour_statut(self):
        """Après un changement de statut, la re-sauvegarde doit être cohérente."""
        self.db.sauvegarder_commande(self.commande)
        self.commande.changer_statut(StatutCommande.EN_PREPARATION)
        self.db.sauvegarder_commande(self.commande)
        commandes = self.db.charger_commandes_du_jour()
        self.assertEqual(commandes[0]["statut"],
                         StatutCommande.EN_PREPARATION.value)

    def test_historique(self):
        """historique doit retourner les commandes dans la plage de dates."""
        self.db.sauvegarder_commande(self.commande)
        aujourd_hui = datetime.now().strftime("%Y-%m-%d")
        result = self.db.historique(aujourd_hui, aujourd_hui)
        self.assertEqual(len(result), 1)

    def test_historique_hors_plage(self):
        """historique ne doit rien retourner hors de la plage de dates."""
        self.db.sauvegarder_commande(self.commande)
        result = self.db.historique("2000-01-01", "2000-01-02")
        self.assertEqual(len(result), 0)

    def test_chiffre_affaires_commande_payee(self):
        """Le CA ne doit compter que les commandes PAYÉES."""
        self.db.sauvegarder_commande(self.commande)
        for s in [StatutCommande.EN_PREPARATION, StatutCommande.PRET,
                  StatutCommande.SERVI, StatutCommande.PAYE]:
            self.commande.changer_statut(s)
        self.db.sauvegarder_commande(self.commande)
        aujourd_hui = datetime.now().strftime("%Y-%m-%d")
        ca = self.db.get_chiffre_affaires(aujourd_hui, aujourd_hui)
        self.assertAlmostEqual(ca, 35.0)

    def test_chiffre_affaires_commande_non_payee(self):
        """Une commande non payée ne doit pas compter dans le CA."""
        self.db.sauvegarder_commande(self.commande)
        aujourd_hui = datetime.now().strftime("%Y-%m-%d")
        ca = self.db.get_chiffre_affaires(aujourd_hui, aujourd_hui)
        self.assertEqual(ca, 0.0)


# ===========================================================================
# Tests Stock
# ===========================================================================

class TestDBManagerStock(unittest.TestCase):
    """Tests de persistance du stock."""

    def setUp(self):
        self.db = DBManager(":memory:")
        self.stock = Stock()
        self.stock.ajouter_ingredient(
            StockIngredient(Ingredient("Boeuf", 200, "g", allergene=True),
                            quantite_disponible=800.0, seuil_alerte=200.0)
        )
        self.stock.ajouter_ingredient(
            StockIngredient(Ingredient("Farine", 100, "g"),
                            quantite_disponible=500.0, seuil_alerte=100.0)
        )

    def tearDown(self):
        self.db.fermer()

    def test_sauvegarder_charger_stock(self):
        """Le stock sauvegardé doit être rechargé avec les bonnes quantités."""
        self.db.sauvegarder_stock(self.stock)
        stock2 = self.db.charger_stock()
        self.assertIn("boeuf", stock2.stock_ingredients)
        self.assertAlmostEqual(
            stock2.get_ingredient("Boeuf").quantite_disponible, 800.0
        )

    def test_sauvegarder_stock_remplace_existant(self):
        """Une deuxième sauvegarde doit remplacer la première."""
        self.db.sauvegarder_stock(self.stock)
        self.stock.get_ingredient("Boeuf").consommer(300.0)
        self.db.sauvegarder_stock(self.stock)
        stock2 = self.db.charger_stock()
        self.assertAlmostEqual(
            stock2.get_ingredient("Boeuf").quantite_disponible, 500.0
        )

    def test_allergene_persiste(self):
        """Le flag allergène doit être correctement persisté."""
        self.db.sauvegarder_stock(self.stock)
        stock2 = self.db.charger_stock()
        self.assertTrue(
            stock2.get_ingredient("Boeuf").ingredient.allergene
        )

    def test_seuil_alerte_persiste(self):
        """Le seuil d'alerte doit être correctement persisté."""
        self.db.sauvegarder_stock(self.stock)
        stock2 = self.db.charger_stock()
        self.assertAlmostEqual(
            stock2.get_ingredient("Boeuf").seuil_alerte, 200.0
        )

    def test_charger_stock_vide(self):
        """Charger un stock vide doit retourner un Stock sans ingrédients."""
        stock_vide = self.db.charger_stock()
        self.assertEqual(len(stock_vide.stock_ingredients), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
