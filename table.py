"""
Module table.py
Définit la classe Table représentant une table physique du restaurant.

Une table porte un statut (LIBRE, OCCUPEE, RESERVEE) et peut être
associée à une commande active. Elle délègue la création de la commande
à la classe Commande pour respecter le principe de responsabilité unique.

Auteur : Marine
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from models.statuts import StatutTable, StatutCommande

if TYPE_CHECKING:
    from models.commande import Commande
    from models.personnel import Serveur


class Table:
    """
    Représente une table physique du restaurant.

    Une table passe par différents états au fil du service :
        LIBRE → OCCUPEE (à l'ouverture d'une commande)
        OCCUPEE → LIBRE (à la fermeture, une fois la commande payée)
        LIBRE → RESERVEE (en cas de réservation)
        RESERVEE → LIBRE (annulation ou arrivée du client)

    Attributs:
        numero (int)                        : Numéro d'identification de la table.
        capacite (int)                      : Nombre de couverts maximum.
        statut (StatutTable)                : État courant de la table.
        commande_active (Commande | None)   : Commande en cours (ou None).
    """

    # Compteur de classe partagé pour générer les identifiants de commandes.
    # Incrémenté à chaque appel à ouvrir_commande().
    _compteur_commandes: int = 0

    def __init__(self, numero: int, capacite: int) -> None:
        """
        Initialise une table libre, sans commande active.

        Args:
            numero (int)    : Numéro de la table (doit être >= 1).
            capacite (int)  : Nombre de couverts maximum (doit être >= 1).

        Raises:
            ValueError: Si numero ou capacite est inférieur à 1.
        """
        if numero < 1:
            raise ValueError(
                f"Le numéro de table doit être >= 1 (reçu : {numero})."
            )
        if capacite < 1:
            raise ValueError(
                f"La capacité doit être >= 1 (reçu : {capacite})."
            )
        self.numero = numero
        self.capacite = capacite
        self.statut: StatutTable = StatutTable.LIBRE
        self.commande_active: Optional[Commande] = None

    # -----------------------------------------------------------------------
    # Gestion de l'occupation
    # -----------------------------------------------------------------------

    def ouvrir_commande(self, serveur: Serveur) -> Commande:
        """
        Ouvre une nouvelle commande pour cette table et la passe à OCCUPEE.

        Crée un objet Commande, l'associe à cette table et au serveur
        fourni, puis change le statut de la table en OCCUPEE.

        Args:
            serveur (Serveur): Le serveur qui prend en charge la table.

        Returns:
            Commande: La nouvelle commande créée.

        Raises:
            ValueError: Si la table n'est pas LIBRE.
        """
        if self.statut != StatutTable.LIBRE:
            raise ValueError(
                f"Impossible d'ouvrir une commande : "
                f"la table n°{self.numero} est '{self.statut}' (pas libre)."
            )
        # Import local pour éviter l'import circulaire
        # (Commande importe Table via TYPE_CHECKING)
        from models.commande import Commande

        Table._compteur_commandes += 1
        self.commande_active = Commande(
            id_commande=Table._compteur_commandes,
            table=self,
            serveur=serveur
        )
        self.statut = StatutTable.OCCUPEE
        return self.commande_active

    def fermer_commande(self) -> None:
        """
        Ferme la commande active et remet la table à LIBRE.

        La fermeture n'est autorisée que si la commande est au statut PAYE,
        ce qui garantit que la table ne sera pas libérée avant règlement.

        Raises:
            ValueError: Si aucune commande n'est en cours.
            ValueError: Si la commande n'est pas encore au statut PAYE.
        """
        if self.commande_active is None:
            raise ValueError(
                f"La table n°{self.numero} n'a pas de commande active à fermer."
            )
        if self.commande_active.statut != StatutCommande.PAYE:
            raise ValueError(
                f"Impossible de fermer la table n°{self.numero} : "
                f"la commande est au statut '{self.commande_active.statut}' "
                f"— elle doit être PAYÉE d'abord."
            )
        self.commande_active = None
        self.statut = StatutTable.LIBRE

    # -----------------------------------------------------------------------
    # Gestion des réservations
    # -----------------------------------------------------------------------

    def reserver(self) -> None:
        """
        Passe la table au statut RESERVEE.

        Raises:
            ValueError: Si la table n'est pas LIBRE.
        """
        if self.statut != StatutTable.LIBRE:
            raise ValueError(
                f"Impossible de réserver la table n°{self.numero} : "
                f"elle est '{self.statut}'."
            )
        self.statut = StatutTable.RESERVEE

    def liberer_reservation(self) -> None:
        """
        Annule la réservation et remet la table au statut LIBRE.

        Raises:
            ValueError: Si la table n'est pas RESERVEE.
        """
        if self.statut != StatutTable.RESERVEE:
            raise ValueError(
                f"La table n°{self.numero} n'est pas réservée "
                f"(statut actuel : '{self.statut}')."
            )
        self.statut = StatutTable.LIBRE

    # -----------------------------------------------------------------------
    # Accesseurs
    # -----------------------------------------------------------------------

    def est_disponible(self) -> bool:
        """
        Indique si la table est disponible pour accueillir des clients.

        Returns:
            bool: True si le statut est LIBRE, False sinon.
        """
        return self.statut == StatutTable.LIBRE

    # -----------------------------------------------------------------------
    # Représentations
    # -----------------------------------------------------------------------

    def __str__(self) -> str:
        cmd_info = (
            f", commande n°{self.commande_active.id_commande}"
            if self.commande_active else ""
        )
        return (
            f"Table n°{self.numero} "
            f"({self.capacite} couverts) — {self.statut}{cmd_info}"
        )

    def __repr__(self) -> str:
        return (
            f"Table(numero={self.numero}, "
            f"capacite={self.capacite}, "
            f"statut='{self.statut}')"
        )
