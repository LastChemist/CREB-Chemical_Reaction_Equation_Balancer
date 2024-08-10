import os
from sympy import sympify
from src.Parser import EquationParser
from utils.JsonHandler import Handler


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

    def loadEquationSolutionInformation(self) -> None:
        json_handler_object = Handler()
        json_handler_object.read()
        self.equation_solution: tuple = sympify(json_handler_object.content["equation_solution"])

    def loadChemicalFormulasDictionary(self, chemical_equation: str):
        equation_parser_object: object = EquationParser(
            chemical_equation=chemical_equation
        )
        equation_parser_object.parse()

        for reactant in equation_parser_object.reactants_list:
            self.chemical_formulas_dict[reactant] = 0
            self.reactants_list.append(reactant)

        for product in equation_parser_object.products_list:
            self.chemical_formulas_dict[product] = 0
            self.products_list.append(product)

    def assignCoefficientsToChemicalFormulas(self) -> None:
        for index, chemical_formula in enumerate(
            list(self.chemical_formulas_dict.keys())
        ):
            self.chemical_formulas_dict[chemical_formula] = self.equation_solution[
                index
            ]

        for reactant in self.reactants_list:
            if self.chemical_formulas_dict[reactant] == 1:
                self.assigned_reactants_list.append(reactant)
            else:
                self.assigned_reactants_list.append(
                    f"{self.chemical_formulas_dict[reactant]} {reactant}"
                )

        for product in self.products_list:
            if self.chemical_formulas_dict[product] == 1:
                self.assigned_products_list.append(product)
            else:
                self.assigned_products_list.append(
                    f"{self.chemical_formulas_dict[product]} {product}"
                )

    def executeRewriter(self, chemical_equation: str) -> str:
        self.loadEquationSolutionInformation()
        self.loadChemicalFormulasDictionary(chemical_equation=chemical_equation)
        self.assignCoefficientsToChemicalFormulas()

        reactants_string: str = ""
        products_string: str = ""

        for reactant in self.assigned_reactants_list:
            reactants_string += f"{reactant} + "

        for product in self.assigned_products_list:
            products_string += f"{product} + "

        reactants_string = reactants_string[:-2]
        products_string = products_string[:-2]

        return f"{reactants_string} = {products_string}"
