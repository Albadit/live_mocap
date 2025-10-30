"""
Coordinate transformation utilities for different spaces.
"""

from mathutils import Vector, Matrix, Quaternion
from typing import Tuple


def world_to_local(world_pos: Vector, parent_matrix: Matrix) -> Vector:
    """
    Convert world space position to local space.
    
    Args:
        world_pos: Position in world space
        parent_matrix: Parent object's world matrix
    
    Returns:
        Position in local space
    """
    parent_inv = parent_matrix.inverted()
    return parent_inv @ world_pos


def local_to_world(local_pos: Vector, parent_matrix: Matrix) -> Vector:
    """
    Convert local space position to world space.
    
    Args:
        local_pos: Position in local space
        parent_matrix: Parent object's world matrix
    
    Returns:
        Position in world space
    """
    return parent_matrix @ local_pos


def world_to_bone_local(world_pos: Vector, bone_matrix: Matrix) -> Vector:
    """
    Convert world space position to bone local space.
    
    Args:
        world_pos: Position in world space
        bone_matrix: Bone's world matrix
    
    Returns:
        Position in bone local space
    """
    bone_inv = bone_matrix.inverted()
    return bone_inv @ world_pos


def bone_local_to_world(local_pos: Vector, bone_matrix: Matrix) -> Vector:
    """
    Convert bone local space position to world space.
    
    Args:
        local_pos: Position in bone local space
        bone_matrix: Bone's world matrix
    
    Returns:
        Position in world space
    """
    return bone_matrix @ local_pos


def mediapipe_to_blender(mp_x: float, mp_y: float, mp_z: float, 
                         scale: float = 1.0, 
                         z_offset: float = 0.0) -> Vector:
    """
    Convert MediaPipe normalized coordinates to Blender space.
    
    MediaPipe uses:
    - x: [0, 1] left to right (0.5 is center)
    - y: [0, 1] top to bottom (0.5 is center)
    - z: depth (relative scale, can be negative)
    
    Blender uses:
    - X: left to right
    - Y: depth (forward/back)
    - Z: up/down
    
    Args:
        mp_x: MediaPipe X coordinate [0, 1]
        mp_y: MediaPipe Y coordinate [0, 1]
        mp_z: MediaPipe Z coordinate (depth)
        scale: Overall scale multiplier
        z_offset: Vertical offset in Blender space
    
    Returns:
        Position in Blender coordinate space
    """
    # Center the coordinates
    x = (mp_x - 0.5) * scale
    y = -mp_z * scale  # Depth becomes Y
    z = -(mp_y - 0.5) * scale + z_offset  # Flip Y to Z, add offset
    
    return Vector((x, y, z))


def compute_bone_direction(start_pos: Vector, end_pos: Vector) -> Tuple[Vector, float]:
    """
    Compute direction and length from start to end position.
    
    Args:
        start_pos: Start position
        end_pos: End position
    
    Returns:
        Tuple of (direction_vector, length)
    """
    direction = end_pos - start_pos
    length = direction.length
    
    if length < 0.001:
        return Vector((0, 1, 0)), 0.0
    
    return direction.normalized(), length


def direction_to_quaternion(direction: Vector, up_hint: Vector = None) -> Quaternion:
    """
    Convert a direction vector to a quaternion rotation.
    
    Args:
        direction: Target direction vector
        up_hint: Optional up vector for twist control
    
    Returns:
        Quaternion representing the rotation
    """
    if direction.length < 0.001:
        return Quaternion((1, 0, 0, 0))
    
    direction = direction.normalized()
    
    # Default up vector
    if up_hint is None:
        up_hint = Vector((0, 0, 1))
    else:
        up_hint = up_hint.normalized()
    
    # Build rotation matrix
    forward = direction
    right = forward.cross(up_hint)
    
    # Handle parallel vectors
    if right.length < 0.001:
        alternate = Vector((1, 0, 0)) if abs(up_hint.x) < 0.9 else Vector((0, 1, 0))
        right = forward.cross(alternate)
    
    right = right.normalized()
    up = right.cross(forward).normalized()
    
    # Create rotation matrix
    mat = Matrix((right, forward, up)).transposed()
    mat.resize_4x4()
    
    return mat.to_quaternion()


def quaternion_from_two_vectors(vec_from: Vector, vec_to: Vector) -> Quaternion:
    """
    Compute quaternion rotation from one vector to another.
    
    Args:
        vec_from: Source direction
        vec_to: Target direction
    
    Returns:
        Quaternion that rotates vec_from to vec_to
    """
    vec_from = vec_from.normalized()
    vec_to = vec_to.normalized()
    
    # Handle parallel vectors
    dot = vec_from.dot(vec_to)
    
    if dot > 0.9999:
        return Quaternion((1, 0, 0, 0))
    
    if dot < -0.9999:
        # 180 degree rotation - find perpendicular axis
        if abs(vec_from.x) < 0.9:
            axis = Vector((1, 0, 0))
        else:
            axis = Vector((0, 1, 0))
        
        axis = vec_from.cross(axis).normalized()
        return Quaternion(axis, 3.14159265)  # π radians
    
    # Normal case
    axis = vec_from.cross(vec_to).normalized()
    angle = vec_from.angle(vec_to)
    
    return Quaternion(axis, angle)
