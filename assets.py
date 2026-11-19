"""Skwizy - 3D assets for compositing in AE. Rendered RGBA over transparent.

Blender's job: geometry, materials, light, and any deformation (the squeeze).
AE's job: type, layout, timing, whips, grade.
"""
import bpy, math

sys_path = "/Users/ariga/Documents/skwizy"


def clear_assets():
    for o in [o for o in bpy.data.objects if o.name not in ("Backdrop", "Cam")]:
        bpy.data.objects.remove(o, do_unlink=True)


# ------------------------------------------------------------ fluted glass
def fluted_glass(name="GlassFluted", tint=(1.00, 0.68, 0.34, 1.0)):
    """Plain blue glass. The ribbing is geometry now (see hero_cube), so the
    shader does not fake it."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    glass = nt.nodes.new("ShaderNodeBsdfGlass")
    glass.inputs["IOR"].default_value = 1.46
    glass.inputs["Roughness"].default_value = 0.0
    # tint multiplies through ~18 plates, so it has to start nearly clear
    glass.inputs["Color"].default_value = tint

    nt.links.new(glass.outputs["BSDF"], out.inputs["Surface"])
    return mat


def inner_substance(parent, scale=0.50):
    """The white mass suspended inside the glass. Without it the cube is just a
    hollow shell refracting the backdrop, which reads thin - the flutes need
    something bright behind them to smear into vertical streaks."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0,
                                          location=parent.location)
    blob = bpy.context.object
    blob.name = "Substance"
    blob.scale = (scale, scale * 0.82, scale * 0.95)
    blob.parent = parent
    blob.matrix_parent_inverse = parent.matrix_world.inverted()

    # irregular, so it doesn't read as a sphere through the glass
    # tighter, stronger noise: a smooth blob stays a smooth blob through the
    # plates, where the reference shatters into an irregular barcode
    tex = bpy.data.textures.new("BlobNoise", "CLOUDS")
    tex.noise_scale = 0.22
    tex.noise_depth = 4
    warp = blob.modifiers.new("Warp", "DISPLACE")
    warp.texture = tex
    warp.texture_coords = "LOCAL"
    warp.strength = 1.25
    warp.mid_level = 0.36
    smooth = blob.modifiers.new("Smooth", "SUBSURF")
    smooth.levels = smooth.render_levels = 2

    mat = bpy.data.materials.new("Substance")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    # thin enough to stay translucent, lit from within so it reads white
    # has to punch through the whole plate stack to read
    vol.inputs["Density"].default_value = 4.5
    vol.inputs["Emission Strength"].default_value = 2.6
    vol.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    blob.data.materials.append(mat)
    return blob


def hero_cube(size=1.6, slabs=28):
    """A stack of thin vertical glass plates, not a cube with a fluted surface.

    That is what the reference actually is: the silhouette is scalloped with
    plate edges, and the ribs run straight across the top face parallel to the
    ones on the front. A bump map cannot do either - it leaves the outline
    perfectly straight.
    """
    w = size / slabs
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    slab = bpy.context.object
    slab.name = "HeroCube"
    slab.dimensions = (w, size, size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # rounds each plate's vertical edges, so every rib acts as a small lens
    bevel = slab.modifiers.new("Bevel", "BEVEL")
    # small: a wide bevel opens see-through gaps between plates, which read as
    # hard black lines the reference does not have
    bevel.width = w * 0.09
    bevel.segments = 4
    bevel.limit_method = "ANGLE"
    bevel.harden_normals = True

    arr = slab.modifiers.new("Stack", "ARRAY")
    arr.count = slabs
    arr.use_relative_offset = True
    arr.relative_offset_displace = (1.0, 0.0, 0.0)

    # the array grows in +X; bring the stack back to centre
    slab.location.x = -(size - w) / 2.0
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    # three-quarter view, as in the reference - dead-on reads as a flat panel
    slab.rotation_euler = (math.radians(14), math.radians(-28), math.radians(6))

    slab.data.materials.append(fluted_glass())
    for poly in slab.data.polygons:
        poly.use_smooth = True
    inner_substance(slab)
    return slab


# ------------------------------------------------------------ lighting
def studio_lights():
    """Glass needs something bright to refract and edge-light it."""
    specs = [
        ("Key",  (-4.0, -3.5,  3.0), 220, 4.0),
        ("Rim",  ( 4.5,  2.0,  2.5), 300, 3.0),
        ("Fill", ( 1.5, -5.0, -2.5),  90, 5.0),
    ]
    made = []
    for name, loc, power, sz in specs:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = power
        data.size = sz
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        bpy.context.collection.objects.link(obj)
        # aim at origin
        d = obj.location.normalized()
        obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        made.append(obj)
    return made


def alpha_setup():
    """RGBA out. The backdrop stays in the scene so the glass has something
    colourful to refract, but it is hidden from camera rays so it never
    lands in the plate."""
    sc = bpy.context.scene
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "16"

    bd = bpy.data.objects.get("Backdrop")
    if bd:
        bd.visible_camera = False
        bd.visible_shadow = False
    return sc


def bounce_setup():
    """Glass wrapped around a volume needs the extra transmission depth."""
    cy = bpy.context.scene.cycles
    cy.max_bounces = 24
    cy.transmission_bounces = 24
    cy.transparent_max_bounces = 24
    cy.volume_bounces = 4


if __name__ == "__main__":
    clear_assets()
    hero_cube()
    bounce_setup()
    studio_lights()
    alpha_setup()
    print("SKWIZY_ASSETS_OK")
