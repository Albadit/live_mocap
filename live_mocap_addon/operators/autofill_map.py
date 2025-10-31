"""Auto-fill bone mappings operator."""
import bpy
from bpy.types import Operator

from ..runtime.mapping import auto_map_bones


class MOCAP_OT_AutoFillBoneMap(Operator):
    """Auto-fill bone mappings based on common naming conventions"""
    bl_idname = "mocap.autofill_bone_map"
    bl_label = "Auto-Fill Bone Map"
    bl_description = "Automatically map MediaPipe landmarks to armature bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        armature = settings.target_armature
        if armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected object is not an armature")
            return {'CANCELLED'}
        
        # Get all bone names
        bone_names = [bone.name for bone in armature.data.bones]
        
        # Auto-map
        mappings = auto_map_bones(bone_names)
        
        # Clear and rebuild
        settings.bone_mappings.clear()
        
        matched_count = 0
        empty_count = 0
        
        for rig_bone_name, bone_data in mappings.items():
            # bone_data format: {"landmark": "LANDMARK_NAME", "bone": "matched_bone_name" or None}
            landmark_name = bone_data.get("landmark")
            matched_bone = bone_data.get("bone")
            
            # Always add the mapping with the landmark
            mapping = settings.bone_mappings.add()
            mapping.rig_bone_name = rig_bone_name  # e.g., "Head", "LeftUpperArm"
            mapping.landmark_name = landmark_name  # e.g., "NOSE", "LEFT_SHOULDER"
            
            # Set bone name if found (exact match only), otherwise leave empty
            if matched_bone and matched_bone in bone_names:
                mapping.bone_name = matched_bone  # e.g., "head", "upper_arm.L"
                mapping.enabled = True
                matched_count += 1
            else:
                mapping.bone_name = ""  # Leave empty if no exact match
                mapping.enabled = False  # Disable by default if no bone matched
                empty_count += 1
        
        if empty_count > 0:
            self.report({'INFO'}, f"Built bone list: {matched_count} matched, {empty_count} need manual selection")
        else:
            self.report({'INFO'}, f"Mapped {matched_count} bones automatically")
        return {'FINISHED'}
