"""Select target armature operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_SelectTarget(Operator):
    """Select active object as target armature"""
    bl_idname = "mocap.select_target"
    bl_label = "Select Target"
    bl_description = "Set the active object as the target armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if not context.active_object:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        if context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature")
            return {'CANCELLED'}
        
        settings.target_armature = context.active_object
        self.report({'INFO'}, f"Target set to: {context.active_object.name}")
        return {'FINISHED'}
