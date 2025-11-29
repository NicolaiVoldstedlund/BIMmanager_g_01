"""
================================================================================
ALL-SPACES ACCESSIBILITY TO EVACUATION ROUTE - MANAGER SCRIPT
================================================================================

PURPOSE:

This script evaluates whether occupants in office spaces have adequate access
to fire evacuation routes according to BR18 Danish Building Regulations.

INPUT FILES:

 - A3/Analyst script results/A3_analyst_checks_GRP2.txt
    (Contains desk counts and door measurements per space)
 - A3/Analyst script results/analysis_summary_20251127_135907.txt
    (Contains corridor/stairway accessibility analysis from GRP04)

OUTPUT FILES:

 - A3/reports/spaces_accessibility_allspaces_<timestamp>.txt
    (Human-readable report with per-space verdicts)
 - A3/reports/spaces_accessibility_allspaces_<timestamp>.json
    (Machine-readable JSON with detailed results)

BR18 COMPLIANCE RULES:

 - Per-space rule: Each desk requires 1.0 cm of door width (DOOR_CM_PER_DESK)
 - Building-level rule: Total building requires 1.0 cm per occupant
    (BR18_CM_PER_OCCUPANT)

DECISION LOGIC:

For each space, the script determines a verdict:
 - FAIL: Insufficient door width based on desk count
    → "Occupants DO NOT have necessary access"
 - PASS: Adequate door width AND no failing elements in analysis
    → "Occupants HAVE access"
 - UNKNOWN: Inconclusive data (missing door measurements)
    → "Occupants' access is UNKNOWN"

Additionally, if GRP04 analysis marks related corridors/stairs as failing,
the fire route statement reflects this even if local space data passes.

================================================================================
"""

# ===========================
# IMPORTS
# ===========================

from pathlib import Path
import re
import json
import datetime
from typing import Dict, Any, List, Tuple, Optional

# OPTIONAL IMPORT FOR CHARTS (non-fatal)

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

# ===========================
# CONSTANTS AND PATHS
# ===========================

REPO_ROOT = Path(__file__).resolve().parents[1]
DESK_TXT = REPO_ROOT / "A3" / "Analyst script results" / "A3_analyst_checks_GRP2.txt"
ANALYSIS_SUMMARY_TXT = REPO_ROOT / "A3" / "Analyst script results" / "analysis_summary_20251127_135907.txt"
REPORT_DIR = REPO_ROOT / "A3" / "Results"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================
# BR18 COMPLIANCE PARAMETERS
# ===========================

DOOR_CM_PER_DESK = 1.0       # 1 cm per desk occupant (space-level check)
BR18_CM_PER_OCCUPANT = 1.0   # 1.0 cm per occupant (building-level minimum total door width)

# ===========================
# UTILITY FUNCTIONS
# ===========================

def now_ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="ignore")

# ===========================
# PARSE ANALYSIS_SUMMARY TXT FOR FAILING ELEMENT IDS
# ===========================

def parse_analysis_summary(path: Path) -> Tuple[Dict[str, set], List[str]]:
    warnings: List[str] = []
    result = {"corridor_fail_ids": set(), "stairflight_fail_ids": set()}
    if not path.exists():
        warnings.append(f"analysis_summary not found: {path}")
        return result, warnings

    text = read_text(path)

    # ---------- HELPER: EXTRACT IDS AFTER SECTION ----------
    def extract_ids_after(section_name: str) -> set:
        ids = set()
        pattern = rf"{re.escape(section_name)}.*?Failing element ID's\s*(?:\"([^\"]+)\"|([^\n]+))"
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        block = None
        if m:
            block = (m.group(1) or m.group(2) or "").strip()
        if block:
            found = re.findall(r"\b[0-9]+\b", block)
            for f in found:
                ids.add(f.strip())
        return ids

    try:
        result["corridor_fail_ids"] = extract_ids_after("Corridors")
        result["stairflight_fail_ids"] = extract_ids_after("Stair flights") | extract_ids_after("Stairs")
    except Exception:
        warnings.append("Failed to robustly parse analysis_summary; heuristic extraction used.")

    # ---------- FALLBACK: SCAN QUOTED BLOCKS AND CLASSIFY BY CONTEXT ----------
    if not (result["corridor_fail_ids"] or result["stairflight_fail_ids"]):
        for m in re.finditer(r"\"([^\"]+)\"", text, re.DOTALL):
            block = m.group(1)
            ctx = text[max(0, m.start() - 200): m.start()].lower()
            found = re.findall(r"\b[0-9]+\b", block)
            if found:
                if "corridor" in ctx:
                    result["corridor_fail_ids"].update(found)
                elif "stair" in ctx:
                    result["stairflight_fail_ids"].update(found)
    return result, warnings

