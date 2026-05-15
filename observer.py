"""
Module observer.py
Implémentation du design pattern Observer pour la gestion des notifications
entre la cuisine et la salle lors des changements de statut des commandes.

Hiérarchie :
    Observer (ABC)
        ├── ObservateurCuisine
        └── ObservateurServeur
    Observable
        └── (hérité par Commande)

Auteur : Marine
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.commande import Commande


# ---------------------------------------------------------------------------
# Interface Observer
# ---------------------------------------------------------------------------

class Observer(ABC):
    """
    Interface abstraite que tout observateur doit implémenter.

    Un observateur s'abonne à un Observable et reçoit une notification
    à chaque fois que l'état de cet observable change.
    """

    @abstractmethod
    def mettre_a_jour(self, commande: Commande) -> None:
        """
        Méthode appelée automatiquement lors d'un changement de statut
        sur une commande observée.

        Args:
            commande (Commande): La commande dont le statut a changé.
        """


# ---------------------------------------------------------------------------
# Classe Observable
# ---------------------------------------------------------------------------

class Observable:
    """
    Classe mixin à hériter pour rendre un objet observable.

    Toute classe héritant d'Observable peut notifier une liste
    d'observateurs abonnés lors d'un changement d'état.
    Utilisée par Commande pour notifier la cuisine et les serveurs.
    """

    def __init__(self) -> None:
        """Initialise la liste des observateurs."""
        self._observers: List[Observer] = []

    def abonner(self, observer: Observer) -> None:
        """
        Abonne un observateur aux notifications de cet objet.

        Args:
            observer (Observer): L'observateur à abonner.

        Raises:
            ValueError: Si l'observateur est déjà abonné.
        """
        if observer in self._observers:
            raise ValueError("Cet observateur est déjà abonné.")
        self._observers.append(observer)

    def desabonner(self, observer: Observer) -> None:
        """
        Désabonne un observateur des notifications de cet objet.

        Args:
            observer (Observer): L'observateur à désabonner.

        Raises:
            ValueError: Si l'observateur n'est pas abonné.
        """
        if observer not in self._observers:
            raise ValueError("Cet observateur n'est pas abonné.")
        self._observers.remove(observer)

    def notifier(self) -> None:
        """
        Notifie tous les observateurs abonnés en appelant
        leur méthode mettre_a_jour().
        """
        for observer in self._observers:
            observer.mettre_a_jour(self)  # type: ignore[arg-type]

    def get_nombre_observateurs(self) -> int:
        """
        Retourne le nombre d'observateurs actuellement abonnés.

        Returns:
            int: Nombre d'observateurs.
        """
        return len(self._observers)


# ---------------------------------------------------------------------------
# Observateurs concrets
# ---------------------------------------------------------------------------

class ObservateurCuisine(Observer):
    """
    Observateur utilisé côté cuisine.

    Se déclenche quand une commande passe au statut EN_ATTENTE.
    Maintient une file des nouvelles commandes à préparer,
    que l'interface graphique d'Owen pourra lire et afficher.

    Attributs:
        nouvelles_commandes (List[Commande]): File des commandes à traiter.
    """

    def __init__(self) -> None:
        """Initialise la file des nouvelles commandes."""
        self.nouvelles_commandes: List[Commande] = []

    def mettre_a_jour(self, commande: Commande) -> None:
        """
        Réagit aux changements de statut d'une commande.
        N'enregistre la commande que si elle passe à EN_ATTENTE.

        Args:
            commande (Commande): La commande dont le statut a changé.
        """
        from models.statuts import StatutCommande
        if commande.statut == StatutCommande.EN_ATTENTE:
            if commande not in self.nouvelles_commandes:
                self.nouvelles_commandes.append(commande)

    def acquitter(self, commande: Commande) -> None:
        """
        Retire une commande de la file une fois que la cuisine
        a pris en charge sa préparation.

        Args:
            commande (Commande): La commande à acquitter.
        """
        if commande in self.nouvelles_commandes:
            self.nouvelles_commandes.remove(commande)

    def get_nombre_en_attente(self) -> int:
        """
        Retourne le nombre de commandes en attente de traitement.

        Returns:
            int: Nombre de commandes non acquittées.
        """
        return len(self.nouvelles_commandes)


class ObservateurServeur(Observer):
    """
    Observateur utilisé côté salle.

    Se déclenche quand une commande passe au statut PRET.
    Maintient une liste des commandes prêtes à servir,
    que l'interface graphique d'Owen pourra lire et afficher.

    Attributs:
        commandes_pretes (List[Commande]): Commandes prêtes à être servies.
    """

    def __init__(self) -> None:
        """Initialise la liste des commandes prêtes."""
        self.commandes_pretes: List[Commande] = []

    def mettre_a_jour(self, commande: Commande) -> None:
        """
        Réagit aux changements de statut d'une commande.
        N'enregistre la commande que si elle passe à PRET.

        Args:
            commande (Commande): La commande dont le statut a changé.
        """
        from models.statuts import StatutCommande
        if commande.statut == StatutCommande.PRET:
            if commande not in self.commandes_pretes:
                self.commandes_pretes.append(commande)

    def acquitter(self, commande: Commande) -> None:
        """
        Retire une commande de la liste une fois qu'elle a été servie.

        Args:
            commande (Commande): La commande à acquitter.
        """
        if commande in self.commandes_pretes:
            self.commandes_pretes.remove(commande)

    def get_nombre_prets(self) -> int:
        """
        Retourne le nombre de commandes prêtes à servir.

        Returns:
            int: Nombre de commandes prêtes non acquittées.
        """
        return len(self.commandes_pretes)
