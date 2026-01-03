# CREB: Chemical Reaction Equation Balancer

CREB (Chemical Reaction Equation Balancer) is a Python project designed to automatically balance chemical equations. This tool makes it easy for students, educators, and chemists to quickly and reliably transform unbalanced chemical equations into balanced ones following the law of conservation of mass.

## Features

- **Automatic balancing** of chemical equations using matrix algebra or algorithmic approaches.
- **User-friendly interface** (CLI or GUI, as available).
- **Easy integration** into other Python workflows.
- **Open source** and actively developed.
- **Supports inorganic, organic, and redox equations**.

## Installation

Clone the repository and install any required dependencies.

```bash
git clone https://github.com/LastChemist/CREB-Chemical_Reaction_Equation_Balancer.git
cd CREB-Chemical_Reaction_Equation_Balancer
pip install -r requirements.txt
```

> **Note:** Ensure you are using Python 3.7 or later.

## Usage

Depending on the interface provided:

### Command Line Interface

```bash
python creb.py
```

You will be prompted to enter an unbalanced chemical equation. For example:

```
Enter equation: H2 + O2 -> H2O
Balanced equation: 2 H2 + O2 -> 2 H2O
```

### As a Python Module

You can also use CREB in your own Python code:

```python
from creb import balance_equation

result = balance_equation("Fe + O2 -> Fe2O3")
print("Balanced:", result)
# Output: Balanced: 4 Fe + 3 O2 -> 2 Fe2O3
```

## Examples

- `H2 + Cl2 -> HCl` → `H2 + Cl2 -> 2 HCl`
- `Na + H2O -> NaOH + H2` → `2 Na + 2 H2O -> 2 NaOH + H2`

## Contributing

Contributions are welcome! You can:

- Submit bug reports and feature requests via [Issues](https://github.com/LastChemist/CREB-Chemical_Reaction_Equation_Balancer/issues)
- Fork the repo and submit pull requests
- Improve documentation and add test cases

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact

Maintainer: [LastChemist](https://github.com/LastChemist)

---

*CREB aims to be your go-to tool for chemical equation balancing. Happy balancing!*
