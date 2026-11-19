"""The squeeze - the one beat that has to be 3D, because it is geometry
deforming rather than a layer being transformed.

48 frames @ 24fps. Renders RGBA for EffectCraft, which adds the blur, the
file-size counter and the grade.
"""
import bpy, math

START, END = 1, 48
SQ_IN, SQ_OUT = 14, 26      # the crush
COLLAPSE = 32               # snaps inward into the compressed cube
BOUNCE, SETTLE = 38, 44


def key(obj, path, frame, value, index=-1,
        interp="BEZIER", easing="AUTO"):
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


def shape(obj, frame_map):
    """frame_map: {frame: (interpolation, easing)}"""
    for fc in curves_of(obj):
        for kp in fc.keyframe_points:
            spec = frame_map.get(int(kp.co.x))
            if spec:
                kp.interpolation, kp.easing = spec


def animate_squeeze():
    cube = bpy.data.objects["HeroCube"]
    blob = bpy.data.objects["Substance"]

    # --- The crush squashes, then the whole thing snaps inward to a SMALLER
    # CUBE. A compressed file is still a file: if X alone collapses the object
    # becomes a plank, stops reading as compression, and the plates get driven
    # so thin the glass goes opaque.
    # Crushed from ABOVE: shorter and wider is what reads as a squeeze.
    # Thinning one horizontal axis while the other two bulge just makes the
    # object taller and narrower - a plank, not a compression.
    for fr, sx, sy, sz in (
        (START,    1.00, 1.00, 1.00),
        (SQ_IN,    1.00, 1.00, 1.00),
        (SQ_OUT,   1.16, 1.16, 0.46),   # pressed flat, squeezed outwards
        (COLLAPSE, 0.42, 0.42, 0.42),   # snaps closed, proportional again
        (BOUNCE,   0.46, 0.46, 0.51),
        (SETTLE,   0.45, 0.45, 0.45),
        (END,      0.45, 0.45, 0.45),
    ):
        key(cube, "scale", fr, sx, index=0)
        key(cube, "scale", fr, sy, index=1)
        key(cube, "scale", fr, sz, index=2)

    shape(cube, {
        SQ_IN:    ("BEZIER", "EASE_IN"),    # anticipation, then it goes
        SQ_OUT:   ("BEZIER", "EASE_IN_OUT"),
        COLLAPSE: ("BACK",   "EASE_OUT"),
        BOUNCE:   ("BEZIER", "EASE_IN_OUT"),
        SETTLE:   ("BEZIER", "EASE_OUT"),
    })

    # --- slow tumble throughout, so it never reads as a flat card
    key(cube, "rotation_euler", START, math.radians(-34), index=1)
    key(cube, "rotation_euler", END, math.radians(-14), index=1)
    key(cube, "rotation_euler", START, math.radians(10), index=0)
    key(cube, "rotation_euler", END, math.radians(17), index=0)

    # --- the data inside gets denser and hotter as it is forced down
    vol = blob.data.materials[0].node_tree.nodes["Principled Volume"]
    for fr, dens, emit in (
        (START,    4.5, 2.6),
        (SQ_IN,    4.5, 2.6),
        (SQ_OUT,  11.0, 6.0),
        (COLLAPSE, 16.0, 8.5),    # peak compression = peak brightness
        (SETTLE,  12.0, 5.5),
        (END,     12.0, 5.5),
    ):
        vol.inputs["Density"].default_value = dens
        vol.inputs["Density"].keyframe_insert("default_value", frame=fr)
        vol.inputs["Emission Strength"].default_value = emit
        vol.inputs["Emission Strength"].keyframe_insert("default_value", frame=fr)

    return cube


def render_setup(path="//renders/squeeze/sq_"):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = START, END
    sc.render.filepath = path
    sc.render.film_transparent = True            # RGBA for compositing
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "16"
    sc.render.use_motion_blur = False            # EffectCraft owns the blur
    bpy.data.objects["Cam"].data.dof.use_dof = False
    bd = bpy.data.objects.get("Backdrop")
    if bd:
        bd.visible_camera = False                # refracted, never in the plate
    sc.cycles.samples = 128
    sc.cycles.transmission_bounces = 18
    sc.cycles.volume_bounces = 2
    sc.cycles.blur_glossy = 1.5
    return sc


if __name__ == "__main__":
    animate_squeeze()
    render_setup()
    print("SQUEEZE_RIGGED_OK")