# ===========================
# PARSE GRP02 DESK TXT INTO SPACE RECORDS
# ===========================
def split_space_blocks(txt: str) -> List[str]:
    blocks = re.split(r"\n(?=Space\s*:)", txt)
    return [b.strip() for b in blocks if b.strip()]

def parse_space_block(block: str) -> Optional[Dict[str, Any]]:
    first = block.splitlines()[0].strip()
    m = re.match(r"Space\s*:\s*(.+)$", first, re.IGNORECASE)
    if not m:
        return None
    title = m.group(1).strip()
    parts = re.split(r"[:\s]+", title)
    space_id = parts[-1] if parts else title

    def find_int(label: str) -> Optional[int]:
        mm = re.search(rf"{re.escape(label)}\s*:\s*([0-9]+)", block, re.IGNORECASE)
        return int(mm.group(1)) if mm else None

    n_desks = find_int("No. of desks in this space") or 0
    n_doors = find_int("No. of doors")

    total_door = None
    mm = re.search(r"Total door width(?:[^\n:]*):\s*([\d\.,]+)\s*(cm|mm|m)?", block, re.IGNORECASE)
    if mm:
        val = float(mm.group(1).replace(",", "."))
        unit = (mm.group(2) or "cm").lower()
        if unit == "m":
            total_door = val * 100.0
        elif unit == "mm":
            total_door = val / 10.0
        else:
            total_door = val

    ratio = None
    mm2 = re.search(r"Desk to door width ratio\s*:\s*([\d\.,]+)\s*(cm|mm|m)?", block, re.IGNORECASE)
    if mm2:
        val = float(mm2.group(1).replace(",", "."))
        unit = (mm2.group(2) or "cm").lower()
        if unit == "m":
            ratio = val * 100.0
        elif unit == "mm":
            ratio = val / 10.0
        else:
            ratio = val

    floor = None
    mf = re.search(r"Floor\s*:\s*(.+)", block, re.IGNORECASE)
    if mf:
        floor = mf.group(1).strip()

    area = None
    ma = re.search(r"Area\s*:\s*([\d\.,]+)\s*m2", block, re.IGNORECASE)
    if ma:
        area = float(ma.group(1).replace(",", "."))

    height = None
    mh = re.search(r"Height of space\s*:\s*([\d\.,]+)\s*m", block, re.IGNORECASE)
    if mh:
        height = float(mh.group(1).replace(",", "."))

    return {
        "space_id": str(space_id),
        "title": title,
        "n_desks": n_desks,
        "n_doors_reported": n_doors,
        "total_door_width_cm_reported": total_door,
        "desk_to_door_ratio_cm": ratio,
        "area_m2": area,
        "height_m": height,
        "floor": floor,
        "raw": block,
    }

# ===========================
# PARSE SPACES WITH NO DESKS SECTION
# ===========================

def parse_spaces_without_desks(txt: str) -> List[str]:
    out: List[str] = []
    m = re.search(r"={5,}\s*SPACES WITH NO DESKS\s*={5,}([\s\S]+?)(?:={2,}|$)", txt, re.IGNORECASE)
    section = m.group(1) if m else None
    if section:
        for ln in section.splitlines():
            ln = ln.strip()
            if ln.startswith("- "):
                val = ln.lstrip("- ").strip()
                last = val.split()[-1]
                out.append(last.strip())
    return out

# ===========================
# PARSE DESKS NOT IN ANY IFCSPACE SECTION
# ===========================

