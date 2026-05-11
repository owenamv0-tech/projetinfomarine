"""
Module article_carte.py
Définit la hiérarchie de classes pour les articles de la carte du restaurant.

Hiérarchie :
    ArticleCarte (ABC)
        ├── Entree
        ├── PlatPrincipal
        ├── Dessert
        └── Boisson

Auteur : [Votre nom]
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from models.ingredient import Ingredient


# ---------------------------------------------------------------------------
# Classe abstraite de base
# ---------------------------------------------------------------------------

class ArticleCarte(ABC):
    """
    Classe abstraite représentant un article de la carte du restaurant.

    Tout article possède un identifiant, un nom, un prix et un statut
    de disponibilité. Les sous-classes doivent implémenter les méthodes
    abstraites qui dépendent du type d'article.

    Attributs:
        id_article (int)        : Identifiant unique de l'article.
        nom (str)               : Nom affiché sur la carte.
        description (str)       : Description courte du plat.
        prix (float)            : Prix en euros (HT).
        disponible (bool)       : True si l'article est proposé aujourd'hui.
    """

    def __init__(self, id_article: int, nom: str, description: str, prix: float,
                 disponible: bool = True):
        """
        Initialise un article de la carte.

        Args:
            id_article (int)    : Identifiant unique.
            nom (str)           : Nom de l'article.
            description (str)   : Description courte.
            prix (float)        : Prix en euros.
            disponible (bool)   : Disponibilité (défaut: True).

        Raises:
            ValueError: Si le prix est négatif.
        """
        if prix < 0:
            raise ValueError(f"Le prix de '{nom}' ne peut pas être négatif.")
        self.id_article = id_article
        self.nom = nom
        self.description = description
        self.prix = prix
        self.disponible = disponible

    # --- Méthodes abstraites (obligatoires dans chaque sous-classe) ----------

    @abstractmethod
    def get_type(self) -> str:
        """
        Retourne la catégorie de l'article ('Entrée', 'Plat', 'Dessert', 'Boisson').

        Returns:
            str: Le type de l'article.
        """

    @abstractmethod
    def get_temps_preparation(self) -> int:
        """
        Retourne le temps de préparation estimé en minutes.

        Returns:
            int: Temps de préparation en minutes.
        """

    @abstractmethod
    def get_ingredients(self) -> List[Ingredient]:
        """
        Retourne la liste des ingrédients nécessaires pour une portion.

        Returns:
            List[Ingredient]: Liste des ingrédients.
        """

    @abstractmethod
    def get_details(self) -> str:
        """
        Retourne une description détaillée et formatée de l'article,
        incluant les informations spécifiques à son type.

        Returns:
            str: Détails complets de l'article.
        """

    # --- Méthodes concrètes (communes à tous les articles) ------------------

    def est_disponible(self) -> bool:
        """
        Indique si l'article est actuellement disponible à la commande.

        Returns:
            bool: True si disponible, False sinon.
        """
        return self.disponible

    def activer(self) -> None:
        """Rend l'article disponible sur la carte."""
        self.disponible = True

    def desactiver(self) -> None:
        """Retire l'article de la carte (indisponible)."""
        self.disponible = False

    def appliquer_reduction(self, taux: float) -> float:
        """
        Calcule le prix après application d'une réduction.

        Args:
            taux (float): Taux de réduction en pourcentage (ex: 10 pour 10%).

        Returns:
            float: Prix réduit arrondi à 2 décimales.

        Raises:
            ValueError: Si le taux est hors de l'intervalle [0, 100].
        """
        if not (0 <= taux <= 100):
            raise ValueError(f"Le taux de réduction doit être entre 0 et 100 (reçu: {taux}).")
        return round(self.prix * (1 - taux / 100), 2)

    def get_allergenes(self) -> List[str]:
        """
        Retourne la liste des noms d'ingrédients allergènes présents dans l'article.

        Returns:
            List[str]: Noms des ingrédients allergènes.
        """
        return [ing.nom for ing in self.get_ingredients() if ing.allergene]

    def __str__(self) -> str:
        dispo = "✓" if self.disponible else "✗"
        return f"[{dispo}] {self.get_type():12s} | {self.nom:25s} | {self.prix:.2f}€"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id_article}, nom='{self.nom}', prix={self.prix})"


# ---------------------------------------------------------------------------
# Sous-classe : Entrée
# ---------------------------------------------------------------------------

