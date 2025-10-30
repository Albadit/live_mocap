"""Add bone mapping operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_AddBoneMapping(Operator):
    """Add a new bone mapping entry"""
    bl_idname = "mocap.add_bone_mapping"
    bl_label = "Add Mapping"
    bl_description = "Add a new bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        mapping = settings.bone_mappings.add()
        mapping.landmark_name = "NEW_LANDMARK"
        mapping.bone_name = ""
        mapping.enabled = True
        settings.bone_mapping_index = len(settings.bone_mappings) - 1
        return {'FINISHED'}
