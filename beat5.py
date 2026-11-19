"""Beat 5 (9-11.5s) - the camera pushes into the laptop screen.

Continues straight out of beat 4: the camera starts exactly where that beat
left it and travels in until the screen fills the frame. The dashboard is a
flat emissive plane rather than a lit surface, because a real screen emits -
lighting it would make it read as a printed poster.

The screen in deskset.py is a thin box, whose six faces each carry their own
UVs, so an image mapped onto it lands wrong. It gets replaced here with a
plane that has the same transform and a clean 0-1 unwrap.
"""
import bpy, math
from mathutils import Vector

UI = "/Users/ariga/Documents/skwizy/renders/ui/screen.png"
START, END = 1, 60

# where deskset.py put the screen
SCREEN_LOC = (1.105, 0.705, 0.311)
# deskset.py tilts the screen -74 on X, which leaves the plane's +Z - its
# right-reading face - pointing into the lid, so a push ends looking at the
# back of it. Adding 180 turns the face toward the room.
SCREEN_ROT = (106, 0, -16)
SCREEN_DIM = (0.88, 0.56)

CAM_START = ((0.14, -2.78, 0.80), (95.3, 0, 2.3))   # beat 4's last frame


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


def make_screen():
    old = bpy.data.objects.get("Screen")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    bpy.ops.mesh.primitive_plane_add(size=1, location=SCREEN_LOC)
    scr = bpy.context.view_layer.objects.active
    scr.name = "Screen"
    scr.scale = (SCREEN_DIM[0], SCREEN_DIM[1], 1)
    scr.rotation_euler = tuple(math.radians(r) for r in SCREEN_ROT)

    mat = bpy.data.materials.new("ScreenUI")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(UI, check_existing=True)
    tex.interpolation = "Cubic"
    # No UV correction. Rotating the plane 180 on X carries its texture with
    # it, so the compensating V-flip I first added was itself the bug: tested
    # against all four orientations, plain (1, 1) is the one that reads.
    emit.inputs["Strength"].default_value = 1.9
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    scr.data.materials.append(mat)
    return scr


def push(cam, scr):
    """End square-on to the screen, computed from the screen's own matrix
    rather than guessed - the panel is tilted on two axes."""
    cam.animation_data_clear()
    loc, rot = CAM_START
    for i, v in enumerate(loc):
        key(cam, "location", START, v, index=i)
    for i, dgr in enumerate(rot):
        key(cam, "rotation_euler", START, math.radians(dgr), index=i)

    # matrix_world lags until the view layer updates: without this the
    # rotation has not applied yet and the normal comes back as world +Z,
    # which parks the camera directly above the screen instead of in front
    # of it.
    bpy.context.view_layer.update()
    target = scr.matrix_world.translation
    normal = (scr.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    # a plane has two faces; take the one the camera is already on, or the
    # push ends up behind the lid looking at the back of the screen
    if normal.dot(Vector(CAM_START[0]) - target) < 0:
        normal = -normal
    end = target + normal * 0.62
    look = (target - end).to_track_quat("-Z", "Y").to_euler()

    for i, v in enumerate(end):
        key(cam, "location", END, v, index=i)
    for i, v in enumerate(look):
        key(cam, "rotation_euler", END, v, index=i)

    for fc in curves_of(cam):
        for kp in fc.keyframe_points:
            kp.interpolation, kp.easing = "BEZIER", "EASE_IN_OUT"

    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = scr
    cam.data.dof.aperture_fstop = 1.4
    print("CAM_END", [round(v, 3) for v in end])


def render_setup(path="//renders/beat5/p_"):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = START, END
    sc.render.filepath = path
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    sc.render.use_motion_blur = False
    sc.cycles.samples = 96


if __name__ == "__main__":
    scr = make_screen()
    push(bpy.data.objects["DeskCam"], scr)
    render_setup()
    bpy.ops.wm.save_as_mainfile(
        filepath="/Users/ariga/Documents/skwizy/beat5.blend")
    print("BEAT5_OK")
