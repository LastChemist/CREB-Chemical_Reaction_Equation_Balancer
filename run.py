# Note: Docstring is made by copilot

from plugins.stoichiometry import UI, Stoichiometry
from Core import CREB

class ExampleUsage:
    def __init__(self):
        """
        Initializes the ExampleUsage class with an empty chemical equation.
        """
        self.chemical_equation: str = ""

    def title(self):
        """
        Prints the title and a separator line.
        """
        print("CREB - CHEMICAL REACTIONS EQUATION BALANCER - V0.3")
        print("-" * 10)

    def balance_equation(self):
        """
        Prompts the user to enter a chemical equation, balances it, and prints the solution.
        """
        self.chemical_equation = input("Enter chemical equation: ").replace(" ", "")
        print(
            "Equation solution: ",
            CREB.balance(input_chemical_equation=self.chemical_equation),
        )

    def stoichiometry(self):
        """
        Performs stoichiometric calculations and displays the results.
        """
        st = Stoichiometry(chemical_equation=self.chemical_equation)
        st.calc_species_molar_weight()
        ui = UI()
        ui.display_reaction_table()
        ui.specie_selection()
        ui.mode_selection()
        ui.get_species_value()
        ui.display_output_table()

    def menu(self):
        """
        Displays the menu and processes user input to navigate the options.
        """
        print("[1] - Regular equation balancer")
        print("[2] - Equation balancer with stoichiometry")
        print("[0] - exit")
        selection = input(" > ")
        match selection:
            case "1":
                self.balance_equation()
                print("-" * 15)
                self.menu()
            case "2":
                self.balance_equation()
                self.stoichiometry()
                print("-_" * 5, "_-" * 5)
                self.menu()
            case "0":
                input("Press enter to exit")
                exit(code=0)

# Example usage
if __name__ == "__main__":
    eu = ExampleUsage()
    eu.title()
    eu.menu()
