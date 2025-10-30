"""Load bone mappings operator."""
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import os

from ..io.json_maps import load_bone_map, get_default_map_directory


class MOCAP_OT_LoadBoneMap(Operator):
    """Load bone mappings from JSON file"""
    bl_idname = "mocap.load_bone_map"
    bl_label = "Load Map"
    bl_description = "Load bone mappings from JSON file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(subtype="FILE_PATH")
    
    def invoke(self, context, event):
        # Default to mocap_maps directory
        blend_filepath = bpy.data.filepath
        maps_dir = get_default_map_directory(blend_filepath)
        
        if blend_filepath and os.path.exists(maps_dir):
            self.filepath = maps_dir
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        # Load
        mappings_data = load_bone_map(self.filepath)
        
        if not mappings_data:
            self.report({'ERROR'}, "Failed to load mappings")
            return {'CANCELLED'}
        
        # Clear and rebuild
        settings.bone_mappings.clear()
        
        for data in mappings_data:
            mapping = settings.bone_mappings.add()
            mapping.landmark_name = data.get("landmark", "")
            mapping.bone_name = data.get("bone", "")
            mapping.enabled = data.get("enabled", True)
        
        self.report({'INFO'}, f"Loaded {len(mappings_data)} mappings")
        return {'FINISHED'}
