# A3 - Manager

---

## About the Tool

### Problem / Claim
The tool addresses the problem of ensuring safe and compliant access to evacuation routes in building designs. Specifically, it checks whether the arrangement of desks obstructs evacuation routes, which is critical for occupant safety during emergencies. This problem is derived from the BR18 regulations, which mandate that evacuation routes must be accessible, unobstructed, and appropriately dimensioned based on the number of occupants in the building.

### Description of the Tool
The tool is a custom Python script utilizing IfcOpenShell to automatically analyze evacuation route accessibility and desk arrangements within IFC models. It integrates data from various analyst scripts to validate compliance with fire safety regulations, producing a clear compliance report for stakeholders.

### Instructions to Run the Tool

Prerequisites
- Python 3.8 or newer
- (Optional) matplotlib — required only for generating the PASS/FAIL PNG chart

Recommended quick setup (Windows, PowerShell)
1. Open a terminal and change to the repository root:
   ```
   cd "c:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\BIMmanager_g_01"
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```

3. Install matplotlib if you want the PNG chart output:
   ```
   pip install matplotlib
   ```

Run the script
- Execute the manager that generates the reports and optional chart:
  ```
  python A3\main.py
  ```

What the script produces
- Text report: A3/reports/spaces_accessibility_allspaces_<timestamp>.txt
- JSON summary:  A3/reports/spaces_accessibility_allspaces_<timestamp>.json
- Optional PNG chart: A3/reports/spaces_accessibility_chart_<timestamp>.png (created if matplotlib is installed)

Inputs
- The script reads these files by default:
  - A3/Analyst script results/A3_analyst_checks_GRP2.txt
  - A3/Analyst script results/analysis_summary_20251127_135907.txt
- Adjust the input paths in `A3/main.py` constants near the top if needed.

Configuration
- Per-space requirement (BR18): DOOR_CM_PER_DESK (default 1.0 cm/desk)
- Building-level requirement (BR18): BR18_CM_PER_OCCUPANT (default 1.0 cm/person)
- Edit these constants in `A3/main.py` to change the rules.

Notes
- If matplotlib is not available, the script still creates the text and JSON reports and adds a warning indicating chart generation was skipped.
- The generated JSON includes totals, per-space details and the chart path (or null when the chart is not created).
```// filepath: c:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\BIMmanager_g_01\A3\README.md

## Running the A3 Manager script

Prerequisites
- Python 3.8 or newer
- (Optional) matplotlib — required only for generating the PASS/FAIL PNG chart

Recommended quick setup (Windows, PowerShell)
1. Open a terminal and change to the repository root:
   ```
   cd "c:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\BIMmanager_g_01"
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```

3. Install matplotlib if you want the PNG chart output:
   ```
   pip install matplotlib
   ```

Run the script
- Execute the manager that generates the reports and optional chart:
  ```
  python A3\main.py
  ```

---

## Advanced Building Design

### Building Design Stage
This tool is particularly useful in **Stage C** (Detailed Design) of the Advanced Building Design process, where the arrangement of spaces and furniture is finalized.

### Subjects That Might Use It
- Architects
- Building Managers
- Safety Consultants
- Regulatory Compliance Officers

### Required Information in the Model
For the tool to function effectively, the following information must be present in the IFC model:
- Desk locations and quantities
- Evacuation route elements (corridors, doors, stairs, spaces, walls)
- Spatial relationships between desks and evacuation routes