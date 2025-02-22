from Core.src.LinearEquationsSystem import Generator
from Core.utils.ChemicalEquationRewriter import Rewriter


def balance(input_chemical_equation: str) -> str:

    linear_equations_system_object: object = Generator.FileMaker(
        chemical_equation=input_chemical_equation
    )
    linear_equations_system_object.generateEquationAndSaveSolverFile()
    linear_equations_system_object.executeSolverFile()
    return Rewriter().executeRewriter(chemical_equation=input_chemical_equation)


# a simple usage
# print(balance(input_chemical_equation="H2 + O2 = H2O"))
# should out put : (H2) + 1/2 (O2) = (H2O)