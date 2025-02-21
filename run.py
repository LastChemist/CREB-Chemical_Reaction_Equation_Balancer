from plugins.stoichiometry import UI, Stoichiometry

st = Stoichiometry(chemical_equation="H2SO4 + KOH = K2SO4 + H2O")
st.calc_species_molar_weight()
ui = UI()
ui.display_reaction_table()
ui.specie_selection()
ui.mode_selection()
ui.get_species_value()
ui.display_output_table()
