"""Clear bone mappings operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_ClearBoneMap(Operator):
    """Clear all bone mappings"""
    bl_idname = "mocap.clear_bone_map"
    bl_label = "Clear Map"
    bl_description = "Clear all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        settings.bone_mappings.clear()
        self.report({'INFO'}, "Bone mappings cleared")
        return {'FINISHED'}
