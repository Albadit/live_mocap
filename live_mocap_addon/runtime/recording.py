"""
Keyframe recording and action baking.
"""

import bpy
from datetime import datetime
from typing import Optional

from ..utils.logging_utils import get_logger


class KeyframeRecorder:
    """Handles keyframe insertion during recording."""
    
    def __init__(self, armature):
        """
        Initialize recorder.
        
        Args:
            armature: Target armature object
        """
        self.armature = armature
        self.start_frame = 1
        self.frame_count = 0
        self.logger = get_logger()
    
    def start(self, start_frame: int = 1):
        """
        Start recording.
        
        Args:
            start_frame: Frame to start recording at
        """
        self.start_frame = start_frame
        self.frame_count = 0
        self.logger.info(f"Recording started at frame {start_frame}")
    
    def insert_keyframe(self, bone_name: str, location: bool = True, 
                       rotation: bool = True, frame: Optional[int] = None):
        """
        Insert keyframe for a bone.
        
        Args:
            bone_name: Name of the bone
            location: Insert location keyframe
            rotation: Insert rotation keyframe
            frame: Frame number (None = current scene frame)
        """
        if bone_name not in self.armature.pose.bones:
            return
        
        bone = self.armature.pose.bones[bone_name]
        
        if frame is None:
            frame = bpy.context.scene.frame_current
        
        try:
            if location:
                bone.keyframe_insert(data_path="location", frame=frame)
            
            if rotation:
                bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            
            self.frame_count += 1
            
        except Exception as e:
            self.logger.error(f"Keyframe insertion failed for {bone_name}: {str(e)}")
    
    def stop(self):
        """Stop recording."""
        self.logger.info(f"Recording stopped. Total frames: {self.frame_count}")
    
    def get_frame_count(self) -> int:
        """Get number of frames recorded."""
        return self.frame_count


def create_action(armature, name: Optional[str] = None) -> bpy.types.Action:
    """
    Create a new action for the armature.
    
    Args:
        armature: Target armature
        name: Action name (auto-generated if None)
    
    Returns:
        Created action
    """
    if name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"Mediapipe_Capture_{timestamp}"
    
    action = bpy.data.actions.new(name=name)
    
    if not armature.animation_data:
        armature.animation_data_create()
    
    armature.animation_data.action = action
    
    return action


def bake_action(armature, start_frame: int, end_frame: int, 
               clean: bool = True) -> bool:
    """
    Bake and clean up the action.
    
    Args:
        armature: Target armature
        start_frame: Start frame
        end_frame: End frame
        clean: Whether to clean/simplify keyframes
    
    Returns:
        True if successful
    """
    logger = get_logger()
    
    try:
        # Ensure action exists
        if not armature.animation_data or not armature.animation_data.action:
            logger.error("No action to bake")
            return False
        
        # Optional: Clean up keyframes (simplify)
        if clean:
            # TODO: Implement keyframe cleanup/simplification
            pass
        
        logger.info(f"Action baked: {armature.animation_data.action.name}")
        return True
        
    except Exception as e:
        logger.error(f"Bake failed: {str(e)}")
        return False
