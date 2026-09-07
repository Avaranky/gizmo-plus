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

        # EN:
        # Keep Gizmo Plus alive while Blender's native transform operator
        # is running. Finishing this operator too early would release the
        # cursor grab used by the native transform.
        #
        # RU:
        # Оставляем Gizmo Plus активным, пока работает нативный оператор
        # трансформации Blender. Если завершить наш оператор слишком рано,
        # Blender снимет захват курсора, используемый нативной трансформацией.
        if self.phase == "TRANSFORM":
            if self._native_transform_running(context):
                return {"RUNNING_MODAL", "PASS_THROUGH"}

            return {"FINISHED", "PASS_THROUGH"}

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

            # EN:
            # Do not finish Gizmo Plus here. Switch to TRANSFORM phase
            # and let the native transform own the interaction.
            #
            # RU:
            # Не завершаем Gizmo Plus здесь. Переходим в фазу TRANSFORM
            # и позволяем нативной трансформации управлять взаимодействием.
            self.phase = "TRANSFORM"

            return {"RUNNING_MODAL", "PASS_THROUGH"}

        if (
            event.value == "PRESS"
            and event.type == self.trigger_key
        ):
            if self._handle_repeat(context):
                # EN:
                # Repeat transforms such as Vert Slide and Trackball also
                # start native modal operators, so the same rule applies.
                #
                # RU:
                # Повторные операции вроде Vert Slide и Trackball тоже
                # запускают нативные modal-операторы, поэтому правило то же.
                self.phase = "TRANSFORM"
                return {"RUNNING_MODAL", "PASS_THROUGH"}

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

                # EN:
                # Previously this returned FINISHED immediately after
                # starting Blender's transform. That could release the
                # continuous cursor grab. Keep this operator alive instead.
                #
                # RU:
                # Раньше сразу после запуска трансформации Blender здесь
                # возвращался FINISHED. Это могло снять непрерывный захват
                # курсора. Теперь наш оператор остаётся активным.
                self.phase = "TRANSFORM"

                return {"RUNNING_MODAL", "PASS_THROUGH"}

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

    # EN:
    # Check whether Blender still has a native TRANSFORM_OT_* modal
    # operator running in the current window.
    #
    # RU:
    # Проверяем, работает ли в текущем окне нативный modal-оператор
    # Blender семейства TRANSFORM_OT_*.
    def _native_transform_running(self, context):
        return any(
            op is not self
            and op.bl_idname.startswith("TRANSFORM_OT_")
            for op in context.window.modal_operators
        )

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
