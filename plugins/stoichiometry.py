from Core.src import Parser, LinearEquationsSystem
from Core.utils import ChemicalEquationRewriter, Assets

from prettytable import PrettyTable


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


class UI:
    def __init__(self):
        pass

    def create_table(
        self, field_names: list, rows: list, divider="-----"
    ) -> PrettyTable:
        """
        Creates a PrettyTable with the specified field names and rows, adding dividers between rows.

        Args:
            field_names (list): The names of the columns.
            rows (list): The rows of data to be added to the table.
            divider (str): The divider string to be added between rows. Default is "-----".

        Returns:
            PrettyTable: The created PrettyTable object.
        """
        table = PrettyTable()

        # Set the table field names
        table.field_names = field_names

        # Add rows to the table with dividers
        for row_index, row in enumerate(rows):
            if len(row) != len(table.field_names):
                raise ValueError(
                    f"Row has incorrect number of values, (actual) {len(row)} != {len(table.field_names)} (expected)"
                )
            table.add_row(row=row)
            if row_index < len(rows) - 1:  # Ensure the last row doesn't add a divider
                table.add_row([divider] * len(table.field_names))

        table.align = "c"  # Center-align all columns

        return table

    def display_reaction_table(self):
        chemical_formulas = (
            ["Chemical Formula"]
            + GlobalVariables.reactants_list
            + ["="]
            + GlobalVariables.products_list
        )

        molar_weights = (
            ["Molar weight"]
            + GlobalVariables.reactants_molar_weights_list
            + ["***"]
            + GlobalVariables.products_molar_weights_list
        )

        ui = UI()
        table = ui.create_table(field_names=chemical_formulas, rows=[molar_weights])

        print(table)

    def specie_selection(self):
        """
        Prompt the user to select a species for stoichiometric calculations.

        This method prompts the user to enter a selection, confirming their choice.
        If the user confirms the selection, it proceeds to calculate the stoichiometric ratio.
        If the user does not confirm, they can re-enter their selection.

        Global Variables:
            GlobalVariables.selected_specie (str): Stores the selected species.

        Returns:
            None
        """
        GlobalVariables.selected_specie = input("Enter your selection: ")
        print(f'Selected "{GlobalVariables.selected_specie}"')
        if (
            input(
                "Continue? [Y/n] \nHint: if no, you can edit your selection.\n > "
            ).lower()
            == "y"
        ):
            self.stoichiometry_calculator.calc_ratio()
        else:
            self.specie_selection()

    def mode_selection(self):
        """
        Prompt the user to select the mode for entering the starter quantity.

        This method displays a menu for the user to choose whether to enter the starter
        quantity as moles or grams. The user's choice is stored in the GlobalVariables.mode.

        Global Variables:
            GlobalVariables.mode (str): Stores the selected mode (mole or gram).

        Returns:
            None
        """
        print("Select one of the following options:")
        print(
            "Hint: Choose how you would like to enter the starter - as moles or grams."
        )
        print("[1] - Mole")
        print("[2] - Gram")
        GlobalVariables.mode = input("> ")

    def get_species_value(self):
        """
        Calculate and display the moles and grams of each species based on the user's input.

        This method prompts the user to enter either a mole or gram value based on the selected mode.
        It then calculates the moles and grams of each species and stores the values in GlobalVariables.

        Global Variables:
            GlobalVariables.mode (str): Indicates the mode of input (1 for mole, 2 for gram).
            GlobalVariables.selected_species (str): The index of the selected species.
            GlobalVariables.ratios (list): The stoichiometric ratios of the species.

        Returns:
            None
        """
        total_molar_weights = (
            GlobalVariables.reactants_molar_weights_list
            + GlobalVariables.products_molar_weights_list
        )

        species_moles = []
        species_grams = []

        if GlobalVariables.mode == "1":
            input_mole_value = float(input("Enter mole value: "))
            for index, ratio in enumerate(GlobalVariables.ratios):
                calculated_moles = round(ratio * input_mole_value, 3)
                calculated_grams = ratio * input_mole_value * total_molar_weights[index]
                species_moles.append(calculated_moles)
                species_grams.append(calculated_grams)

        elif GlobalVariables.mode == "2":
            input_gram_value = float(input("Enter gram value: "))
            selected_chemical = GlobalVariables.total_species_chemical_formulas[
                int(GlobalVariables.selected_specie)
            ]
            input_mole_value = input_gram_value / Stoichiometry.calc_molar_weight(
                chemical_formula=selected_chemical
            )
            for index, ratio in enumerate(GlobalVariables.ratios):
                calculated_moles = round(ratio * input_mole_value, 3)
                calculated_grams = ratio * input_mole_value * total_molar_weights[index]
                species_moles.append(calculated_moles)
                species_grams.append(calculated_grams)

        # Storing the calculated values in global variables
        GlobalVariables.moles_list = species_moles
        GlobalVariables.grams_list = species_grams


# UI().display_reaction_table()
