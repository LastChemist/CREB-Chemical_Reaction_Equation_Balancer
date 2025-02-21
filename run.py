from plugins.stoichiometry import UI, Stoichiometry


# chemicals = ["A", "B", "=", "C", "D"]
# field_names = ["Chemical Formula"] + chemicals
# weights = ["weights", 14, 2, "***", 45, 12]
# moles = ["Moles", 0.1, 2, "***", 0.8, 0.3]

st = Stoichiometry(chemical_equation="H2SO4 + KOH = K2SO4 + H2O")
# st.calc_ratio()
st.calc_species_molar_weight()
ui = UI()
# print(obj.create_table(field_names=field_names, rows=[weights, moles]))
# table(table_field_names=field_names, rows=[weights, moles])

ui.display_reaction_table()
