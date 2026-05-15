"""
Module test_articles.py
Tests unitaires pour les classes Ingredient et ArticleCarte (et ses sous-classes).

Auteur : [Votre nom]
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from models.ingredient import Ingredient
from models.article_carte import Entree, PlatPrincipal, Dessert, Boisson


class TestIngredient(unittest.TestCase):
    """Tests unitaires pour la classe Ingredient."""

    def test_creation_valide(self):
        """Un ingrédient avec des valeurs correctes doit être créé sans erreur."""
        ing = Ingredient("Farine", 200, "g", allergene=False)
        self.assertEqual(ing.nom, "Farine")
        self.assertEqual(ing.quantite, 200)
        self.assertEqual(ing.unite, "g")
        self.assertFalse(ing.allergene)

    def test_creation_quantite_negative(self):
        """Une quantité négative ou nulle doit lever une ValueError."""
        with self.assertRaises(ValueError):
            Ingredient("Sel", -5, "g")
        with self.assertRaises(ValueError):
            Ingredient("Sel", 0, "g")

    def test_egalite_insensible_casse(self):
        """Deux ingrédients avec le même nom (casse différente) doivent être égaux."""
        ing1 = Ingredient("Tomate", 100, "g")
        ing2 = Ingredient("TOMATE", 50, "g")
        self.assertEqual(ing1, ing2)

    def test_inegalite(self):
        """Deux ingrédients avec des noms différents ne doivent pas être égaux."""
        ing1 = Ingredient("Tomate", 100, "g")
        ing2 = Ingredient("Poivron", 100, "g")
        self.assertNotEqual(ing1, ing2)


class TestEntree(unittest.TestCase):
    """Tests unitaires pour la classe Entree."""

    def setUp(self):
        """Prépare les objets communs aux tests."""
        self.ing1 = Ingredient("Salade", 80, "g")
        self.ing2 = Ingredient("Noix", 30, "g", allergene=True)
        self.entree = Entree(
            id_article=1,
            nom="Salade aux noix",
            description="Salade verte garnie de noix et vinaigrette",
            prix=7.50,
            temps_preparation=5,
            ingredients=[self.ing1, self.ing2],
            servie_chaude=False
        )

    def test_get_type(self):
        """Le type d'une entrée doit être 'Entrée'."""
        self.assertEqual(self.entree.get_type(), "Entrée")

    def test_prix_valide(self):
        """Le prix doit être correctement enregistré."""
        self.assertEqual(self.entree.prix, 7.50)

    def test_prix_negatif_interdit(self):
        """Un prix négatif doit lever une ValueError."""
        with self.assertRaises(ValueError):
            Entree(2, "Test", "desc", -5.0, 5, [])

    def test_temps_preparation_negatif_interdit(self):
        """Un temps de préparation négatif doit lever une ValueError."""
        with self.assertRaises(ValueError):
            Entree(2, "Test", "desc", 5.0, -10, [])

    def test_disponibilite(self):
        """L'article doit être disponible par défaut et modifiable."""
        self.assertTrue(self.entree.est_disponible())
        self.entree.desactiver()
        self.assertFalse(self.entree.est_disponible())
        self.entree.activer()
        self.assertTrue(self.entree.est_disponible())

    def test_allergenes(self):
        """Seuls les ingrédients marqués allergènes doivent apparaître."""
        allergenes = self.entree.get_allergenes()
        self.assertIn("Noix", allergenes)
        self.assertNotIn("Salade", allergenes)

    def test_appliquer_reduction(self):
        """La réduction doit être calculée correctement."""
        prix_reduit = self.entree.appliquer_reduction(20)  # 20% de réduction
        self.assertAlmostEqual(prix_reduit, 6.00)

    def test_reduction_invalide(self):
        """Un taux hors de [0, 100] doit lever une ValueError."""
        with self.assertRaises(ValueError):
            self.entree.appliquer_reduction(110)
        with self.assertRaises(ValueError):
            self.entree.appliquer_reduction(-5)


