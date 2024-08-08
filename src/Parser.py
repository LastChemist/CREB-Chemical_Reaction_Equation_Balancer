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

    def parseFormula(self) -> Counter:
        def expand(match):
            content, count = match.groups()
            if count == "":
                count = 1
            else:
                count = int(count)
            return content * count

        # Expand parentheses
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
