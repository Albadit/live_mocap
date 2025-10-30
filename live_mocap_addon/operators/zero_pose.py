"""Zero pose operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_ZeroPose(Operator):
    """Reset mapped bones to rest pose"""
    bl_idname = "mocap.zero_pose"
    bl_label = "Zero Pose"
    bl_description = "Reset all mapped bones to rest pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature")
            return {'CANCELLED'}
        
        armature = settings.target_armature
        
        for mapping in settings.bone_mappings:
            if mapping.enabled and mapping.bone_name:
                if mapping.bone_name in armature.pose.bones:
                    bone = armature.pose.bones[mapping.bone_name]
                    bone.location = (0, 0, 0)
                    bone.rotation_quaternion = (1, 0, 0, 0)
                    bone.scale = (1, 1, 1)
        
        self.report({'INFO'}, "Reset to rest pose")
        return {'FINISHED'}
