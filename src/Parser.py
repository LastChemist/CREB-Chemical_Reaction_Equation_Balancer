import re
from collections import Counter

# region Element Mapper


class ElementMapper:
    def __init__(self, chemical_formula: str) -> None:
        self.chemical_formula: str = chemical_formula

    def search(self) -> dict:
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
    def __init__(self, chemical_formula: str) -> None:
        self.chemical_formula = chemical_formula


# end region
