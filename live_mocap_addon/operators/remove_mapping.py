"""Remove bone mapping operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_RemoveBoneMapping(Operator):
    """Remove selected bone mapping entry"""
    bl_idname = "mocap.remove_bone_mapping"
    bl_label = "Remove Mapping"
    bl_description = "Remove selected bone mapping entry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if len(settings.bone_mappings) > 0:
            settings.bone_mappings.remove(settings.bone_mapping_index)
            settings.bone_mapping_index = max(0, settings.bone_mapping_index - 1)
        
        return {'FINISHED'}
