import ifcopenshell

from external.BIManalyst_g_xy.rules import windowRule
from external.BIManalyst_g_xy.rules import doorRule
# from external.BIManalyst_g_xy.rules import xxxx
# from external.BIManalyst_g_xy.rules import xxxx
# from external.BIManalyst_g_xy.rules import xxxx

model = ifcopenshell.open(r"C:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\AdvancedBIM_ARCH\model\25-16-D-ARCH.ifc")

windowResult = windowRule.checkRule(model)
doorResult = doorRule.checkRule(model)

print("Window result:", windowResult)
print("Door result:", doorResult)
