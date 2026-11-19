"""The desk set - beat 4.

Everything here is heavily defocused in the reference, the laptop screen
included. Only the flying object is sharp. So this is built for silhouette,
colour and light, not detail: low-poly throughout, and the depth of field
does the rest. Detail here would be invisible and cost render time.
"""
import bpy, math

# ------------------------------------------------------------------ helpers
def wipe():
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
                 bpy.data.cameras, bpy.data.lights, bpy.data.curves):
        for item in list(coll):
            coll.remove(item)


def mat(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    return m


def box(name, size, loc, rot=(0, 0, 0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.dimensions = size
    o.rotation_euler = tuple(math.radians(r) for r in rot)
    if material:
        o.data.materials.append(material)
    return o


# ------------------------------------------------------------------ the set
def pegboard():
    """White panel, navy holes on a grid. Geometry rather than a shader:
    an array of discs is cheaper to get right than procedural dots."""
    # big enough to fill the background at any framing - a visible top edge
    # leaves a dark void where the reference has wall
    panel = box("Pegboard", (8.2, 0.06, 3.6), (0, 1.62, 1.55),
                material=mat("PegWhite", (0.93, 0.93, 0.91), rough=0.75))

    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.02,
                                        vertices=16,
                                        location=(-3.85, 1.585, 0.16))
    dot = bpy.context.view_layer.objects.active
    dot.name = "PegDot"
    dot.rotation_euler = (math.radians(90), 0, 0)
    dot.data.materials.append(mat("PegNavy", (0.07, 0.12, 0.55), rough=0.5))

    ax = dot.modifiers.new("Across", "ARRAY")
    ax.use_relative_offset = False
    ax.use_constant_offset = True
    ax.constant_offset_displace = (0.26, 0, 0)
    ax.count = 31

    up = dot.modifiers.new("Up", "ARRAY")
    up.use_relative_offset = False
    up.use_constant_offset = True
    up.constant_offset_displace = (0, 0.26, 0)   # local Y = world Z once rotated
    up.count = 13
    return panel, dot


def desk():
    return box("Desk", (5.0, 2.2, 0.08), (0, 0.55, -0.04),
               material=mat("DeskBlue", (0.13, 0.18, 0.46), rough=0.3))


def laptop():
    body = box("LaptopBase", (0.95, 0.66, 0.035), (0.95, 0.30, 0.018),
               rot=(0, 0, -16),
               material=mat("Charcoal", (0.08, 0.085, 0.10), rough=0.4))
    lid = box("LaptopLid", (0.95, 0.62, 0.028), (1.11, 0.72, 0.31),
              rot=(-74, 0, -16), material=bpy.data.materials["Charcoal"])
    # the screen: emissive, dim, cool - it is defocused, so it only has to glow
    screen = box("Screen", (0.88, 0.56, 0.004), (1.105, 0.705, 0.311),
                 rot=(-74, 0, -16),
                 material=mat("ScreenGlow", (0.02, 0.025, 0.035), rough=0.3,
                              emit=(0.10, 0.13, 0.22), emit_strength=0.8))
    return body, lid, screen


def lamp():
    base = box("LampBase", (0.42, 0.22, 0.035), (-0.18, 0.62, 0.018),
               material=mat("LampBlack", (0.03, 0.03, 0.04), rough=0.35))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=1.15, vertices=14,
                                        location=(-0.18, 0.62, 0.60))
    stem = bpy.context.view_layer.objects.active
    stem.name = "LampStem"
    stem.data.materials.append(bpy.data.materials["LampBlack"])

    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.78, vertices=14,
                                        location=(0.12, 0.60, 1.02))
    tube = bpy.context.view_layer.objects.active
    tube.name = "LampTube"
    tube.rotation_euler = (0, math.radians(74), 0)
    tube.data.materials.append(
        mat("TubeGlow", (1.0, 0.97, 0.9), emit=(1.0, 0.96, 0.88),
            emit_strength=22.0))
    return base, stem, tube


