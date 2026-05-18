"""
Module test_menu_carte.py
Tests unitaires pour les classes Menu et Carte.

Auteur : Marine
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile

from models.ingredient import Ingredient
from models.article_carte import Entree, PlatPrincipal, Dessert, Boisson
from models.menu import Menu
from models.carte import Carte


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def creer_entree(id_a: int = 1) -> Entree:
    return Entree(id_a, "Soupe", "Soupe du jour", 5.0, 5,
                  [Ingredient("Légumes", 200, "g")], servie_chaude=True)

def creer_plat(id_a: int = 2) -> PlatPrincipal:
    return PlatPrincipal(id_a, "Steak", "Steak frites", 15.0, 15,
                         [Ingredient("Boeuf", 200, "g", allergene=True)],
                         accompagnement="Frites")

def creer_dessert(id_a: int = 3) -> Dessert:
    return Dessert(id_a, "Tarte", "Tarte aux pommes", 5.0, 10,
                   [Ingredient("Pomme", 100, "g")])

def creer_boisson(id_a: int = 4) -> Boisson:
    return Boisson(id_a, "Eau", "Eau minérale", 2.0, 50)

def creer_menu_complet() -> Menu:
    return Menu(1, "Menu du jour", 20.0,
                plat=creer_plat(),
                entree=creer_entree(),
                dessert=creer_dessert(),
                boisson=creer_boisson())

def creer_carte_remplie() -> Carte:
    carte = Carte()
    carte.ajouter_article(creer_entree(1))
    carte.ajouter_article(creer_plat(2))
    carte.ajouter_article(creer_dessert(3))
    carte.ajouter_article(creer_boisson(4))
    return carte


# ===========================================================================
# Tests Menu
# ===========================================================================

class TestMenu(unittest.TestCase):
    """Tests unitaires pour la classe Menu."""

    def setUp(self):
        self.menu = creer_menu_complet()

    # --- Création ----------------------------------------------------------

    def test_creation_valide(self):
        """Un menu valide doit être créé avec les bons attributs."""
        self.assertEqual(self.menu.nom, "Menu du jour")
        self.assertEqual(self.menu.prix, 20.0)
        self.assertTrue(self.menu.disponible)

    def test_prix_negatif_interdit(self):
        """Un prix négatif doit lever ValueError."""
        with self.assertRaises(ValueError):
            Menu(2, "Test", -5.0, plat=creer_plat())

    def test_nom_vide_interdit(self):
        """Un nom vide doit lever ValueError."""
        with self.assertRaises(ValueError):
            Menu(2, "  ", 20.0, plat=creer_plat())

    # --- get_articles ------------------------------------------------------

    def test_get_articles_inclut_tous(self):
        """get_articles doit inclure le plat et tous les optionnels présents."""
        articles = self.menu.get_articles()
        self.assertEqual(len(articles), 4)

    def test_get_articles_sans_optionnels(self):
        """Un menu avec seulement un plat ne doit retourner qu'un article."""
        menu = Menu(2, "Plat seul", 12.0, plat=creer_plat())
        self.assertEqual(len(menu.get_articles()), 1)

    # --- calculer_prix_a_la_carte / calculer_economie ----------------------

    def test_calculer_prix_a_la_carte(self):
        """Le prix à la carte doit être la somme des articles."""
        # 5 + 15 + 5 + 2 = 27
        self.assertAlmostEqual(self.menu.calculer_prix_a_la_carte(), 27.0)

    def test_calculer_economie(self):
        """L'économie doit être prix_a_la_carte - prix_menu."""
        # 27 - 20 = 7
        self.assertAlmostEqual(self.menu.calculer_economie(), 7.0)

    def test_calculer_economie_menu_plus_cher(self):
        """Si le menu est plus cher qu'à la carte, l'économie vaut 0."""
        menu = Menu(2, "Cher", 50.0, plat=creer_plat())
        self.assertEqual(menu.calculer_economie(), 0.0)

    # --- est_complet -------------------------------------------------------

    def test_est_complet_tous_disponibles(self):
        """est_complet doit retourner True si tous les articles sont disponibles."""
        self.assertTrue(self.menu.est_complet())

    def test_est_complet_plat_indisponible(self):
        """est_complet doit retourner False si le plat est indisponible."""
        self.menu.plat.desactiver()
        self.assertFalse(self.menu.est_complet())

    def test_est_complet_optionnel_indisponible(self):
        """est_complet doit retourner False si un optionnel est indisponible."""
        self.menu.entree.desactiver()
        self.assertFalse(self.menu.est_complet())

    # --- get_allergenes ----------------------------------------------------

    def test_get_allergenes_union(self):
        """get_allergenes doit agréger les allergènes de tous les articles."""
        allergenes = self.menu.get_allergenes()
        self.assertIn("Boeuf", allergenes)

    def test_get_allergenes_sans_doublon(self):
        """Un allergène présent dans plusieurs articles ne doit apparaître qu'une fois."""
        allergenes = self.menu.get_allergenes()
        self.assertEqual(len(allergenes), len(set(allergenes)))

    def test_get_allergenes_aucun(self):
        """Un menu sans allergène doit retourner une liste vide."""
        menu = Menu(3, "Sans allergène", 10.0,
                    plat=PlatPrincipal(5, "P", "d", 10.0, 5, []))
        self.assertEqual(menu.get_allergenes(), [])

    # --- get_temps_preparation_total ---------------------------------------

    def test_temps_preparation_total(self):
        """Le temps de préparation doit être le maximum des articles."""
        # entree=5, plat=15, dessert=10, boisson=0 → max = 15
        self.assertEqual(self.menu.get_temps_preparation_total(), 15)

    # --- Disponibilité -----------------------------------------------------

    def test_activer_desactiver(self):
        """activer/desactiver doivent changer le flag disponible."""
        self.menu.desactiver()
        self.assertFalse(self.menu.disponible)
        self.menu.activer()
        self.assertTrue(self.menu.disponible)

    # --- to_dict -----------------------------------------------------------

    def test_to_dict_contient_les_cles(self):
        """to_dict doit contenir toutes les clés attendues."""
        d = self.menu.to_dict()
        for cle in ["id_menu", "nom", "prix", "disponible",
                    "id_plat", "id_entree", "id_dessert", "id_boisson"]:
            self.assertIn(cle, d)


