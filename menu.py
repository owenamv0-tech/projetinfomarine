"""
Module menu.py
Définit la classe Menu représentant une offre à prix fixe de la carte.

Un menu regroupe un plat principal (obligatoire) et optionnellement
une entrée, un dessert et une boisson, proposés à un prix forfaitaire
inférieur à la somme des articles pris séparément.

Auteur : Marine
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Any

if TYPE_CHECKING:
    from models.article_carte import Entree, PlatPrincipal, Dessert, Boisson


class Menu:
    """
    Représente un menu à prix fixe proposé sur la carte du restaurant.

    Un menu est composé d'un plat principal obligatoire et d'articles
    optionnels (entrée, dessert, boisson). Son prix forfaitaire est
    inférieur à la somme des articles commandés séparément.

    Attributs:
        id_menu (int)               : Identifiant unique du menu.
        nom (str)                   : Nom affiché sur la carte.
        prix (float)                : Prix forfaitaire en euros.
        plat (PlatPrincipal)        : Plat principal (obligatoire).
        entree (Entree | None)      : Entrée incluse (optionnelle).
        dessert (Dessert | None)    : Dessert inclus (optionnel).
        boisson (Boisson | None)    : Boisson incluse (optionnelle).
        disponible (bool)           : Menu proposé aujourd'hui.
    """

    def __init__(self, id_menu: int, nom: str, prix: float,
                 plat: PlatPrincipal,
                 entree: Optional[Entree] = None,
                 dessert: Optional[Dessert] = None,
                 boisson: Optional[Boisson] = None,
                 disponible: bool = True) -> None:
        """
        Initialise un menu.

        Args:
            id_menu (int)           : Identifiant unique.
            nom (str)               : Nom du menu.
            prix (float)            : Prix forfaitaire en euros.
            plat (PlatPrincipal)    : Plat principal (obligatoire).
            entree (Entree)         : Entrée incluse (défaut: None).
            dessert (Dessert)       : Dessert inclus (défaut: None).
            boisson (Boisson)       : Boisson incluse (défaut: None).
            disponible (bool)       : Disponibilité (défaut: True).

        Raises:
            ValueError: Si le prix est négatif.
            ValueError: Si le nom est vide.
        """
        if prix < 0:
            raise ValueError(
                f"Le prix du menu '{nom}' ne peut pas être négatif."
            )
        if not nom.strip():
            raise ValueError("Le nom du menu ne peut pas être vide.")

        self.id_menu = id_menu
        self.nom = nom.strip()
        self.prix = prix
        self.plat = plat
        self.entree = entree
        self.dessert = dessert
        self.boisson = boisson
        self.disponible = disponible

    # -----------------------------------------------------------------------
    # Accesseurs et calculs
    # -----------------------------------------------------------------------

    def get_articles(self) -> list:
        """
        Retourne la liste de tous les articles présents dans ce menu,
        en excluant les optionnels absents (None).

        Returns:
            list[ArticleCarte]: Articles composant le menu.
        """
        articles = [self.plat]
        for article in [self.entree, self.dessert, self.boisson]:
            if article is not None:
                articles.append(article)
        return articles

    def calculer_prix_a_la_carte(self) -> float:
        """
        Calcule le prix total si chaque article était commandé séparément.

        Returns:
            float: Somme des prix individuels des articles du menu.
        """
        return round(sum(a.prix for a in self.get_articles()), 2)

    def calculer_economie(self) -> float:
        """
        Calcule l'économie réalisée en prenant le menu plutôt qu'à la carte.

        Returns:
            float: Différence entre prix à la carte et prix du menu.
                   Retourne 0 si le menu est plus cher (ne devrait pas arriver).
        """
        return round(max(0.0, self.calculer_prix_a_la_carte() - self.prix), 2)

    def est_complet(self) -> bool:
        """
        Vérifie si tous les articles présents dans ce menu sont disponibles.

        Le plat est obligatoire. Les articles optionnels non nuls
        doivent également être disponibles.

        Returns:
            bool: True si tous les articles présents sont disponibles.
        """
        return all(a.est_disponible() for a in self.get_articles())

    def get_allergenes(self) -> List[str]:
        """
        Retourne la liste unifiée des allergènes présents dans le menu,
        en agrégeant les allergènes de tous les articles.

        Returns:
            List[str]: Noms des ingrédients allergènes (sans doublons, triés).
        """
        allergenes = set()
        for article in self.get_articles():
            for nom in article.get_allergenes():
                allergenes.add(nom)
        return sorted(allergenes)

    def get_temps_preparation_total(self) -> int:
        """
        Retourne le temps de préparation total du menu.
        Correspond au maximum des temps de préparation de chaque article
        (les plats sont préparés en parallèle en cuisine).

        Returns:
            int: Temps de préparation maximal en minutes.
        """
        return max(a.get_temps_preparation() for a in self.get_articles())

    # -----------------------------------------------------------------------
    # Disponibilité
    # -----------------------------------------------------------------------

    def activer(self) -> None:
        """Rend le menu disponible sur la carte."""
        self.disponible = True

    def desactiver(self) -> None:
        """Retire le menu de la carte."""
        self.disponible = False

    # -----------------------------------------------------------------------
    # Sérialisation
    # -----------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise le menu en dictionnaire pour la persistance JSON ou SQLite.

        Returns:
            Dict[str, Any]: Représentation du menu.
        """
        return {
            "id_menu": self.id_menu,
            "nom": self.nom,
            "prix": self.prix,
            "disponible": self.disponible,
            "id_plat": self.plat.id_article,
            "id_entree": self.entree.id_article if self.entree else None,
            "id_dessert": self.dessert.id_article if self.dessert else None,
            "id_boisson": self.boisson.id_article if self.boisson else None,
        }

    # -----------------------------------------------------------------------
    # Représentations
    # -----------------------------------------------------------------------

    def __str__(self) -> str:
        dispo = "✓" if self.disponible else "✗"
        articles = " + ".join(a.nom for a in self.get_articles())
        economie = self.calculer_economie()
        return (
            f"[{dispo}] {self.nom} — {self.prix:.2f}€ "
            f"(économie : {economie:.2f}€) | {articles}"
        )

    def __repr__(self) -> str:
        return (
            f"Menu(id={self.id_menu}, nom='{self.nom}', "
            f"prix={self.prix})"
        )
