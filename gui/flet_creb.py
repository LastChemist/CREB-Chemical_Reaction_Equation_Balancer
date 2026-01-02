import flet as ft
from Core.src.LinearEquationsSystem import Generator
from plugins import stoichiometry_bare_bone
from plugins.stoichiometry_bare_bone import GlobalVariables
import pyperclip
import threading
import time
import sympy


class ChemicalApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()

        # Initialize data structures
        self.stoichiometry_data = {
            "reactants": [],
            "products": [],
            "molar_weights_reactants": [],
            "molar_weights_products": [],
            "gram_inputs": [],
            "mole_inputs": [],
            "radio_buttons": [],
            "selected_index": None,
            "all_compounds": [],
            "total_molar_weights": [],
        }

        # Build UI
        self.build_ui()

    def setup_page(self):
        """Configure page settings"""
        self.page.title = "CREB - Chemical Reaction Suite"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_resizable = True
        self.page.padding = 0
        self.page.scroll = "auto"

    def build_ui(self):
        """Build the complete UI"""
        main_content = self.create_main_content()

        self.layout = ft.Row(
            [main_content],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.page.add(self.layout)

        # Set initial focus
        if hasattr(self, "equation_input"):
            self.equation_input.focus()

    def create_main_content(self):
        """Create the main content area"""
        return ft.Container(
            content=ft.Column(
                [
                    self.create_header(),
                    self.create_tabs(),
                    self.create_footer(),
                ],
                expand=True,
            ),
            padding=20,
            expand=True,
        )

    def create_header(self):
        """Create application header"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.SCIENCE, size=40, color=ft.colors.BLUE),
                            ft.Text(
                                "CREB Suite",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_800,
                            ),
                            ft.Text(
                                "Chemical Reaction Tools",
                                size=20,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=10,
                    ),
                ]
            ),
            padding=ft.padding.only(bottom=20),
        )

    def create_footer(self):
        """Create footer with status"""
        return ft.Container(
            content=ft.Text("Ready", size=12, color=ft.colors.GREY_500),
            padding=ft.padding.only(top=20),
            alignment=ft.alignment.center,
        )

    def create_tabs(self):
        """Create tabbed interface"""
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Reaction Balancer",
                    icon=ft.icons.BALANCE,
                    content=self.create_balancer_tab(),
                ),
                ft.Tab(
                    text="Stoichiometry Calculator",
                    icon=ft.icons.CALCULATE,
                    content=self.create_stoichiometry_tab(),
                ),
            ],
            expand=1,
        )

    def create_balancer_tab(self):
        """Create the reaction balancer tab"""
        # Input field - MODERN SIZE (REVERTED)
        self.equation_input = ft.TextField(
            label="Enter Chemical Equation",
            hint_text="Example: H2 + O2 -> H2O",
            width=900,
            height=60,
            text_size=16,
            border_color=ft.colors.BLUE_400,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            multiline=False,  # Single line
            prefix_icon=ft.icons.TELEGRAM,
            text_align=ft.TextAlign.LEFT,
            content_padding=ft.padding.symmetric(
                horizontal=20, vertical=15
            ),  # Balanced padding
        )

        # Buttons - CENTERED
        self.balance_button = ft.ElevatedButton(
            "Balance Equation",
            icon=ft.icons.BALANCE,
            on_click=self.balance_equation,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
            ),
        )

        self.clear_button = ft.OutlinedButton(
            "Clear",
            icon=ft.icons.CLEAR,
            on_click=self.clear_balancer,
        )

        # Output container
        self.output_container = ft.Container(
            padding=20,
            border_radius=10,
            border=ft.border.all(2, ft.colors.GREEN_200),
            bgcolor=ft.colors.GREEN_50,
            visible=False,
        )

        self.balanced_equation_text = ft.Text(
            "", size=20, selectable=True, weight=ft.FontWeight.BOLD
        )

        self.coefficients_text = ft.Text("", size=16, color=ft.colors.GREY_700)

        # Solution steps container
        self.solution_steps_container = ft.Container(
            padding=ft.padding.only(top=15, left=10, right=10, bottom=10),
            visible=False,
        )

        self.copy_equation_button = ft.IconButton(
            icon=ft.icons.COPY,
            icon_size=20,
            tooltip="Copy balanced equation",
            on_click=lambda e: self.copy_to_clipboard(
                self.balanced_equation_text.value, "Balanced equation copied!"
            ),
        )

        self.copy_coefficients_button = ft.IconButton(
            icon=ft.icons.COPY,
            icon_size=20,
            tooltip="Copy coefficients",
            on_click=lambda e: self.copy_to_clipboard(
                self.coefficients_text.value, "Coefficients copied!"
            ),
        )

        # Toggle button for solution steps
        self.toggle_solution_button = ft.ElevatedButton(
            "Show Detailed Solution Steps",
            icon=ft.icons.EXPAND_MORE,
            on_click=self.toggle_solution_steps,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                bgcolor=ft.colors.BLUE_50,
                color=ft.colors.BLUE,
            ),
        )

        # Create solution steps section and store it as an attribute
        self.solution_steps_section = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.SCHOOL, size=20, color=ft.colors.BLUE_700),
                            ft.Text(
                                "Algebraic Method Solution Steps",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=5, color=ft.colors.BLUE_200),
                    self.solution_steps_container,
                ],
                spacing=10,
            ),
            padding=10,
            border=ft.border.all(1, ft.colors.GREEN_300),
            border_radius=8,
            bgcolor=ft.colors.GREEN_100,
            visible=False,  # Initially hidden
        )

        self.output_container.content = ft.Column(
            [
                ft.Text(
                    "Balanced Equation",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREEN_800,
                ),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.Row(
                    [
                        ft.Container(content=self.balanced_equation_text, expand=True),
                        self.copy_equation_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=5),
                ft.Row(
                    [
                        ft.Container(content=self.coefficients_text, expand=True),
                        self.copy_coefficients_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=15),
                # Toggle button and solution steps section
                ft.Column(
                    [
                        ft.Row(
                            [self.toggle_solution_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        self.solution_steps_section,
                    ],
                    spacing=10,
                ),
                ft.Divider(height=20),
            ],
            spacing=5,
        )

        # Error container
        self.error_container = ft.Container(
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.RED_50,
            border=ft.border.all(1, ft.colors.RED_400),
            visible=False,
        )

        self.error_text = ft.Text("", color=ft.colors.RED_700, size=16)
        self.error_container.content = ft.Row(
            [ft.Icon(ft.icons.ERROR, color=ft.colors.RED), self.error_text], spacing=10
        )

        # Status message for copy operations
        self.copy_status_text = ft.Text("", size=14, color=ft.colors.GREY_600)

        # Examples
        example_equations = [
            ("H2 + O2 → H2O", "H2 + O2 -> H2O"),
            ("CH4 + O2 → CO2 + H2O", "CH4 + O2 -> CO2 + H2O"),
            ("Fe + O2 → Fe2O3", "Fe + O2 -> Fe2O3"),
            ("NaOH + H2SO4 = Na2SO4 + H2O", "NaOH + H2SO4 = Na2SO4 + H2O"),
        ]

        example_rows = []
        for i in range(0, len(example_equations), 3):
            row_buttons = []
            for j in range(3):
                if i + j < len(example_equations):
                    text, eq = example_equations[i + j]
                    row_buttons.append(
                        ft.TextButton(
                            text,
                            on_click=lambda e, eq=eq: self.load_example(eq),
                        )
                    )
            if row_buttons:
                example_rows.append(ft.Row(row_buttons, spacing=20))

        self.examples_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Try these examples:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Column(example_rows, spacing=10),
                ],
                spacing=10,
            ),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            bgcolor=ft.colors.GREY_50,
        )

        return ft.Container(
            content=ft.Column(
                [
                    # Top expanding space
                    ft.Container(expand=1),
                    # Equation input in the middle - MODERN SIZE
                    ft.Container(
                        content=self.equation_input,
                        alignment=ft.alignment.center,
                    ),
                    # Buttons centered
                    ft.Row(
                        [self.balance_button, self.clear_button],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=10),
                    self.copy_status_text,
                    ft.Divider(height=30),
                    self.output_container,
                    ft.Divider(height=10),
                    self.error_container,
                    ft.Divider(height=30),
                    self.examples_container,
                    # Bottom expanding space
                    ft.Container(expand=1),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            padding=20,
            expand=True,
        )

    def create_stoichiometry_tab(self):
        """Create the stoichiometry calculator tab"""
        self.stoich_equation_text = ft.Text(
            "Balance an equation first to use stoichiometry calculator",
            size=14,
            color=ft.colors.GREY_600,
        )

        self.scrollable_grid_container = ft.Container(
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=12,
            padding=20,
            bgcolor=ft.colors.WHITE,
            visible=False,
            height=350,
        )

        self.stoich_result_text = ft.Text("", size=14, color=ft.colors.GREY_600)

        self.view_table_button = ft.ElevatedButton(
            "View Full Table",
            icon=ft.icons.TABLE_CHART,
            on_click=self.show_full_table_viewer,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                bgcolor=ft.colors.GREEN_50,
                color=ft.colors.GREEN,
            ),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Divider(height=20),
                    self.stoich_equation_text,
                    ft.Divider(height=20),
                    self.scrollable_grid_container,
                    ft.Divider(height=20),
                    self.create_stoichiometry_controls(),
                    ft.Divider(height=10),
                    ft.Row(
                        [self.view_table_button], alignment=ft.MainAxisAlignment.CENTER
                    ),
                ],
                spacing=20,
            ),
            padding=20,
        )

    def create_stoichiometry_controls(self):
        """Create controls for stoichiometry tab"""
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Calculate Stoichiometry",
                            icon=ft.icons.CALCULATE,
                            on_click=self.calculate_stoichiometry,
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(
                                    horizontal=25, vertical=12
                                ),
                                bgcolor=ft.colors.BLUE,
                                color=ft.colors.WHITE,
                            ),
                        ),
                        ft.OutlinedButton(
                            "Clear All",
                            icon=ft.icons.CLEAR,
                            on_click=self.clear_stoichiometry,
                        ),
                        ft.OutlinedButton(
                            "Load from Balanced",
                            icon=ft.icons.UPLOAD,
                            on_click=self.load_balanced_to_stoichiometry,
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(height=10),
                self.stoich_result_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def copy_to_clipboard(self, text, success_message="Copied to clipboard!"):
        """Copy text to clipboard and show status message"""
        if not text:
            return

        try:
            pyperclip.copy(text)
            self.show_copy_status(success_message, ft.colors.GREEN)
        except Exception as e:
            self.show_copy_status(f"Failed to copy: {str(e)}", ft.colors.RED)

    def show_copy_status(self, message, color):
        """Show temporary status message for copy operations"""
        self.copy_status_text.value = message
        self.copy_status_text.color = color
        self.page.update()

        def clear_message():
            time.sleep(2)
            self.copy_status_text.value = ""
            self.page.update()

        threading.Thread(target=clear_message, daemon=True).start()

    def toggle_solution_steps(self, e=None):
        """Toggle visibility of solution steps"""
        if hasattr(self, "solution_steps_expanded"):
            self.solution_steps_expanded = not self.solution_steps_expanded
        else:
            self.solution_steps_expanded = True

        # Update button icon and text
        if self.solution_steps_expanded:
            self.toggle_solution_button.icon = ft.icons.EXPAND_LESS
            self.toggle_solution_button.text = "Hide Detailed Solution Steps"
            # Show the solution steps section
            self.solution_steps_section.visible = True
        else:
            self.toggle_solution_button.icon = ft.icons.EXPAND_MORE
            self.toggle_solution_button.text = "Show Detailed Solution Steps"
            # Hide the solution steps section
            self.solution_steps_section.visible = False

        self.page.update()

    def format_value(self, value, is_molar_weight=False):
        """Format a numeric value properly - FIXED FOR ALL CASES"""
        try:
            if value is None:
                return ""
            
            # Convert to float
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return str(value)
            
            # Check if value is effectively zero
            if abs(value) < 0.000000001:  # Very close to zero
                return "0"
            
            # For molar weights, always use 3 decimal places
            if is_molar_weight:
                return f"{value:.3f}"
            
            # For other values (grams and moles):
            # 1. Check if it's very small but not zero
            if abs(value) < 0.001 and abs(value) > 0.000000001:
                # Use scientific notation for very small non-zero values
                return f"{value:.2e}"
            
            # 2. Check if it's very large
            if abs(value) >= 1000000:
                return f"{value:.2e}"
            
            # 3. For normal values, check if it's effectively an integer
            if abs(value - round(value, 4)) < 0.00001:
                return f"{int(round(value, 0))}"
            
            # 4. For decimal values, use up to 6 decimal places
            formatted = f"{value:.6f}"
            
            # Remove trailing zeros and decimal point if unnecessary
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
                # If we removed everything after decimal, add .0 for clarity
                if '.' not in formatted and abs(value - int(value)) > 0.000000001:
                    formatted = f"{value:.1f}"
            
            return formatted
                
        except Exception as e:
            return str(value)
    
    def generate_solution_steps(self, equation_solver):
        """Generate CLEAN step-by-step solution guide - SIMPLIFIED VERSION"""
        try:
            # Get equation data from the generator
            equation = self.equation_input.value.strip()

            steps_content = []

            # Step 1: Parse reactants and products
            steps_content.append(
                self.create_step_container(
                    step_num=1,
                    title="Parse Reactants and Products",
                    content=[
                        f"Original equation: {equation}",
                        f"Reactants: {', '.join(equation_solver.reactants_list)}",
                        f"Products: {', '.join(equation_solver.products_list)}",
                    ],
                )
            )

            # Step 2: Identify all elements
            elements = equation_solver.presentElementsInReaction()
            steps_content.append(
                self.create_step_container(
                    step_num=2,
                    title="Identify All Elements",
                    content=[
                        f"Elements present: {', '.join(elements)}",
                        f"Number of elements: {len(elements)}",
                    ],
                )
            )

            # Step 3: Assign variables and create equations
            equation_solver.assignParameter()
            equations_list, all_variables_str, _ = (
                equation_solver.generateLinearEquationsSystem()
            )

            # Create variable mapping
            var_mapping = []
            for i, reactant in enumerate(equation_solver.reactants_list):
                var = equation_solver.reactants_assigned_parameter_dict[reactant]
                var_mapping.append(f"{var} → {reactant}")

            for i, product in enumerate(equation_solver.products_list):
                var = equation_solver.products_assigned_parameter_dict[product]
                var_mapping.append(f"{var} → {product}")

            # Format equations with parentheses
            equation_display = []
            for i, eq in enumerate(equations_list):
                # Format with parentheses around negative coefficients
                parts = eq.replace(" ", "").split("+")
                formatted_parts = []
                for part in parts:
                    if part.startswith("-"):
                        if "*" in part:
                            coeff, var = part.split("*", 1)
                            formatted_parts.append(f"({coeff})*{var}")
                        else:
                            formatted_parts.append(f"({part})")
                    else:
                        formatted_parts.append(part)
                formatted_eq = " + ".join(formatted_parts)
                equation_display.append(f"Element {elements[i]}: {formatted_eq} = 0")

            steps_content.append(
                self.create_step_container(
                    step_num=3,
                    title="Set Up Algebraic Equations",
                    content=var_mapping + [""] + equation_display,
                )
            )

            # Step 4: Solve and get integer coefficients
            if equation_solver.equation_solution:
                # Calculate LCM for denominators
                denominators = []
                for val in equation_solver.equation_solution:
                    if hasattr(val, "as_numer_denom"):
                        _, den = val.as_numer_denom()
                        if den != 1:
                            denominators.append(den)

                coeff_steps = []

                if denominators:
                    # Calculate LCM
                    lcm_val = 1
                    for den in denominators:
                        lcm_val = sympy.lcm(lcm_val, den)

                    coeff_steps.append(
                        f"Denominators found: {', '.join(map(str, denominators))}"
                    )
                    coeff_steps.append(f"Least Common Multiple (LCM): {lcm_val}")
                    coeff_steps.append("")
                    coeff_steps.append(
                        "Multiplying all coefficients by LCM to get integers:"
                    )

                    for i, (var, val) in enumerate(
                        zip(
                            all_variables_str.split(","),
                            equation_solver.equation_solution,
                        )
                    ):
                        if hasattr(val, "as_numer_denom"):
                            num, den = val.as_numer_denom()
                            if den == 1:
                                coeff_steps.append(
                                    f"{var}: {num} × {lcm_val} = {int(num * lcm_val)}"
                                )
                            else:
                                coeff_steps.append(
                                    f"{var}: {num}/{den} × {lcm_val} = {int(num * (lcm_val // den))}"
                                )
                        else:
                            coeff_steps.append(f"{var}: {val}")

                # Show final coefficients
                coeff_steps.append("")
                coeff_steps.append("Final integer coefficients:")
                for compound, coeff in equation_solver.balanced_coefficients.items():
                    coeff_steps.append(f"{compound}: {coeff}")

                steps_content.append(
                    self.create_step_container(
                        step_num=4,
                        title="Obtain Integer Coefficients",
                        content=coeff_steps,
                    )
                )

                # Step 5: Final balanced equation
                steps_content.append(
                    self.create_step_container(
                        step_num=5,
                        title="Final Balanced Equation",
                        content=[f"{equation_solver.balanced_equation_str}"],
                    )
                )

            return ft.Column(steps_content, spacing=10)

        except Exception as e:
            return ft.Text(
                f"Could not generate detailed steps: {str(e)}",
                size=12,
                color=ft.colors.RED,
            )

    def create_step_container(self, step_num, title, content):
        """Create a styled container for each solution step"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    str(step_num),
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.WHITE,
                                ),
                                bgcolor=ft.colors.BLUE_700,
                                border_radius=15,
                                width=30,
                                height=30,
                                alignment=ft.alignment.center,
                            ),
                            ft.Text(
                                title,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(line, size=13, color=ft.colors.GREY_700)
                                for line in content
                            ],
                            spacing=3,
                        ),
                        padding=ft.padding.only(left=40, top=5, bottom=5),
                    ),
                ],
                spacing=5,
            ),
            padding=10,
            bgcolor=ft.colors.GREEN_50 if step_num % 2 == 0 else ft.colors.WHITE,
            border_radius=8,
            border=ft.border.all(
                1, ft.colors.GREEN_200 if step_num % 2 == 0 else ft.colors.BLUE_100
            ),
        )

    def show_full_table_viewer(self, e=None):
        """Show a dialog with the full stoichiometry table"""
        if not self.stoichiometry_data.get("all_compounds"):
            self.stoich_result_text.value = "Please load a balanced equation first"
            self.stoich_result_text.color = ft.colors.RED
            self.page.update()
            return

        table_content = self.build_full_stoichiometry_table()

        table_dialog = ft.AlertDialog(
            title=ft.Text("Full Stoichiometry Table"),
            content=ft.Container(content=table_content, width=900, height=500),
            actions=[
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Export Table",
                            icon=ft.icons.DOWNLOAD,
                            on_click=lambda e: self.export_table_to_clipboard(),
                        ),
                        ft.OutlinedButton(
                            "Close",
                            on_click=lambda e: self.close_dialog(table_dialog),
                        ),
                    ],
                    spacing=20,
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = table_dialog
        table_dialog.open = True
        self.page.update()

    def build_full_stoichiometry_table(self):
        """Build a detailed stoichiometry table with PROPER FORMATTING"""
        compounds = self.stoichiometry_data["all_compounds"]
        molar_weights = self.stoichiometry_data["total_molar_weights"]

        if not compounds:
            return ft.Text("No data available", color=ft.colors.GREY_600)

        table_rows = []

        # Header
        header_row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Compound", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataCell(
                    ft.Text("Molar Weight (g/mol)", weight=ft.FontWeight.BOLD, size=14)
                ),
                ft.DataCell(ft.Text("Grams (g)", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataCell(ft.Text("Moles (mol)", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataCell(ft.Text("Type", weight=ft.FontWeight.BOLD, size=14)),
            ]
        )
        table_rows.append(header_row)

        # Data rows - USING NEW FORMAT_VALUE FUNCTION
        num_reactants = len(self.stoichiometry_data.get("reactants", []))

        for i, (compound, mw) in enumerate(zip(compounds, molar_weights)):
            # Get gram value
            gram_input = (
                self.stoichiometry_data["gram_inputs"][i]
                if i < len(self.stoichiometry_data["gram_inputs"])
                else None
            )
            grams = ""
            if gram_input and gram_input.value:
                try:
                    grams = self.format_value(float(gram_input.value))
                except (ValueError, TypeError):
                    grams = ""

            # Get mole value
            mole_input = (
                self.stoichiometry_data["mole_inputs"][i]
                if i < len(self.stoichiometry_data["mole_inputs"])
                else None
            )
            moles = ""
            if mole_input and mole_input.value:
                try:
                    moles = self.format_value(float(mole_input.value))
                except (ValueError, TypeError):
                    moles = ""

            # Format molar weight
            mw_formatted = (
                self.format_value(mw, is_molar_weight=True) if mw is not None else "—"
            )

            is_reactant = i < num_reactants
            compound_type = "Reactant" if is_reactant else "Product"

            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                compound,
                                color=(
                                    ft.colors.BLUE_700
                                    if is_reactant
                                    else ft.colors.GREEN_700
                                ),
                                weight=ft.FontWeight.BOLD,
                                size=14,
                            )
                        ),
                        ft.DataCell(ft.Text(mw_formatted, size=14)),
                        ft.DataCell(ft.Text(grams or "—", size=14)),
                        ft.DataCell(ft.Text(moles or "—", size=14)),
                        ft.DataCell(
                            ft.Text(
                                compound_type,
                                color=(
                                    ft.colors.BLUE if is_reactant else ft.colors.GREEN
                                ),
                                size=14,
                            )
                        ),
                    ]
                )
            )

        return ft.ListView(
            controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Compound")),
                        ft.DataColumn(ft.Text("MW")),
                        ft.DataColumn(ft.Text("Grams")),
                        ft.DataColumn(ft.Text("Moles")),
                        ft.DataColumn(ft.Text("Type")),
                    ],
                    rows=table_rows,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    heading_row_color=ft.colors.GREY_100,
                    column_spacing=30,
                    horizontal_margin=15,
                    vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_200),
                    horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_200),
                )
            ],
            expand=True,
        )

    def export_table_to_clipboard(self):
        """Export table data to clipboard with PROPER FORMATTING"""
        compounds = self.stoichiometry_data["all_compounds"]
        molar_weights = self.stoichiometry_data["total_molar_weights"]

        if not compounds:
            return

        text = "Compound,Molar Weight (g/mol),Grams (g),Moles (mol),Type\n"

        num_reactants = len(self.stoichiometry_data.get("reactants", []))

        for i, (compound, mw) in enumerate(zip(compounds, molar_weights)):
            # Get and format grams
            gram_input = (
                self.stoichiometry_data["gram_inputs"][i]
                if i < len(self.stoichiometry_data["gram_inputs"])
                else None
            )
            grams = ""
            if gram_input and gram_input.value:
                try:
                    grams = self.format_value(float(gram_input.value))
                except (ValueError, TypeError):
                    grams = ""

            # Get and format moles
            mole_input = (
                self.stoichiometry_data["mole_inputs"][i]
                if i < len(self.stoichiometry_data["mole_inputs"])
                else None
            )
            moles = ""
            if mole_input and mole_input.value:
                try:
                    moles = self.format_value(float(mole_input.value))
                except (ValueError, TypeError):
                    moles = ""

            # Format molar weight
            mw_formatted = (
                self.format_value(mw, is_molar_weight=True) if mw is not None else ""
            )
            compound_type = "Reactant" if i < num_reactants else "Product"

            text += f'{compound},{mw_formatted},{grams or ""},{moles or ""},{compound_type}\n'

        self.copy_to_clipboard(text, "Table data copied to clipboard!")

    def close_dialog(self, dialog):
        """Close a dialog"""
        dialog.open = False
        self.page.update()

    def load_example(self, equation: str):
        """Load an example equation"""
        self.equation_input.value = equation
        self.page.update()

    def clear_balancer(self, e=None):
        """Clear all inputs and outputs in balancer"""
        self.equation_input.value = ""
        self.output_container.visible = False
        self.solution_steps_container.visible = False
        if hasattr(self, "solution_steps_expanded"):
            self.solution_steps_expanded = False
        if hasattr(self, "solution_steps_section"):
            self.solution_steps_section.visible = False
        self.error_container.visible = False
        self.copy_status_text.value = ""
        self.page.update()

    def show_error(self, message: str):
        """Display error message"""
        self.error_text.value = message
        self.error_container.visible = True
        self.output_container.visible = False
        self.solution_steps_container.visible = False
        self.page.update()

    def show_result(self, balanced_eq: str, equation_solver=None):
        """Display the balancing result with solution steps"""
        self.balanced_equation_text.value = balanced_eq

        # Generate coefficients text
        if equation_solver and equation_solver.balanced_coefficients:
            coeff_text = "Coefficients: "
            for compound, coeff in equation_solver.balanced_coefficients.items():
                coeff_text += f"{compound}: {coeff}, "
            self.coefficients_text.value = coeff_text.rstrip(", ")
        else:
            self.coefficients_text.value = ""

        # Generate and show solution steps if we have the equation_solver
        if equation_solver:
            solution_steps = self.generate_solution_steps(equation_solver)
            self.solution_steps_container.content = solution_steps
            self.solution_steps_container.visible = True

            # Reset toggle state
            self.solution_steps_expanded = False
            self.toggle_solution_button.icon = ft.icons.EXPAND_MORE
            self.toggle_solution_button.text = "Show Detailed Solution Steps"
            if hasattr(self, "solution_steps_section"):
                self.solution_steps_section.visible = False

        self.output_container.visible = True
        self.error_container.visible = False
        self.page.update()

    def balance_equation(self, e=None):
        """Main balancing function with step-by-step solution"""
        equation = self.equation_input.value.strip()

        if not equation:
            self.show_error("Please enter a chemical equation")
            return

        try:
            equation_solver = Generator(chemical_equation=equation)
            equation_solver.solveEquations()
            equation_solver._generateBalancedEquationStr()

            self.show_result(
                balanced_eq=equation_solver.balanced_equation_str,
                equation_solver=equation_solver,
            )

            # Update stoichiometry tab with this equation
            self.stoich_equation_text.value = (
                f"Balanced Equation: {equation_solver.balanced_equation_str}"
            )
            self.page.update()

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def create_copy_button(self, text_field, value_type):
        """Create a copy button for a text field"""
        return ft.IconButton(
            icon=ft.icons.COPY,
            icon_size=16,
            tooltip=f"Copy {value_type} value",
            on_click=lambda e: self.copy_text_field(text_field, value_type),
        )

    def copy_text_field(self, text_field, value_type):
        """Copy text field value to clipboard"""
        if text_field.value:
            self.copy_to_clipboard(
                text_field.value, f"{value_type.capitalize()} value copied!"
            )

    def build_chemical_grid(
        self, reactants, products, molar_weights_reactants, molar_weights_products
    ):
        """Build the stoichiometry grid with PROPER FORMATTING"""
        total_compounds = len(reactants) + len(products)

        # Clear previous data
        self.stoichiometry_data["gram_inputs"] = []
        self.stoichiometry_data["mole_inputs"] = []
        self.stoichiometry_data["radio_buttons"] = []
        self.stoichiometry_data["all_compounds"] = reactants + products
        self.stoichiometry_data["total_molar_weights"] = (
            molar_weights_reactants + molar_weights_products
        )

        # Create grid structure
        grid_container = ft.Container(
            width=120 + (140 * total_compounds) + 50, height=300
        )
        grid = ft.Column(spacing=15)

        # Header
        header = ft.Row(
            [
                ft.Container(width=120),
                *[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    r,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.BLUE_700,
                                    size=14,
                                ),
                                ft.Text(
                                    f"{self.format_value(mw, is_molar_weight=True)} g/mol",
                                    size=11,
                                    color=ft.colors.GREY_600,
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=140,
                        alignment=ft.alignment.center,
                    )
                    for r, mw in zip(reactants, molar_weights_reactants)
                ],
                ft.Container(
                    content=ft.Text("→", size=20, weight=ft.FontWeight.BOLD), width=50
                ),
                *[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    p,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.GREEN_700,
                                    size=14,
                                ),
                                ft.Text(
                                    f"{self.format_value(mw, is_molar_weight=True)} g/mol",
                                    size=11,
                                    color=ft.colors.GREY_600,
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=140,
                        alignment=ft.alignment.center,
                    )
                    for p, mw in zip(products, molar_weights_products)
                ],
            ]
        )
        grid.controls.append(header)

        # Radio buttons row
        radio_row = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        "Select Compound:", weight=ft.FontWeight.BOLD, size=12
                    ),
                    width=120,
                    alignment=ft.alignment.center_right,
                    padding=ft.padding.only(right=10),
                )
            ]
        )

        # Create radio buttons
        for i in range(total_compounds):
            checkbox = ft.Checkbox(
                on_change=lambda e, idx=i: self.on_checkbox_changed(e, idx)
            )
            self.stoichiometry_data["radio_buttons"].append(checkbox)

            container = ft.Container(
                content=checkbox, width=140, alignment=ft.alignment.center
            )

            if i < len(reactants):
                radio_row.controls.append(container)
            elif i == len(reactants):
                radio_row.controls.append(ft.Container(width=50))
                radio_row.controls.append(container)
            else:
                radio_row.controls.append(container)

        grid.controls.append(radio_row)

        # Grams and moles rows
        grams_row = self.create_input_row("Grams (g):", "gram_inputs")
        moles_row = self.create_input_row("Moles (mol):", "mole_inputs")

        grid.controls.append(grams_row)
        grid.controls.append(moles_row)

        # Add grid to scrollable container
        grid_container.content = ft.Row([grid], scroll=ft.ScrollMode.AUTO)
        return grid_container

    def create_input_row(self, label_text, input_key):
        """Create a row of input fields (grams or moles)"""
        row = ft.Row(
            [
                ft.Container(
                    content=ft.Text(label_text, weight=ft.FontWeight.BOLD, size=12),
                    width=120,
                    alignment=ft.alignment.center_right,
                    padding=ft.padding.only(right=10),
                )
            ]
        )

        for i in range(len(self.stoichiometry_data["all_compounds"])):
            input_field = ft.TextField(
                width=100,
                height=35,
                text_size=12,
                disabled=True,
                border_color=ft.colors.GREY_400,
                hint_text="Enter value",
                content_padding=8,
                border_radius=5,
            )

            if input_key == "gram_inputs":
                self.stoichiometry_data["gram_inputs"].append(input_field)
            else:
                self.stoichiometry_data["mole_inputs"].append(input_field)

            copy_button = self.create_copy_button(
                input_field, "grams" if input_key == "gram_inputs" else "moles"
            )

            input_container = ft.Column(
                [
                    ft.Row([input_field, copy_button], spacing=5),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            container = ft.Container(
                content=input_container, width=140, alignment=ft.alignment.center
            )

            if i < len(self.stoichiometry_data["reactants"]):
                row.controls.append(container)
            elif i == len(self.stoichiometry_data["reactants"]):
                row.controls.append(ft.Container(width=50))
                row.controls.append(container)
            else:
                row.controls.append(container)

        return row

    def on_checkbox_changed(self, e, index):
        """Handle checkbox selection in stoichiometry tab"""
        # Uncheck all other checkboxes
        for i, checkbox in enumerate(self.stoichiometry_data["radio_buttons"]):
            if i != index:
                checkbox.value = False

        # Update selected index
        self.stoichiometry_data["selected_index"] = index if e.control.value else None

        # Enable/disable inputs
        for i, (gram_input, mole_input) in enumerate(
            zip(
                self.stoichiometry_data["gram_inputs"],
                self.stoichiometry_data["mole_inputs"],
            )
        ):
            is_selected = i == self.stoichiometry_data["selected_index"]
            gram_input.disabled = not is_selected
            mole_input.disabled = not is_selected

            if is_selected:
                gram_input.border_color = ft.colors.BLUE
                mole_input.border_color = ft.colors.BLUE
                gram_input.value = ""
                mole_input.value = ""
            else:
                gram_input.border_color = ft.colors.GREY_400
                mole_input.border_color = ft.colors.GREY_400
                gram_input.value = ""
                mole_input.value = ""

        self.page.update()

    def load_balanced_to_stoichiometry(self, e=None):
        """Load the balanced equation into stoichiometry calculator"""
        if not self.equation_input.value.strip():
            self.stoich_result_text.value = "Please balance an equation first"
            self.stoich_result_text.color = ft.colors.RED
            self.page.update()
            return

        try:
            equation = self.equation_input.value.strip()
            equation_solver = Generator(chemical_equation=equation)
            equation_solver.solveEquations()
            equation_solver._generateBalancedEquationStr()

            stoichiometry_calc = stoichiometry_bare_bone.Stoichiometry(
                chemical_equation=equation
            )
            stoichiometry_calc.balance_equation()
            stoichiometry_calc.calc_species_molar_weight()

            reactants = equation_solver.reactants_list
            products = equation_solver.products_list

            molar_weights_reactants = GlobalVariables.reactants_molar_weights_list
            molar_weights_products = GlobalVariables.products_molar_weights_list

            # Store data
            self.stoichiometry_data["reactants"] = reactants
            self.stoichiometry_data["products"] = products
            self.stoichiometry_data["molar_weights_reactants"] = molar_weights_reactants
            self.stoichiometry_data["molar_weights_products"] = molar_weights_products

            # Build grid
            grid = self.build_chemical_grid(
                reactants, products, molar_weights_reactants, molar_weights_products
            )
            self.scrollable_grid_container.content = grid
            self.scrollable_grid_container.visible = True

            self.stoich_result_text.value = (
                "Select a compound and enter values to calculate"
            )
            self.stoich_result_text.color = ft.colors.GREY_600

            self.page.update()

        except Exception as ex:
            self.stoich_result_text.value = f"Error loading equation: {str(ex)}"
            self.stoich_result_text.color = ft.colors.RED
            self.page.update()

    def calculate_stoichiometry(self, e=None):
        """Calculate stoichiometry - WITH PROPER FORMATTING FOR BOTH GRAMS AND MOLES"""
        if self.stoichiometry_data["selected_index"] is None:
            self.stoich_result_text.value = "Please select a compound first!"
            self.stoich_result_text.color = ft.colors.RED
            self.page.update()
            return

        # Get input values
        selected_idx = self.stoichiometry_data["selected_index"]
        grams = self.stoichiometry_data["gram_inputs"][selected_idx].value
        moles = self.stoichiometry_data["mole_inputs"][selected_idx].value

        if not grams and not moles:
            self.stoich_result_text.value = (
                "Enter gram or mole value for selected compound"
            )
            self.stoich_result_text.color = ft.colors.ORANGE
            self.page.update()
            return

        try:
            # Set GlobalVariables
            GlobalVariables.selected_specie = str(selected_idx)
            equation = self.equation_input.value.strip()
            stoichiometry_calc = stoichiometry_bare_bone.Stoichiometry(
                chemical_equation=equation
            )
            stoichiometry_calc.balance_equation()
            stoichiometry_calc.calc_species_molar_weight()

            if moles:
                GlobalVariables.mode = "1"
                input_mole_value = float(moles)
                stoichiometry_calc.calc_ratio()

                for index, ratio in enumerate(GlobalVariables.ratios):
                    if index < len(self.stoichiometry_data["gram_inputs"]):
                        calculated_moles = ratio * input_mole_value
                        calculated_grams = (
                            calculated_moles
                            * self.stoichiometry_data["total_molar_weights"][index]
                        )

                        # Use format_value for proper formatting
                        self.stoichiometry_data["gram_inputs"][index].value = (
                            self.format_value(calculated_grams)
                        )
                        self.stoichiometry_data["mole_inputs"][index].value = (
                            self.format_value(calculated_moles)
                        )

            elif grams:
                GlobalVariables.mode = "2"
                input_gram_value = float(grams)

                selected_chemical = self.stoichiometry_data["all_compounds"][
                    selected_idx
                ]
                # Use the stored molar weight for consistency
                molar_weight = self.stoichiometry_data["total_molar_weights"][
                    selected_idx
                ]
                input_mole_value = input_gram_value / molar_weight

                stoichiometry_calc.calc_ratio()

                for index, ratio in enumerate(GlobalVariables.ratios):
                    if index < len(self.stoichiometry_data["gram_inputs"]):
                        calculated_moles = ratio * input_mole_value
                        calculated_grams = (
                            calculated_moles
                            * self.stoichiometry_data["total_molar_weights"][index]
                        )

                        # Use format_value for proper formatting
                        self.stoichiometry_data["gram_inputs"][index].value = (
                            self.format_value(calculated_grams)
                        )
                        self.stoichiometry_data["mole_inputs"][index].value = (
                            self.format_value(calculated_moles)
                        )

            # Update result
            compound_name = self.stoichiometry_data["all_compounds"][selected_idx]
            self.stoich_result_text.value = (
                f"✓ Calculated stoichiometry for {compound_name}"
            )
            self.stoich_result_text.color = ft.colors.GREEN

        except Exception as ex:
            self.stoich_result_text.value = f"Error: {str(ex)}"
            self.stoich_result_text.color = ft.colors.RED

        self.page.update()

    def clear_stoichiometry(self, e=None):
        """Clear all stoichiometry inputs"""
        # Clear all inputs
        for gram_input in self.stoichiometry_data["gram_inputs"]:
            gram_input.value = ""
            gram_input.disabled = True
            gram_input.border_color = ft.colors.GREY_400

        for mole_input in self.stoichiometry_data["mole_inputs"]:
            mole_input.value = ""
            mole_input.disabled = True
            mole_input.border_color = ft.colors.GREY_400

        # Clear checkboxes
        for checkbox in self.stoichiometry_data["radio_buttons"]:
            checkbox.value = False

        # Reset selected index
        self.stoichiometry_data["selected_index"] = None

        # Reset result
        self.stoich_result_text.value = (
            "Select a compound and enter values to calculate"
        )
        self.stoich_result_text.color = ft.colors.GREY_600

        # Hide grid
        self.scrollable_grid_container.visible = False
        self.page.update()


def main(page: ft.Page):
    ChemicalApp(page)


if __name__ == "__main__":
    ft.app(target=main)
