"""Save bone mappings operator."""
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import os

from ..io.json_maps import save_bone_map, get_default_map_directory


class MOCAP_OT_SaveBoneMap(Operator):
    """Save bone mappings to JSON file"""
    bl_idname = "mocap.save_bone_map"
    bl_label = "Save Map"
    bl_description = "Save bone mappings to JSON file"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(subtype="FILE_PATH")
    
    def invoke(self, context, event):
        # Get default directory
        blend_filepath = bpy.data.filepath
        maps_dir = get_default_map_directory(blend_filepath)
        
        if blend_filepath:
            os.makedirs(maps_dir, exist_ok=True)
            self.filepath = os.path.join(maps_dir, "bone_map.json")
        else:
            self.filepath = "bone_map.json"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        # Build mapping data
        mappings_data = []
        for mapping in settings.bone_mappings:
            mappings_data.append({
                "landmark": mapping.landmark_name,
                "bone": mapping.bone_name,
                "enabled": mapping.enabled
            })
        
        # Save
        if save_bone_map(mappings_data, self.filepath):
            self.report({'INFO'}, f"Saved mappings to {self.filepath}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to save mappings")
            return {'CANCELLED'}
