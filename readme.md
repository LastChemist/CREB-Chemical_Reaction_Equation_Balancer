## Modules and Classes

### [`Core/src/Parser.py`](Core/src/Parser.py)

- **ElementMapper**

  - Description: Maps elements in a chemical formula to their positions.
  - Methods: [`search()`](Core/src/Parser.py)

- **ElementCounter**

  - Description: Counts elements in a chemical formula.
  - Methods: [`parseFormula()`](Core/src/Parser.py)

- **EquationParser**
  - Description: Parses and balances chemical equations.
  - Methods: [`splitIntoChemicalSpecies()`](Core/src/Parser.py), [`countElementsInChemicalSpecie()`](Core/src/Parser.py), [`parse()`](Core/src/Parser.py)

### [`Core/src/LinearEquationsSystem.py`](Core/src/LinearEquationsSystem.py)

- **Generator**

  - Description: Generates linear equations for balancing chemical equations.
  - Methods: [`presentElementsInChemicalFormula()`](Core/src/LinearEquationsSystem.py), [`presentElementsInReaction()`](Core/src/LinearEquationsSystem.py), [`assignParameter()`](Core/src/LinearEquationsSystem.py), [`generateLinearEquationsSystem()`](Core/src/LinearEquationsSystem.py)

- **FileMaker**
  - Description: Creates and executes a solver file for the system of linear equations.
  - Methods: [`generateEquationAndSaveSolverFile()`](Core/src/LinearEquationsSystem.py), [`executeSolverFile()`](Core/src/LinearEquationsSystem.py)

### [`Core/utils/JsonHandler.py`](Core/utils/JsonHandler.py)

- **Handler**
  - Description: Handles reading, writing, updating, and removing JSON data files.
  - Methods: [`write()`](/c:/Users/ALI/.vscode/extensions/ms-python.vscode-pylance-2025.2.1/dist/typeshed-fallback/stdlib/_io.pyi), [`read()`](/c:/Users/ALI/.vscode/extensions/ms-python.vscode-pylance-2025.2.1/dist/typeshed-fallback/stdlib/_io.pyi), [`update()`](Core/utils/JsonHandler.py), [`removeJsonDataFile()`](Core/utils/JsonHandler.py)

### [`Core/utils/ChemicalEquationRewriter.py`](Core/utils/ChemicalEquationRewriter.py)

- **Rewriter**
  - Description: Rewrites chemical equations with balanced coefficients.
  - Methods: [`loadEquationSolutionInformation()`](Core/utils/ChemicalEquationRewriter.py), [`loadChemicalFormulasDictionary()`](Core/utils/ChemicalEquationRewriter.py), [`assignCoefficientsToChemicalFormulas()`](Core/utils/ChemicalEquationRewriter.py), [`executeRewriter()`](Core/utils/ChemicalEquationRewriter.py)

### [`plugins/stoichiometry.py`](plugins/stoichiometry.py)

- **Stoichiometry**

  - Description: Performs stoichiometric calculations for chemical equations.
  - Methods: [`balance_equation()`](plugins/stoichiometry.py), [`calc_molar_weight()`](plugins/stoichiometry.py), [`calc_ratio()`](plugins/stoichiometry.py), [`calc_species_molar_weight()`](plugins/stoichiometry.py), [`calc_moles_grams()`](plugins/stoichiometry.py)

- **UI**
  - Description: Provides a user interface for stoichiometric calculations.
  - Methods: `create_table()`, `display_reaction_table()`, `specie_selection()`, `mode_selection()`, `get_species_value()`, `display_output_table()`

## Contributing

We welcome contributions to the project! Please follow these guidelines:

- Fork the repository
- Create a new branch for your feature or bug fix
- Submit a pull request with a detailed description of your changes

## License

This project is licensed under the AGPL-3 License.

## Contact
For any questions or support, please contact [LastChemist](https://github.com/LastChemist/creb).

###### made with ❤️ and tons of ATP (Adenosine triphosphate)