class Entree(ArticleCarte):
    """
    Représente une entrée de la carte.

    En plus des attributs de base, une entrée possède un temps de préparation,
    une liste d'ingrédients et une indication sur le service (chaude ou froide).

    Attributs supplémentaires:
        temps_preparation (int)     : Temps de préparation en minutes.
        ingredients (List[Ingredient]): Ingrédients nécessaires.
        servie_chaude (bool)        : True si l'entrée est servie chaude.
    """

    def __init__(self, id_article: int, nom: str, description: str, prix: float,
                 temps_preparation: int, ingredients: List[Ingredient],
                 servie_chaude: bool = False, disponible: bool = True):
        """
        Initialise une entrée.

        Args:
            id_article (int)            : Identifiant unique.
            nom (str)                   : Nom de l'entrée.
            description (str)           : Description courte.
            prix (float)                : Prix en euros.
            temps_preparation (int)     : Temps de préparation en minutes.
            ingredients (List[Ingredient]): Liste des ingrédients.
            servie_chaude (bool)        : Entrée chaude ou froide (défaut: False).
            disponible (bool)           : Disponibilité (défaut: True).

        Raises:
            ValueError: Si temps_preparation est négatif.
        """
        super().__init__(id_article, nom, description, prix, disponible)
        if temps_preparation < 0:
            raise ValueError("Le temps de préparation ne peut pas être négatif.")
        self._temps_preparation = temps_preparation
        self._ingredients = ingredients
        self.servie_chaude = servie_chaude

    def get_type(self) -> str:
        return "Entrée"

    def get_temps_preparation(self) -> int:
        return self._temps_preparation

    def get_ingredients(self) -> List[Ingredient]:
        return self._ingredients

    def get_details(self) -> str:
        """Retourne les détails complets de l'entrée."""
        temperature = "🔥 Chaude" if self.servie_chaude else "❄️  Froide"
        ingredients_str = ", ".join(str(i) for i in self._ingredients) or "Non renseigné"
        allergenes = self.get_allergenes()
        allergenes_str = ", ".join(allergenes) if allergenes else "Aucun"
        return (
            f"--- Entrée : {self.nom} ---\n"
            f"  Description  : {self.description}\n"
            f"  Prix         : {self.prix:.2f}€\n"
            f"  Service      : {temperature}\n"
            f"  Préparation  : {self._temps_preparation} min\n"
            f"  Ingrédients  : {ingredients_str}\n"
            f"  Allergènes   : {allergenes_str}\n"
            f"  Disponible   : {'Oui' if self.disponible else 'Non'}"
        )


# ---------------------------------------------------------------------------
# Sous-classe : Plat Principal
# ---------------------------------------------------------------------------

class PlatPrincipal(ArticleCarte):
    """
    Représente un plat principal de la carte.

    Un plat principal possède un temps de préparation, une liste d'ingrédients
    et un accompagnement proposé.

    Attributs supplémentaires:
        temps_preparation (int)     : Temps de préparation en minutes.
        ingredients (List[Ingredient]): Ingrédients nécessaires.
        accompagnement (str)        : Accompagnement proposé avec le plat.
    """

    def __init__(self, id_article: int, nom: str, description: str, prix: float,
                 temps_preparation: int, ingredients: List[Ingredient],
                 accompagnement: str = "Sans accompagnement", disponible: bool = True):
        """
        Initialise un plat principal.

        Args:
            id_article (int)            : Identifiant unique.
            nom (str)                   : Nom du plat.
            description (str)           : Description courte.
            prix (float)                : Prix en euros.
            temps_preparation (int)     : Temps de préparation en minutes.
            ingredients (List[Ingredient]): Liste des ingrédients.
            accompagnement (str)        : Accompagnement (défaut: "Sans accompagnement").
            disponible (bool)           : Disponibilité (défaut: True).
        """
        super().__init__(id_article, nom, description, prix, disponible)
        if temps_preparation < 0:
            raise ValueError("Le temps de préparation ne peut pas être négatif.")
        self._temps_preparation = temps_preparation
        self._ingredients = ingredients
        self.accompagnement = accompagnement

    def get_type(self) -> str:
        return "Plat"

    def get_temps_preparation(self) -> int:
        return self._temps_preparation

    def get_ingredients(self) -> List[Ingredient]:
        return self._ingredients

    def get_details(self) -> str:
        """Retourne les détails complets du plat principal."""
        ingredients_str = ", ".join(str(i) for i in self._ingredients) or "Non renseigné"
        allergenes = self.get_allergenes()
        allergenes_str = ", ".join(allergenes) if allergenes else "Aucun"
        return (
            f"--- Plat : {self.nom} ---\n"
            f"  Description    : {self.description}\n"
            f"  Prix           : {self.prix:.2f}€\n"
            f"  Accompagnement : {self.accompagnement}\n"
            f"  Préparation    : {self._temps_preparation} min\n"
            f"  Ingrédients    : {ingredients_str}\n"
            f"  Allergènes     : {allergenes_str}\n"
            f"  Disponible     : {'Oui' if self.disponible else 'Non'}"
        )


# ---------------------------------------------------------------------------
# Sous-classe : Dessert
# ---------------------------------------------------------------------------

