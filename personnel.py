"""
Module personnel.py
Définit la hiérarchie de classes pour le personnel du restaurant.

Hiérarchie :
    Personnel (ABC)
        ├── Serveur
        └── Cuisinier

Le module utilise des annotations différées (from __future__ import annotations)
pour éviter les imports circulaires avec table.py et commande.py qui
seront écrits aux étapes suivantes.

Auteur : Marine
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

# Imports uniquement pour la vérification de types (évite les imports circulaires)
if TYPE_CHECKING:
    from models.table import Table
    from models.commande import Commande
    from models.statuts import StatutCommande


# ---------------------------------------------------------------------------
# Classe abstraite de base
# ---------------------------------------------------------------------------

class Personnel(ABC):
    """
    Classe abstraite représentant un membre du personnel du restaurant.

    Regroupe les attributs communs à tout le personnel. Cette classe
    ne peut pas être instanciée directement : il faut utiliser
    Serveur ou Cuisinier.

    Attributs:
        id_personnel (int)  : Identifiant unique du membre du personnel.
        nom (str)           : Nom de famille.
        prenom (str)        : Prénom.
    """

    def __init__(self, id_personnel: int, nom: str, prenom: str):
        """
        Initialise un membre du personnel.

        Args:
            id_personnel (int)  : Identifiant unique.
            nom (str)           : Nom de famille.
            prenom (str)        : Prénom.

        Raises:
            ValueError: Si nom ou prénom est vide.
        """
        if not nom.strip():
            raise ValueError("Le nom du personnel ne peut pas être vide.")
        if not prenom.strip():
            raise ValueError("Le prénom du personnel ne peut pas être vide.")

        self.id_personnel = id_personnel
        self.nom = nom.strip()
        self.prenom = prenom.strip()

    @abstractmethod
    def get_role(self) -> str:
        """
        Retourne le rôle du membre du personnel.

        Returns:
            str: 'Serveur' ou 'Cuisinier' selon la sous-classe.
        """

    def get_nom_complet(self) -> str:
        """
        Retourne le prénom et le nom concaténés.

        Returns:
            str: Prénom et nom (ex: 'Alice Dupont').
        """
        return f"{self.prenom} {self.nom}"

    def __str__(self) -> str:
        return f"[{self.get_role()}] {self.get_nom_complet()} (id={self.id_personnel})"

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"id={self.id_personnel}, "
                f"nom='{self.nom}', "
                f"prenom='{self.prenom}')")

    def __eq__(self, other: object) -> bool:
        """Deux membres du personnel sont égaux s'ils ont le même id."""
        if not isinstance(other, Personnel):
            return False
        return self.id_personnel == other.id_personnel


# ---------------------------------------------------------------------------
# Sous-classe : Serveur
# ---------------------------------------------------------------------------

