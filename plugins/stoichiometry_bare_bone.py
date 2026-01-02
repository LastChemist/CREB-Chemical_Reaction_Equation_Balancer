"""
This python file is BARE BONE VERSION of file Core/plugins/stoichiometry.py .
This file can be used for general purposes and fast prototyping.
The previous file contains pre-made menu and table for balancing and stoichiometry calculations.
"""

from Core.src import Parser, LinearEquationsSystem
from Core.utils import Assets


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

    reactants_mole_list: list[float] = []
    products_mole_list: list[float] = []

    total_chemicals_moles: list[float] = []
    """Stores reactants and products calculated mole values\n
    Note: This variable allocates value when calculate_values called"""

    reactants_gram_list: list[float] = []
    products_gram_list: list[float] = []

    total_chemicals_grams: list[float] = []
    """Stores reactants and products calculated gram values\n
    Note: This variable allocates value when calculate_values called"""

    reactants_weights_list: list[float] = []
    products_weights_list: list[float] = []
    """Calculated weights"""

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

    def balance_equation(self):
        """Balances the chemical equation."""
        generator: object = LinearEquationsSystem.Generator(
            chemical_equation=self.chemical_equation
        )
        generator.solveEquations()
        equation_solution: tuple = generator.equation_solution

        # Convert the equation solution from a tuple to a list of coefficients
        coefficients_list: list[int] = []

        for coefficient in equation_solution:
            coefficients_list.append(coefficient)

        GlobalVariables.equation_solution = coefficients_list

    def calc_molar_weight(self, chemical_formula: str) -> float:
        """
        Calculates the molar weight of the given chemical formula.

        The molar weight is calculated using atomic masses from Assets.py.

        Args:
            chemical_formula (str): The chemical formula for which to calculate the molar weight.

        Returns:
            float: The molar weight rounded to 3 decimal places.
        """
        molar_weight: float = 0

        # Get the count of each element in the chemical formula
        elements_count_dict: dict[str, int] = dict(
            Parser.ElementCounter(chemical_formula=chemical_formula).parseFormula()
        )

        # Calculate the molar weight
        for element in elements_count_dict.keys():
            molar_weight += (
                elements_count_dict[element] * Assets.periodic_table[element]
            )

        return round(molar_weight, 3)

    def calc_ratio(self) -> None:
        """
        Calculates the stoichiometric ratios for the chemical equation.

        The ratios are calculated based on the coefficients of the balanced equation
        and the selected species. The result is stored in the GlobalVariables.ratios list.

        Returns:
            None
        """
        ratios = []
        for coefficient in GlobalVariables.equation_solution:
            ratios.append(
                coefficient
                / GlobalVariables.equation_solution[
                    int(GlobalVariables.selected_specie)
                ]
            )
        GlobalVariables.ratios = ratios

    def calc_species_molar_weight(self) -> None:
        """
        Calculates and stores the molar weights of the reactants and products.

        This method first balances the chemical equation. Then it calculates the molar weights
        of each chemical formula in the reactants and products lists. The results are stored
        in GlobalVariables.reactants_molar_weights_list and GlobalVariables.products_molar_weights_list.

        Returns:
            None
        """
        # Balance the chemical equation
        self.balance_equation()

        # Calculate and store the molar weights of reactants
        [
            GlobalVariables.reactants_molar_weights_list.append(
                self.calc_molar_weight(chemical_formula=chemical_formula)
            )
            for chemical_formula in GlobalVariables.reactants_list
        ]

        # Calculate and store the molar weights of products
        [
            GlobalVariables.products_molar_weights_list.append(
                self.calc_molar_weight(chemical_formula=chemical_formula)
            )
            for chemical_formula in GlobalVariables.products_list
        ]

    def calc_moles_grams(self):
        """
        Calculate and store the moles and grams of reactants and products.

        This method iterates over the reactants and products, calculating their weights, moles, and grams
        based on the stoichiometric ratios and molar weights. The results are stored in the corresponding
        global variables.

        For reactants:
            - Calculates the weight using the molar weight and stoichiometric ratio.
            - Retrieves and rounds the mole value.
            - Retrieves and rounds the gram value.

        For products:
            - Calculates the weight using the molar weight and stoichiometric ratio.
            - Retrieves and rounds the mole value.
            - Retrieves and rounds the gram value.

        Global Variables:
            GlobalVariables.reactants_list (list): List of reactants' chemical formulas.
            GlobalVariables.products_list (list): List of products' chemical formulas.
            GlobalVariables.ratios (list): Stoichiometric ratios of the species.
            GlobalVariables.reactants_weights_list (list): Weights of reactants.
            GlobalVariables.reactants_mole_list (list): Moles of reactants.
            GlobalVariables.reactants_gram_list (list): Grams of reactants.
            GlobalVariables.products_weights_list (list): Weights of products.
            GlobalVariables.products_mole_list (list): Moles of products.
            GlobalVariables.products_gram_list (list): Grams of products.
            GlobalVariables.moles_list (list): Calculated moles.
            GlobalVariables.grams_list (list): Calculated grams.

        Returns:
            None
        """

        for reactant in GlobalVariables.reactants_list:
            GlobalVariables.reactants_weights_list.append(
                round(
                    self.calc_molar_weight(chemical_formula=reactant)
                    * GlobalVariables.ratios[
                        GlobalVariables.reactants_list.index(reactant)
                    ],
                    3,
                )
            )

            GlobalVariables.reactants_mole_list.append(
                round(
                    GlobalVariables.moles_list[
                        GlobalVariables.reactants_list.index(reactant)
                    ],
                    3,
                )
            )

            GlobalVariables.reactants_gram_list.append(
                round(
                    GlobalVariables.grams_list[
                        GlobalVariables.reactants_list.index(reactant)
                    ],
                    3,
                )
            )

        for product in GlobalVariables.products_list:
            GlobalVariables.products_weights_list.append(
                round(
                    self.calc_molar_weight(chemical_formula=product)
                    * GlobalVariables.ratios[
                        GlobalVariables.products_list.index(product)
                    ],
                    3,
                )
            )

            GlobalVariables.products_mole_list.append(
                round(
                    GlobalVariables.moles_list[
                        len(GlobalVariables.reactants_list)
                        + GlobalVariables.products_list.index(product)
                    ],
                    3,
                )
            )

            GlobalVariables.products_gram_list.append(
                round(
                    GlobalVariables.grams_list[
                        len(GlobalVariables.reactants_list)
                        + GlobalVariables.products_list.index(product)
                    ],
                    3,
                )
            )

    def run(self):
        self.balance_equation()
        self.calc_species_molar_weight()
        self.calc_ratio()
        self.calc_moles_grams()
