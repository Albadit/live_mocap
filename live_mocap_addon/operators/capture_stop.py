"""Stop capture operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_CaptureStop(Operator):
    """Stop live motion capture"""
    bl_idname = "mocap.capture_stop"
    bl_label = "Stop Capture"
    bl_description = "Stop capturing motion from webcam"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        settings.is_capturing = False
        return {'FINISHED'}
