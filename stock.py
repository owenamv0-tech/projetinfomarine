"""
Module stock.py
Définit les classes StockIngredient et Stock pour la gestion
des ingrédients disponibles en cuisine.

Contient également l'algorithme d'optimisation suggerer_menus_realisables()
qui identifie les menus faisables en minimisant le gaspillage.

Auteur : Marine
"""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Dict, List, Tuple
from models.ingredient import Ingredient

if TYPE_CHECKING:
    from models.article_carte import ArticleCarte
    from models.menu import Menu


# ---------------------------------------------------------------------------
# StockIngredient
# ---------------------------------------------------------------------------

class StockIngredient:
    """
    Représente la quantité disponible d'un ingrédient en cuisine.

    Fait le lien entre un Ingredient (description) et sa réalité
    physique en stock (quantité disponible, seuil d'alerte).

    Attributs:
        ingredient (Ingredient)         : L'ingrédient concerné.
        quantite_disponible (float)     : Quantité actuellement en stock.
        seuil_alerte (float)            : Seuil en dessous duquel une alerte
                                          est déclenchée.
    """

    def __init__(self, ingredient: Ingredient, quantite_disponible: float,
                 seuil_alerte: float = 0.0) -> None:
        """
        Initialise un stock pour un ingrédient.

        Args:
            ingredient (Ingredient)         : L'ingrédient.
            quantite_disponible (float)     : Quantité initiale en stock.
            seuil_alerte (float)            : Seuil d'alerte (défaut: 0).

        Raises:
            ValueError: Si quantite_disponible ou seuil_alerte est négatif.
        """
        if quantite_disponible < 0:
            raise ValueError(
                f"La quantité disponible ne peut pas être négative "
                f"(reçu : {quantite_disponible})."
            )
        if seuil_alerte < 0:
            raise ValueError(
                f"Le seuil d'alerte ne peut pas être négatif "
                f"(reçu : {seuil_alerte})."
            )
        self.ingredient = ingredient
        self.quantite_disponible = quantite_disponible
        self.seuil_alerte = seuil_alerte

    def est_en_alerte(self) -> bool:
        """
        Indique si le stock est en dessous du seuil d'alerte.

        Returns:
            bool: True si quantite_disponible <= seuil_alerte.
        """
        return self.quantite_disponible <= self.seuil_alerte

    def consommer(self, quantite: float) -> None:
        """
        Décrémente le stock d'une quantité donnée.

        Args:
            quantite (float): Quantité à consommer (doit être > 0).

        Raises:
            ValueError: Si quantite <= 0.
            ValueError: Si le stock est insuffisant.
        """
        if quantite <= 0:
            raise ValueError(
                f"La quantité à consommer doit être positive (reçu : {quantite})."
            )
        if quantite > self.quantite_disponible:
            raise ValueError(
                f"Stock insuffisant pour '{self.ingredient.nom}' : "
                f"demandé {quantite} {self.ingredient.unite}, "
                f"disponible {self.quantite_disponible} {self.ingredient.unite}."
            )
        self.quantite_disponible -= quantite
        self.quantite_disponible = round(self.quantite_disponible, 4)

    def reapprovisionner(self, quantite: float) -> None:
        """
        Augmente le stock d'une quantité donnée.

        Args:
            quantite (float): Quantité à ajouter (doit être > 0).

        Raises:
            ValueError: Si quantite <= 0.
        """
        if quantite <= 0:
            raise ValueError(
                f"La quantité à ajouter doit être positive (reçu : {quantite})."
            )
        self.quantite_disponible += quantite
        self.quantite_disponible = round(self.quantite_disponible, 4)

    def to_dict(self) -> dict:
        """Sérialise le stock d'un ingrédient en dictionnaire."""
        return {
            "nom": self.ingredient.nom,
            "quantite_disponible": self.quantite_disponible,
            "seuil_alerte": self.seuil_alerte,
            "unite": self.ingredient.unite,
            "allergene": self.ingredient.allergene,
        }

    def __str__(self) -> str:
        alerte = " ⚠️ ALERTE" if self.est_en_alerte() else ""
        return (f"{self.ingredient.nom} : "
                f"{self.quantite_disponible} {self.ingredient.unite}"
                f"{alerte}")

    def __repr__(self) -> str:
        return (f"StockIngredient(nom='{self.ingredient.nom}', "
                f"dispo={self.quantite_disponible}, "
                f"seuil={self.seuil_alerte})")


# ---------------------------------------------------------------------------
# Stock
# ---------------------------------------------------------------------------

