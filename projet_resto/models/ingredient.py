"""
Module ingredient.py
Définit la classe Ingredient utilisée pour composer les articles de la carte.

Auteur : [Votre nom]
"""


class Ingredient:
    """
    Représente un ingrédient utilisé dans la préparation d'un article de la carte.

    Attributs:
        nom (str)               : Nom de l'ingrédient (ex: "farine", "tomate").
        quantite (float)        : Quantité nécessaire pour UNE portion.
        unite (str)             : Unité de mesure (ex: "g", "cl", "unité").
        allergene (bool)        : True si l'ingrédient est un allergène majeur.
    """

    def __init__(self, nom: str, quantite: float, unite: str, allergene: bool = False):
        """
        Initialise un ingrédient.

        Args:
            nom (str)               : Nom de l'ingrédient.
            quantite (float)        : Quantité nécessaire pour une portion.
            unite (str)             : Unité de mesure.
            allergene (bool)        : Indique si c'est un allergène (défaut: False).

        Raises:
            ValueError: Si la quantité est négative ou nulle.
        """
        if quantite <= 0:
            raise ValueError(f"La quantité de '{nom}' doit être positive (reçu: {quantite}).")
        self.nom = nom
        self.quantite = quantite
        self.unite = unite
        self.allergene = allergene

    def __repr__(self) -> str:
        """Retourne une représentation lisible de l'ingrédient."""
        alg = " [ALLERGÈNE]" if self.allergene else ""
        return f"{self.nom} ({self.quantite} {self.unite}){alg}"

    def __eq__(self, other) -> bool:
        """Deux ingrédients sont égaux s'ils ont le même nom (insensible à la casse)."""
        if not isinstance(other, Ingredient):
            return False
        return self.nom.lower() == other.nom.lower()
