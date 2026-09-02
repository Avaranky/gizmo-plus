import bpy


class GIZMOPLUS_PT_main(bpy.types.Panel):
    bl_label = "Gizmo Plus"
    bl_idname = "GIZMOPLUS_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Gizmo Plus"

    @classmethod
    def poll(cls, context):
        addon = context.preferences.addons.get(__package__)

        return (
            addon is not None
            and addon.preferences.show_n_panel
        )

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.label(text="Enable or disable Gizmo Plus")
        layout.prop(preferences, "enabled")

        layout.label(text="Time allowed for additional input after G / R / S")
        layout.prop(preferences, "activation_delay")


def register_panel():
    bpy.utils.register_class(GIZMOPLUS_PT_main)


def unregister_panel():
    bpy.utils.unregister_class(GIZMOPLUS_PT_main)
