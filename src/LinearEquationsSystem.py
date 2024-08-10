from utils import Assets
from src.Parser import ElementMapper, EquationParser
import os

# region Generator


class Generator:
    """
    A class to generate linear equations for balancing chemical equations.

    Attributes:
        chemical_equation : str
            The chemical equation to be parsed.
        parameter_symbols : str
            Symbols used for parameters in the equations.
        reactants_list : list[str]
            List of reactants.
        products_list : list[str]
            List of products.
        present_elements_in_reaction : list[str]
            List of elements present in the reaction.
        parsed_reactants : dict[str, dict[str, str]]
            Parsed reactants with element counts.
        parsed_products : dict[str, dict[str, str]]
            Parsed products with element counts.
        reactants_assigned_parameter_dict : dict[str, str]
            Dictionary of reactants assigned to parameters.
        products_assigned_parameter_dict : dict[str, str]
            Dictionary of products assigned to parameters.
        demand_for_variables_to_solve_count : int
            Number of variables to solve for.
        parametric_equations_list : list[str]
            List of parametric equations.

    Methods:
        presentElementsInChemicalFormula(chemical_formula: str) -> list:
            Returns a list of elements present in the given chemical formula.
        presentElementsInReaction() -> list:
            Identifies and returns a list of elements present in the reaction.
        assignParameter() -> None:
            Assigns parameters to reactants and products.
        generateLinearEquationsSystem() -> list:
            Generates a system of linear equations for the reaction.
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
        # Junior code, fix it
        equation_parser_object: object = EquationParser(
            chemical_equation=chemical_equation
        )
        equation_parser_object.parse()
        #
        self.reactants_list: list[str] = equation_parser_object.reactants_list
        self.products_list: list[str] = equation_parser_object.products_list

        self.present_elements_in_reaction: list[str] = []

        self.parsed_reactants: dict[str, dict[str, str]] = (
            equation_parser_object.parsed_reactants
        )
        self.parsed_products: dict[str, dict[str, str]] = (
            equation_parser_object.parsed_products
        )
        self.reactants_assigned_parameter_dict: dict[str, str] = {}
        self.products_assigned_parameter_dict: dict[str, str] = {}
        self.demand_for_variables_to_solve_count: int = 0
        self.parametric_equations_list: list[str] = []

    def presentElementsInChemicalFormula(self, chemical_formula: str) -> list:
        """
        Returns a list of elements present in the given chemical formula.

        Parameters:
            chemical_formula : str
                The chemical formula to be parsed.

        Returns:
            list: A list of elements present in the chemical formula.
        """
        return list(ElementMapper(chemical_formula=chemical_formula).search())

    def presentElementsInReaction(self) -> list:
        """
        Identifies and returns a list of elements present in the reaction.

        Returns:
            list: A list of elements present in the reaction.
        """
        element_list: list[str] = []
        temp_list: list = []
        reactants_list: list[str] = self.reactants_list
        products_list: list[str] = self.products_list

        for reactant in reactants_list:
            temp_list.append(
                self.presentElementsInChemicalFormula(chemical_formula=reactant)
            )

        for product in products_list:
            temp_list.append(
                self.presentElementsInChemicalFormula(chemical_formula=product)
            )

        for sublist in temp_list:
            element_list.extend(sublist)

        element_list = list(set(element_list))
        self.present_elements_in_reaction = element_list
        self.demand_for_variables_to_solve_count = len(self.reactants_list) + len(
            self.products_list
        )  # Junior code, fix the formula for "self.demand_for_variables_to_solve_count"

    def assignParameter(self) -> None:
        """
        Assigns parameters to reactants and products.
        """
        self.presentElementsInReaction()
        removing_index: int = 0

        for i, reactant in enumerate(self.reactants_list):
            self.reactants_assigned_parameter_dict[reactant] = self.parameter_symbols[i]
            removing_index = i

        self.parameter_symbols = self.parameter_symbols[removing_index + 1 :]

        for i, product in enumerate(self.products_list):
            self.products_assigned_parameter_dict[product] = self.parameter_symbols[i]
            removing_index = i

        self.parameter_symbols = self.parameter_symbols[removing_index + 1 :]

    def generateLinearEquationsSystem(self) -> list:
        """
        Generates a system of linear equations for the reaction.

        Returns:
            list: A list of linear equations.
        """
        self.assignParameter()
        equations_list: list[str] = []
        equation: str = ""
        left_hand: str = ""
        right_hand: str = ""

        for element in self.present_elements_in_reaction:
            for reactant in self.reactants_list:
                if element in self.parsed_reactants[reactant]:
                    left_hand += f"{self.parsed_reactants[reactant][element]}*{self.reactants_assigned_parameter_dict[reactant]}+"

            for product in self.products_list:
                if element in self.parsed_products[product]:
                    right_hand += f"{self.parsed_products[product][element]}*{self.products_assigned_parameter_dict[product]}-"

            left_hand = left_hand[:-1]
            right_hand = right_hand[:-1]

            equation = f"{left_hand}-{right_hand}"
            equations_list.append(equation)
            left_hand = ""
            right_hand = ""

        return equations_list

    # end region

    # region Solver File maker

    class FileMaker:
        """
        A class to create and execute a solver file for the system of linear equations.

        Attributes:
            chemical_equation : str
                The chemical equation to be parsed.
            current_directory : str
                The current directory of the file.
            system_of_linear_equations : list
                The system of linear equations generated.
            num_of_variables : int
                Number of variables to solve for.
            symbols_list : str
                List of parameter symbols.
            variables_str : str
                String representation of variables.

        Methods:
            generateEquationAndSaveSolverFile() -> None:
                Generates the equation and saves the solver file.
            executeSolverFile() -> None:
                Executes the solver file.
        """

        def __init__(self, chemical_equation: str) -> None:
            """
            Constructs all the necessary attributes for the FileMaker object.

            Parameters:
                chemical_equation : str
                    The chemical equation to be parsed.
            """
            self.chemical_equation = chemical_equation

            self.current_directory = os.path.dirname(__file__)

            equation_generator_object = Generator(
                chemical_equation=self.chemical_equation
            )
            self.system_of_linear_equations: list = (
                equation_generator_object.generateLinearEquationsSystem()
            )

            self.num_of_variables = (
                equation_generator_object.demand_for_variables_to_solve_count
            )
            self.symbols_list = Assets.parameter_symbols
            self.variables_str = ""

            for i, symbol in enumerate(self.symbols_list):
                self.variables_str += symbol
                if self.num_of_variables == i:
                    break
                else:
                    self.variables_str += ","

        def generateEquationAndSaveSolverFile(self) -> None:
            """
            Generates the equation and saves the solver file.
            """
            self.variables_str: str = self.variables_str[0:-2]
            file_content: str = rf"""# [DO NOT MODIFY] Automatically generated.
from sympy import symbols
from sympy.solvers.solveset import linsolve
import os
from utils.JsonHandler import Handler


current_directory = os.path.dirname(__file__)
{self.variables_str} = symbols("{self.variables_str}")
equation_solution = linsolve({self.system_of_linear_equations},({self.variables_str}))


x = symbols(str({self.variables_str[::-1][0]}))
equation_solution = [expr.subs(x, 1) for expr in equation_solution][0]


handler_object = Handler()
handler_object.write()

handler_object.update(key="equation_solution",value=str(equation_solution))
    """
            #
            # Note : I know this is not a best practice to repeat and place the file name twice instead of 
            # defining a single variable and do the job but, ... ... o well ¯\_(ツ)_/¯ it works, then I never touch it ¬_¬
            with open(
                rf"{self.current_directory}\linear_equations_system_solver.automatic.py",
                "w",
            ) as solver_file:
                solver_file.write(file_content)

        def executeSolverFile(self):
            with open(
                rf"{self.current_directory}\linear_equations_system_solver.automatic.py"
            ) as file:
                exec(file.read())


# end region