class TestPlatPrincipal(unittest.TestCase):
    """Tests unitaires pour la classe PlatPrincipal."""

    def setUp(self):
        self.plat = PlatPrincipal(
            id_article=10,
            nom="Magret de canard",
            description="Magret poêlé, sauce aux cèpes",
            prix=22.00,
            temps_preparation=20,
            ingredients=[
                Ingredient("Magret de canard", 180, "g"),
                Ingredient("Cèpes", 80, "g"),
                Ingredient("Gluten", 10, "g", allergene=True),
            ],
            accompagnement="Gratin dauphinois"
        )

    def test_get_type(self):
        self.assertEqual(self.plat.get_type(), "Plat")

    def test_temps_preparation(self):
        self.assertEqual(self.plat.get_temps_preparation(), 20)

    def test_ingredients(self):
        self.assertEqual(len(self.plat.get_ingredients()), 3)

    def test_accompagnement(self):
        self.assertEqual(self.plat.accompagnement, "Gratin dauphinois")

    def test_allergenes_plat(self):
        allergenes = self.plat.get_allergenes()
        self.assertIn("Gluten", allergenes)
        self.assertEqual(len(allergenes), 1)


class TestDessert(unittest.TestCase):
    """Tests unitaires pour la classe Dessert."""

    def setUp(self):
        self.dessert = Dessert(
            id_article=20,
            nom="Moelleux au chocolat",
            description="Moelleux fondant servi tiède",
            prix=6.50,
            temps_preparation=15,
            ingredients=[
                Ingredient("Chocolat noir", 100, "g", allergene=True),
                Ingredient("Oeufs", 2, "unité", allergene=True),
                Ingredient("Beurre", 50, "g"),
            ],
            fait_maison=True
        )

    def test_get_type(self):
        self.assertEqual(self.dessert.get_type(), "Dessert")

    def test_fait_maison(self):
        self.assertTrue(self.dessert.fait_maison)

    def test_plusieurs_allergenes(self):
        allergenes = self.dessert.get_allergenes()
        self.assertIn("Chocolat noir", allergenes)
        self.assertIn("Oeufs", allergenes)
        self.assertEqual(len(allergenes), 2)

    def test_reduction_zero(self):
        """Une réduction de 0% doit retourner le prix initial."""
        self.assertEqual(self.dessert.appliquer_reduction(0), 6.50)

    def test_reduction_totale(self):
        """Une réduction de 100% doit retourner 0."""
        self.assertEqual(self.dessert.appliquer_reduction(100), 0.00)


class TestBoisson(unittest.TestCase):
    """Tests unitaires pour la classe Boisson."""

    def setUp(self):
        self.boisson = Boisson(
            id_article=30,
            nom="Eau minérale",
            description="Eau minérale naturelle",
            prix=2.50,
            volume_cl=50,
            est_alcoolisee=False,
            temperature_service="fraîche"
        )

    def test_get_type(self):
        self.assertEqual(self.boisson.get_type(), "Boisson")

    def test_temps_preparation_nul(self):
        """Une boisson doit avoir un temps de préparation de 0."""
        self.assertEqual(self.boisson.get_temps_preparation(), 0)

    def test_ingredients_vide(self):
        """Une boisson ne doit pas avoir d'ingrédients."""
        self.assertEqual(self.boisson.get_ingredients(), [])

    def test_volume_negatif_interdit(self):
        with self.assertRaises(ValueError):
            Boisson(31, "Test", "desc", 2.0, -10, False, "fraîche")

    def test_temperature_invalide(self):
        with self.assertRaises(ValueError):
            Boisson(32, "Test", "desc", 2.0, 25, False, "tiède")

    def test_non_alcoolisee(self):
        self.assertFalse(self.boisson.est_alcoolisee)

    def test_boisson_alcoolisee(self):
        vin = Boisson(33, "Bordeaux", "Vin rouge", 8.00, 15, True, "ambiante")
        self.assertTrue(vin.est_alcoolisee)


if __name__ == "__main__":
    unittest.main(verbosity=2)
