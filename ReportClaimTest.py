# This Script analyses a claim made in a report and verifies its validity.

import ifcopenshell
import os

# Amount of levels in the building:

def count_building_storeys(ifc_path):
    model = ifcopenshell.open(ifc_path)
    storeys = model.by_type("IfcBuildingStorey")
    over_ground = 0
    under_ground = 0

    print(f"Antal building storeys: {len(storeys)}")

    if len(storeys) == 6:
        print("Claim is correct: The building has 6 storeys.")
    else:
        print("Claim is incorrect: The building does not have 6 storeys.")

    for storey in storeys:
        elevation = getattr(storey, 'Elevation', None)
        print(f"Storey #{storey.id()} - Name: {storey.Name}, Elevation: {elevation if elevation is not None else 'Ukendt'}")
        if elevation is not None:
            if elevation < 0:
                under_ground += 1
            else:
                over_ground += 1
        else:
            print(f"Warning: Elevation not assigned to {storey.Name}")

    print(f"Amount of floors above ground: {over_ground}")
    print(f"Amount of floors below ground: {under_ground}")
    print(f"Total amount of floors: {len(storeys)}")
    return len(storeys), over_ground, under_ground

# Reading environmental data on materials if available:

def check_material_environmental_data(ifc_path):
    model = ifcopenshell.open(ifc_path)
    found = False
    for material in model.by_type("IfcMaterial"):
        if hasattr(material, "HasProperties"):
            for prop_set in material.HasProperties:
                if prop_set.is_a("IfcPropertySet"):
                    for prop in prop_set.HasProperties:
                        # Look for environmentally relevant properties
                        if any(keyword in prop.Name.lower() for keyword in ["co2", "gwp", "epd", "environment", "miljø", "carbon"]):
                            print(f"Material: {material.Name} - Property: {prop.Name} - Value: {getattr(prop, 'NominalValue', '')}")
                            found = True
    if not found:
        print("No environmental data found on materials.")

if __name__ == "__main__":
    # Find IFC file in 'model' folder
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    ifc_files = [f for f in os.listdir(model_dir) if f.lower().endswith(".ifc")]
    if not ifc_files:
        print("No IFC file found in the 'model' folder.")
        exit(1)
    ifc_path = os.path.join(model_dir, ifc_files[0])

    print("Select the claim you want to check:")
    print("1: Number of storeys")
    print("2: Environmental data on materials")
    choice = input("Enter number (1-2): ")

    if choice == "1":
        count_building_storeys(ifc_path)
    elif choice == "2":
        check_material_environmental_data(ifc_path)
    else:
        print("Invalid choice.")