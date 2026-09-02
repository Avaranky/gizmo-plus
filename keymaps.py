import bpy


KEYMAP_NAMES = (
    "3D View", "Pose", "Object Mode", "Curve", "Curves",
    "Mesh", "Armature", "Metaball", "Lattice", "UV Editor",
)

TRANSFORM_OPERATORS = {
    "transform.translate": "gizmo_plus.move",
    "transform.rotate": "gizmo_plus.rotate",
    "transform.resize": "gizmo_plus.scale",
}

addon_keymaps = []


def register_keymaps():
    if addon_keymaps:
        return

    window_manager = bpy.context.window_manager

    if window_manager is None:
        return

    addon_keyconfig = window_manager.keyconfigs.addon
    user_keyconfig = window_manager.keyconfigs.user

    if addon_keyconfig is None or user_keyconfig is None:
        return

    for name in KEYMAP_NAMES:
        source_keymap = user_keyconfig.keymaps.get(name)

        if source_keymap is None:
            continue

        addon_keymap = None

        for item in list(source_keymap.keymap_items):
            if (
                item.idname not in TRANSFORM_OPERATORS
                or not item.active
                or item.map_type != "KEYBOARD"
            ):
                continue

            if item.properties and any(
                item.properties.is_property_set(prop.identifier)
                for prop in item.properties.bl_rna.properties
                if prop.identifier != "rna_type"
            ):
                continue

            if addon_keymap is None:
                addon_keymap = addon_keyconfig.keymaps.new(
                    name=name,
                    space_type=source_keymap.space_type,
                    region_type=source_keymap.region_type,
                )

            kwargs = {
                key: getattr(item, key)
                for key in (
                    "any", "shift", "ctrl", "alt",
                    "oskey", "key_modifier", "repeat",
                )
            }

            if hasattr(item, "hyper"):
                kwargs["hyper"] = item.hyper

            addon_item = addon_keymap.keymap_items.new(
                TRANSFORM_OPERATORS[item.idname],
                item.type,
                item.value,
                **kwargs,
            )

            addon_keymaps.append((addon_keymap, addon_item))


def unregister_keymaps():
    for keymap, item in reversed(addon_keymaps):
        try:
            keymap.keymap_items.remove(item)
        except ReferenceError:
            pass

    addon_keymaps.clear()
