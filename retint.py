"""Apply the warm hero tint to an existing blend and save it.

Kept separate from assets.py because the squeeze and tumble rigs are already
baked into their .blend files - rebuilding the scenes from scratch would throw
the animation away.
"""
import bpy, sys

TINT = (1.00, 0.68, 0.34, 1.0)      # amber glass
CORE = (1.00, 0.76, 0.42, 1.0)      # the glow inside it

out = sys.argv[-1]
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_GLASS" and "Card" not in mat.name:
            n.inputs["Color"].default_value = TINT
        if n.type == "PRINCIPLED_VOLUME":
            n.inputs["Emission Color"].default_value = CORE
bpy.ops.wm.save_as_mainfile(filepath=out)
print("RETINTED", out)
