import bpy

from bpy.app.handlers import persistent


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


def _perform_keymap_registration():
    if addon_keymaps:
        return True

    window_manager = bpy.context.window_manager

    if window_manager is None:
        return False

    addon_keyconfig = window_manager.keyconfigs.addon
    user_keyconfig = window_manager.keyconfigs.user

    if addon_keyconfig is None or user_keyconfig is None:
        return False

    registered = False

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
                prop.identifier != "rna_type"
                and item.properties.is_property_set(prop.identifier)
                for prop in item.properties.bl_rna.properties
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
            registered = True

    return registered


@persistent
def _keymaps_load_post_handler(dummy):
    if _perform_keymap_registration():
        if _keymaps_load_post_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(
                _keymaps_load_post_handler
            )


def register_keymaps():
    if _perform_keymap_registration():
        return

    if _keymaps_load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(
            _keymaps_load_post_handler
        )


def unregister_keymaps():
    if _keymaps_load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(
            _keymaps_load_post_handler
        )

    for keymap, item in reversed(addon_keymaps):
        try:
            keymap.keymap_items.remove(item)
        except ReferenceError:
            pass

    addon_keymaps.clear()