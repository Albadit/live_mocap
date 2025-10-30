"""Apply rest offset operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_ApplyRestOffset(Operator):
    """Compute initial offsets between landmarks and bones"""
    bl_idname = "mocap.apply_rest_offset"
    bl_label = "Apply Rest Offset"
    bl_description = "Compute rest pose offsets for better retargeting"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # TODO: Implement rest offset computation
        self.report({'INFO'}, "Rest offset applied (placeholder)")
        return {'FINISHED'}
