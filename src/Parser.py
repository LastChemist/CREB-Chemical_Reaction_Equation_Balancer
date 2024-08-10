import re
from collections import Counter

# region Element Mapper


class ElementMapper:
    """
    A class to map elements in a chemical formula to their positions.

    Attributes:
        chemical_formula : str
            The chemical formula to be parsed.

    Methods:
        search() -> dict:
            Searches for elements in the chemical formula and returns a dictionary
            with elements as keys and their positions as values.
    """

    def __init__(self, chemical_formula: str) -> None:
        """
        Constructs all the necessary attributes for the ElementMapper object.

        Parameters:
            chemical_formula : str
                The chemical formula to be parsed.
        """
        self.chemical_formula: str = chemical_formula

    def search(self) -> dict:
        """
        Searches for elements in the chemical formula.

        Returns:
            dict: A dictionary with elements as keys and their positions as values.
        """
        pattern: re.Pattern[str] = re.compile(
            r"([A-Z][a-z]*)"
        )  # Note : I don't know that using re.Pattern[str] is best practice or not!
        found_elements: dict = {}
        for match in pattern.finditer(self.chemical_formula):
            element: str = match.group(1)
            index: int = match.start()

            if element in found_elements:
                found_elements[element].append(index)
            else:
                found_elements[element] = [index]
        return found_elements


# end region


# region Element Counter
class ElementCounter:
    """
    A class to count elements in a chemical formula.

    Attributes:
        chemical_formula : str
            The chemical formula to be parsed.

    Methods:
        parseFormula() -> Counter:
            Parses the chemical formula and returns a Counter object with element counts.
    """

    def __init__(self, chemical_formula: str) -> None:
        """
        Constructs all the necessary attributes for the ElementCounter object.

        Parameters:
            chemical_formula : str
                The chemical formula to be parsed.
        """
        self.chemical_formula = chemical_formula

    def parseFormula(self) -> Counter:
        """
        Parses the chemical formula and counts the elements.

        Returns:
            Counter: A Counter object with element counts.
        """

        def expand(match):
            content, count = match.groups()
            if count == "":
                count = 1
            else:
                count = int(count)
            return content * count

        # Expand parentheses
        # [Temporary] Note : the commented codes are left intentionally because
        # they are never used
        while "(" in self.chemical_formula:  # or '[' in formula or '{' in formula:
            self.chemical_formula = re.sub(
                r"\(([^()]+)\)(\d*)", expand, self.chemical_formula
            )
            # formula = re.sub(r'\[([^()]+)\](\d*)', expand, formula)
            # formula = re.sub(r'\{([^()]+)\}(\d*)', expand, formula)

        # Count elements
        element_counts: Counter = Counter()
        for element, count in re.findall(r"([A-Z][a-z]*)(\d*)", self.chemical_formula):
            if count == "":
                count = 1
            else:
                count = int(count)
            element_counts[element] += count

        return element_counts


# end region

# region Equation Parser


class EquationParser:
    """
    A class to parse and balance chemical equations.

    Attributes:
        chemical_equation : str
            The chemical equation to be parsed.
        equation_splitter : str
            The character used to split reactants and products.
        chemical_species_splitter : str
            The character used to split different species.
        reactants_list : list[str]
            List of reactants.
        products_list : list[str]
            List of products.
        parsed_reactants : dict[str, Counter]
            Parsed reactants with element counts.
        parsed_products : dict[str, Counter]
            Parsed products with element counts.

    Methods:
        splitIntoChemicalSpecies() -> None:
            Splits the chemical equation into reactants and products.
        countElementsInChemicalSpecie() -> None:
            Counts elements in each chemical species.
        parse() -> list[dict, dict]:
            Parses the chemical equation and returns parsed reactants and products.
    """

    def __init__(self, chemical_equation: str) -> None:
        """
        Constructs all the necessary attributes for the EquationParser object.

        Parameters:
            chemical_equation : str
                The chemical equation to be parsed.
        """
        self.chemical_equation: str = chemical_equation
        self.equation_splitter: str = "="
        self.chemical_species_splitter: str = "+"

        self.reactants_list: list[str] = []
        self.products_list: list[str] = []

        self.parsed_reactants: dict[str, Counter] = {}
        self.parsed_products: dict[str, Counter] = {}

    def splitIntoChemicalSpecies(self) -> None:
        """
        Splits the chemical equation into reactants and products.
        """
        splitted_equation: list[str] = self.chemical_equation.split(
            self.equation_splitter
        )
        self.reactants_list = [
            (
                "(" + species.strip() + ")"
                if not species.strip().startswith("(")
                else species.strip()
            )
            for species in splitted_equation[0].split(self.chemical_species_splitter)
        ]
        self.products_list = [
            (
                "(" + species.strip() + ")"
                if not species.strip().startswith("(")
                else species.strip()
            )
            for species in splitted_equation[1].split(self.chemical_species_splitter)
        ]

    def countElementsInChemicalSpecie(self) -> None:
        """
        Counts elements in each chemical species.
        """

        for reactant in self.reactants_list:
            self.parsed_reactants[reactant] = ElementCounter(
                chemical_formula=reactant
            ).parseFormula()

        for product in self.products_list:
            self.parsed_products[product] = ElementCounter(
                chemical_formula=product
            ).parseFormula()

    def parse(self) -> list[dict, dict]:
        """
        Parses the chemical equation and returns parsed reactants and products.

        Returns:
            list[dict, dict]: A list containing dictionaries of parsed reactants and products.
        """
        self.splitIntoChemicalSpecies()
        self.countElementsInChemicalSpecie()
        return [self.parsed_reactants, self.parsed_products]


# end region
