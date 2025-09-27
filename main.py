import ifcopenshell

from external.BIMANALYST_G_4.rules import FacadeTransparency
from external.openBIM2025_GRP2.rules import alisaRule

model = ifcopenshell.open(
    r"C:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\AdvancedBIM_ARCH\model\25-16-D-ARCH.ifc"
)

rules = {
    "1": ("Facade Transparency Rule", FacadeTransparency.checkRule),
    "2": ("Classification Rule", alisaRule.checkRule)
}

print("Vælg hvilken rule du vil køre:")
for key, (name, _) in rules.items():
    print(f"{key}: {name}")

valg = input("Indtast nummeret på den ønskede rule: ")

if valg in rules:
    rule_name, rule_func = rules[valg]
    result = rule_func(model)
    print(f"{rule_name} result:", result)
else:
    print("Ugyldigt valg.")