class Stock:
    """
    Gère l'ensemble des ingrédients disponibles en cuisine.

    Permet de vérifier la faisabilité des plats, de consommer les
    ingrédients après préparation, et de détecter les pénuries.

    Attributs:
        stock_ingredients (Dict[str, StockIngredient]):
            Dictionnaire indexé par le nom de l'ingrédient (en minuscules).
    """

    def __init__(self) -> None:
        """Initialise un stock vide."""
        self.stock_ingredients: Dict[str, StockIngredient] = {}

    # --- Gestion du stock --------------------------------------------------

    def ajouter_ingredient(self, stock_ingredient: StockIngredient) -> None:
        """
        Enregistre un ingrédient dans le stock.

        Args:
            stock_ingredient (StockIngredient): L'ingrédient à enregistrer.

        Raises:
            ValueError: Si l'ingrédient est déjà présent dans le stock.
        """
        cle = stock_ingredient.ingredient.nom.lower()
        if cle in self.stock_ingredients:
            raise ValueError(
                f"L'ingrédient '{stock_ingredient.ingredient.nom}' "
                f"est déjà dans le stock."
            )
        self.stock_ingredients[cle] = stock_ingredient

    def get_ingredient(self, nom: str) -> StockIngredient:
        """
        Retourne le stock d'un ingrédient par son nom.

        Args:
            nom (str): Nom de l'ingrédient (insensible à la casse).

        Returns:
            StockIngredient: Le stock correspondant.

        Raises:
            KeyError: Si l'ingrédient n'est pas référencé dans le stock.
        """
        cle = nom.lower()
        if cle not in self.stock_ingredients:
            raise KeyError(
                f"Ingrédient '{nom}' introuvable dans le stock."
            )
        return self.stock_ingredients[cle]

    # --- Vérification et consommation --------------------------------------

    def peut_preparer(self, article: ArticleCarte) -> bool:
        """
        Vérifie si tous les ingrédients nécessaires à la préparation
        d'un article sont disponibles en quantité suffisante.

        Args:
            article (ArticleCarte): L'article à vérifier.

        Returns:
            bool: True si tous les ingrédients sont disponibles.
        """
        for ingredient in article.get_ingredients():
            cle = ingredient.nom.lower()
            if cle not in self.stock_ingredients:
                return False
            if self.stock_ingredients[cle].quantite_disponible < ingredient.quantite:
                return False
        return True

    def consommer_pour(self, article: ArticleCarte) -> None:
        """
        Décrémente le stock pour tous les ingrédients d'un article.
        Vérifie la disponibilité avant de consommer.

        Args:
            article (ArticleCarte): L'article préparé.

        Raises:
            ValueError: Si un ingrédient est manquant ou insuffisant.
        """
        if not self.peut_preparer(article):
            raise ValueError(
                f"Impossible de préparer '{article.nom}' : "
                f"stock insuffisant."
            )
        for ingredient in article.get_ingredients():
            self.stock_ingredients[ingredient.nom.lower()].consommer(
                ingredient.quantite
            )

    # --- Alertes -----------------------------------------------------------

    def get_alertes(self) -> List[StockIngredient]:
        """
        Retourne la liste des ingrédients en dessous de leur seuil d'alerte.

        Returns:
            List[StockIngredient]: Ingrédients en alerte, triés par nom.
        """
        return sorted(
            [s for s in self.stock_ingredients.values() if s.est_en_alerte()],
            key=lambda s: s.ingredient.nom
        )

    # --- Algorithme d'optimisation (Figure bonus n°3) ----------------------

    def suggerer_menus_realisables(
            self, menus: List[Menu]) -> List[Tuple[Menu, float]]:
        """
        Algorithme d'optimisation : identifie les menus réalisables
        avec le stock actuel et les trie pour minimiser le gaspillage.

        Le score de gaspillage d'un menu est calculé comme la somme,
        pour chaque ingrédient utilisé, du ratio :
            quantite_utilisee / quantite_disponible

        Un score proche de 1.0 signifie qu'on utilise une grande part
        du stock disponible → moins de gaspillage potentiel.

        Args:
            menus (List[Menu]): Liste des menus à évaluer.

        Returns:
            List[Tuple[Menu, float]]: Menus réalisables avec leur score,
                triés du score le plus élevé au plus faible (meilleure
                utilisation des stocks en premier).
        """
        realisables = []

        for menu in menus:
            articles = [a for a in [menu.entree, menu.plat,
                                    menu.dessert, menu.boisson]
                        if a is not None]

            if not all(self.peut_preparer(a) for a in articles):
                continue

            # Calcul du score d'utilisation du stock
            score = 0.0
            nb_ingredients = 0
            for article in articles:
                for ing in article.get_ingredients():
                    cle = ing.nom.lower()
                    if cle in self.stock_ingredients:
                        dispo = self.stock_ingredients[cle].quantite_disponible
                        if dispo > 0:
                            score += ing.quantite / dispo
                            nb_ingredients += 1

            score_moyen = round(score / nb_ingredients, 4) if nb_ingredients else 0.0
            realisables.append((menu, score_moyen))

        return sorted(realisables, key=lambda x: x[1], reverse=True)

    # --- Persistance -------------------------------------------------------

    def sauvegarder(self, chemin: str) -> None:
        """
        Sauvegarde l'état du stock dans un fichier JSON.

        Args:
            chemin (str): Chemin du fichier de destination.
        """
        données = {
            nom: si.to_dict()
            for nom, si in self.stock_ingredients.items()
        }
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(données, f, ensure_ascii=False, indent=2)

    def charger(self, chemin: str) -> None:
        """
        Charge l'état du stock depuis un fichier JSON.
        Remplace le contenu actuel du stock.

        Args:
            chemin (str): Chemin du fichier source.

        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
        """
        with open(chemin, "r", encoding="utf-8") as f:
            données = json.load(f)

        self.stock_ingredients.clear()
        for _, infos in données.items():
            ingredient = Ingredient(
                nom=infos["nom"],
                quantite=1.0,   # quantite de référence, non stockée dans JSON
                unite=infos["unite"],
                allergene=infos["allergene"]
            )
            si = StockIngredient(
                ingredient=ingredient,
                quantite_disponible=infos["quantite_disponible"],
                seuil_alerte=infos["seuil_alerte"]
            )
            self.stock_ingredients[infos["nom"].lower()] = si

    def __str__(self) -> str:
        if not self.stock_ingredients:
            return "Stock vide."
        lignes = [str(si) for si in self.stock_ingredients.values()]
        return "Stock :\n  " + "\n  ".join(lignes)

    def __repr__(self) -> str:
        return f"Stock({len(self.stock_ingredients)} ingrédients)"
