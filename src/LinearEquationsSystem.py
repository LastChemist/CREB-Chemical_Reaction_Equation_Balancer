from utils import Assets
from Parser import ElementMapper, EquationParser


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


# end region
