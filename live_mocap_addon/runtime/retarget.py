"""
Landmark to bone retargeting with math utilities.
"""

from mathutils import Vector, Quaternion
from typing import List, Dict, Optional

from ..utils.coords import (
    mediapipe_to_blender,
    direction_to_quaternion,
    compute_bone_direction
)
from ..utils.logging_utils import get_logger


def landmarks_to_positions(landmarks: List, scale: float = 1.0, 
                           z_offset: float = 0.0) -> List[Vector]:
    """
    Convert MediaPipe landmarks to Blender positions.
    
    Args:
        landmarks: MediaPipe landmark list
        scale: Overall scale factor
        z_offset: Vertical offset
    
    Returns:
        List of Vector positions
    """
    positions = []
    
    for lm in landmarks:
        pos = mediapipe_to_blender(
            lm.x, lm.y, 
            lm.z if hasattr(lm, 'z') else 0.0,
            scale, z_offset
        )
        positions.append(pos)
    
    return positions


def normalize_skeleton_scale(positions: List[Vector], 
                            reference_indices: tuple = (11, 12)) -> float:
    """
    Normalize skeleton scale based on shoulder width.
    
    Args:
        positions: List of landmark positions
        reference_indices: Indices of reference points (shoulders)
    
    Returns:
        Scale factor
    """
    if len(positions) <= max(reference_indices):
        return 1.0
    
    idx1, idx2 = reference_indices
    dist = (positions[idx1] - positions[idx2]).length
    
    if dist < 0.001:
        return 1.0
    
    # Standard shoulder width assumption
    standard_width = 0.4
    return standard_width / dist


def compute_spine_position(positions: List[Vector]) -> Optional[Vector]:
    """
    Compute spine proxy position from hips and shoulders.
    
    Args:
        positions: List of landmark positions
    
    Returns:
        Spine position or None
    """
    # Indices: 23=LEFT_HIP, 24=RIGHT_HIP, 11=LEFT_SHOULDER, 12=RIGHT_SHOULDER
    if len(positions) < 25:
        return None
    
    hip_center = (positions[23] + positions[24]) / 2
    shoulder_center = (positions[11] + positions[12]) / 2
    spine_pos = (hip_center + shoulder_center) / 2
    
    return spine_pos


def compute_bone_rotation_from_chain(start_pos: Vector, end_pos: Vector,
                                     up_hint: Vector = None) -> Quaternion:
    """
    Compute bone rotation from start to end position.
    
    Args:
        start_pos: Start position
        end_pos: End position
        up_hint: Optional up vector
    
    Returns:
        Quaternion rotation
    """
    direction, length = compute_bone_direction(start_pos, end_pos)
    
    if length < 0.001:
        return Quaternion((1, 0, 0, 0))
    
    return direction_to_quaternion(direction, up_hint)
