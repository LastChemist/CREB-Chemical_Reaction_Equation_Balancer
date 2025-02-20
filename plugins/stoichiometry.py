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

    def balance_equation(self):
        """Balances the chemical equation."""

        # Generate and solve the system of linear equations representing the chemical equation
        linear_equations_system_object: object = (
            LinearEquationsSystem.Generator.FileMaker(
                chemical_equation=self.chemical_equation
            )
        )
        linear_equations_system_object.generateEquationAndSaveSolverFile()
        linear_equations_system_object.executeSolverFile()

        # Retrieve the solution to the chemical equation as a tuple
        rewriter_object: object = ChemicalEquationRewriter.Rewriter()
        rewriter_object.loadEquationSolutionInformation()
        equation_solution: tuple = rewriter_object.equation_solution

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


class UI:
    pass
