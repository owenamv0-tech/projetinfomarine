"""
Module commande.py
Définit les classes LigneCommande et Commande.

Une Commande hérite d'Observable : tout changement de statut
déclenche automatiquement les notifications aux observateurs abonnés
(cuisine, serveurs).

Auteur : Marine
"""

from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Dict, Any

from models.statuts import StatutCommande
from utils.observer import Observable

if TYPE_CHECKING:
    from models.article_carte import ArticleCarte
    from models.table import Table
    from models.personnel import Serveur


# ---------------------------------------------------------------------------
# LigneCommande
# ---------------------------------------------------------------------------

class LigneCommande:
    """
    Représente une ligne dans une commande : un article et sa quantité.

    Attributs:
        article (ArticleCarte)  : L'article commandé.
        quantite (int)          : Nombre de portions commandées.
        commentaire (str)       : Instruction particulière (ex: 'sans oignon').
    """

    def __init__(self, article: ArticleCarte, quantite: int,
                 commentaire: str = "") -> None:
        """
        Initialise une ligne de commande.

        Args:
            article (ArticleCarte)  : L'article commandé.
            quantite (int)          : Quantité (doit être >= 1).
            commentaire (str)       : Commentaire libre (défaut: '').

        Raises:
            ValueError: Si la quantité est inférieure à 1.
        """
        if quantite < 1:
            raise ValueError(
                f"La quantité doit être au moins 1 (reçu : {quantite})."
            )
        self.article = article
        self.quantite = quantite
        self.commentaire = commentaire

    def sous_total(self) -> float:
        """
        Calcule le sous-total de cette ligne.

        Returns:
            float: prix de l'article multiplié par la quantité.
        """
        return round(self.article.prix * self.quantite, 2)

    def __str__(self) -> str:
        commentaire = f" ({self.commentaire})" if self.commentaire else ""
        return (f"{self.quantite}x {self.article.nom}"
                f"{commentaire} — {self.sous_total():.2f}€")

    def __repr__(self) -> str:
        return (f"LigneCommande(article='{self.article.nom}', "
                f"quantite={self.quantite})")


# ---------------------------------------------------------------------------
# Commande
# ---------------------------------------------------------------------------

