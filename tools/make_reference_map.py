"""Make a clean occupancy-grid map of the arena straight from the world file.

This is a fallback for anyone who could not build their own map with SLAM.
It uses the same frame as a SLAM map: map (0, 0) is where the robot starts
(world x = -3, y = 0), facing +x. So the same Nav2 settings and initial
pose work for this map and for your own.

    python3 tools/make_reference_map.py pushbot_gazebo/worlds/arena_empty.sdf \
        pushbot_navigation/maps/reference_arena

writes reference_arena.pgm and reference_arena.yaml.
"""
import sys
import xml.etree.ElementTree as ET

RES = 0.05              # m per cell, same as slam_params.yaml
SPAWN = (-3.0, 0.0)     # robot start in the world frame = map origin
MARGIN = 0.5            # unknown border around the arena (m)
FREE, OCC, UNKNOWN = 254, 0, 205

world, out = sys.argv[1], sys.argv[2]
root = ET.parse(world).getroot()

boxes = []  # (xmin, xmax, ymin, ymax) in the world frame, static models only
for m in root.iter("model"):
    static = m.find("static")
    if m.get("name") == "ground_plane" or static is None or static.text.strip() != "true":
        continue
    col = m.find(".//collision/geometry/box/size")
    if col is None:
        continue  # visual-only models (the goal zone) are not obstacles
    x, y, *_ = map(float, m.find("pose").text.split())
    sx, sy, _ = map(float, col.text.split())
    boxes.append((x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2))

xmin = min(b[0] for b in boxes) - MARGIN
xmax = max(b[1] for b in boxes) + MARGIN
ymin = min(b[2] for b in boxes) - MARGIN
ymax = max(b[3] for b in boxes) + MARGIN
# Inside of the outer walls: the free area
inner = (min(b[1] for b in boxes), max(b[0] for b in boxes),
         min(b[3] for b in boxes), max(b[2] for b in boxes))

w = int(round((xmax - xmin) / RES))
h = int(round((ymax - ymin) / RES))
rows = []
for r in range(h):                      # row 0 is the top (largest y)
    cy = ymax - (r + 0.5) * RES
    row = bytearray()
    for c in range(w):
        cx = xmin + (c + 0.5) * RES
        v = FREE if inner[0] < cx < inner[1] and inner[2] < cy < inner[3] else UNKNOWN
        for b in boxes:
            if b[0] <= cx <= b[1] and b[2] <= cy <= b[3]:
                v = OCC
                break
        row.append(v)
    rows.append(bytes(row))

with open(out + ".pgm", "wb") as f:
    f.write(b"P5\n# PDE4430 reference arena map\n%d %d\n255\n" % (w, h))
    for row in rows:
        f.write(row)

name = out.split("/")[-1]
with open(out + ".yaml", "w") as f:
    f.write(
        f"# Reference map generated from {world.split('/')[-1]} by tools/make_reference_map.py\n"
        f"# Map frame: (0, 0) is the robot's start pose (world x = {SPAWN[0]}, y = {SPAWN[1]}).\n"
        f"image: {name}.pgm\n"
        f"mode: trinary\n"
        f"resolution: {RES}\n"
        f"origin: [{xmin - SPAWN[0]:.3f}, {ymin - SPAWN[1]:.3f}, 0.0]\n"
        f"negate: 0\n"
        f"occupied_thresh: 0.65\n"
        f"free_thresh: 0.25\n"
    )
print(f"{w} x {h} cells, {len(boxes)} static obstacles")
