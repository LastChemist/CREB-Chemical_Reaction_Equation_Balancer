from Core.utils import Assets
from Core.src.Parser import ElementMapper, EquationParser
import sympy
from sympy import symbols, linsolve, Matrix, lcm, S, solve
import numpy as np

# region Generator


class Generator:
    """
    A class to generate and solve linear equations for balancing chemical equations.
    """

    def __init__(self, chemical_equation: str) -> None:
        """
        Constructs all the necessary attributes for the Generator object.

        Parameters:
            chemical_equation : str
                The chemical equation to be parsed.
        """
        self.chemical_equation: str = chemical_equation
        self.parameter_symbols: str = Assets.parameter_symbols

        # Parse the equation
        equation_parser_object = EquationParser(chemical_equation=chemical_equation)
        equation_parser_object.parse()

        self.reactants_list: list[str] = equation_parser_object.reactants_list
        self.products_list: list[str] = equation_parser_object.products_list
        self.parsed_reactants: dict[str, dict[str, str]] = (
            equation_parser_object.parsed_reactants
        )
        self.parsed_products: dict[str, dict[str, str]] = (
            equation_parser_object.parsed_products
        )

        self.present_elements_in_reaction: list[str] = []
        self.reactants_assigned_parameter_dict: dict[str, str] = {}
        self.products_assigned_parameter_dict: dict[str, str] = {}
        self.demand_for_variables_to_solve_count: int = 0

        # NEW: Store the solution as a class variable
        self.equation_solution = None
        self.balanced_coefficients = None
        self.solution_variables = None
        self.balanced_equation_str = None

    def presentElementsInChemicalFormula(self, chemical_formula: str) -> list:
        """Returns a list of elements present in the given chemical formula."""
        return list(ElementMapper(chemical_formula=chemical_formula).search())

    def presentElementsInReaction(self) -> list:
        """Identifies and returns a list of elements present in the reaction."""
        element_list: list[str] = []
        temp_list: list = []

        for reactant in self.reactants_list:
            temp_list.append(
                self.presentElementsInChemicalFormula(chemical_formula=reactant)
            )

        for product in self.products_list:
            temp_list.append(
                self.presentElementsInChemicalFormula(chemical_formula=product)
            )

        for sublist in temp_list:
            element_list.extend(sublist)

        element_list = list(set(element_list))
        self.present_elements_in_reaction = element_list

        # Number of variables = number of compounds
        self.demand_for_variables_to_solve_count = len(self.reactants_list) + len(
            self.products_list
        )
        return element_list

    def assignParameter(self) -> None:
        """Assigns parameters to reactants and products."""
        self.presentElementsInReaction()

        # Reset dictionaries
        self.reactants_assigned_parameter_dict = {}
        self.products_assigned_parameter_dict = {}

        # Use different symbols to avoid conflict with imaginary unit 'i'
        # Use lowercase letters, skipping 'i' which is the imaginary unit
        available_symbols = [sym for sym in self.parameter_symbols if sym != "i"]

        # Assign parameters to reactants
        for i, reactant in enumerate(self.reactants_list):
            if i < len(available_symbols):
                self.reactants_assigned_parameter_dict[reactant] = available_symbols[i]
            else:
                # If we run out of symbols, use something like x1, x2, etc.
                self.reactants_assigned_parameter_dict[reactant] = f"x{i}"

        # Assign parameters to products
        for i, product in enumerate(self.products_list):
            idx = len(self.reactants_list) + i
            if idx < len(available_symbols):
                self.products_assigned_parameter_dict[product] = available_symbols[idx]
            else:
                self.products_assigned_parameter_dict[product] = f"x{idx}"

    def generateLinearEquationsSystem(self) -> tuple:
        """
        Generates a system of linear equations for the reaction.

        Returns:
            tuple: (equations_list, all_variables_str, all_variables)
        """
        self.assignParameter()
        equations_list: list[str] = []

        # Create list of all variables in order: reactants then products
        all_variables = []
        for reactant in self.reactants_list:
            all_variables.append(self.reactants_assigned_parameter_dict[reactant])
        for product in self.products_list:
            all_variables.append(self.products_assigned_parameter_dict[product])

        all_variables_str = ",".join(all_variables)

        # Generate equations for each element
        for element in self.present_elements_in_reaction:
            equation_parts = []

            # Reactants side (positive coefficients)
            for reactant in self.reactants_list:
                if element in self.parsed_reactants[reactant]:
                    coeff = self.parsed_reactants[reactant][element]
                    param = self.reactants_assigned_parameter_dict[reactant]
                    equation_parts.append(f"{coeff}*{param}")

            # Products side (negative coefficients)
            for product in self.products_list:
                if element in self.parsed_products[product]:
                    coeff = self.parsed_products[product][element]
                    param = self.products_assigned_parameter_dict[product]
                    equation_parts.append(f"-{coeff}*{param}")

            # Create equation: sum = 0
            if equation_parts:
                equation = "+".join(equation_parts)
                equations_list.append(equation)

        return equations_list, all_variables_str, all_variables

    def solveEquations(self):
        """
        Solves the system of linear equations using SymPy directly.
        Stores the solution in class variables.
        """
        try:
            equations_list, all_variables_str, all_variables = (
                self.generateLinearEquationsSystem()
            )

            # Create SymPy symbols
            sympy_symbols = symbols(all_variables_str)

            # Convert equations to SymPy expressions
            sympy_equations = []
            for eq_str in equations_list:
                expr = sympy.sympify(eq_str)
                sympy_equations.append(expr)

            # Solve the system
            solution = linsolve(sympy_equations, sympy_symbols)

            # Convert solution to list
            solution_list = list(solution)

            if not solution_list or len(solution_list[0]) == 0:
                raise ValueError("No solution found for the system of equations")

            # Get the solution tuple
            solution_tuple = solution_list[0]

            # Check if there's a free variable (underdetermined system)
            # We need to set one variable to a constant and solve for the rest
            if any(
                hasattr(coeff, "free_symbols") and len(coeff.free_symbols) > 0
                for coeff in solution_tuple
            ):
                # Find the free variable (usually the last one)
                free_vars = set()
                for coeff in solution_tuple:
                    if hasattr(coeff, "free_symbols"):
                        free_vars.update(coeff.free_symbols)

                if free_vars:
                    # Pick one free variable to set to 1
                    free_var = list(free_vars)[0]

                    # Substitute free_var = 1
                    subs_dict = {free_var: 1}
                    solution_tuple = tuple(
                        coeff.subs(subs_dict) for coeff in solution_tuple
                    )

            # Convert all coefficients to rational numbers
            solution_tuple = tuple(sympy.nsimplify(coeff) for coeff in solution_tuple)

            # Find LCM of denominators to get integer coefficients
            denominators = []
            for coeff in solution_tuple:
                if hasattr(coeff, "as_numer_denom"):
                    _, denom = coeff.as_numer_denom()
                    if denom != 1:
                        denominators.append(denom)

            if denominators:
                # Find LCM of all denominators
                lcm_val = denominators[0]
                for denom in denominators[1:]:
                    lcm_val = sympy.lcm(lcm_val, denom)

                # Multiply all coefficients by LCM to get integers
                solution_tuple = tuple(coeff * lcm_val for coeff in solution_tuple)

            # Simplify to get integer coefficients
            solution_tuple = tuple(sympy.simplify(coeff) for coeff in solution_tuple)

            # Store results
            self.equation_solution = solution_tuple
            self.solution_variables = all_variables

            # Create balanced coefficients dictionary
            self.balanced_coefficients = {}
            for i, reactant in enumerate(self.reactants_list):
                self.balanced_coefficients[reactant] = solution_tuple[i]

            for i, product in enumerate(self.products_list):
                idx = len(self.reactants_list) + i
                self.balanced_coefficients[product] = solution_tuple[idx]

            # Generate balanced equation string
            self._generateBalancedEquationStr()

            return solution_tuple

        except Exception as e:
            print(f"Error solving equations: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _generateBalancedEquationStr(self):
        """Generates the balanced equation string."""
        if not self.balanced_coefficients:
            return

        # Build reactants side
        reactants_parts = []
        for reactant in self.reactants_list:
            coeff = self.balanced_coefficients[reactant]
            if coeff == 1:
                reactants_parts.append(reactant)
            else:
                reactants_parts.append(f"{coeff}{reactant}")

        # Build products side
        products_parts = []
        for product in self.products_list:
            coeff = self.balanced_coefficients[product]
            if coeff == 1:
                products_parts.append(product)
            else:
                products_parts.append(f"{coeff}{product}")

        self.balanced_equation_str = (
            " + ".join(reactants_parts) + " → " + " + ".join(products_parts)
        )

    def getBalancedEquation(self) -> str:
        """
        Returns the balanced chemical equation as a string.
        """
        if not self.balanced_equation_str:
            self.solveEquations()

        return self.balanced_equation_str or "Could not balance equation"

    def printSolution(self):
        """Prints the balanced equation and coefficients."""
        if not self.equation_solution:
            self.solveEquations()

        if self.equation_solution:
            print("\n=== Balanced Chemical Equation ===")
            print(f"Original: {self.chemical_equation}")
            print(f"Balanced: {self.getBalancedEquation()}")

            print("\n=== Coefficients ===")
            for compound, coeff in self.balanced_coefficients.items():
                print(f"{compound}: {coeff}")

            print("\n=== Solution Variables ===")
            for var, val in zip(self.solution_variables, self.equation_solution):
                print(f"{var} = {val}")
        else:
            print("Failed to solve the equation.")

    def getCoefficients(self) -> dict:
        """Returns the balanced coefficients as a dictionary."""
        if not self.balanced_coefficients:
            self.solveEquations()
        return self.balanced_coefficients.copy()


# Alternative solver using matrix approach (more robust)
class MatrixSolver:
    """Alternative solver using matrix approach."""

    @staticmethod
    def balance_equation(chemical_equation: str):
        """Static method to balance chemical equation."""
        generator = Generator(chemical_equation)
        generator.solveEquations()
        return generator


# Example usage (if running this file directly)
if __name__ == "__main__":
    # Test with your complex equation
    equation = (
        "K4Fe(CN)6 + KMnO4 + H2SO4 = Fe2(SO4)3 + MnSO4 + KNO3 + CO2 + K2SO4 + H2O"
    )
    generator = Generator(chemical_equation=equation)

    # This will automatically solve and store the solution
    solution = generator.solveEquations()

    # Print the results
    generator.printSolution()

    # Access the stored solution directly
    print(f"\nStored solution: {generator.equation_solution}")
    print(f"Balanced coefficients: {generator.balanced_coefficients}")

    # Get just the coefficients
    coefficients = generator.getCoefficients()
    print(f"\nCoefficients dict: {coefficients}")
