# BIMmanager group 01

# Link to repository 
https://github.com/NicolaiVoldstedlund/BIMmanager_g_01

# Focus Area 
Architecture

# Claims

Checking various claims made on page 3 in the report: 25-16-D-ARCH.pdf 
    Claim 1: Facade transparency is 57%
    Claim 2: Elements have a classification system
    Claim 3: Amount of levels is 6

# Summary of scrips

## Managers main script

This script is a simple command-line tool for running BIM model checks using different rule modules.
It loads an IFC model and presents a menu, allowing the user to select which rule to run.
Each rule analyzes the model in a specific way (e.g., facade transparency, classification, or storey count) and prints the result.

How it works:
Loads the IFC model from a specified path.
Imports rule modules for different types of checks.
Displays a menu for the user to choose a rule.
Runs the selected rule on the model and prints the result.

Purpose:
To make it easy to run and compare different BIM analysis rules on the same model from a single script.

Link to repository: https://github.com/NicolaiVoldstedlund/BIMmanager_g_01 

## Script 1 - Facade Transparency

This script analyzes the transparency of the building facade in the IFC model.
It calculates the total facade surface area and the total window area, then computes the average transparency percentage.
The script is designed to verify claims about facade transparency and outputs a summary of the results.

How it works:

Receives the IFC model as input.
Identifies external walls and windows.
Calculates areas based on IFC properties.
Computes and prints the facade transparency percentage.

Purpose:
To check and validate claims about the building’s facade transparency in a BIM model.

Link to repository: https://github.com/LisannePut/BIMANALYST_G_4

## Script 2 - Classification Rule

This script checks whether elements in the IFC model have classification references.
It counts the number of elements with and without classification systems and provides a summary.

How it works:

Receives the IFC model as input.
Iterates through all elements in the model.
Checks for classification references using IFC utilities.
Prints the count of classified and unclassified elements.

Purpose:
To verify that elements in the BIM model are properly classified according to a system.

Link to repository: https://github.com/aalisa0/openBIM2025_GRP2

## Script 3 - Storey Rule  

This script analyzes the number of building storeys in the IFC model.
It counts total storeys, distinguishes between above and below ground levels, and checks if the number matches a specific claim.

How it works:

Receives the IFC model as input.
Identifies all building storeys.
Determines elevation to classify storeys as above or below ground.
Prints a summary and verifies the claim about the number of levels.

Purpose:
To validate claims about the number of storeys in the BIM model and provide detailed storey information.

Link to repository: https://github.com/NicolaiVoldstedlund/BIManalyst_g_01