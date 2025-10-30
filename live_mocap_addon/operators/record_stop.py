"""Stop recording operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_RecordStop(Operator):
    """Stop recording keyframes"""
    bl_idname = "mocap.record_stop"
    bl_label = "Stop Recording"
    bl_description = "Stop recording keyframes"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        settings.is_recording = False
        
        self.report({'INFO'}, f"Recording stopped. {settings.recorded_frames} frames recorded.")
        return {'FINISHED'}