def plant():
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.26, vertices=24,
                                        location=(-1.15, 0.52, 0.13))
    pot = bpy.context.view_layer.objects.active
    pot.name = "Pot"
    pot.data.materials.append(mat("PotWhite", (0.95, 0.95, 0.94), rough=0.6))

    leaf_mat = mat("LeafTeal", (0.04, 0.30, 0.26), rough=0.55)
    leaves = []
    # fat rounded rosette, not a palm: wide leaves, barely elongated
    for ring, (count, tilt, rad, scale) in enumerate(
            [(8, 68, 0.15, 0.115), (7, 44, 0.095, 0.095), (5, 18, 0.04, 0.07)]):
        for i in range(count):
            a = (2 * math.pi * i / count) + ring * 0.45
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
            lf = bpy.context.view_layer.objects.active
            lf.name = "Leaf"
            lf.scale = (scale * 0.78, scale, scale * 1.05)
            lf.location = (-1.15 + math.cos(a) * rad,
                           0.52 + math.sin(a) * rad,
                           0.27 + ring * 0.045)
            lf.rotation_euler = (math.radians(tilt) * math.sin(a),
                                 -math.radians(tilt) * math.cos(a), 0)
            lf.data.materials.append(leaf_mat)
            for poly in lf.data.polygons:      # icospheres read faceted raw
                poly.use_smooth = True
            leaves.append(lf)
    return pot, leaves


def posters():
    """Two prints on the pegboard. Flat emissive-ish planes - they are only
    ever colour shapes behind heavy blur."""
    p1 = box("PosterA", (0.52, 0.012, 0.70), (-0.42, 1.57, 1.08),
             material=mat("PrintBlue", (0.13, 0.33, 0.85), rough=0.6))
    p2 = box("PosterB", (0.60, 0.012, 0.74), (0.38, 1.57, 1.14),
             material=mat("PrintPink", (0.86, 0.44, 0.72), rough=0.6))
    return p1, p2


# ------------------------------------------------------------------ lighting
def lighting():
    specs = [
        ("KeyCool",  "AREA",  (-1.6, -1.2, 2.2), 70, 3.0, (0.72, 0.80, 1.0)),
        ("RimPurple", "AREA", (-2.1,  0.1, 0.8), 70, 1.6, (0.52, 0.28, 1.0)),
        ("Fill",     "AREA",  ( 2.2, -0.9, 1.4), 32, 2.5, (0.80, 0.86, 1.0)),
    ]
    for name, kind, loc, power, size, col in specs:
        d = bpy.data.lights.new(name, kind)
        d.energy = power
        d.size = size
        d.color = col
        o = bpy.data.objects.new(name, d)
        o.location = loc
        bpy.context.collection.objects.link(o)
        direction = (bpy.data.objects["Desk"].location - o.location)
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def camera():
    cd = bpy.data.cameras.new("DeskCam")
    cd.lens = 55
    cd.dof.use_dof = True
    cd.dof.focus_distance = 1.35
    cd.dof.aperture_fstop = 1.2        # the reference is almost entirely bokeh
    cam = bpy.data.objects.new("DeskCam", cd)
    bpy.context.collection.objects.link(cam)
    # 90 deg looks dead horizontal; past 90 tilts down onto the desk
    # 55mm covers distance*36/55 of width; plant-to-laptop is ~2.6m, so it has
    # to sit ~3.5m back from the desk, not 1.5m
    cam.location = (0.02, -3.05, 0.84)
    cam.rotation_euler = (math.radians(95), 0, math.radians(2))
    bpy.context.scene.camera = cam
    return cam


def render_setup():
    sc = bpy.context.scene
    try:
        sc.render.engine = "CYCLES"
    except TypeError as e:
        print("engines:", e)
        raise
    sc.cycles.device = "GPU"
    sc.cycles.samples = 128
    sc.cycles.use_denoising = True
    sc.cycles.blur_glossy = 2.0
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = 24
    sc.render.use_motion_blur = False       # EffectCraft owns blur
    sc.view_settings.view_transform = "Standard"
    if sc.world is None:                     # an empty homefile has no world
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.05, 0.06, 0.16, 1)
    bg.inputs["Strength"].default_value = 0.12


if __name__ == "__main__":
    wipe()
    desk()
    pegboard()
    laptop()
    lamp()
    plant()
    posters()
    lighting()
    camera()
    render_setup()
    print("DESKSET_OK")
