"""Draw a top-down diagram of arena.sdf (walls, boxes, goal, spawn) to docs/arena.png."""
import sys, xml.etree.ElementTree as ET
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

world, out = sys.argv[1], sys.argv[2]
root = ET.parse(world).getroot()
fig, ax = plt.subplots(figsize=(8, 6.4), dpi=150)
for m in root.iter("model"):
    name = m.get("name")
    if name == "ground_plane": continue
    x, y, *_ = map(float, m.find("pose").text.split())
    sx, sy, _ = map(float, m.find(".//visual/geometry/box/size").text.split())
    if name.startswith("box"):
        fc, ec, z = "#cc2222", "black", 3
    elif name == "goal_zone":
        fc, ec, z = "#33aa44", "none", 1
    else:
        fc, ec, z = "#888888", "none", 2
    ax.add_patch(Rectangle((x - sx/2, y - sy/2), sx, sy, fc=fc, ec=ec, zorder=z))
    if name.startswith("box") or name == "goal_zone":
        ax.annotate(name, (x, y + sy/2 + 0.1), ha="center", fontsize=8, zorder=4)
# spawn pose
ax.add_patch(Rectangle((-3.2, -0.15), 0.4, 0.3, fc="#2659bf", zorder=3))
ax.add_patch(FancyArrow(-3.0, 0, 0.45, 0, width=0.03, color="#2659bf", zorder=3))
ax.annotate("PushBot spawn (-3, 0)", (-3.0, -0.45), ha="center", fontsize=8)
ax.set_xlim(-4.5, 4.5); ax.set_ylim(-3.5, 3.5); ax.set_aspect("equal")
ax.set_xticks(range(-4, 5)); ax.set_yticks(range(-3, 4)); ax.grid(alpha=0.3)
ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
ax.set_title("PDE4430 arena (world frame, top view)")
fig.tight_layout(); fig.savefig(out)
