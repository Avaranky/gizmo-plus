import bpy

from .keymaps import register_keymaps, unregister_keymaps


def update_enabled(self, context):
    if self.enabled:
        register_keymaps()
    else:
        unregister_keymaps()


class GizmoPlusPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    enabled: bpy.props.BoolProperty(
        name="Enabled",
        description="Enable or disable Gizmo Plus",
        default=True,
        update=update_enabled,
    )

    activation_delay: bpy.props.FloatProperty(
        name="Input Timeout",
        description="Time allowed for additional input after pressing G, R, or S",
        default=2.0,
        min=1.0,
        max=5.0,
        precision=1,
        unit="TIME",
    )

    show_n_panel: bpy.props.BoolProperty(
        name="Show N-Panel",
        description="Show the Gizmo Plus tab in the 3D View N-panel",
        default=True,
    )

    show_shortcuts: bpy.props.BoolProperty(
        name="Gizmo Plus Shortcuts",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "activation_delay")
        layout.prop(self, "show_n_panel")

        if not self.enabled:
            return

        layout.separator()

        layout.prop(
            self,
            "show_shortcuts",
            icon="KEYINGSET",
            toggle=True,
        )

        if self.show_shortcuts:
            import rna_keymap_ui

            keyconfig = context.window_manager.keyconfigs.user

            for keymap in keyconfig.keymaps:
                items = [
                    item
                    for item in keymap.keymap_items
                    if item.idname.startswith("gizmo_plus.")
                ]

                if not items:
                    continue

                box = layout.box()
                box.label(text=keymap.name)
                box.context_pointer_set("keymap", keymap)

                for item in items:
                    rna_keymap_ui.draw_kmi(
                        [],
                        keyconfig,
                        keymap,
                        item,
                        box,
                        0,
                    )