# ===========================================================================
# Tests Carte
# ===========================================================================

class TestCarte(unittest.TestCase):
    """Tests unitaires pour la classe Carte."""

    def setUp(self):
        self.carte = creer_carte_remplie()

    # --- ajouter_article ---------------------------------------------------

    def test_ajouter_article_entree(self):
        """Une entrée doit atterrir dans la liste entrees."""
        self.assertEqual(len(self.carte.entrees), 1)
        self.assertEqual(self.carte.entrees[0].nom, "Soupe")

    def test_ajouter_article_plat(self):
        """Un plat doit atterrir dans la liste plats."""
        self.assertEqual(len(self.carte.plats), 1)

    def test_ajouter_article_doublon_interdit(self):
        """Ajouter un article avec un id existant doit lever ValueError."""
        with self.assertRaises(ValueError):
            self.carte.ajouter_article(creer_entree(1))

    def test_ajouter_article_type_inconnu(self):
        """Un type d'article non reconnu doit lever TypeError."""
        with self.assertRaises(TypeError):
            self.carte._get_liste_pour(object())  # type: ignore

    # --- supprimer_article -------------------------------------------------

    def test_supprimer_article(self):
        """Supprimer un article doit le retirer de la bonne liste."""
        self.carte.supprimer_article(1)
        self.assertEqual(len(self.carte.entrees), 0)

    def test_supprimer_article_inexistant(self):
        """Supprimer un article inexistant doit lever ValueError."""
        with self.assertRaises(ValueError):
            self.carte.supprimer_article(999)

    # --- ajouter_menu / supprimer_menu -------------------------------------

    def test_ajouter_menu(self):
        """Un menu ajouté doit apparaître dans la liste menus."""
        self.carte.ajouter_menu(creer_menu_complet())
        self.assertEqual(len(self.carte.menus), 1)

    def test_ajouter_menu_doublon_interdit(self):
        """Ajouter deux fois le même menu doit lever ValueError."""
        self.carte.ajouter_menu(creer_menu_complet())
        with self.assertRaises(ValueError):
            self.carte.ajouter_menu(creer_menu_complet())

    def test_supprimer_menu(self):
        """Supprimer un menu doit le retirer de la liste."""
        self.carte.ajouter_menu(creer_menu_complet())
        self.carte.supprimer_menu(1)
        self.assertEqual(len(self.carte.menus), 0)

    def test_supprimer_menu_inexistant(self):
        with self.assertRaises(ValueError):
            self.carte.supprimer_menu(999)

    # --- get_articles_disponibles (récursion) ------------------------------

    def test_get_articles_disponibles_tous(self):
        """Tous les articles disponibles doivent être retournés."""
        result = self.carte.get_articles_disponibles(self.carte.plats)
        self.assertEqual(len(result), 1)

    def test_get_articles_disponibles_filtre(self):
        """Les articles indisponibles ne doivent pas apparaître."""
        self.carte.plats[0].desactiver()
        result = self.carte.get_articles_disponibles(self.carte.plats)
        self.assertEqual(len(result), 0)

    def test_get_articles_disponibles_liste_vide(self):
        """Sur une liste vide, la récursion doit retourner []."""
        result = self.carte.get_articles_disponibles([])
        self.assertEqual(result, [])

    def test_get_articles_disponibles_mixte(self):
        """Seuls les articles disponibles d'une liste mixte doivent être retournés."""
        self.carte.ajouter_article(creer_entree(5))
        self.carte.entrees[0].desactiver()  # entree id=1 indispo
        result = self.carte.get_articles_disponibles(self.carte.entrees)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id_article, 5)

    # --- rechercher_par_nom ------------------------------------------------

    def test_rechercher_par_nom_trouve(self):
        """Une recherche correspondante doit retourner l'article."""
        result = self.carte.rechercher_par_nom("steak")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].nom, "Steak")

    def test_rechercher_par_nom_insensible_casse(self):
        """La recherche doit être insensible à la casse."""
        self.assertEqual(
            self.carte.rechercher_par_nom("SOUPE"),
            self.carte.rechercher_par_nom("soupe")
        )

    def test_rechercher_par_nom_introuvable(self):
        """Une recherche sans résultat doit retourner une liste vide."""
        self.assertEqual(self.carte.rechercher_par_nom("Pizza"), [])

    # --- rechercher_par_id -------------------------------------------------

    def test_rechercher_par_id_trouve(self):
        result = self.carte.rechercher_par_id(2)
        self.assertIsNotNone(result)
        self.assertEqual(result.nom, "Steak")

    def test_rechercher_par_id_introuvable(self):
        self.assertIsNone(self.carte.rechercher_par_id(999))

    # --- get_articles_avec_allergene ---------------------------------------

    def test_get_articles_avec_allergene(self):
        """Les articles contenant l'allergène doivent être retournés."""
        result = self.carte.get_articles_avec_allergene("Boeuf")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].nom, "Steak")

    def test_get_articles_sans_allergene(self):
        result = self.carte.get_articles_avec_allergene("Gluten")
        self.assertEqual(result, [])

    # --- get_menus_disponibles ---------------------------------------------

    def test_get_menus_disponibles(self):
        """get_menus_disponibles ne doit retourner que les menus complets."""
        self.carte.ajouter_menu(creer_menu_complet())
        result = self.carte.get_menus_disponibles()
        self.assertEqual(len(result), 1)

    def test_get_menus_disponibles_menu_desactive(self):
        """Un menu désactivé ne doit pas apparaître."""
        menu = creer_menu_complet()
        menu.desactiver()
        self.carte.ajouter_menu(menu)
        self.assertEqual(len(self.carte.get_menus_disponibles()), 0)

    # --- to_json / from_json -----------------------------------------------

    def test_sauvegarder_charger_json(self):
        """Sauvegarder puis recharger doit restituer la même carte."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            chemin = f.name
        try:
            self.carte.ajouter_menu(creer_menu_complet())
            self.carte.to_json(chemin)
            carte2 = Carte()
            carte2.from_json(chemin)
            self.assertEqual(len(carte2.entrees),  len(self.carte.entrees))
            self.assertEqual(len(carte2.plats),    len(self.carte.plats))
            self.assertEqual(len(carte2.desserts), len(self.carte.desserts))
            self.assertEqual(len(carte2.boissons), len(self.carte.boissons))
            self.assertEqual(len(carte2.menus),    len(self.carte.menus))
        finally:
            os.unlink(chemin)

    def test_from_json_fichier_inexistant(self):
        """Charger un fichier inexistant doit lever FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.carte.from_json("/chemin/inexistant.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
