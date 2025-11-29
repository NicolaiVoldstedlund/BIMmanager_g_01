# A3 - Manager

---

## About the Tool

### Problem / Claim
The tool evaluates whether occupants have good accessibility to the fire route — i.e., whether desk locations, door provision and circulation allow safe and compleiant evacuation in accordance with BR18.

### Description of the Tool
The tool is a custom Python script utilizing IfcOpenShell to automatically analyze evacuation route accessibility and desk arrangements within IFC models. It integrates data from various analyst scripts to validate compliance with fire safety regulations, producing a clear compliance report for stakeholders.

## Instructions to run the tool

Prerequisites
- Python 3.8 or newer
- Optional: matplotlib (only for generating the PNG chart)

Quick start (Windows, PowerShell)
1. Open a terminal and go to the repository root:
    ```
    cd "c:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\BIMmanager_g_01"
    ```
2. Optional: create and activate a virtual environment:
    ```
    python -m venv .venv
    .\.venv\Scripts\Activate
    ```
3. Optional: install matplotlib for chart output:
    ```
    pip install matplotlib
    ```
4. Run the manager:
    ```
    python A3\main.py
    ```

What you get
- Text report: A3/reports/spaces_accessibility_allspaces_<timestamp>.txt
- JSON summary: A3/reports/spaces_accessibility_allspaces_<timestamp>.json
- PNG chart (only if matplotlib is installed): A3/reports/spaces_accessibility_chart_<timestamp>.png

Inputs (defaults)
- A3/Analyst script results/A3_analyst_checks_GRP2.txt
- A3/Analyst script results/analysis_summary_20251127_135907.txt
- If your files differ, update the input paths in A3/main.py (constants near the top).

Configuration
- Per-space door width requirement (BR18): DOOR_CM_PER_DESK (default 1.0 cm per desk)
- Building-level width requirement (BR18): BR18_CM_PER_OCCUPANT (default 1.0 cm per person)
- Edit these constants in A3/main.py to change the rules.

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