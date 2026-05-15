"""
Module statuts.py
Définit les énumérations des statuts utilisés dans le logiciel.

Les Enums garantissent qu'un statut ne peut prendre qu'une valeur
prédéfinie, ce qui évite les erreurs de saisie et facilite les
comparaisons dans le code.

Auteur : Marine
"""

from enum import Enum


class StatutCommande(Enum):
    """
    Énumération des statuts possibles d'une commande.

    Une commande suit ce cycle de vie dans l'ordre :
        EN_ATTENTE → EN_PREPARATION → PRET → SERVI → PAYE

    Valeurs:
        EN_ATTENTE    : La commande a été prise mais pas encore
                        transmise en cuisine.
        EN_PREPARATION: La cuisine a commencé la préparation.
        PRET          : Les plats sont prêts, en attente du service.
        SERVI         : Les plats ont été apportés à la table.
        PAYE          : La commande a été réglée, table libérée.
    """
    EN_ATTENTE     = "En attente"
    EN_PREPARATION = "En préparation"
    PRET           = "Prêt à servir"
    SERVI          = "Servi"
    PAYE           = "Payé"

    def __str__(self) -> str:
        """Retourne la valeur lisible du statut."""
        return self.value

    def transitions_autorisees(self) -> list:
        """
        Retourne la liste des statuts vers lesquels on peut
        transitionner depuis le statut courant.

        Returns:
            list[StatutCommande]: Transitions valides depuis ce statut.

        Exemple:
            >>> StatutCommande.EN_ATTENTE.transitions_autorisees()
            [<StatutCommande.EN_PREPARATION: 'En préparation'>]
        """
        transitions = {
            StatutCommande.EN_ATTENTE:     [StatutCommande.EN_PREPARATION],
            StatutCommande.EN_PREPARATION: [StatutCommande.PRET],
            StatutCommande.PRET:           [StatutCommande.SERVI],
            StatutCommande.SERVI:          [StatutCommande.PAYE],
            StatutCommande.PAYE:           [],
        }
        return transitions[self]

    def peut_transitionner_vers(self, cible: 'StatutCommande') -> bool:
        """
        Vérifie si la transition vers un statut cible est autorisée.

        Args:
            cible (StatutCommande): Le statut vers lequel on veut aller.

        Returns:
            bool: True si la transition est valide, False sinon.

        Exemple:
            >>> StatutCommande.EN_ATTENTE.peut_transitionner_vers(
            ...     StatutCommande.EN_PREPARATION)
            True
            >>> StatutCommande.EN_ATTENTE.peut_transitionner_vers(
            ...     StatutCommande.PAYE)
            False
        """
        return cible in self.transitions_autorisees()


class StatutTable(Enum):
    """
    Énumération des statuts possibles d'une table du restaurant.

    Valeurs:
        LIBRE    : La table est disponible, aucun client.
        OCCUPEE  : Des clients sont installés, commande en cours.
        RESERVEE : La table est réservée pour plus tard.
    """
    LIBRE    = "Libre"
    OCCUPEE  = "Occupée"
    RESERVEE = "Réservée"

    def __str__(self) -> str:
        """Retourne la valeur lisible du statut."""
        return self.value
