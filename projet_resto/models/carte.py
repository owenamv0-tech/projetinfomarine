"""
Module carte.py
Définit la classe Carte représentant l'ensemble de l'offre du restaurant.

La carte regroupe tous les articles disponibles (entrées, plats, desserts,
boissons) ainsi que les menus à prix fixe. Elle est le point d'entrée
consulté par les serveurs pour prendre les commandes.

Contient la fonction récursive get_articles_disponibles() (figure bonus n°2).

Auteur : Marine
"""

from __future__ import annotations
import json
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from models.article_carte import (ArticleCarte, Entree, PlatPrincipal,
                                   Dessert, Boisson)
from models.menu import Menu


class Carte:
    """
    Représente la carte complète du restaurant.

    Regroupe tous les articles à la carte (entrées, plats principaux,
    desserts, boissons) et les menus à prix fixe. Fournit des méthodes
    de recherche, de filtrage et de persistance.

    Attributs:
        entrees (List[Entree])              : Entrées disponibles.
        plats (List[PlatPrincipal])         : Plats principaux disponibles.
        desserts (List[Dessert])            : Desserts disponibles.
        boissons (List[Boisson])            : Boissons disponibles.
        menus (List[Menu])                  : Menus à prix fixe.
    """

    def __init__(self) -> None:
        """Initialise une carte vide."""
        self.entrees: List[Entree] = []
        self.plats: List[PlatPrincipal] = []
        self.desserts: List[Dessert] = []
        self.boissons: List[Boisson] = []
        self.menus: List[Menu] = []

    # -----------------------------------------------------------------------
    # Ajout et suppression d'articles
    # -----------------------------------------------------------------------

    def ajouter_article(self, article: ArticleCarte) -> None:
        """
        Ajoute un article dans la liste correspondant à son type.
        Le type est détecté automatiquement via isinstance().

        Args:
            article (ArticleCarte): L'article à ajouter.

        Raises:
            ValueError: Si un article avec le même id existe déjà.
            TypeError:  Si le type de l'article n'est pas reconnu.
        """
        liste = self._get_liste_pour(article)
        if any(a.id_article == article.id_article for a in liste):
            raise ValueError(
                f"Un article avec l'id {article.id_article} "
                f"existe déjà dans la carte."
            )
        liste.append(article)

    def supprimer_article(self, id_article: int) -> None:
        """
        Supprime l'article dont l'identifiant correspond, quelle que soit
        sa catégorie.

        Args:
            id_article (int): Identifiant de l'article à supprimer.

        Raises:
            ValueError: Si aucun article ne correspond à cet identifiant.
        """
        for liste in [self.entrees, self.plats, self.desserts, self.boissons]:
            for article in liste:
                if article.id_article == id_article:
                    liste.remove(article)
                    return
        raise ValueError(
            f"Aucun article avec l'id {id_article} trouvé dans la carte."
        )

    def ajouter_menu(self, menu: Menu) -> None:
        """
        Ajoute un menu à prix fixe à la carte.

        Args:
            menu (Menu): Le menu à ajouter.

        Raises:
            ValueError: Si un menu avec le même id existe déjà.
        """
        if any(m.id_menu == menu.id_menu for m in self.menus):
            raise ValueError(
                f"Un menu avec l'id {menu.id_menu} existe déjà dans la carte."
            )
        self.menus.append(menu)

    def supprimer_menu(self, id_menu: int) -> None:
        """
        Supprime un menu de la carte.

        Args:
            id_menu (int): Identifiant du menu à supprimer.

        Raises:
            ValueError: Si aucun menu ne correspond à cet identifiant.
        """
        for menu in self.menus:
            if menu.id_menu == id_menu:
                self.menus.remove(menu)
                return
        raise ValueError(
            f"Aucun menu avec l'id {id_menu} trouvé dans la carte."
        )

    # -----------------------------------------------------------------------
    # Fonction récursive — Figure bonus n°2
    # -----------------------------------------------------------------------

    def get_articles_disponibles(self, liste: List[ArticleCarte],
                                  index: int = 0) -> List[ArticleCarte]:
        """
        Retourne la sous-liste des articles disponibles parmi une liste donnée.

        Fonction récursive : parcourt la liste article par article en
        s'appelant elle-même avec index + 1 jusqu'à atteindre la fin.

        Complexité : O(n) — chaque article est examiné une fois.

        Args:
            liste (List[ArticleCarte])  : Liste d'articles à filtrer.
            index (int)                 : Indice courant (défaut: 0).

        Returns:
            List[ArticleCarte]: Articles dont est_disponible() est True.

        Exemple:
            >>> carte.get_articles_disponibles(carte.plats)
            [PlatPrincipal(...), PlatPrincipal(...)]
        """
        # Cas de base : on a parcouru toute la liste
        if index >= len(liste):
            return []

        article = liste[index]
        reste = self.get_articles_disponibles(liste, index + 1)

        if article.est_disponible():
            return [article] + reste
        return reste

    # -----------------------------------------------------------------------
    # Accès et recherche
    # -----------------------------------------------------------------------

    def get_menus_disponibles(self) -> List[Menu]:
        """
        Retourne les menus dont tous les articles sont disponibles.

        Returns:
            List[Menu]: Menus disponibles et complets.
        """
        return [m for m in self.menus if m.disponible and m.est_complet()]

    def get_tous_les_articles(self) -> List[ArticleCarte]:
        """
        Retourne l'ensemble des articles de la carte, toutes catégories
        confondues.

        Returns:
            List[ArticleCarte]: Tous les articles de la carte.
        """
        return self.entrees + self.plats + self.desserts + self.boissons

    def rechercher_par_nom(self, nom: str) -> List[ArticleCarte]:
        """
        Recherche des articles dont le nom contient la chaîne donnée,
        sans tenir compte de la casse.

        Args:
            nom (str): Chaîne de caractères à rechercher.

        Returns:
            List[ArticleCarte]: Articles correspondants.
        """
        nom_lower = nom.lower()
        return [
            a for a in self.get_tous_les_articles()
            if nom_lower in a.nom.lower()
        ]

    def rechercher_par_id(self, id_article: int) -> Optional[ArticleCarte]:
        """
        Recherche un article par son identifiant unique.

        Args:
            id_article (int): Identifiant de l'article.

        Returns:
            ArticleCarte | None: L'article trouvé, ou None.
        """
        for article in self.get_tous_les_articles():
            if article.id_article == id_article:
                return article
        return None

    def get_articles_avec_allergene(self, allergene: str) -> List[ArticleCarte]:
        """
        Retourne tous les articles contenant un allergène donné.

        Args:
            allergene (str): Nom de l'allergène recherché.

        Returns:
            List[ArticleCarte]: Articles contenant cet allergène.
        """
        allergene_lower = allergene.lower()
        return [
            a for a in self.get_tous_les_articles()
            if any(al.lower() == allergene_lower for al in a.get_allergenes())
        ]

    def filtrer_sans_allergene(self, allergene: str) -> List[ArticleCarte]:
        """
        Retourne tous les articles qui ne contiennent PAS l'allergène donné.

        Args:
            allergene (str): Nom de l'allergène à éviter.

        Returns:
            List[ArticleCarte]: Articles sûrs (ne contenant pas l'allergène).
        """
        allergene_lower = allergene.lower()
        articles_sans_allergene = []

        # On utilise ta méthode existante pour parcourir toute la carte d'un coup
        for article in self.get_tous_les_articles():
            # On récupère les allergènes de l'article en minuscules
            allergenes_article = [al.lower() for al in article.get_allergenes()]

            # Si l'allergène ciblé n'est pas dans la liste de l'article, on le garde
            if allergene_lower not in allergenes_article:
                articles_sans_allergene.append(article)

        return articles_sans_allergene
    # -----------------------------------------------------------------------
    # Statistiques
    # -----------------------------------------------------------------------

    def get_prix_moyen_par_type(self) -> Dict[str, float]:
        """
        Calcule le prix moyen par catégorie d'article.

        Returns:
            Dict[str, float]: Dictionnaire type → prix moyen.
                              Les catégories sans article sont exclues.
        """
        categories = {
            "Entrée": self.entrees,
            "Plat": self.plats,
            "Dessert": self.desserts,
            "Boisson": self.boissons,
        }
        return {
            type_: round(sum(a.prix for a in liste) / len(liste), 2)
            for type_, liste in categories.items()
            if liste
        }

    # -----------------------------------------------------------------------
    # Persistance JSON — Figure imposée n°6
    # -----------------------------------------------------------------------

    def to_json(self, chemin: str) -> None:
        """
        Sauvegarde la carte complète dans un fichier JSON.

        Chaque article est sérialisé avec ses attributs principaux.
        Les menus ne stockent que les identifiants de leurs articles.

        Args:
            chemin (str): Chemin du fichier de destination.
        """
        def article_to_dict(a: ArticleCarte) -> Dict[str, Any]:
            base = {
                "id_article": a.id_article,
                "type": a.get_type(),
                "nom": a.nom,
                "description": a.description,
                "prix": a.prix,
                "disponible": a.disponible,
                "temps_preparation": a.get_temps_preparation(),
                "ingredients": [
                    {
                        "nom": ing.nom,
                        "quantite": ing.quantite,
                        "unite": ing.unite,
                        "allergene": ing.allergene,
                    }
                    for ing in a.get_ingredients()
                ],
            }
            # Attributs spécifiques à chaque type
            if isinstance(a, Entree):
                base["servie_chaude"] = a.servie_chaude
            elif isinstance(a, PlatPrincipal):
                base["accompagnement"] = a.accompagnement
            elif isinstance(a, Dessert):
                base["fait_maison"] = a.fait_maison
            elif isinstance(a, Boisson):
                base["volume_cl"] = a.volume_cl
                base["est_alcoolisee"] = a.est_alcoolisee
                base["temperature_service"] = a.temperature_service
            return base

        donnees = {
            "entrees":  [article_to_dict(a) for a in self.entrees],
            "plats":    [article_to_dict(a) for a in self.plats],
            "desserts": [article_to_dict(a) for a in self.desserts],
            "boissons": [article_to_dict(a) for a in self.boissons],
            "menus":    [m.to_dict() for m in self.menus],
        }
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)

    def from_json(self, chemin: str) -> None:
        """
        Charge la carte depuis un fichier JSON.
        Remplace intégralement le contenu actuel de la carte.

        Args:
            chemin (str): Chemin du fichier source.

        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
        """
        from models.ingredient import Ingredient

        with open(chemin, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        # Réinitialise la carte
        self.entrees.clear()
        self.plats.clear()
        self.desserts.clear()
        self.boissons.clear()
        self.menus.clear()

        def charger_ingredients(data: list) -> list:
            return [
                Ingredient(
                    nom=i["nom"],
                    quantite=i["quantite"],
                    unite=i["unite"],
                    allergene=i["allergene"]
                )
                for i in data
            ]

        for d in donnees.get("entrees", []):
            self.entrees.append(Entree(
                id_article=d["id_article"], nom=d["nom"],
                description=d["description"], prix=d["prix"],
                temps_preparation=d["temps_preparation"],
                ingredients=charger_ingredients(d["ingredients"]),
                servie_chaude=d.get("servie_chaude", False),
                disponible=d["disponible"]
            ))

        for d in donnees.get("plats", []):
            self.plats.append(PlatPrincipal(
                id_article=d["id_article"], nom=d["nom"],
                description=d["description"], prix=d["prix"],
                temps_preparation=d["temps_preparation"],
                ingredients=charger_ingredients(d["ingredients"]),
                accompagnement=d.get("accompagnement", ""),
                disponible=d["disponible"]
            ))

        for d in donnees.get("desserts", []):
            self.desserts.append(Dessert(
                id_article=d["id_article"], nom=d["nom"],
                description=d["description"], prix=d["prix"],
                temps_preparation=d["temps_preparation"],
                ingredients=charger_ingredients(d["ingredients"]),
                fait_maison=d.get("fait_maison", True),
                disponible=d["disponible"]
            ))

        for d in donnees.get("boissons", []):
            self.boissons.append(Boisson(
                id_article=d["id_article"], nom=d["nom"],
                description=d["description"], prix=d["prix"],
                volume_cl=d["volume_cl"],
                est_alcoolisee=d.get("est_alcoolisee", False),
                temperature_service=d.get("temperature_service", "fraîche"),
                disponible=d["disponible"]
            ))

        # Reconstruction des menus à partir des ids
        for d in donnees.get("menus", []):
            plat = self.rechercher_par_id(d["id_plat"])
            if plat is None or not isinstance(plat, PlatPrincipal):
                continue

            entree = self.rechercher_par_id(d["id_entree"]) \
                if d.get("id_entree") else None
            dessert = self.rechercher_par_id(d["id_dessert"]) \
                if d.get("id_dessert") else None
            boisson = self.rechercher_par_id(d["id_boisson"]) \
                if d.get("id_boisson") else None

            self.menus.append(Menu(
                id_menu=d["id_menu"], nom=d["nom"], prix=d["prix"],
                plat=plat,
                entree=entree if isinstance(entree, Entree) else None,
                dessert=dessert if isinstance(dessert, Dessert) else None,
                boisson=boisson if isinstance(boisson, Boisson) else None,
                disponible=d["disponible"]
            ))

    # -----------------------------------------------------------------------
    # Représentations
    # -----------------------------------------------------------------------

    def _get_liste_pour(self, article: ArticleCarte) -> list:
        """
        Retourne la liste interne correspondant au type de l'article.

        Args:
            article (ArticleCarte): L'article dont on cherche la liste.

        Returns:
            list: La liste correspondante (entrees, plats, desserts, boissons).

        Raises:
            TypeError: Si le type n'est pas reconnu.
        """
        if isinstance(article, Entree):
            return self.entrees
        if isinstance(article, PlatPrincipal):
            return self.plats
        if isinstance(article, Dessert):
            return self.desserts
        if isinstance(article, Boisson):
            return self.boissons
        raise TypeError(
            f"Type d'article non reconnu : {type(article).__name__}"
        )

    def __str__(self) -> str:
        lignes = [f"=== Carte du restaurant ==="]
        for titre, liste in [
            ("Entrées",  self.entrees),
            ("Plats",    self.plats),
            ("Desserts", self.desserts),
            ("Boissons", self.boissons),
        ]:
            if liste:
                lignes.append(f"\n-- {titre} --")
                lignes.extend(f"  {a}" for a in liste)
        if self.menus:
            lignes.append("\n-- Menus --")
            lignes.extend(f"  {m}" for m in self.menus)
        return "\n".join(lignes)

    def __repr__(self) -> str:
        return (
            f"Carte({len(self.entrees)} entrées, "
            f"{len(self.plats)} plats, "
            f"{len(self.desserts)} desserts, "
            f"{len(self.boissons)} boissons, "
            f"{len(self.menus)} menus)"
        )
