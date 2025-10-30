"""Remove camera index operator."""
import bpy
from bpy.types import Operator
from bpy.props import IntProperty


class MOCAP_OT_RemoveCameraIndex(Operator):
    """Remove a camera index from the list"""
    bl_idname = "mocap.remove_camera_index"
    bl_label = "Remove Camera Index"
    bl_description = "Remove a camera index from the capture list"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(
        name="Index",
        description="Index of camera to remove",
        default=0
    )
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if 0 <= self.index < len(settings.camera_indices):
            settings.camera_indices.remove(self.index)
            self.report({'INFO'}, f"Removed camera at index {self.index}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Invalid camera index")
            return {'CANCELLED'}
