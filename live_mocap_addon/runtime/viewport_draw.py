"""
Draw camera feed and MediaPipe landmarks in 3D Viewport.
"""

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
import numpy as np

from ..utils.logging_utils import get_logger


# Global draw handler
_draw_handler = None
_camera_texture = None
_current_frame = None
_current_landmarks = None


def create_camera_texture(width, height):
    """Create a GPU texture for the camera feed."""
    global _camera_texture
    
    try:
        # Create texture (RGBA format)
        # Note: We'll update this each frame, so just store dimensions for now
        _camera_texture = {
            'width': width,
            'height': height,
            'texture': None
        }
        
        return _camera_texture
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to create camera texture: {str(e)}")
        return None


def update_camera_frame(frame):
    """
    Update the camera texture with a new frame.
    
    Args:
        frame: NumPy array (BGR format from OpenCV)
    """
    global _current_frame, _camera_texture
    
    from ..runtime.dependency_check import safe_import_cv2
    cv2 = safe_import_cv2()
    
    if cv2 is None or frame is None:
        return
    
    try:
        # Convert BGR to RGBA
        frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        
        # Flip vertically for OpenGL coordinate system
        frame_rgba = np.flipud(frame_rgba)
        
        # Store current frame
        _current_frame = frame_rgba
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to update camera frame: {str(e)}")


def update_landmarks(landmarks):
    """
    Update the landmarks to draw.
    
    Args:
        landmarks: MediaPipe landmarks object
    """
    global _current_landmarks
    _current_landmarks = landmarks


def draw_camera_feed():
    """Draw the camera feed as a texture in the viewport."""
    global _current_frame, _camera_texture
    
    if _current_frame is None and _camera_texture is None:
        return
    
    try:
        # Get viewport dimensions
        region = bpy.context.region
        
        # Define dimensions for camera feed
        # Use camera's aspect ratio if available
        if _camera_texture and 'width' in _camera_texture and 'height' in _camera_texture:
            cam_width = _camera_texture['width']
            cam_height = _camera_texture['height']
            aspect_ratio = cam_width / cam_height if cam_height > 0 else 4/3
        else:
            aspect_ratio = 4 / 3  # Default
        
        # Fixed height, calculate width based on aspect ratio
        feed_height = 240
        feed_width = int(feed_height * aspect_ratio)
        margin = 10
        
        x = margin
        y = margin
        
        # Draw background rectangle
        vertices = [
            (x, y),
            (x + feed_width, y),
            (x + feed_width, y + feed_height),
            (x, y + feed_height)
        ]
        
        indices = [(0, 1, 2), (0, 2, 3)]
        
        # Create shader for solid color (background)
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        
        # Enable blending
        gpu.state.blend_set('ALPHA')
        
        # Draw dark background
        shader.bind()
        shader.uniform_float("color", (0.0, 0.0, 0.0, 0.8))
        batch.draw(shader)
        
        # Draw border
        border_vertices = [
            (x-1, y-1),
            (x + feed_width + 1, y-1),
            (x + feed_width + 1, y + feed_height + 1),
            (x-1, y + feed_height + 1),
            (x-1, y-1)
        ]
        
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": border_vertices})
        gpu.state.line_width_set(2.0)
        shader.bind()
        shader.uniform_float("color", (0.3, 0.3, 0.3, 1.0))
        batch.draw(shader)
        
        gpu.state.blend_set('NONE')
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to draw camera feed: {str(e)}")