class Serveur(Personnel):
    """
    Représente un serveur du restaurant.

    Un serveur est responsable d'un ensemble de tables. Il prend les
    commandes et assure le service entre la cuisine et les clients.

    Attributs supplémentaires:
        tables_assignees (List[Table]) : Tables dont il est responsable.
    """

    def __init__(self, id_personnel: int, nom: str, prenom: str):
        """
        Initialise un serveur.

        Args:
            id_personnel (int)  : Identifiant unique.
            nom (str)           : Nom de famille.
            prenom (str)        : Prénom.
        """
        super().__init__(id_personnel, nom, prenom)
        self.tables_assignees: List[Table] = []

    def get_role(self) -> str:
        """Retourne le rôle 'Serveur'."""
        return "Serveur"

    def assigner_table(self, table: Table) -> None:
        """
        Assigne une table à ce serveur.

        Args:
            table (Table): La table à assigner.

        Raises:
            ValueError: Si la table est déjà assignée à ce serveur.
        """
        if table in self.tables_assignees:
            raise ValueError(
                f"La table n°{table.numero} est déjà assignée "
                f"à {self.get_nom_complet()}."
            )
        self.tables_assignees.append(table)

    def retirer_table(self, table: Table) -> None:
        """
        Retire une table des responsabilités de ce serveur.

        Args:
            table (Table): La table à retirer.

        Raises:
            ValueError: Si la table n'est pas assignée à ce serveur.
        """
        if table not in self.tables_assignees:
            raise ValueError(
                f"La table n°{table.numero} n'est pas assignée "
                f"à {self.get_nom_complet()}."
            )
        self.tables_assignees.remove(table)

    def get_commandes_en_cours(self) -> List[Commande]:
        """
        Retourne la liste de toutes les commandes actives sur les tables
        assignées à ce serveur (c'est-à-dire les commandes dont le statut
        n'est ni SERVI ni PAYE).

        Returns:
            List[Commande]: Commandes en cours sur les tables du serveur.
        """
        from models.statuts import StatutCommande

        statuts_termines = {StatutCommande.SERVI, StatutCommande.PAYE}
        commandes = []

        for table in self.tables_assignees:
            if (table.commande_active is not None
                    and table.commande_active.statut not in statuts_termines):
                commandes.append(table.commande_active)

        return commandes

    def get_nombre_tables(self) -> int:
        """
        Retourne le nombre de tables assignées à ce serveur.

        Returns:
            int: Nombre de tables.
        """
        return len(self.tables_assignees)


# ---------------------------------------------------------------------------
# Sous-classe : Cuisinier
# ---------------------------------------------------------------------------

class Cuisinier(Personnel):
    """
    Représente un cuisinier du restaurant.

    Un cuisinier reçoit les commandes transmises par les serveurs,
    les prépare et les marque comme prêtes pour le service.

    Attributs supplémentaires:
        specialite (str) : Domaine de spécialité (ex: 'Pâtisserie', 'Grill').
    """

    def __init__(self, id_personnel: int, nom: str, prenom: str,
                 specialite: str = "Cuisine générale"):
        """
        Initialise un cuisinier.

        Args:
            id_personnel (int)  : Identifiant unique.
            nom (str)           : Nom de famille.
            prenom (str)        : Prénom.
            specialite (str)    : Spécialité culinaire (défaut: 'Cuisine générale').
        """
        super().__init__(id_personnel, nom, prenom)
        self.specialite = specialite

    def get_role(self) -> str:
        """Retourne le rôle 'Cuisinier'."""
        return "Cuisinier"

    def get_commandes_a_preparer(
            self, toutes_commandes: List[Commande]) -> List[Commande]:
        """
        Filtre une liste de commandes pour ne retourner que celles
        qui sont en attente ou en cours de préparation.

        Args:
            toutes_commandes (List[Commande]): Toutes les commandes actives
                                              du restaurant.

        Returns:
            List[Commande]: Commandes à traiter par ce cuisinier,
                            triées par heure de création (la plus ancienne
                            en premier).
        """
        from models.statuts import StatutCommande

        statuts_a_traiter = {
            StatutCommande.EN_ATTENTE,
            StatutCommande.EN_PREPARATION
        }
        a_preparer = [
            cmd for cmd in toutes_commandes
            if cmd.statut in statuts_a_traiter
        ]
        # Priorité FIFO : la commande la plus ancienne en premier
        return sorted(a_preparer, key=lambda cmd: cmd.horodatage_creation)

    def marquer_prete(self, commande: Commande) -> None:
        """
        Marque une commande comme prête à être servie.
        Déclenche la notification aux serveurs via le pattern Observer.

        Args:
            commande (Commande): La commande à marquer comme prête.

        Raises:
            ValueError: Si la commande n'est pas en cours de préparation.
        """
        from models.statuts import StatutCommande

        if commande.statut != StatutCommande.EN_PREPARATION:
            raise ValueError(
                f"Impossible de marquer comme prête : la commande "
                f"n°{commande.id_commande} est en statut "
                f"'{commande.statut}' (attendu : EN_PREPARATION)."
            )
        commande.changer_statut(StatutCommande.PRET)
