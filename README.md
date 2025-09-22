# BIMmanager group 01

# Link to repository: https://github.com/NicolaiVoldstedlund/AdvancedBIM_ARCH_GR01_Manager

# Focus Area: ARCHITECTURE

# Checking if some of the claims made on page 3 coincides with the ifc model. 

# Script explanation:

# This script analyzes and verifies specific claims about a building model described in an IFC file (25-16-D-ARCH.ifc).
# It provides a simple menu where you can choose which claim to check. The script includes two main functions:

# count_building_storeys:
# Counts all building storeys (IfcBuildingStorey), prints their names and elevations, checks if the building has exactly 6 storeys, and reports how   many are above or below ground (based on elevation).

# check_material_environmental_data:
# Searches all materials (IfcMaterial) for environmental data properties (like CO₂, GWP, EPD, etc.) and prints them if found.

# When you run the script, you are prompted to select which claim to check, and only the relevant function is executed. This makes it easy to verify specific aspects of the building model as described in a report.