class Dessert(ArticleCarte):
    """
    Représente un dessert de la carte.

    Un dessert possède un temps de préparation, une liste d'ingrédients
    et une indication sur sa fabrication (maison ou non).

    Attributs supplémentaires:
        temps_preparation (int)     : Temps de préparation en minutes.
        ingredients (List[Ingredient]): Ingrédients nécessaires.
        fait_maison (bool)          : True si le dessert est fait maison.
    """

    def __init__(self, id_article: int, nom: str, description: str, prix: float,
                 temps_preparation: int, ingredients: List[Ingredient],
                 fait_maison: bool = True, disponible: bool = True):
        """
        Initialise un dessert.

        Args:
            id_article (int)            : Identifiant unique.
            nom (str)                   : Nom du dessert.
            description (str)           : Description courte.
            prix (float)                : Prix en euros.
            temps_preparation (int)     : Temps de préparation en minutes.
            ingredients (List[Ingredient]): Liste des ingrédients.
            fait_maison (bool)          : Fait maison ou non (défaut: True).
            disponible (bool)           : Disponibilité (défaut: True).
        """
        super().__init__(id_article, nom, description, prix, disponible)
        if temps_preparation < 0:
            raise ValueError("Le temps de préparation ne peut pas être négatif.")
        self._temps_preparation = temps_preparation
        self._ingredients = ingredients
        self.fait_maison = fait_maison

    def get_type(self) -> str:
        return "Dessert"

    def get_temps_preparation(self) -> int:
        return self._temps_preparation

    def get_ingredients(self) -> List[Ingredient]:
        return self._ingredients

    def get_details(self) -> str:
        """Retourne les détails complets du dessert."""
        ingredients_str = ", ".join(str(i) for i in self._ingredients) or "Non renseigné"
        allergenes = self.get_allergenes()
        allergenes_str = ", ".join(allergenes) if allergenes else "Aucun"
        label_fm = "🏠 Fait maison" if self.fait_maison else "Industriel"
        return (
            f"--- Dessert : {self.nom} ---\n"
            f"  Description  : {self.description}\n"
            f"  Prix         : {self.prix:.2f}€\n"
            f"  Fabrication  : {label_fm}\n"
            f"  Préparation  : {self._temps_preparation} min\n"
            f"  Ingrédients  : {ingredients_str}\n"
            f"  Allergènes   : {allergenes_str}\n"
            f"  Disponible   : {'Oui' if self.disponible else 'Non'}"
        )


# ---------------------------------------------------------------------------
# Sous-classe : Boisson
# ---------------------------------------------------------------------------

class Boisson(ArticleCarte):
    """
    Représente une boisson de la carte.

    Une boisson se distingue des autres articles : elle n'a pas de temps de
    préparation significatif ni d'ingrédients au sens culinaire. Elle possède
    un volume et une indication sur sa teneur en alcool.

    Attributs supplémentaires:
        volume_cl (float)       : Volume en centilitres.
        est_alcoolisee (bool)   : True si la boisson contient de l'alcool.
        temperature_service (str): 'fraîche', 'ambiante' ou 'chaude'.
    """

    TEMPERATURES_VALIDES = ("fraîche", "ambiante", "chaude")

    def __init__(self, id_article: int, nom: str, description: str, prix: float,
                 volume_cl: float, est_alcoolisee: bool = False,
                 temperature_service: str = "fraîche", disponible: bool = True):
        """
        Initialise une boisson.

        Args:
            id_article (int)            : Identifiant unique.
            nom (str)                   : Nom de la boisson.
            description (str)           : Description courte.
            prix (float)                : Prix en euros.
            volume_cl (float)           : Volume en centilitres.
            est_alcoolisee (bool)       : Alcoolisée ou non (défaut: False).
            temperature_service (str)   : Température de service (défaut: 'fraîche').
            disponible (bool)           : Disponibilité (défaut: True).

        Raises:
            ValueError: Si le volume est négatif ou la température invalide.
        """
        super().__init__(id_article, nom, description, prix, disponible)
        if volume_cl <= 0:
            raise ValueError("Le volume d'une boisson doit être positif.")
        if temperature_service not in self.TEMPERATURES_VALIDES:
            raise ValueError(
                f"Température invalide '{temperature_service}'. "
                f"Valeurs acceptées : {self.TEMPERATURES_VALIDES}"
            )
        self.volume_cl = volume_cl
        self.est_alcoolisee = est_alcoolisee
        self.temperature_service = temperature_service

    def get_type(self) -> str:
        return "Boisson"

    def get_temps_preparation(self) -> int:
        """Les boissons n'ont pas de temps de préparation (service immédiat)."""
        return 0

    def get_ingredients(self) -> List[Ingredient]:
        """Les boissons n'ont pas de liste d'ingrédients."""
        return []

    def get_details(self) -> str:
        """Retourne les détails complets de la boisson."""
        alcool = "🍷 Alcoolisée" if self.est_alcoolisee else "Sans alcool"
        return (
            f"--- Boisson : {self.nom} ---\n"
            f"  Description  : {self.description}\n"
            f"  Prix         : {self.prix:.2f}€\n"
            f"  Volume       : {self.volume_cl} cl\n"
            f"  Type         : {alcool}\n"
            f"  Service      : {self.temperature_service}\n"
            f"  Disponible   : {'Oui' if self.disponible else 'Non'}"
        )
