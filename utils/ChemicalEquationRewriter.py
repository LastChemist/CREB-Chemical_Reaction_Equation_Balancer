import os
from sympy import sympify
from src.Parser import EquationParser
from JsonHandler import Handler


class Rewriter:
    def __init__(self) -> None:
        self.parent_folder_directory: str = os.path.dirname(__file__)
        self.equation_solution: tuple = ()
        self.chemical_formulas_dict = {}
        self.reactants_list: list[str] = []
        self.products_list: list[str] = []
        # self.last_parameter: str = ""

        self.assigned_reactants_list: list[str] = []
        self.assigned_products_list: list[str] = []

        self.json_handler_object: object = Handler(
            file_path=rf"{self.parent_folder_directory}"
        )
        self.json_handler_object.read()

    def loadEquationSolutionInformation(self) -> None:
        self.equation_solution: tuple = sympify(
            self.json_handler_object.content["equation_solution"]
        )
