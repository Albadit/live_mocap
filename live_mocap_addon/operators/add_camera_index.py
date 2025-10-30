"""Add camera index operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_AddCameraIndex(Operator):
    """Add a new camera index to the list"""
    bl_idname = "mocap.add_camera_index"
    bl_label = "Add Camera Index"
    bl_description = "Add a new camera index for multi-camera capture"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        # Add new camera index
        new_cam = settings.camera_indices.add()
        
        # Set default index to the next available number
        if len(settings.camera_indices) > 0:
            new_cam.index = len(settings.camera_indices) - 1
        else:
            new_cam.index = 0
        
        self.report({'INFO'}, f"Added camera index {new_cam.index}")
        return {'FINISHED'}