def parse_desks_not_in_space(txt: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    m = re.search(r"={5,}\s*DESKS NOT IN ANY 'IfcSpace'\s*={5,}([\s\S]+)$", txt, re.IGNORECASE)
    if not m:
        return out
    section = m.group(1)
    for ln in section.splitlines():
        ln = ln.strip()
        if ln.startswith("- "):
            parts = re.split(r"\s*\(\s*GlobalId\s*:\s*", ln, flags=re.IGNORECASE)
            left = parts[0]
            mm = re.search(r"Desk\s*[:\s]*([A-Za-z0-9\-_]+)", left, re.IGNORECASE)
            gid = parts[1].rstrip(")") if len(parts) > 1 else None
            if mm:
                out.append({"desk": mm.group(1), "globalid": gid})
    return out

# ===========================
# DECISION + FIRE-ROUTE STATEMENT
# ===========================

def decide_verdict(space: Dict[str, Any], analysis: Dict[str, set]) -> Tuple[str, List[str], str]:
    """
    Returns (verdict, reasons[], fire_route_statement).
    Final fire_route_statement rules:
     - If base verdict == FAIL -> "Occupants DO NOT have the necessary access..."
     - Else if analysis lists failing element for this space -> "Occupants DO NOT have access..."
     - Else if base verdict == PASS -> "Occupants HAVE access..."
     - Else -> "Occupants' access is UNKNOWN..."
    """
    reasons: List[str] = []
    n = space.get("n_desks") or 0
    sid = str(space.get("space_id") or "")

    if n == 0:
        return "NOT_APPLICABLE", ["No desks in this space"], "Not applicable (no desks)"

    # evaluate local door evidence
    n_doors = space.get("n_doors_reported")
    total_door = space.get("total_door_width_cm_reported")
    if n_doors and n_doors > 0:
        reasons.append(f"Reported number of doors: {n_doors}")
        if total_door is None:
            reasons.append("Door(s) present; width not reported — treat as PASS")
            base_verdict = "PASS"
        else:
            required = n * DOOR_CM_PER_DESK
            if total_door >= required:
                reasons.append(f"Total door width {total_door:.1f} cm >= required {required:.1f} cm (BR18)")
                base_verdict = "PASS"
            else:
                reasons.append(f"Total door width {total_door:.1f} cm < required {required:.1f} cm (BR18)")
                base_verdict = "FAIL"
    else:
        # no door count reported
        if total_door is not None:
            required = n * DOOR_CM_PER_DESK
            if total_door >= required:
                reasons.append(f"Total door width {total_door:.1f} cm >= required {required:.1f} cm (BR18)")
                base_verdict = "PASS"
            else:
                reasons.append(f"Total door width {total_door:.1f} cm < required {required:.1f} cm (BR18)")
                base_verdict = "FAIL"
        elif n_doors == 0:
            reasons.append("Reported 0 doors in space")
            base_verdict = "FAIL"
        else:
            reasons.append("No explicit door/width evidence to decide")
            base_verdict = "UNKNOWN"

    # determine if analysis_summary indicates failing element for this space
    cid_set = analysis.get("corridor_fail_ids", set())
    stf_set = analysis.get("stairflight_fail_ids", set())
    sid_digits = re.findall(r"\b[0-9]+\b", sid)
    check_ids = set(sid_digits) if sid_digits else {sid.strip()}
    analysis_failing = bool(check_ids & (cid_set | stf_set))

    # Compose final natural-language statement
    if base_verdict == "FAIL":
        fire_route_statement = "Occupants DO NOT have the necessary access to the fire route (desk/door data fails BR18)."
    elif analysis_failing:
        fire_route_statement = "Occupants DO NOT have access to the fire route located by GRP04 (related element reported as failing)."
    elif base_verdict == "PASS":
        fire_route_statement = "Occupants HAVE access to the fire route (desk/door data PASS BR18)."
    else:
        fire_route_statement = "Occupants' access to the fire route is UNKNOWN — desk/door data inconclusive and analysis contains no failing entry for this space."

    return base_verdict, reasons, fire_route_statement

# ===========================
# CHART CREATION: PASS/FAIL/UNKNOWN/NOT_APPLICABLE BAR CHART (PNG)
# ===========================

def create_pass_fail_chart(counts: Dict[str, int], out_path: Path) -> Optional[Path]:
    """
    Creates and saves a simple bar chart showing counts for PASS/FAIL/UNKNOWN/NOT_APPLICABLE.
    Returns out_path on success or None if matplotlib not available or error occurred.
    """
    if not MATPLOTLIB_AVAILABLE:
        return None
    labels = []
    values = []
    colors = []
    mapping_colors = {
        "PASS": "#2ca02c", "FAIL": "#d62728", "UNKNOWN": "#ff7f0e", "NOT_APPLICABLE": "#7f7f7f"
    }
    for k in ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"):
        labels.append(k)
        values.append(counts.get(k, 0))
        colors.append(mapping_colors.get(k, "#808080"))
    try:
        plt.figure(figsize=(6,4), dpi=150)
        bars = plt.bar(labels, values, color=colors)
        plt.title("Spaces accessibility verdicts")
        plt.ylabel("Number of spaces")
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, h + 0.5, str(int(h)), ha="center", va="bottom", fontsize=8)
        plt.tight_layout()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception:
        return None

