"""Beat 6 (11.5-13.5s) - the phone notification.

A clean build rather than an addition to the desk set: the reference cuts to
a different place entirely, a phone on a blue-to-teal field, and holds on a
slow push while the notification sits there.

The lock screen is an emissive plane, same reasoning as the laptop in beat 5 -
a screen emits, so lighting it would make it look printed. The body is dark
metal so the rim lights catch the edges, which is most of what sells it as a
phone rather than a slab.
"""
import bpy, math

UI = "/Users/ariga/Documents/skwizy/renders/ui/phone.png"
START, END = 1, 48

BODY = (0.74, 1.52, 0.085)      # a phone, scaled up for a comfortable camera
SCREEN = (0.685, 1.45)
# The phone has to face the camera. Lying flat with the screen up left it
# almost edge-on and unreadable; standing it up and leaning it back is the
# reference's pose.
# -76 turns the screen away from the camera: Rx(-76) sends +Z to +Y, and the
# camera is at -Y. Positive tilts it toward the lens.
TILT = (76, 0, -13)


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


def wipe():
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
                 bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            coll.remove(item)


def backdrop():
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 7.0, 0))
    bd = bpy.context.view_layer.objects.active
    bd.name = "Backdrop"
    # Size is a trade: too large and the lens sees a quarter of the ramp, so
    # it reads as one flat blue; too small and the plane's own edge walks into
    # shot. This is sized for the view and then centred on it below.
    bd.scale = (12.5, 7.6, 1)
    bd.rotation_euler = (math.radians(90), 0, 0)

    mat = bpy.data.materials.new("Field")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    # Build the diagonal from the Generated components directly. A Mapping
    # rotation turns about the origin, not the centre, so a 0-1 coordinate
    # square swings mostly negative and the gradient clamps to one colour -
    # which is why the first backdrop came back flat navy.
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY"
    mx.inputs[1].default_value = 0.38
    my = nt.nodes.new("ShaderNodeMath"); my.operation = "MULTIPLY"
    my.inputs[1].default_value = 0.62
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"

    ramp.color_ramp.elements[0].position = 0.08
    ramp.color_ramp.elements[0].color = (0.016, 0.035, 0.22, 1)
    ramp.color_ramp.elements[1].position = 0.94
    ramp.color_ramp.elements[1].color = (0.04, 0.62, 0.55, 1)
    mid = ramp.color_ramp.elements.new(0.52)
    mid.color = (0.09, 0.26, 0.95, 1)

    nt.links.new(coord.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["X"], mx.inputs[0])
    nt.links.new(sep.outputs["Y"], my.inputs[0])
    nt.links.new(mx.outputs["Value"], add.inputs[0])
    nt.links.new(my.outputs["Value"], add.inputs[1])
    nt.links.new(add.outputs["Value"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
    emit.inputs["Strength"].default_value = 1.0
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    bd.data.materials.append(mat)
    return bd


def phone():
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    body = bpy.context.view_layer.objects.active
    body.name = "Phone"
    body.dimensions = BODY
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bev = body.modifiers.new("Round", "BEVEL")
    # 0.042 on an 0.085 body consumed the entire thickness and the phone came
    # back as a bar of soap
    bev.width = 0.011
    bev.segments = 6
    bev.limit_method = "ANGLE"
    for poly in body.data.polygons:
        poly.use_smooth = True

    m = bpy.data.materials.new("Titanium")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.055, 0.058, 0.07, 1)
    b.inputs["Metallic"].default_value = 0.92
    b.inputs["Roughness"].default_value = 0.28
    body.data.materials.append(m)

    bpy.ops.mesh.primitive_plane_add(size=1,
                                     location=(0, 0, BODY[2] / 2 + 0.002))
    scr = bpy.context.view_layer.objects.active
    scr.name = "PhoneScreen"
    scr.scale = (SCREEN[0], SCREEN[1], 1)

    sm = bpy.data.materials.new("LockScreen")
    sm.use_nodes = True
    nt = sm.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(UI, check_existing=True)
    tex.interpolation = "Cubic"
    emit.inputs["Strength"].default_value = 1.75
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    scr.data.materials.append(sm)

    scr.parent = body
    scr.matrix_parent_inverse = body.matrix_world.inverted()
    body.rotation_euler = tuple(math.radians(r) for r in TILT)
    return body, scr


def lighting():
    specs = [
        ("Key", (-2.4, -2.6, 2.6), 420, 3.2, (0.80, 0.86, 1.0)),
        ("Rim", (2.8, 1.1, 1.6), 260, 2.0, (0.35, 0.95, 0.88)),
        ("Fill", (1.6, -3.0, -1.2), 110, 3.0, (0.72, 0.80, 1.0)),
    ]
    for name, loc, power, size, col in specs:
        d = bpy.data.lights.new(name, "AREA")
        d.energy, d.size, d.color = power, size, col
        o = bpy.data.objects.new(name, d)
        o.location = loc
        bpy.context.collection.objects.link(o)
        direction = bpy.data.objects["Phone"].location - o.location
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def camera():
    cd = bpy.data.cameras.new("PhoneCam")
    cd.lens = 62
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 2.2
    cam = bpy.data.objects.new("PhoneCam", cd)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cd.dof.focus_object = bpy.data.objects["PhoneScreen"]

    # Frame the notification, not the phone's centre. The card sits about a
    # quarter of the way down the lock screen, so the aim point comes off the
    # screen plane's own matrix rather than the body origin - and the camera
    # sits close enough that the phone runs past the frame edges, as it does
    # in the reference.
    from mathutils import Vector
    bpy.context.view_layer.update()
    scr = bpy.data.objects["PhoneScreen"]
    aim = scr.matrix_world @ Vector((0.0, 0.26, 0.0))
    direction = Vector((0.26, -1.0, 0.17)).normalized()

    for fr, dist in ((START, 4.62), (END, 4.12)):
        loc = aim + direction * dist
        for i, v in enumerate(loc):
            key(cam, "location", fr, v, index=i)
    cam.location = aim + direction * 4.62
    bpy.context.view_layer.update()
    rot = (aim - cam.location).to_track_quat("-Z", "Y").to_euler()
    for fr in (START, END):
        for i, v in enumerate(rot):
            key(cam, "rotation_euler", fr, v, index=i)
    for fc in curves_of(cam):
        for kp in fc.keyframe_points:
            kp.interpolation, kp.easing = "BEZIER", "EASE_IN_OUT"
    return cam


def render_setup(path="//renders/beat6/n_"):
    sc = bpy.context.scene
    try:
        sc.render.engine = "CYCLES"
    except TypeError as e:
        print("engines:", e)
        raise
    sc.cycles.device = "GPU"
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    sc.frame_start, sc.frame_end = START, END
    sc.render.filepath = path
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = 24
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = "Standard"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.03, 0.06, 0.16, 1)
    bg.inputs["Strength"].default_value = 0.35


def centre_backdrop(cam, bd):
    """Put the plane where the lens is actually pointing. The camera is offset
    in X and angled, so a backdrop centred on the world origin shows its own
    left edge."""
    from mathutils import Vector
    bpy.context.view_layer.update()
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    hit = cam.location + fwd * ((bd.location.y - cam.location.y) / fwd.y)
    bd.location = (hit.x, bd.location.y, hit.z)
    print("BACKDROP_AT", [round(v, 2) for v in bd.location])


if __name__ == "__main__":
    wipe()
    bd = backdrop()
    phone()
    lighting()
    cam = camera()
    centre_backdrop(cam, bd)
    render_setup()
    bpy.ops.wm.save_as_mainfile(
        filepath="/Users/ariga/Documents/skwizy/beat6.blend")
    print("BEAT6_OK")