class Commande(Observable):
    """
    Représente une commande passée par un client à une table.

    Hérite d'Observable : chaque appel à changer_statut() notifie
    automatiquement tous les observateurs abonnés (ObservateurCuisine,
    ObservateurServeur).

    Cycle de vie du statut :
        EN_ATTENTE → EN_PREPARATION → PRET → SERVI → PAYE

    Attributs:
        id_commande (int)                   : Identifiant unique.
        table (Table)                       : Table concernée.
        serveur (Serveur)                   : Serveur ayant pris la commande.
        lignes (List[LigneCommande])        : Articles commandés.
        statut (StatutCommande)             : Statut courant.
        horodatage_creation (datetime)      : Heure de prise de commande.
        horodatage_service (datetime|None)  : Heure de service effectif.
    """

    def __init__(self, id_commande: int, table: Table,
                 serveur: Serveur) -> None:
        """
        Initialise une commande.

        Args:
            id_commande (int)   : Identifiant unique.
            table (Table)       : Table pour laquelle la commande est passée.
            serveur (Serveur)   : Serveur qui prend la commande.
        """
        super().__init__()   # initialise Observable (_observers = [])
        self.id_commande = id_commande
        self.table = table
        self.serveur = serveur
        self.lignes: List[LigneCommande] = []
        self.statut: StatutCommande = StatutCommande.EN_ATTENTE
        self.horodatage_creation: datetime = datetime.now()
        self.horodatage_service: Optional[datetime] = None

    # --- Gestion des lignes ------------------------------------------------

    def ajouter_ligne(self, article: ArticleCarte, quantite: int = 1,
                      commentaire: str = "") -> None:
        """
        Ajoute un article à la commande.

        Args:
            article (ArticleCarte)  : L'article à ajouter.
            quantite (int)          : Nombre de portions (défaut: 1).
            commentaire (str)       : Commentaire libre (défaut: '').

        Raises:
            ValueError: Si l'article n'est pas disponible.
            ValueError: Si la commande est déjà fermée (SERVI ou PAYE).
        """
        if not article.est_disponible():
            raise ValueError(
                f"Impossible d'ajouter '{article.nom}' : article non disponible."
            )
        statuts_fermes = {StatutCommande.SERVI, StatutCommande.PAYE}
        if self.statut in statuts_fermes:
            raise ValueError(
                f"Impossible de modifier une commande au statut '{self.statut}'."
            )
        self.lignes.append(LigneCommande(article, quantite, commentaire))

    def supprimer_ligne(self, id_article: int) -> None:
        """
        Supprime la ligne correspondant à l'article donné.

        Args:
            id_article (int): Identifiant de l'article à retirer.

        Raises:
            ValueError: Si aucune ligne ne correspond à cet identifiant.
        """
        for ligne in self.lignes:
            if ligne.article.id_article == id_article:
                self.lignes.remove(ligne)
                return
        raise ValueError(
            f"Aucune ligne trouvée pour l'article id={id_article}."
        )

    # --- Calculs -----------------------------------------------------------

    def total(self) -> float:
        """
        Calcule le montant total de la commande.

        Returns:
            float: Somme des sous-totaux de toutes les lignes.
                   Retourne 0.0 si la commande est vide.
        """
        return round(sum(ligne.sous_total() for ligne in self.lignes), 2)

    def nombre_articles(self) -> int:
        """
        Retourne le nombre total de portions commandées.

        Returns:
            int: Somme des quantités de toutes les lignes.
        """
        return sum(ligne.quantite for ligne in self.lignes)

    def duree_preparation(self) -> int:
        """
        Calcule le temps écoulé depuis la création de la commande.

        Returns:
            int: Durée en minutes depuis horodatage_creation.
        """
        delta = datetime.now() - self.horodatage_creation
        return int(delta.total_seconds() // 60)

    # --- Changement de statut (cœur de l'Observer) -------------------------

    def changer_statut(self, nouveau_statut: StatutCommande) -> None:
        """
        Change le statut de la commande et notifie tous les observateurs.

        Vérifie que la transition est autorisée selon le cycle de vie
        défini dans StatutCommande.transitions_autorisees().

        Args:
            nouveau_statut (StatutCommande): Le statut cible.

        Raises:
            ValueError: Si la transition est interdite.
        """
        if not self.statut.peut_transitionner_vers(nouveau_statut):
            raise ValueError(
                f"Transition interdite : '{self.statut}' → '{nouveau_statut}'."
            )
        self.statut = nouveau_statut

        if nouveau_statut == StatutCommande.SERVI:
            self.horodatage_service = datetime.now()

        self.notifier()   # ← déclenche tous les observers abonnés

    # --- Sérialisation -----------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise la commande en dictionnaire pour la persistance SQLite.

        Returns:
            Dict[str, Any]: Représentation de la commande.
        """
        return {
            "id_commande": self.id_commande,
            "id_table": self.table.numero,
            "id_serveur": self.serveur.id_personnel,
            "statut": self.statut.value,
            "horodatage_creation": self.horodatage_creation.isoformat(),
            "horodatage_service": (self.horodatage_service.isoformat()
                                   if self.horodatage_service else None),
            "total": self.total(),
            "lignes": [
                {
                    "article_id": l.article.id_article,
                    "article_nom": l.article.nom,
                    "quantite": l.quantite,
                    "commentaire": l.commentaire,
                    "sous_total": l.sous_total(),
                }
                for l in self.lignes
            ],
        }

    def __str__(self) -> str:
        lignes_str = "\n  ".join(str(l) for l in self.lignes) or "Aucun article"
        return (
            f"Commande n°{self.id_commande} — Table {self.table.numero} "
            f"— {self.serveur.get_nom_complet()}\n"
            f"  Statut : {self.statut}\n"
            f"  {lignes_str}\n"
            f"  Total  : {self.total():.2f}€"
        )

    def __repr__(self) -> str:
        return (f"Commande(id={self.id_commande}, "
                f"statut='{self.statut}', "
                f"total={self.total()})")
