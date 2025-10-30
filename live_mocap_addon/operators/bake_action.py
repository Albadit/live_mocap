"""Bake action operator."""
import bpy
from bpy.types import Operator

from ..runtime.recording import create_action, bake_action


class MOCAP_OT_BakeAction(Operator):
    """Bake recorded motion to an action"""
    bl_idname = "mocap.bake_action"
    bl_label = "Bake to Action"
    bl_description = "Finalize recording as an action on the target armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature")
            return {'CANCELLED'}
        
        armature = settings.target_armature
        
        # Create action
        action = create_action(armature)
        
        # Bake (optional cleanup)
        start_frame = settings.start_frame
        end_frame = start_frame + settings.recorded_frames
        bake_action(armature, start_frame, end_frame, clean=True)
        
        self.report({'INFO'}, f"Created action: {action.name}")
        return {'FINISHED'}
