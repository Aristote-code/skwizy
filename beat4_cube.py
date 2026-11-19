"""Beat 4, foreground pass - the compressed cube tumbling on alpha.

Read from the reference first: the object does NOT fly across the room. It
holds centre frame, tumbling at a constant rate, drifting a little right and
receding a little, for the whole beat. What changes is behind it - the blue
gradient of beats 1-3 cross-dissolves into the desk set over about 0.45s.
The object is the constant; the context arrives around it.

That makes the beat two cheap passes instead of one expensive one: glass
rendered in an empty frame (known cost) plus a set with no glass in it (known
cost), dissolved in EffectCraft. Rendering the cube inside the set would have
meant transmission rays hitting real geometry - over 200s a frame when I timed
it, against roughly 120 + 86 for the two passes separately.

The cube keeps refracting the gradient backdrop even once the set is behind
it. Both are defocused blue, so the cheat holds.
"""
import bpy, math

START, END = 1, 60

# camera distance, not object scale, does the sizing. At 50mm from 6.2m the
# compressed cube is 16% of frame width - too small to carry a shot. From
# 3.15m it is a third of the width, which is where the reference object sits.
CAM_Y = -3.15

DRIFT = [
    (1,  (-0.35, -0.15, 0.20)),
    (60, ( 0.22,  0.55, 0.10)),
]
# Brightness here is governed by one number, and it is worth stating exactly
# because guessing at it cost several renders.
#
# The plates are stacked along local X. Looking ACROSS the stack means seeing
# through roughly one plate face - bright. Looking ALONG it means traversing
# all 28 in series, 56 interfaces of tint and Fresnel - dark. So what matters
# is the angle between the stack axis and the view, and for Blender's XYZ
# euler the stack axis works out as
#
#     localX = (cos Z cos Y,  sin Z cos Y,  -sin Y)
#
# and with the camera looking down +Y the governing term is simply
#
#     axis . view = sin(Z) * cos(Y)
#
# X does not appear. X spin really is free, and the darkening I first blamed
# on it was Z all along: rotating Z from 12 to 40 nearly tripled sin(Z) and
# took the cube from 164 mean luminance to 46. Measured against renders this
# predicts 0.134 / 0.436 / 0.492 for the three poses tested, exactly.
#
# So: spend the tumble on X, keep Z small, and the cube stays lit throughout.
SPIN_FROM = (25, 50, 10)
SPIN_BY = (320, -25, -4)      # 320 deg of free X spin; Z stays near zero


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


def linear(obj, paths):
    """A free-floating object has momentum - it must not ease in or out of
    its own tumble."""
    for fc in curves_of(obj):
        if fc.data_path in paths:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def strip_squeeze(cube, blob):
    """Clear the squeeze keyframes and pin the compressed end state."""
    cube.animation_data_clear()
    blob.animation_data_clear()
    cube.scale = (0.45, 0.45, 0.45)

    mat = blob.data.materials[0]
    mat.node_tree.animation_data_clear()
    vol = mat.node_tree.nodes["Principled Volume"]
    vol.inputs["Density"].default_value = 12.0        # compressed, dense
    vol.inputs["Emission Strength"].default_value = 5.5


def animate(cube, cam):
    cam.location.y = CAM_Y
    for fr, loc in DRIFT:
        for i, v in enumerate(loc):
            key(cube, "location", fr, v, index=i)
    for i, (a, b) in enumerate(zip(SPIN_FROM, SPIN_BY)):
        key(cube, "rotation_euler", START, math.radians(a), index=i)
        key(cube, "rotation_euler", END, math.radians(a + b), index=i)
    linear(cube, {"location", "rotation_euler"})


def render_setup(path="//renders/beat4cube/c_"):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = START, END
    sc.render.filepath = path
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "16"
    sc.render.use_motion_blur = False       # EffectCraft owns blur
    sc.cycles.samples = 96
    sc.cycles.transmission_bounces = 10   # 18 is wasted at this size
    sc.cycles.volume_bounces = 1


if __name__ == "__main__":
    cube = bpy.data.objects["HeroCube"]
    blob = bpy.data.objects["Substance"]
    strip_squeeze(cube, blob)
    animate(cube, bpy.data.objects["Cam"])
    render_setup()
    bpy.ops.wm.save_as_mainfile(
        filepath="/Users/ariga/Documents/skwizy/beat4_cube.blend")
    print("BEAT4_CUBE_OK")