# ===========================
# GENERATE FULL REPORT FOR ALL SPACES
# ===========================

def generate_report_for_all_spaces(txt_path: Path, analysis_path: Path) -> Path:
    raw = read_text(txt_path)
    blocks = split_space_blocks(raw)
    parsed_spaces: Dict[str, Dict[str, Any]] = {}
    warnings: List[str] = []

    for blk in blocks:
        parsed = parse_space_block(blk)
        if parsed:
            parsed_spaces[parsed["space_id"]] = parsed

    # add any explicitly listed "spaces with no desks"
    no_desks_list = parse_spaces_without_desks(raw)
    for sid in no_desks_list:
        if sid not in parsed_spaces:
            parsed_spaces[sid] = {
                "space_id": sid,
                "title": sid,
                "n_desks": 0,
                "n_doors_reported": None,
                "total_door_width_cm_reported": None,
                "desk_to_door_ratio_cm": None,
                "area_m2": None,
                "height_m": None,
                "floor": None,
                "raw": "Listed under SPACES WITH NO DESKS",
            }

    desks_outside = parse_desks_not_in_space(raw)

    analysis, a_warnings = parse_analysis_summary(analysis_path)
    warnings.extend(a_warnings)

    details: List[Dict[str, Any]] = []
    totals = {"spaces_scanned": 0, "spaces_with_desks": 0, "spaces_pass": 0, "spaces_fail": 0, "spaces_unknown": 0, "desks_total": 0, "spaces_not_applicable": 0}

    for sid, info in parsed_spaces.items():
        totals["spaces_scanned"] += 1
        n = info.get("n_desks") or 0
        totals["desks_total"] += n
        if n > 0:
            totals["spaces_with_desks"] += 1

        verdict, reasons, fire_route_statement = decide_verdict(info, analysis)
        if verdict == "PASS":
            totals["spaces_pass"] += 1
        elif verdict == "FAIL":
            totals["spaces_fail"] += 1
        elif verdict == "UNKNOWN":
            totals["spaces_unknown"] += 1
        elif verdict == "NOT_APPLICABLE":
            totals["spaces_not_applicable"] += 1

        details.append({
            "space_id": sid,
            "title": info.get("title"),
            "n_desks": n,
            "n_doors_reported": info.get("n_doors_reported"),
            "total_door_width_cm_reported": info.get("total_door_width_cm_reported"),
            "desk_to_door_ratio_cm": info.get("desk_to_door_ratio_cm"),
            "area_m2": info.get("area_m2"),
            "height_m": info.get("height_m"),
            "floor": info.get("floor"),
            "verdict": verdict,
            "reasons": reasons,
            "fire_route_statement": fire_route_statement,
        })

    details = sorted(details, key=lambda d: str(d["space_id"]))

    # building-level occupants and BR18 minimum total door width
    occupants_total = totals["desks_total"]
    br18_min_total_door_width_cm = round(occupants_total * BR18_CM_PER_OCCUPANT, 1)

    ts = now_ts()
    out_txt = REPORT_DIR / f"spaces_accessibility_allspaces_{ts}.txt"
    out_json = REPORT_DIR / f"spaces_accessibility_allspaces_{ts}.json"

    # write text report
    with out_txt.open("w", encoding="utf-8") as f:
        f.write("All-spaces accessibility to fire route\n")
        f.write(f"Generated: {ts}\n\n")
        f.write(f"Source: {txt_path}\n")
        f.write(f"Reference analysis: {analysis_path}\n\n")
        if warnings:
            f.write("Notes / parsing warnings:\n")
            for w in warnings:
                f.write(f" - {w}\n")
            f.write("\n")

        f.write("=== Summary ===\n")
        f.write(f"Spaces scanned: {totals['spaces_scanned']}\n")
        f.write(f"Spaces with desks: {totals['spaces_with_desks']}\n")
        f.write(f"Total desks (sum): {totals['desks_total']}\n")

        # building-level entries
        f.write(f"Total occupants (based on desks): {occupants_total}\n")
        f.write(f"BR18 minimum total door width required (1.0 cm per occupant): {br18_min_total_door_width_cm:.1f} cm\n")

        f.write(f"PASS: {totals['spaces_pass']}  FAIL: {totals['spaces_fail']}  UNKNOWN: {totals['spaces_unknown']}\n\n")
        f.write("=== Per-space details ===\n")
        for d in details:
            f.write("\n---\n")
            f.write(f"Space: {d['space_id']}  ({d.get('title')})\n")
            f.write(f" Floor: {d['floor']}, Area: {d['area_m2']}, Height: {d['height_m']}\n")
            f.write(f" Desks: {d['n_desks']} | Doors reported: {d['n_doors_reported']} | Total door width (cm): {d['total_door_width_cm_reported']}\n")
            f.write(f" Desk-to-door ratio (cm): {d['desk_to_door_ratio_cm']}\n")
            f.write(f" Verdict: {d['verdict']}\n")
            for r in d['reasons']:
                f.write(f"  - {r}\n")
            f.write(f" Statement: {d.get('fire_route_statement')}\n")

        if desks_outside:
            f.write("\n\n=== Desks not in any IfcSpace (listed) ===\n")
            for item in desks_outside:
                f.write(f" Desk: {item.get('desk')}  GlobalId: {item.get('globalid')}\n")

    # CREATE PASS/FAIL CHART (PNG) AND ADD PATH TO JSON TOTALS (NON-DESTRUCTIVE ADDITION)
    chart_counts = {
        "PASS": totals.get("spaces_pass", 0),
        "FAIL": totals.get("spaces_fail", 0),
        "UNKNOWN": totals.get("spaces_unknown", 0),
        "NOT_APPLICABLE": totals.get("spaces_not_applicable", 0)
    }
    chart_path = REPORT_DIR / f"spaces_accessibility_chart_{ts}.png"
    chart_file = None
    if MATPLOTLIB_AVAILABLE:
        chart_file = create_pass_fail_chart(chart_counts, chart_path)
        if chart_file is None:
            warnings.append("matplotlib available but chart creation failed.")
    else:
        warnings.append("matplotlib not available — skipping chart generation.")

    # update totals for JSON and write
    totals["occupants_total"] = occupants_total
    totals["br18_min_total_door_width_cm"] = br18_min_total_door_width_cm
    totals["chart_path"] = str(chart_file) if chart_file else None

    out_json.write_text(json.dumps({"generated": ts, "totals": totals, "details": details, "desks_outside": desks_outside}, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_txt

# ===========================
# MAIN / CLI
# ===========================

def main():
    try:
        out = generate_report_for_all_spaces(DESK_TXT, ANALYSIS_SUMMARY_TXT)
        print("Report written:", out)
    except FileNotFoundError as e:
        print("Missing input:", e)

if __name__ == "__main__":
    main()