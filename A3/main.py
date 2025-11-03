import os
import math
import argparse
import ifcopenshell
import ifcopenshell.geom

def get_bbox(element):
    """Return bbox as (minx,miny,minz,maxx,maxy,maxz) or None on failure."""
    try:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, element)
        return shape.geometry.bbox
    except Exception:
        return None

def bbox_centroid(bbox):
    minx, miny, minz, maxx, maxy, maxz = bbox
    return ((minx + maxx) / 2.0, (miny + maxy) / 2.0, (minz + maxz) / 2.0)

def bbox_proj_rect(bbox):
    """Return 2D rectangle from bbox: (minx,miny,maxx,maxy)."""
    minx, miny, _, maxx, maxy, _ = bbox
    return (minx, miny, maxx, maxy)

def rect_contains_point(rect, p):
    minx, miny, maxx, maxy = rect
    x, y = p
    return (minx <= x <= maxx) and (miny <= y <= maxy)

def segments_intersect(p1, p2, q1, q2):
    """2D segment intersection test."""
    def orient(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    a, b, c, d = p1, p2, q1, q2
    o1 = orient(a,b,c)
    o2 = orient(a,b,d)
    o3 = orient(c,d,a)
    o4 = orient(c,d,b)
    if o1 == o2 == o3 == o4 == 0:
        # Colinear - check overlap in projection
        def on_seg(a,b,c):
            return min(a[0],b[0]) <= c[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= c[1] <= max(a[1],b[1])
        return on_seg(a,b,c) or on_seg(a,b,d) or on_seg(c,d,a) or on_seg(c,d,b)
    return (o1*o2 <= 0) and (o3*o4 <= 0)

def segment_intersects_rect(p1, p2, rect):
    """Check if segment p1-p2 intersects rectangle rect=(minx,miny,maxx,maxy)."""
    if rect_contains_point(rect, p1) or rect_contains_point(rect, p2):
        return True
    minx, miny, maxx, maxy = rect
    corners = [(minx,miny),(maxx,miny),(maxx,maxy),(minx,maxy)]
    # test against each edge
    for i in range(4):
        q1 = corners[i]
        q2 = corners[(i+1)%4]
        if segments_intersect((p1[0],p1[1]), (p2[0],p2[1]), q1, q2):
            return True
    return False

def euclidean_2d(a,b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def friendly(obj):
    name = getattr(obj, "Name", None) or getattr(obj, "LongName", None) or obj.is_a()
    try:
        eid = obj.id()
        return f"{name} (id={eid})"
    except Exception:
        return str(name)

def find_space_for_point(point, spaces, space_rects):
    for sp, rect in zip(spaces, space_rects):
        if rect and rect_contains_point(rect, (point[0], point[1])):
            return sp
    return None

def run_check(ifc_path, max_travel_distance=30.0):
    model = ifcopenshell.open(ifc_path)

    # Collect elements
    spaces = model.by_type("IfcSpace")
    doors = model.by_type("IfcDoor")
    stairs = model.by_type("IfcStair")
    walls = model.by_type("IfcWall")
    furnishings = model.by_type("IfcFurnishingElement")  # desks likely here
    # fallback: some desks might be IfcFurniture or IfcBuildingElementProxy etc.
    extra_candidates = model.by_type("IfcFurniture") if hasattr(model, "by_type") else []

    # prepare bboxes and centroids (2D)
    space_bboxes = [get_bbox(s) for s in spaces]
    space_rects = [bbox_proj_rect(b) if b else None for b in space_bboxes]
    door_bboxes = [get_bbox(d) for d in doors]
    door_centroids = [bbox_centroid(b)[:2] if b else None for b in door_bboxes]
    stair_bboxes = [get_bbox(s) for s in stairs]
    stair_centroids = [bbox_centroid(b)[:2] if b else None for b in stair_bboxes]
    wall_bboxes = [get_bbox(w) for w in walls]
    wall_rects = [bbox_proj_rect(b) for b in wall_bboxes if b]

    # identify desks: filter furnishings by name or type keywords
    desks = []
    for f in furnishings:
        name = getattr(f, "Name", "") or ""
        typename = f.is_a() or ""
        if any(k in name.lower() for k in ("desk","workstation","table")) or "Furnishing" in typename:
            b = get_bbox(f)
            if b:
                desks.append((f,b))
    # also consider IfcFurniture or proxies
    for f in extra_candidates:
        b = get_bbox(f)
        if b:
            desks.append((f,b))

    # if none found, try scanning all elements for "desk" in Name
    if not desks:
        for el in model:
            name = getattr(el, "Name", "") or ""
            if "desk" in name.lower():
                b = get_bbox(el)
                if b:
                    desks.append((el,b))

    # Build desk centroids and rects
    desk_centroids = [bbox_centroid(b)[0:2] for (_,b) in desks]
    desk_rects = [bbox_proj_rect(b) for (_,b) in desks]

    # Determine corridor spaces: heuristic by Name/LongName
    corridors = []
    corridor_rects = []
    for sp, rect in zip(spaces, space_rects):
        name = (getattr(sp, "Name", "") or "").lower()
        longname = (getattr(sp, "LongName", "") or "").lower()
        if any(k in name for k in ("corridor","gang","corridor")) or any(k in longname for k in ("corridor","gang")):
            corridors.append(sp)
            corridor_rects.append(rect)

    # Prepare outputs
    total_desks = len(desks)
    problematic = []

    # For each desk, check path to nearest door or corridor
    for idx, (desk, dbbox) in enumerate(desks):
        dc = desk_centroids[idx]
        # find containing space
        containing_space = find_space_for_point(dc+(0,), spaces, space_rects)  # point needs only xy
        # if desk sits inside a corridor space => flagged as obstruction (desk in corridor)
        in_corridor = False
        if containing_space and any(containing_space == c for c in corridors):
            in_corridor = True

        # nearest door
        valid_doors = [(i, c) for i,c in enumerate(door_centroids) if c]
        nearest = None
        if valid_doors:
            nearest = min(valid_doors, key=lambda ic: euclidean_2d(dc, ic[1]))
            door_index, door_c = nearest
            dist_to_door = euclidean_2d(dc, door_c)
        else:
            door_index = None
            door_c = None
            dist_to_door = None

        # path straight-line check: check intersection with walls or other desk rects
        blocked_by_wall = False
        blocked_by_furn = False
        if door_c:
            p1 = (dc[0], dc[1])
            p2 = (door_c[0], door_c[1])
            # check walls
            for wr in wall_rects:
                if segment_intersects_rect(p1, p2, wr):
                    blocked_by_wall = True
                    break
            # check other desks
            for j, dr in enumerate(desk_rects):
                if j == idx:
                    continue
                if segment_intersects_rect(p1, p2, dr):
                    blocked_by_furn = True
                    break

        # decide problematic criteria:
        # - desk in corridor (obstruction)
        # - straight-line blocked by wall or other desk
        # - distance to door exceeds max_travel_distance (configurable)
        is_problem = False
        reasons = []
        if in_corridor:
            is_problem = True
            reasons.append("Desk located inside corridor space (obstruction).")
        if door_c and (blocked_by_wall or blocked_by_furn):
            is_problem = True
            reasons.append("Straight-line path to nearest door intersects wall or other furniture.")
        if dist_to_door is None:
            is_problem = True
            reasons.append("No door geometry found in model.")
        else:
            if dist_to_door > max_travel_distance:
                is_problem = True
                reasons.append(f"Distance to nearest door is {dist_to_door:.1f} m (> {max_travel_distance} m).")

        if is_problem:
            problematic.append({
                "desk": friendly(desk),
                "space": friendly(containing_space) if containing_space else "Unknown",
                "dist_to_nearest_door_m": round(dist_to_door,2) if dist_to_door is not None else None,
                "reasons": reasons
            })

    # Build summary text
    lines = []
    lines.append(f"Model: {os.path.basename(ifc_path)}")
    lines.append(f"Total desks detected: {total_desks}")
    lines.append(f"Total doors detected: {len(doors)}")
    lines.append(f"Total corridors detected (heuristic): {len(corridors)}")
    lines.append("")
    lines.append(f"Problematic desks: {len(problematic)}")
    if problematic:
        lines.append("")
        for p in problematic:
            lines.append(f"- {p['desk']}")
            lines.append(f"    Space: {p['space']}")
            if p['dist_to_nearest_door_m'] is not None:
                lines.append(f"    Distance to nearest door: {p['dist_to_nearest_door_m']} m")
            for r in p['reasons']:
                lines.append(f"    - {r}")
            lines.append("")
    else:
        lines.append("No obvious desk obstructions detected by the heuristic checks.")
    lines.append("")
    lines.append("Notes:")
    lines.append("- This tool uses simple geometric heuristics (bounding boxes, straight-line paths and name heuristics).")
    lines.append("- For full code-compliant evacuation checks (BR18) you need route graph/travel distance maps and official regulatory parameters.")
    lines.append("- If geometry cannot be generated for an element its bbox is ignored. Consider exporting tessellated geometry or enabling ifcopenshell geom backend.")
    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evacuation route / desk placement checker (heuristic).")
    parser.add_argument("ifc", nargs="?", help="Path to IFC file", default=r"C:\Users\nicol\OneDrive - Danmarks Tekniske Universitet\DTU\7. Semester\41934 Advanced Building Information Modeling\GitHub\AdvancedBIM_ARCH\model\25-16-D-ARCH.ifc")
    parser.add_argument("--max-distance", type=float, default=30.0, help="Maximum allowed straight-line distance to door (m)")
    args = parser.parse_args()
    result_text = run_check(args.ifc, max_travel_distance=args.max_distance)
    print(result_text)