def draw_landmarks_2d():
    """Draw MediaPipe landmarks as 2D overlay."""
    global _current_landmarks, _camera_texture
    
    if _current_landmarks is None:
        return
    
    try:
        from ..runtime.trackers import POSE_CONNECTIONS
        
        # Get viewport dimensions
        region = bpy.context.region
        
        # Camera feed dimensions - match the feed size
        # Use camera's aspect ratio if available
        if _camera_texture and 'width' in _camera_texture and 'height' in _camera_texture:
            cam_width = _camera_texture['width']
            cam_height = _camera_texture['height']
            aspect_ratio = cam_width / cam_height if cam_height > 0 else 4/3
        else:
            aspect_ratio = 4 / 3  # Default
        
        # Fixed height, calculate width based on aspect ratio
        feed_height = 240
        feed_width = int(feed_height * aspect_ratio)
        margin = 10
        
        # Prepare vertices for landmarks
        landmark_positions = []
        landmarks_in_bounds = []  # Track which landmarks are visible
        
        # Handle different landmark container types
        # MediaPipe returns RepeatedCompositeContainer which is iterable
        try:
            for idx, landmark in enumerate(_current_landmarks):
                # Convert normalized coordinates to screen space
                x = margin + (landmark.x * feed_width)
                y = margin + ((1.0 - landmark.y) * feed_height)  # Flip Y
                
                # Clamp coordinates to stay within the viewport box
                x = max(margin, min(x, margin + feed_width))
                y = max(margin, min(y, margin + feed_height))
                
                landmark_positions.append((x, y))
                
                # Check if landmark is within original bounds (before clamping)
                original_x = margin + (landmark.x * feed_width)
                original_y = margin + ((1.0 - landmark.y) * feed_height)
                is_in_bounds = (margin <= original_x <= margin + feed_width and 
                               margin <= original_y <= margin + feed_height)
                landmarks_in_bounds.append(is_in_bounds)
                
        except (TypeError, AttributeError) as e:
            print(f"ERROR: Cannot iterate landmarks: {e}")
            return
        
        # Draw connections (lines)
        # Only draw connections where both landmarks are visible (within original bounds)
        if len(landmark_positions) > 0:
            line_vertices = []
            for connection in POSE_CONNECTIONS:
                idx1, idx2 = connection[0], connection[1]
                if (idx1 < len(landmark_positions) and idx2 < len(landmark_positions) and
                    idx1 < len(landmarks_in_bounds) and idx2 < len(landmarks_in_bounds)):
                    # Only draw line if both endpoints are within bounds
                    if landmarks_in_bounds[idx1] and landmarks_in_bounds[idx2]:
                        line_vertices.append(landmark_positions[idx1])
                        line_vertices.append(landmark_positions[idx2])
            
            if line_vertices:
                shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {"pos": line_vertices})
                
                gpu.state.blend_set('ALPHA')
                gpu.state.line_width_set(2.0)
                
                shader.bind()
                shader.uniform_float("color", (0.0, 1.0, 0.0, 0.7))  # Green lines
                batch.draw(shader)
                
                gpu.state.blend_set('NONE')
        
        # Draw landmarks (points)
        # Only draw landmarks that are within bounds
        if landmark_positions and landmarks_in_bounds:
            visible_landmarks = [pos for pos, in_bounds in zip(landmark_positions, landmarks_in_bounds) if in_bounds]
            
            if visible_landmarks:
                shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'POINTS', {"pos": visible_landmarks})
                
                gpu.state.blend_set('ALPHA')
                gpu.state.point_size_set(5.0)
                
                shader.bind()
                shader.uniform_float("color", (1.0, 0.0, 0.0, 0.9))  # Red points
                batch.draw(shader)
                
                gpu.state.blend_set('NONE')
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to draw landmarks: {str(e)}")


def draw_callback():
    """Main draw callback function."""
    try:
        # Draw camera feed
        draw_camera_feed()
        
        # Draw landmarks overlay
        draw_landmarks_2d()
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Draw callback error: {str(e)}")
        import traceback
        traceback.print_exc()


def register_draw_handler():
    """Register the draw handler for viewport drawing."""
    global _draw_handler
    
    if _draw_handler is not None:
        return  # Already registered
    
    try:
        # Register draw handler for 2D overlay in VIEW_3D
        _draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback,
            (),
            'WINDOW',
            'POST_PIXEL'
        )
        
        logger = get_logger()
        logger.info("Viewport draw handler registered")
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to register draw handler: {str(e)}")
        import traceback
        traceback.print_exc()


def unregister_draw_handler():
    """Unregister the draw handler."""
    global _draw_handler, _camera_texture, _current_frame, _current_landmarks
    
    if _draw_handler is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
            _draw_handler = None
            
            logger = get_logger()
            logger.info("Viewport draw handler unregistered")
            
        except Exception as e:
            logger = get_logger()
            logger.error(f"Failed to unregister draw handler: {str(e)}")
    
    # Cleanup
    _camera_texture = None
    _current_frame = None
    _current_landmarks = None


def is_draw_handler_active():
    """Check if draw handler is currently active."""
    return _draw_handler is not None


# Utility functions for drawing in 3D space (optional)
def draw_landmarks_3d(positions, scale=1.0):
    """
    Draw landmarks in 3D space for debugging.
    
    Args:
        positions: List of Vector positions in 3D space
        scale: Scale factor for visualization
    """
    if not positions:
        return
    
    try:
        # Prepare vertices
        vertices = [(p.x, p.y, p.z) for p in positions]
        
        # Draw points
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'POINTS', {"pos": vertices})
        
        gpu.state.blend_set('ALPHA')
        gpu.state.point_size_set(10.0)
        
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 0.0, 0.8))  # Yellow points
        batch.draw(shader)
        
        gpu.state.blend_set('NONE')
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to draw 3D landmarks: {str(e)}")
