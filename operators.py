import time

import bpy

from bpy.types import Operator


MOUSE_THRESHOLD = 4


class GIZMOPLUS_OT_transform_base(Operator):
    """Base operator for Gizmo Plus transforms"""

    tool_id = ""

    @classmethod
    def poll(cls, context):
        return (
            context.area is not None
            and context.area.ui_type in {"VIEW_3D", "UV"}
            and __package__ in context.preferences.addons
        )

    def invoke(self, context, event):
        self.trigger_key = event.type
        self.mouse_origin = (event.mouse_x, event.mouse_y)
        self.area_type = context.area.ui_type
        self.phase = "KEYPRESS"
        self.wait_started = 0.0

        bpy.ops.wm.tool_set_by_id(name=self.tool_id)

        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        preferences = context.preferences.addons[
            __package__
        ].preferences

        if not preferences.enabled:
            return {"FINISHED", "PASS_THROUGH"}

        if event.type == "ESC":
            return {"CANCELLED"}

        if self.phase == "KEYPRESS":
            return self._keypress_phase(context, event)

        if (
            time.monotonic() - self.wait_started
            >= preferences.activation_delay
        ):
            return {"FINISHED", "PASS_THROUGH"}

        if event.value == "PRESS" and event.type in {"X", "Y", "Z"}:
            if self.area_type == "UV" and event.type == "Z":
                return {"PASS_THROUGH"}

            if event.ctrl or event.alt or event.oskey:
                return {"PASS_THROUGH"}

            constraint_axis = {
                "X": (True, False, False),
                "Y": (False, True, False),
                "Z": (False, False, True),
            }[event.type]

            if event.shift:
                constraint_axis = tuple(
                    not axis for axis in constraint_axis
                )

            self._invoke_transform(
                constraint_axis=constraint_axis,
            )

            return {"FINISHED"}

        if (
            event.value == "PRESS"
            and event.type == self.trigger_key
        ):
            if self._handle_repeat(context):
                return {"FINISHED"}

            return {"FINISHED", "PASS_THROUGH"}

        return {"PASS_THROUGH"}

    def _keypress_phase(self, context, event):
        if event.type == "MOUSEMOVE":
            delta_x = abs(self.mouse_origin[0] - event.mouse_x)
            delta_y = abs(self.mouse_origin[1] - event.mouse_y)

            if (
                delta_x > MOUSE_THRESHOLD
                or delta_y > MOUSE_THRESHOLD
            ):
                self._invoke_transform()
                return {"FINISHED"}

        if (
            event.type == self.trigger_key
            and event.value == "RELEASE"
        ):
            preferences = context.preferences.addons[
                __package__
            ].preferences

            if preferences.activation_delay <= 0.0:
                return {"FINISHED"}

            self.phase = "WAIT"
            self.wait_started = time.monotonic()

            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _invoke_transform(self, **kwargs):
        raise NotImplementedError

    def _handle_repeat(self, context):
        return False


class GIZMOPLUS_OT_move(GIZMOPLUS_OT_transform_base):
    bl_idname = "gizmo_plus.move"
    bl_label = "Move"

    tool_id = "builtin.move"

    def _invoke_transform(self, **kwargs):
        bpy.ops.transform.translate(
            "INVOKE_DEFAULT",
            **kwargs,
        )

    def _handle_repeat(self, context):
        if (
            self.area_type == "VIEW_3D"
            and context.mode == "EDIT_MESH"
        ):
            bpy.ops.transform.vert_slide("INVOKE_DEFAULT")
            return True

        return False


class GIZMOPLUS_OT_rotate(GIZMOPLUS_OT_transform_base):
    bl_idname = "gizmo_plus.rotate"
    bl_label = "Rotate"

    tool_id = "builtin.rotate"

    def _invoke_transform(self, **kwargs):
        bpy.ops.transform.rotate(
            "INVOKE_DEFAULT",
            **kwargs,
        )

    def _handle_repeat(self, context):
        if self.area_type != "VIEW_3D":
            return False

        bpy.ops.transform.trackball("INVOKE_DEFAULT")
        return True


class GIZMOPLUS_OT_scale(GIZMOPLUS_OT_transform_base):
    bl_idname = "gizmo_plus.scale"
    bl_label = "Scale"

    tool_id = "builtin.scale"

    def _invoke_transform(self, **kwargs):
        bpy.ops.transform.resize(
            "INVOKE_DEFAULT",
            **kwargs,
        )


CLASSES = (
    GIZMOPLUS_OT_move,
    GIZMOPLUS_OT_rotate,
    GIZMOPLUS_OT_scale,
)


def register_operators():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister_operators():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
