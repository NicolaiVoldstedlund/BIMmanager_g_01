import ifcopenshell

from external.BIMANALYST_G_4.rules import FacadeTransparency
from external.openBIM2025_GRP2.rules import alisaRule
from external.BIManalyst_g_01.rules import StoreyRule

model = ifcopenshell.open(
    r"C:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\AdvancedBIM_ARCH\model\25-16-D-ARCH.ifc"
)

rules = {
    "1": ("Facade Transparency Rule", FacadeTransparency.checkRule),
    "2": ("Classification Rule", alisaRule.checkRule), 
    "3": ("Storey Rule", StoreyRule.checkRule)
}

print("Select which rule you want to run:")
for key, (name, _) in rules.items():
    print(f"{key}: {name}")

choice = input("Enter the number of the desired rule: ")

if choice in rules:
    rule_name, rule_func = rules[choice]
    result = rule_func(model)
    print(f"{rule_name} result:", result)
else:
    print("Invalid choice.")
