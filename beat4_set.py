"""Beat 4, background pass - the desk set with a slow push.

No cube in here: it is composited over the top. The set keeps the focus
distance it was framed with, 1.35m, which puts the focal plane in empty space
in front of the desk and leaves the whole set in bokeh. That is what the
reference does, and it is why this set could be built low-poly.

DOF stays ON for this pass because defocus is depth-dependent and EffectCraft
has no depth channel to rebuild it from. Motion blur still goes to EffectCraft.
"""
import bpy, math

START, END = 1, 60

# a drift rather than a move - in the reference the set barely travels
CAM = [
    (1,  (0.02, -3.05, 0.84), (95.0, 0, 2.0)),
    (60, (0.14, -2.78, 0.80), (95.3, 0, 2.3)),
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


def animate(cam):
    cam.animation_data_clear()
    for fr, loc, rot in CAM:
        for i, v in enumerate(loc):
            key(cam, "location", fr, v, index=i)
        for i, d in enumerate(rot):
            key(cam, "rotation_euler", fr, math.radians(d), index=i)
    for fc in curves_of(cam):
        for kp in fc.keyframe_points:
            kp.interpolation, kp.easing = "BEZIER", "EASE_IN_OUT"


def grade():
    """The set was lit too warm on the red channel. Measured against the
    reference: it runs R-G at -13, a cool slightly cyan cast, while this set
    ran +8 - a 21 point swing into magenta - and about 25 points hot overall.

    The cause is the rim light, whose green sat at 0.28 against red 0.52. That
    ratio is the magenta. Raising green above red turns the same light into a
    blue-violet, which is where the reference keeps its purple: in the poster
    artwork and a faint edge, not over the whole frame.

    Fixed here rather than graded later because a directional cast cannot be
    taken out by a global grade, and because baking a known fault into an hour
    of render only to fight it downstream is the expensive way round.
    """
    lights = bpy.data.lights
    rim = lights["RimPurple"]
    rim.color = (0.34, 0.36, 1.00)
    rim.energy = 40.0
    lights["KeyCool"].energy = 46.0
    lights["Fill"].energy = 18.0
    bpy.context.scene.view_settings.exposure = -0.15

    # Checked against the reference rather than trusted: the set is already
    # at about the right softness. Opening up to f/0.7 blurred the pegboard
    # dots into featureless circles, where the reference keeps them as
    # distinct dots. f/1.2 was the better reading all along - the earlier
    # impression that it was too sharp came from comparing against downscaled
    # reference frames, which flatter their own blur.
    cam = bpy.data.objects["DeskCam"].data
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = 1.2
    cam.dof.focus_distance = 1.35


def render_setup(path="//renders/beat4set/s_"):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = START, END
    sc.render.filepath = path
    sc.render.film_transparent = False      # this pass IS the background
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "16"
    sc.render.use_motion_blur = False
    sc.cycles.samples = 96


if __name__ == "__main__":
    grade()
    animate(bpy.data.objects["DeskCam"])
    render_setup()
    bpy.ops.wm.save_as_mainfile(
        filepath="/Users/ariga/Documents/skwizy/beat4_set.blend")
    print("BEAT4_SET_OK")
