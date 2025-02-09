from Core.src import Parser, LinearEquationsSystem
from Core.utils import ChemicalEquationRewriter, Assets


class GlobalVariables:

    mode: str = ""
    """options: gram, mole"""
    selected_specie: str = ""
    """Selected specie as calculation starter"""

    reactants_list: list[str] = []
    products_list: list[str] = []

    total_species_chemical_formulas: list[str] = []
    """Stores reactants and products chemical formulas.\n
    Note: This variable allocates value when Stoichiometry initialized"""

    reactants_molar_weights_list: list[float] = []
    products_molar_weights_list: list[float] = []

    total_chemicals_molar_weights: list[float] = []
    """Stores reactants and products molar weights.\n
    Note: This variable allocates value when Stoichiometry initialized"""

    equation_solution: list[int | float] = []
    """Stores the equation solution"""

    ratios: list[int] = []
    """Stores the stoichiometric ratios with respect to selected_specie"""
    moles_list: list[float] = []
    """Stores calculated moles"""
    grams_list: list[float] = []
    """Stores calculated grams"""

class Stoichiometry:
    pass


class UI:
    pass
