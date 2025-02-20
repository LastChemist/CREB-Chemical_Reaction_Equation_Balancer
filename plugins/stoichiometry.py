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
    def __init__(self, chemical_equation: str = ""):
        self.chemical_equation: str = chemical_equation

        self.equation_parser_object: object = Parser.EquationParser(
            chemical_equation=self.chemical_equation
        )
        self.equation_parser_object.parse()

        GlobalVariables.reactants_list = self.equation_parser_object.reactants_list
        GlobalVariables.products_list = self.equation_parser_object.products_list

        [
            GlobalVariables.total_species_chemical_formulas.append(chemical_formula)
            for chemical_formula in GlobalVariables.reactants_list
        ]
        [
            GlobalVariables.total_species_chemical_formulas.append(chemical_formula)
            for chemical_formula in GlobalVariables.products_list
        ]

        self.specie_molar_weight: dict[str, float] = {}


class UI:
    pass
