"""Beat 1 - the glass file cards converging from both sides.

This is the part of the reference opening that actually sells the moment: as
the words stack up, glass objects fly in from the left and right edges and
settle around the text, meeting in the middle. The type alone reads thin
without them.

Built on skwizy.blend so the cards inherit the hero cube's lighting and
backdrop, which is what keeps them in the same material world as the cube
that arrives later.

One adaptation. In the reference the objects arrive at the assembly and then
hold for nearly two seconds, because its dark section runs to 4.4s. Ours ends
at 2.625s, so arriving at the assembly would leave them on screen for about
0.4s - not long enough to read as objects at all. They therefore start their
run earlier, at 1.5s, and are settling as the stack forms rather than after
it. Same convergence, spread over the window we actually have.
"""
import bpy, math

FONT = "/Users/ariga/Library/Fonts/Satoshi-Bold.otf"

START, ARRIVE, END = 36, 54, 63      # 1.50s, 2.25s, 2.625s at 24fps

# Tints have to start nearly clear. A saturated Glass BSDF colour multiplies
# through every interface, and on a slab this thick it stops reading as glass
# and turns into flat coloured plastic - which is exactly what the first pass
# came back as. Enough hue to tell the cards apart, no more. Same lesson the
# hero cube's glass needed.
#
# label, tint, settled position, settled rotation (deg), size, entry x
CARDS = [
    ("PSD", (0.72, 0.85, 1.00, 1), (-1.60,  0.55, -0.62), ( 14, -22, -9),  0.62, -4.6),
    ("ZIP", (0.75, 0.97, 0.94, 1), (-1.72, -0.55,  0.68), (-10,  24, 12),  0.56, -5.1),
    ("MP4", (0.84, 0.76, 1.00, 1), ( 1.42,  0.25,  0.60), ( 18,  14, -7),  0.52,  4.6),
    ("PDF", (1.00, 0.82, 0.79, 1), ( 1.30, -0.45, -0.70), (-8,  -19, 10),  0.46,  5.1),
]


def key(obj, path, frame, value, index=-1):
    if index >= 0:
        getattr(obj, path)[index] = value
    else:
        setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame, index=index)


def curves_of(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    for layer in ad.action.layers:
        for strip in layer.strips:
            for slot in ad.action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


def ease(obj, spec):
    for fc in curves_of(obj):
        for kp in fc.keyframe_points:
            found = spec.get(int(kp.co.x))
            if found:
                kp.interpolation, kp.easing = found


def card_glass(name, tint):
    """Ribbed glass, not a plain slab.

    A flat pane of tinted glass with nothing bright behind it is just a window
    onto darkness, which is why the first two passes read as plastic. The hero
    cube escapes this because 28 stacked plates give it internal structure and
    a glowing core. These cards get the same idea cheaply: a wave bump across
    the face, so every rib catches the lights and throws a highlight.

    It also ties them to the cube's visual language - the whole piece is made
    of ribbed glass.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    glass = nt.nodes.new("ShaderNodeBsdfGlass")
    glass.inputs["IOR"].default_value = 1.46
    glass.inputs["Roughness"].default_value = 0.02
    glass.inputs["Color"].default_value = tint

    coord = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"          # ribs run up the card face
    wave.wave_profile = "SIN"
    wave.inputs["Scale"].default_value = 11.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.42

    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], glass.inputs["Normal"])
    nt.links.new(glass.outputs["BSDF"], out.inputs["Surface"])
    return mat


def label_mat():
    mat = bpy.data.materials.new("CardLabel")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (1, 1, 1, 1)
    emit.inputs["Strength"].default_value = 2.2
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_card(text, tint, size, font, lab):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    card = bpy.context.view_layer.objects.active
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

    cur = bpy.data.curves.new("T_" + text, type="FONT")
    cur.body = text
    if font:
        cur.font = font
    cur.align_x = "CENTER"
    cur.align_y = "CENTER"
    cur.size = 0.30 * size
    cur.extrude = 0.012 * size
    tobj = bpy.data.objects.new("Label_" + text, cur)
    bpy.context.collection.objects.link(tobj)
    tobj.data.materials.append(lab)
    tobj.rotation_euler = (math.radians(90), 0, 0)
    tobj.location = (0, -0.085 * size, 0)
    tobj.parent = card
    tobj.matrix_parent_inverse = card.matrix_world.inverted()
    return card


def build():
    for o in [o for o in bpy.data.objects
              if o.name.startswith(("Card_", "Label_"))]:
        bpy.data.objects.remove(o, do_unlink=True)

    # the cube belongs to beats 3 and 4, not here
    for name in ("HeroCube", "Substance"):
        o = bpy.data.objects.get(name)
        if o:
            o.hide_render = True

    try:
        font = bpy.data.fonts.load(FONT, check_existing=True)
    except RuntimeError:
        font = None
    lab = label_mat()

    for text, tint, dest, rot, size, entry_x in CARDS:
        card = make_card(text, tint, size, font, lab)

        # fly in from its own side, overshoot slightly, settle
        over = [dest[i] + (0.08 if entry_x < 0 else -0.08) * (1 if i == 0 else 0)
                for i in range(3)]
        for i, v in enumerate((entry_x, dest[1], dest[2])):
            key(card, "location", START, v, index=i)
        for i, v in enumerate(over):
            key(card, "location", ARRIVE, v, index=i)
        for i, v in enumerate(dest):
            key(card, "location", END, v, index=i)

        # tumbling on the way in, almost still once it lands
        spin = 150 if entry_x < 0 else -150
        for i, d in enumerate(rot):
            key(card, "rotation_euler", START, math.radians(d + spin), index=i)
            key(card, "rotation_euler", ARRIVE, math.radians(d), index=i)
            key(card, "rotation_euler", END, math.radians(d - 3), index=i)

        ease(card, {START: ("BEZIER", "EASE_IN"),
                    ARRIVE: ("BACK", "EASE_OUT"),
                    END: ("BEZIER", "EASE_IN_OUT")})


def render_setup(path="//renders/beat1cards/k_"):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = START, END
    sc.render.filepath = path
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "16"
    sc.render.use_motion_blur = False        # EffectCraft owns blur
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.cycles.samples = 96
    sc.cycles.transmission_bounces = 10
    bd = bpy.data.objects.get("Backdrop")
    if bd:
        bd.visible_camera = False            # refracted, never in the plate
    cam = bpy.data.objects.get("Cam")
    if cam:
        cam.location.y = -6.2                # the wide framing, not beat 4's
        cam.data.dof.use_dof = False

    # Glass only reads if it has something bright to refract. In the reference
    # the flying objects are clearly brighter than the dark gradient they sit
    # on - they are lit by a bright surround, not by the background. Since the
    # backdrop here is hidden from camera and only feeds refraction, it can be
    # lifted for this pass without touching what composites underneath.
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    wbg = sc.world.node_tree.nodes["Background"]
    wbg.inputs["Color"].default_value = (0.58, 0.72, 1.0, 1)
    wbg.inputs["Strength"].default_value = 1.6


if __name__ == "__main__":
    build()
    render_setup()
    bpy.ops.wm.save_as_mainfile(
        filepath="/Users/ariga/Documents/skwizy/beat1_cards.blend")
    print("BEAT1_CARDS_OK")
