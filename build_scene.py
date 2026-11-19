"""Skwizy spot - scene build. Run inside Blender."""
import bpy, math

W, H, FPS = 1920, 1080, 24

# ---------------------------------------------------------------- scene reset
def wipe():
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
                 bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            coll.remove(item)


def all_fcurves(action):
    """Blender 5.x slotted actions: fcurves live under layers > strips > channelbag."""
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


def ease(action, kind="LINEAR"):
    for fc in all_fcurves(action):
        for kp in fc.keyframe_points:
            kp.interpolation = kind


def set_engine(name):
    """scene.render.engine under-reports; let the TypeError list the options."""
    try:
        bpy.context.scene.render.engine = name
        return name
    except TypeError as e:
        print("engine options:", e)
        raise


def setup():
    sc = bpy.context.scene
    set_engine("CYCLES")
    sc.cycles.device = "GPU"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.render.resolution_x = W
    sc.render.resolution_y = H
    sc.render.fps = FPS
    sc.render.film_transparent = False
    # smooth gradients quantise badly at 8-bit: the plate shows contour banding
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.dither_intensity = 2.0
    # the signature of the reference: very long shutter
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 1.0
    # graphic emission, not photoreal lighting: AgX desaturates the palette
    sc.view_settings.view_transform = "Standard"
    return sc


# ---------------------------------------------------------------- background
# Reference structure: one dark corner, a bright bloom, a white falloff.
# Hue shifted off Dropbox blue into violet -> magenta -> coral.
PALETTE_DARK = [
    (0.00, (0.010, 0.016, 0.090, 1)),   # near-black navy
    (0.38, (0.060, 0.120, 0.620, 1)),   # deep blue
    (0.62, (0.160, 0.350, 0.950, 1)),   # electric blue
    (0.84, (0.600, 0.780, 1.000, 1)),   # pale blue
    (1.00, (1.000, 1.000, 1.000, 1)),   # white
]


def gradient_bg(stops, name="BG"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    # noise Fac clusters around 0.5; stretch it so the palette reaches both ends
    contrast = nt.nodes.new("ShaderNodeMapRange")
    contrast.inputs["From Min"].default_value = 0.33
    contrast.inputs["From Max"].default_value = 0.72
    contrast.clamp = True
    noise = nt.nodes.new("ShaderNodeTexNoise")
    mapping = nt.nodes.new("ShaderNodeMapping")
    coord = nt.nodes.new("ShaderNodeTexCoord")

    # big soft blobs, not detail
    noise.inputs["Scale"].default_value = 1.4
    noise.inputs["Detail"].default_value = 1.0
    noise.inputs["Roughness"].default_value = 0.35
    noise.inputs["Distortion"].default_value = 0.6

    el = ramp.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    el[0].position, el[0].color = stops[0]
    for pos, col in stops[1:]:
        e = el.new(pos)
        e.color = col

    emit.inputs["Strength"].default_value = 1.15

    nt.links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], contrast.inputs["Value"])
    nt.links.new(contrast.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat, mapping


def build_bg():
    # camera sits at -Y looking up +Y, so "behind" is +Y, not -Z
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 14, 0))
    plane = bpy.context.object
    plane.name = "Backdrop"
    plane.scale = (46, 26, 1)
    plane.rotation_euler = (math.radians(90), 0, 0)
    mat, mapping = gradient_bg(PALETTE_DARK)
    plane.data.materials.append(mat)

    # drift the gradient so the bloom moves through the shot
    mapping.inputs["Location"].default_value = (0, 0, 0)
    mapping.inputs["Location"].keyframe_insert("default_value", frame=1)
    mapping.inputs["Location"].default_value = (0.55, 0.30, 0.0)
    mapping.inputs["Location"].keyframe_insert("default_value", frame=120)
    ease(mat.node_tree.animation_data.action, "LINEAR")
    return plane


# ---------------------------------------------------------------- camera
def build_camera():
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 50
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 10.0
    cam_data.dof.aperture_fstop = 1.4
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0, -10, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = cam
    return cam


if __name__ == "__main__":
    wipe()
    setup()
    build_bg()
    build_camera()
    print("SKWIZY_BUILD_OK")
