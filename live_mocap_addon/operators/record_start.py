"""Start recording operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_RecordStart(Operator):
    """Start recording keyframes"""
    bl_idname = "mocap.record_start"
    bl_label = "Record"
    bl_description = "Start recording keyframes"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if not settings.is_capturing:
            self.report({'ERROR'}, "Start capture first")
            return {'CANCELLED'}
        
        settings.is_recording = True
        settings.start_frame = context.scene.frame_current
        settings.recorded_frames = 0
        
        self.report({'INFO'}, "Recording started")
        return {'FINISHED'}
