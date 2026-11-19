"""Glass file cards for the opener - the things that get squeezed.

Drawn rather than borrowed: the reference tumbles real Ae/Word app icons,
which we cannot reuse, so these are generic file-type cards in the same
glass language as the hero cube.
"""
import bpy, math

FONT = "/Users/ariga/Library/Fonts/Satoshi-Bold.otf"

# label, glass tint, position, rotation (deg), size
CARDS = [
    ("PSD", (0.35, 0.62, 1.00, 1), (-2.6,  0.4,  1.3), (16, -24, -11), 1.00),
    ("MP4", (0.62, 0.42, 1.00, 1), ( 2.8, -0.6, -0.5), (-12, 28,  14), 0.92),
    ("PDF", (1.00, 0.44, 0.40, 1), (-1.9, -1.1, -1.8), (22,  12,  -6), 0.84),
    ("ZIP", (0.40, 0.90, 0.85, 1), ( 2.2,  1.2,  1.9), (-8, -18,   9), 0.78),
]


def get_font():
    try:
        return bpy.data.fonts.load(FONT, check_existing=True)
    except RuntimeError:
        return None


def card_glass(name, tint):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    glass = nt.nodes.new("ShaderNodeBsdfGlass")
    glass.inputs["IOR"].default_value = 1.46
    glass.inputs["Roughness"].default_value = 0.04
    glass.inputs["Color"].default_value = tint
    nt.links.new(glass.outputs["BSDF"], out.inputs["Surface"])
    return mat


def label_mat():
    mat = bpy.data.materials.new("Label")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (1, 1, 1, 1)
    emit.inputs["Strength"].default_value = 2.2
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_card(text, tint, loc, rot_deg, size, font, lab_mat):
    # the card body: a rounded slab, document proportions
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    card = bpy.context.object
    card.name = "Card_" + text
    card.dimensions = (1.10 * size, 0.14 * size, 1.40 * size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bev = card.modifiers.new("Round", "BEVEL")
    bev.width = 0.10 * size
    bev.segments = 6
    bev.limit_method = "ANGLE"
    card.data.materials.append(card_glass("Glass_" + text, tint))
    for poly in card.data.polygons:
        poly.use_smooth = True

    # the label, sunk just proud of the front face
    tcur = bpy.data.curves.new("T_" + text, type="FONT")
    tcur.body = text
    if font:
        tcur.font = font
    tcur.align_x = "CENTER"
    tcur.align_y = "CENTER"
    tcur.size = 0.30 * size
    tcur.extrude = 0.012 * size
    tobj = bpy.data.objects.new("Label_" + text, tcur)
    bpy.context.collection.objects.link(tobj)
    tobj.data.materials.append(lab_mat)
    tobj.rotation_euler = (math.radians(90), 0, 0)
    tobj.location = (loc[0], loc[1] - 0.08 * size, loc[2])

    tobj.parent = card
    tobj.matrix_parent_inverse = card.matrix_world.inverted()

    card.rotation_euler = tuple(math.radians(d) for d in rot_deg)
    return card


def build_cards():
    font = get_font()
    lab = label_mat()
    made = []
    for text, tint, loc, rot, size in CARDS:
        made.append(make_card(text, tint, loc, rot, size, font, lab))
    return made


if __name__ == "__main__":
    for o in [o for o in bpy.data.objects
              if o.name.startswith(("Card_", "Label_"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    build_cards()
    print("SKWIZY_CARDS_OK")
