"""
Module test_statuts.py
Tests unitaires pour les énumérations StatutCommande et StatutTable.

Auteur : Marine
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from models.statuts import StatutCommande, StatutTable


class TestStatutCommande(unittest.TestCase):
    """Tests unitaires pour l'énumération StatutCommande."""

    # --- Tests sur les valeurs -------------------------------------------

    def test_valeurs_existantes(self):
        """Les cinq statuts attendus doivent exister."""
        self.assertEqual(StatutCommande.EN_ATTENTE.value,     "En attente")
        self.assertEqual(StatutCommande.EN_PREPARATION.value, "En préparation")
        self.assertEqual(StatutCommande.PRET.value,           "Prêt à servir")
        self.assertEqual(StatutCommande.SERVI.value,          "Servi")
        self.assertEqual(StatutCommande.PAYE.value,           "Payé")

    def test_str(self):
        """__str__ doit retourner la valeur lisible."""
        self.assertEqual(str(StatutCommande.EN_ATTENTE), "En attente")
        self.assertEqual(str(StatutCommande.PAYE),       "Payé")

    # --- Tests sur les transitions autorisées ----------------------------

    def test_transition_en_attente_vers_en_preparation(self):
        """EN_ATTENTE → EN_PREPARATION doit être autorisée."""
        self.assertTrue(
            StatutCommande.EN_ATTENTE.peut_transitionner_vers(
                StatutCommande.EN_PREPARATION
            )
        )

    def test_transition_en_preparation_vers_pret(self):
        """EN_PREPARATION → PRET doit être autorisée."""
        self.assertTrue(
            StatutCommande.EN_PREPARATION.peut_transitionner_vers(
                StatutCommande.PRET
            )
        )

    def test_transition_pret_vers_servi(self):
        """PRET → SERVI doit être autorisée."""
        self.assertTrue(
            StatutCommande.PRET.peut_transitionner_vers(
                StatutCommande.SERVI
            )
        )

    def test_transition_servi_vers_paye(self):
        """SERVI → PAYE doit être autorisée."""
        self.assertTrue(
            StatutCommande.SERVI.peut_transitionner_vers(
                StatutCommande.PAYE
            )
        )

    # --- Tests sur les transitions interdites ----------------------------

    def test_transition_retour_arriere_interdit(self):
        """Revenir en arrière doit être interdit."""
        self.assertFalse(
            StatutCommande.EN_PREPARATION.peut_transitionner_vers(
                StatutCommande.EN_ATTENTE
            )
        )
        self.assertFalse(
            StatutCommande.PAYE.peut_transitionner_vers(
                StatutCommande.SERVI
            )
        )

    def test_transition_saut_interdit(self):
        """Sauter des étapes doit être interdit."""
        self.assertFalse(
            StatutCommande.EN_ATTENTE.peut_transitionner_vers(
                StatutCommande.PAYE
            )
        )
        self.assertFalse(
            StatutCommande.EN_ATTENTE.peut_transitionner_vers(
                StatutCommande.SERVI
            )
        )

    def test_transition_depuis_paye_vide(self):
        """Depuis PAYE, aucune transition ne doit être possible."""
        self.assertEqual(StatutCommande.PAYE.transitions_autorisees(), [])
        self.assertFalse(
            StatutCommande.PAYE.peut_transitionner_vers(
                StatutCommande.EN_ATTENTE
            )
        )

    def test_transition_vers_soi_meme_interdit(self):
        """Une commande ne peut pas transitionner vers son propre statut."""
        self.assertFalse(
            StatutCommande.EN_ATTENTE.peut_transitionner_vers(
                StatutCommande.EN_ATTENTE
            )
        )


class TestStatutTable(unittest.TestCase):
    """Tests unitaires pour l'énumération StatutTable."""

    def test_valeurs_existantes(self):
        """Les trois statuts attendus doivent exister."""
        self.assertEqual(StatutTable.LIBRE.value,    "Libre")
        self.assertEqual(StatutTable.OCCUPEE.value,  "Occupée")
        self.assertEqual(StatutTable.RESERVEE.value, "Réservée")

    def test_str(self):
        """__str__ doit retourner la valeur lisible."""
        self.assertEqual(str(StatutTable.LIBRE),    "Libre")
        self.assertEqual(str(StatutTable.OCCUPEE),  "Occupée")
        self.assertEqual(str(StatutTable.RESERVEE), "Réservée")

    def test_comparaison(self):
        """Deux références au même statut doivent être égales."""
        self.assertEqual(StatutTable.LIBRE, StatutTable.LIBRE)
        self.assertNotEqual(StatutTable.LIBRE, StatutTable.OCCUPEE)

    def test_utilisation_dans_condition(self):
        """Un statut doit pouvoir être utilisé dans un if."""
        statut = StatutTable.LIBRE
        self.assertTrue(statut == StatutTable.LIBRE)
        self.assertFalse(statut == StatutTable.OCCUPEE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
