import flet as ft
from Core import CREB
from plugins import stoi2
from plugins.stoichiometery_bare_bone import GlobalVariables
import pyperclip
import threading
import time


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

        # Sidebar states
        self.left_sidebar_open = False
        self.right_sidebar_open = False

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
        # Create main content
        main_content = self.create_main_content()

        # Create layout
        self.layout = ft.Row(
            [
                main_content,
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        # Add to page
        self.page.add(self.layout)

        # Set initial focus
        if hasattr(self, "equation_input"):
            self.equation_input.focus()

    def create_main_content(self):
        """Create the main content area"""
        # Header
        self.header = self.create_header()

        # Create tabs
        self.tabs = self.create_tabs()

        return ft.Container(
            content=ft.Column(
                [
                    self.header,
                    self.tabs,
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
        # Create balancer tab
        balancer_tab = self.create_balancer_tab()

        # Create stoichiometry tab
        stoichiometry_tab = self.create_stoichiometry_tab()

        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Reaction Balancer",
                    icon=ft.icons.BALANCE,
                    content=balancer_tab,
                ),
                ft.Tab(
                    text="Stoichiometry Calculator",
                    icon=ft.icons.CALCULATE,
                    content=stoichiometry_tab,
                ),
            ],
            expand=1,
        )

    def create_balancer_tab(self):
        """Create the reaction balancer tab"""
        # Input field - now multiline for long equations
        self.equation_input = ft.TextField(
            label="Enter Chemical Equation",
            hint_text="Example: H2 + O2 -> H2O\nFor long equations, use the equation viewer after balancing",
            width=900,
            text_size=16,
            border_color=ft.colors.BLUE_400,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            multiline=True,
            min_lines=2,
            max_lines=4,
            prefix_icon=ft.icons.TELEGRAM,
        )

        # Buttons
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

        self.clear_balance_button = ft.OutlinedButton(
            "Clear",
            icon=ft.icons.CLEAR,
            on_click=self.clear_all_balancer,
        )

        # Output container
        self.output_container = ft.Container(
            padding=20,
            border_radius=10,
            border=ft.border.all(2, ft.colors.GREEN_200),
            bgcolor=ft.colors.GREEN_50,
            visible=False,
        )

        self.output_title = ft.Text(
            "Balanced Equation",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.GREEN_800,
        )
        self.balanced_equation_text = ft.Text(
            "", size=20, selectable=True, weight=ft.FontWeight.BOLD
        )

        # Create copy button for balanced equation
        self.copy_equation_button = ft.IconButton(
            icon=ft.icons.COPY,
            icon_size=20,
            tooltip="Copy balanced equation",
            on_click=lambda e: self.copy_to_clipboard(
                self.balanced_equation_text.value, "Balanced equation copied!"
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.TRANSPARENT,
            ),
        )

        self.coefficients_text = ft.Text("", size=16, color=ft.colors.GREY_700)

        # Create copy button for coefficients
        self.copy_coefficients_button = ft.IconButton(
            icon=ft.icons.COPY,
            icon_size=20,
            tooltip="Copy coefficients",
            on_click=lambda e: self.copy_to_clipboard(
                self.coefficients_text.value, "Coefficients copied!"
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.TRANSPARENT,
            ),
        )

        # Equation viewer button for long equations
        self.view_full_equation_button = ft.ElevatedButton(
            "View Full Equation",
            icon=ft.icons.OPEN_IN_FULL,
            on_click=self.show_full_equation_viewer,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                bgcolor=ft.colors.BLUE_50,
                color=ft.colors.BLUE,
            ),
        )

        self.output_container.content = ft.Column(
            [
                self.output_title,
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                # Row with balanced equation and copy button
                ft.Row(
                    [
                        ft.Container(
                            content=self.balanced_equation_text,
                            expand=True,
                        ),
                        self.copy_equation_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=5),
                # Row with coefficients and copy button
                ft.Row(
                    [
                        ft.Container(
                            content=self.coefficients_text,
                            expand=True,
                        ),
                        self.copy_coefficients_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=10),
                ft.Row(
                    [self.view_full_equation_button],
                    alignment=ft.MainAxisAlignment.CENTER,
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
        example_buttons = [
            ("H2 + O2 → H2O", "H2 + O2 -> H2O"),
            ("CH4 + O2 → CO2 + H2O", "CH4 + O2 -> CO2 + H2O"),
            ("Fe + O2 → Fe2O3", "Fe + O2 -> Fe2O3"),
            ("NaOH + H2SO4 = Na2SO4 + H2O", "NaOH + H2SO4 = Na2SO4 + H2O"),
            (
                "Complex Equation",
                "K4Fe(CN)6 + KMnO4 + H2SO4 = Fe2(SO4)3 + MnSO4 + KNO3 + CO2 + K2SO4 + H2O",
            ),
        ]

        # Create rows of buttons (3 per row)
        example_rows = []
        for i in range(0, len(example_buttons), 3):
            row_buttons = []
            for j in range(3):
                if i + j < len(example_buttons):
                    text, eq = example_buttons[i + j]
                    row_buttons.append(
                        ft.TextButton(
                            text,
                            on_click=lambda e, eq=eq: self.load_example(eq),
                        )
                    )
            if row_buttons:
                example_rows.append(
                    ft.Row(
                        row_buttons,
                        spacing=20,
                    )
                )

        self.examples_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Try these examples:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Column(
                        example_rows,
                        spacing=10,
                    ),
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
                    ft.Divider(height=20),
                    self.equation_input,
                    ft.Row(
                        [self.balance_button, self.clear_balance_button], spacing=20
                    ),
                    ft.Divider(height=10),
                    self.copy_status_text,
                    ft.Divider(height=30),
                    self.output_container,
                    ft.Divider(height=10),
                    self.error_container,
                    ft.Divider(height=30),
                    self.examples_container,
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        )

    def create_stoichiometry_tab(self):
        """Create the stoichiometry calculator tab"""
        # Equation display
        self.stoich_equation_text = ft.Text(
            "Balance an equation first to use stoichiometry calculator",
            size=14,
            color=ft.colors.GREY_600,
        )

        # Create a scrollable container for the grid
        self.scrollable_grid_container = ft.Container(
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=12,
            padding=20,
            bgcolor=ft.colors.WHITE,
            visible=False,
            height=350,  # Fixed height for scrolling
        )

        # Result text
        self.stoich_result_text = ft.Text("", size=14, color=ft.colors.GREY_600)

        # Table viewer button
        self.view_full_table_button = ft.ElevatedButton(
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
                        [self.view_full_table_button],
                        alignment=ft.MainAxisAlignment.CENTER,
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

        # Clear message after 2 seconds
        def clear_message():
            time.sleep(2)
            self.copy_status_text.value = ""
            self.page.update()

        threading.Thread(target=clear_message, daemon=True).start()

    def show_full_equation_viewer(self, e=None):
        """Show a dialog with the full equation"""
        if not self.balanced_equation_text.value:
            return

        # Create a dialog with scrollable content
        equation_dialog = ft.AlertDialog(
            title=ft.Text("Full Equation Viewer"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Original Equation:", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            self.equation_input.value,
                            size=16,
                            selectable=True,
                            overflow=ft.TextOverflow.VISIBLE,
                        ),
                        ft.Divider(height=20),
                        ft.Text("Balanced Equation:", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            self.balanced_equation_text.value,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            selectable=True,
                            overflow=ft.TextOverflow.VISIBLE,
                        ),
                        ft.Divider(height=20),
                        ft.Text("Coefficients:", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            self.coefficients_text.value,
                            size=14,
                            selectable=True,
                            overflow=ft.TextOverflow.VISIBLE,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                ),
                width=700,
            ),
            actions=[
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Copy Equation",
                            icon=ft.icons.COPY,
                            on_click=lambda e: self.copy_to_clipboard(
                                self.balanced_equation_text.value,
                                "Full equation copied!",
                            ),
                        ),
                        ft.OutlinedButton(
                            "Close",
                            on_click=lambda e: self.close_dialog(equation_dialog),
                        ),
                    ],
                    spacing=20,
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = equation_dialog
        equation_dialog.open = True
        self.page.update()

    def show_full_table_viewer(self, e=None):
        """Show a dialog with the full stoichiometry table"""
        if not self.stoichiometry_data.get("all_compounds"):
            self.stoich_result_text.value = "Please load a balanced equation first"
            self.stoich_result_text.color = ft.colors.RED
            self.page.update()
            return

        # Build full table
        table_content = self.build_full_stoichiometry_table()

        # Create a dialog with scrollable content
        table_dialog = ft.AlertDialog(
            title=ft.Text("Full Stoichiometry Table"),
            content=ft.Container(
                content=table_content,
                width=900,
                height=500,
            ),
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
        """Build a detailed stoichiometry table for the viewer"""
        compounds = self.stoichiometry_data["all_compounds"]
        molar_weights = self.stoichiometry_data["total_molar_weights"]

        if not compounds:
            return ft.Text("No data available", color=ft.colors.GREY_600)

        # Create a scrollable table
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

        # Data rows
        num_reactants = len(self.stoichiometry_data.get("reactants", []))

        for i, (compound, mw) in enumerate(zip(compounds, molar_weights)):
            grams = (
                self.stoichiometry_data["gram_inputs"][i].value
                if i < len(self.stoichiometry_data["gram_inputs"])
                else ""
            )
            moles = (
                self.stoichiometry_data["mole_inputs"][i].value
                if i < len(self.stoichiometry_data["mole_inputs"])
                else ""
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
                        ft.DataCell(ft.Text(f"{mw:.3f}", size=14)),
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
        """Export table data to clipboard"""
        compounds = self.stoichiometry_data["all_compounds"]
        molar_weights = self.stoichiometry_data["total_molar_weights"]

        if not compounds:
            return

        # Build CSV-like text
        text = "Compound,Molar Weight (g/mol),Grams (g),Moles (mol),Type\n"

        num_reactants = len(self.stoichiometry_data.get("reactants", []))

        for i, (compound, mw) in enumerate(zip(compounds, molar_weights)):
            grams = (
                self.stoichiometry_data["gram_inputs"][i].value
                if i < len(self.stoichiometry_data["gram_inputs"])
                else ""
            )
            moles = (
                self.stoichiometry_data["mole_inputs"][i].value
                if i < len(self.stoichiometry_data["mole_inputs"])
                else ""
            )
            compound_type = "Reactant" if i < num_reactants else "Product"

            text += f'{compound},{mw:.3f},{grams or ""},{moles or ""},{compound_type}\n'

        self.copy_to_clipboard(text, "Table data copied to clipboard!")

    def close_dialog(self, dialog):
        """Close a dialog"""
        dialog.open = False
        self.page.update()

    # ===== BALANCER METHODS =====

    def load_example(self, equation: str):
        """Load an example equation"""
        self.equation_input.value = equation
        self.page.update()

    def clear_all_balancer(self, e=None):
        """Clear all inputs and outputs in balancer"""
        self.equation_input.value = ""
        self.output_container.visible = False
        self.error_container.visible = False
        self.copy_status_text.value = ""
        self.page.update()

    def show_error(self, message: str):
        """Display error message"""
        self.error_text.value = message
        self.error_container.visible = True
        self.output_container.visible = False
        self.page.update()

    def show_result(self, balanced_eq: str, coefficients: dict = None):
        """Display the balancing result"""
        self.balanced_equation_text.value = balanced_eq

        if coefficients:
            coeff_text = "Coefficients: "
            for formula, coeff in coefficients.items():
                coeff_text += f"{formula}: {coeff}, "
            self.coefficients_text.value = coeff_text.rstrip(", ")
        else:
            self.coefficients_text.value = ""

        self.output_container.visible = True
        self.error_container.visible = False
        self.page.update()

    def balance_equation(self, e=None):
        """Main balancing function"""
        equation = self.equation_input.value.strip()

        if not equation:
            self.show_error("Please enter a chemical equation")
            return

        try:
            creb = CREB
            balanced_equation = creb.balance(input_chemical_equation=equation)

            x = creb.Rewriter()
            x.executeRewriter(chemical_equation=equation)

            self.show_result(
                balanced_eq=balanced_equation, coefficients=x.chemical_formulas_dict
            )

            # Update stoichiometry tab with this equation
            self.stoich_equation_text.value = f"Balanced Equation: {balanced_equation}"
            self.page.update()

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    # ===== STOICHIOMETRY METHODS =====

    def create_copy_button(self, text_field, value_type):
        """Create a copy button for a text field"""
        return ft.IconButton(
            icon=ft.icons.COPY,
            icon_size=16,
            tooltip=f"Copy {value_type} value",
            on_click=lambda e: self.copy_text_field(text_field, value_type),
            style=ft.ButtonStyle(
                padding=ft.padding.all(2),
                bgcolor=ft.colors.TRANSPARENT,
            ),
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
        """Build the stoichiometry grid with copy buttons - now scrollable"""
        total_compounds = len(reactants) + len(products)

        # Clear previous data
        self.stoichiometry_data["gram_inputs"] = []
        self.stoichiometry_data["mole_inputs"] = []
        self.stoichiometry_data["radio_buttons"] = []
        self.stoichiometry_data["all_compounds"] = reactants + products
        self.stoichiometry_data["total_molar_weights"] = (
            molar_weights_reactants + molar_weights_products
        )

        # Calculate total width needed
        total_width = 120 + (140 * total_compounds) + 50

        # Create a scrollable container for the grid
        grid_container = ft.Container(
            width=total_width,
            height=300,
        )

        grid = ft.Column(spacing=15)

        # Header
        header = ft.Row(
            [
                ft.Container(width=120),  # Wider for "Select" label
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
                                    f"{mw:.3f} g/mol", size=11, color=ft.colors.GREY_600
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
                    content=ft.Text("→", size=20, weight=ft.FontWeight.BOLD),
                    width=50,
                    alignment=ft.alignment.center,
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
                                    f"{mw:.3f} g/mol", size=11, color=ft.colors.GREY_600
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
            radio = ft.Checkbox(
                on_change=lambda e, idx=i: self.on_checkbox_changed(e, idx)
            )
            self.stoichiometry_data["radio_buttons"].append(radio)

            container = ft.Container(
                content=radio, width=140, alignment=ft.alignment.center
            )

            if i < len(reactants):
                radio_row.controls.append(container)
            elif i == len(reactants):
                # Add arrow column
                radio_row.controls.append(ft.Container(width=50))
                radio_row.controls.append(container)
            else:
                radio_row.controls.append(container)

        grid.controls.append(radio_row)

        # Grams row
        grams_row = ft.Row(
            [
                ft.Container(
                    content=ft.Text("Grams (g):", weight=ft.FontWeight.BOLD, size=12),
                    width=120,
                    alignment=ft.alignment.center_right,
                    padding=ft.padding.only(right=10),
                )
            ]
        )

        for i in range(total_compounds):
            # Create input field
            gram_input = ft.TextField(
                width=100,
                height=35,
                text_size=12,
                disabled=True,
                border_color=ft.colors.GREY_400,
                hint_text="0.0",
                content_padding=8,
                border_radius=5,
            )
            self.stoichiometry_data["gram_inputs"].append(gram_input)

            # Create copy button
            gram_copy_button = self.create_copy_button(gram_input, "grams")

            # Create container with input and copy button
            input_container = ft.Column(
                [
                    ft.Row(
                        [
                            gram_input,
                            ft.Container(
                                content=gram_copy_button,
                                alignment=ft.alignment.center_right,
                                expand=True,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            container = ft.Container(
                content=input_container, width=140, alignment=ft.alignment.center
            )

            if i < len(reactants):
                grams_row.controls.append(container)
            elif i == len(reactants):
                grams_row.controls.append(ft.Container(width=50))
                grams_row.controls.append(container)
            else:
                grams_row.controls.append(container)

        grid.controls.append(grams_row)

        # Moles row
        moles_row = ft.Row(
            [
                ft.Container(
                    content=ft.Text("Moles (mol):", weight=ft.FontWeight.BOLD, size=12),
                    width=120,
                    alignment=ft.alignment.center_right,
                    padding=ft.padding.only(right=10),
                )
            ]
        )

        for i in range(total_compounds):
            # Create input field
            mole_input = ft.TextField(
                width=100,
                height=35,
                text_size=12,
                disabled=True,
                border_color=ft.colors.GREY_400,
                hint_text="0.0",
                content_padding=8,
                border_radius=5,
            )
            self.stoichiometry_data["mole_inputs"].append(mole_input)

            # Create copy button
            mole_copy_button = self.create_copy_button(mole_input, "moles")

            # Create container with input and copy button
            input_container = ft.Column(
                [
                    ft.Row(
                        [
                            mole_input,
                            ft.Container(
                                content=mole_copy_button,
                                alignment=ft.alignment.center_right,
                                expand=True,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            container = ft.Container(
                content=input_container, width=140, alignment=ft.alignment.center
            )

            if i < len(reactants):
                moles_row.controls.append(container)
            elif i == len(reactants):
                moles_row.controls.append(ft.Container(width=50))
                moles_row.controls.append(container)
            else:
                moles_row.controls.append(container)

        grid.controls.append(moles_row)

        # Add grid to scrollable container
        grid_container.content = ft.Row(
            [grid],
            scroll=ft.ScrollMode.AUTO,
        )

        return grid_container

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
                # Clear other inputs
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
            creb = CREB

            x = creb.Rewriter()
            x.executeRewriter(chemical_equation=equation)

            y = stoi2.Stoichiometry(chemical_equation=equation)
            y.balance_equation()
            y.calc_species_molar_weight()

            reactants = x.reactants_list
            products = x.products_list

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
        """Calculate stoichiometry"""
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

            # Reinitialize stoichiometry with current equation
            equation = self.equation_input.value.strip()
            y = stoi2.Stoichiometry(chemical_equation=equation)
            y.balance_equation()
            y.calc_species_molar_weight()

            if moles:
                # Mole mode
                GlobalVariables.mode = "1"
                input_mole_value = float(moles)

                # Calculate ratios
                y.calc_ratio()

                # Calculate all values
                for index, ratio in enumerate(GlobalVariables.ratios):
                    if index < len(self.stoichiometry_data["gram_inputs"]):
                        calculated_moles = round(ratio * input_mole_value, 3)
                        calculated_grams = round(
                            ratio
                            * input_mole_value
                            * self.stoichiometry_data["total_molar_weights"][index],
                            3,
                        )

                        # Update input fields
                        self.stoichiometry_data["gram_inputs"][index].value = str(
                            calculated_grams
                        )
                        self.stoichiometry_data["mole_inputs"][index].value = str(
                            calculated_moles
                        )

            elif grams:
                # Gram mode
                GlobalVariables.mode = "2"
                input_gram_value = float(grams)

                # Calculate moles from grams
                selected_chemical = self.stoichiometry_data["all_compounds"][
                    selected_idx
                ]
                molar_weight = y.calc_molar_weight(chemical_formula=selected_chemical)
                input_mole_value = input_gram_value / molar_weight

                # Calculate ratios
                y.calc_ratio()

                # Calculate all values
                for index, ratio in enumerate(GlobalVariables.ratios):
                    if index < len(self.stoichiometry_data["gram_inputs"]):
                        calculated_moles = round(ratio * input_mole_value, 3)
                        calculated_grams = round(
                            ratio
                            * input_mole_value
                            * self.stoichiometry_data["total_molar_weights"][index],
                            3,
                        )

                        # Update input fields
                        self.stoichiometry_data["gram_inputs"][index].value = str(
                            calculated_grams
                        )
                        self.stoichiometry_data["mole_inputs"][index].value = str(
                            calculated_moles
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
    # Create the app instance
    app = ChemicalApp(page)


# Run the app
if __name__ == "__main__":
    ft.app(target=main)
