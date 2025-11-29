# A3 - Manager

---

## About the Tool

### Problem / Claim
The tool addresses the problem of ensuring safe and compliant access to evacuation routes in building designs. Specifically, it checks whether the arrangement of desks obstructs evacuation routes, which is critical for occupant safety during emergencies. This problem is derived from the BR18 regulations, which mandate that evacuation routes must be accessible, unobstructed, and appropriately dimensioned based on the number of occupants in the building.

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

## IDS — Information Delivery Specification for the tool

PURPOSE
- Define the exact model content, properties and units required so the A3 script can run reliably and produce valid textual analyst outputs.

SCOPE
- IFC objects and properties used to count desks/occupants, measure door widths and map spaces to corridor/stair failure ids.

REQUIRED IFC ENTITIES & PROPERTIES
- IfcSpace
  - Required attributes: GlobalId, Name
  - Required property / quantity (one of):
    - Pset_SpaceOccupancy: OccupantCount (integer)
    - Pset_Space: DeskCount (integer)
    - OR desks represented as IfcFurnishingElement contained by the space (countable)
  - Optional helpful properties: grossFloorArea (m²), Height (m)
- IfcFurnishingElement / IfcFurniture (desks)
  - Must be classified or typed as a Desk/Workstation and connected to IfcSpace via IfcRelContainedInSpatialStructure.
- IfcDoor
  - Required attributes: GlobalId, Name
  - Required property: clear opening width (Length) — prefer Pset_DoorCommon:OverallWidth or explicit OpeningWidth (unit: m)
  - Doors should reference the IfcSpace they serve (containment/connection).
- IfcStair / IfcStairFlight / corridor indicator
  - Must be identifiable by type/classification or name so analysis can map failing element IDs to spaces.

UNITS & TYPES
- Length/width units in IFC: metres (m). Script converts to cm for reporting.
- Area units: square metres (m²).
- Counts: integers >= 0.

EXPORT / TEXT DERIVATION REQUIREMENTS (for the analyst TXT inputs your script consumes)
- If using intermediary text export, ensure the following lines are present per space:
  - "Space : <Title or id>"
  - "No. of desks in this space: <int>"
  - "No. of doors: <int>" (if available)
  - "Total door width: <numeric> cm|mm|m" (units explicit)
  - "Desk to door width ratio: <numeric> cm" (optional)
- analysis_summary must contain failing element IDs under headings "Corridors" and/or "Stair flights" in quoted lists or inline lists:
  - e.g.: Corridors ... Failing element ID's "12345 12346"

VALIDATION RULES (minimum checks before running the script)
- IfcSpace must provide an occupant/desk count OR contain desks that can be counted.
- IfcDoor must provide a numeric width (or be flagged as "width not reported").
- Units must be consistent (lengths in m); exported TXT must annotate units when not in cm.
- All counts and numeric values must be non-negative and numeric parseable.

ACCEPTANCE CRITERIA / LOIN (level of information need)
- Each space has an occupant count or desks that map to occupant count.
- Every door relevant to evacuation routes has a clear opening width property.
- Spaces and circulation elements (corridor/stair) have identifiers or numeric tokens that can be matched to analysis_summary failing IDs.
- If any required values are missing, they must be flagged in the export (script will treat missing widths as "width not reported" and may mark UNKNOWN / PASS/FAIL accordingly).

REMARKS
- Keep property names, classifications and units stable across exports or provide a mapping.  
- This IDS is intended as a minimal contract to ensure the A3 script can run reliably and produce valid text/JSON report and optional chart output.