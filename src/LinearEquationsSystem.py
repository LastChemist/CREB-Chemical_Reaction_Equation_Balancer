from utils import Assets
from Parser import ElementMapper, EquationParser
import os

# region Generator


class Generator:
    def __init__(self, chemical_equation: str) -> None:
        self.chemical_equation: str = chemical_equation

        self.parameter_symbols: str = Assets.parameter_symbols
        # Junior code, fix it
        equation_parser_object: object = EquationParser.EquationParser(
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
        return list(ElementMapper(chemical_formula=chemical_formula).search())

    def presentElementsInReaction(self) -> list:
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
        def __init__(self, chemical_equation: str) -> None:
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

            self.variables_str: str = self.variables_str[0:-2]
            file_content: str = rf"""# [DO NOT MODIFY] Automatically generated by EquationUtil().LinearEquationSystemSolverFileMaker
from sympy import symbols
from sympy.solvers.solveset import linsolve
import os
from JsonHandler import Handler


current_directory = os.path.dirname(__file__)
{self.variables_str} = symbols("{self.variables_str}")
equation_solution = linsolve({self.system_of_linear_equations},({self.variables_str}))


x = symbols(str({self.variables_str[::-1][0]}))
equation_solution = [expr.subs(x, 1) for expr in equation_solution][0]


handler_object = Handler(file_path=r"{self.current_directory}")
handler_object.write()

handler_object.update(key="equation_solution",value=str(equation_solution))
    """
        #

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
