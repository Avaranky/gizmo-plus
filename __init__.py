import bpy

from .preferences import GizmoPlusPreferences
from .operators import register_operators, unregister_operators
from .keymaps import register_keymaps, unregister_keymaps
from .panel import register_panel, unregister_panel


def register():
    bpy.utils.register_class(GizmoPlusPreferences)

    register_operators()

    preferences = bpy.context.preferences.addons[__package__].preferences

    if preferences.enabled:
        register_keymaps()

    register_panel()


def unregister():
    unregister_panel()
    unregister_keymaps()
    unregister_operators()

    bpy.utils.unregister_class(GizmoPlusPreferences)
