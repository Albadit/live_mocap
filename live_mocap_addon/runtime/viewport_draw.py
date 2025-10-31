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
_current_pose_landmarks = None
_current_hand_landmarks = None
_current_face_landmarks = None


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


def update_landmarks(pose_landmarks=None, hand_landmarks=None, face_landmarks=None):
    """
    Update the landmarks to draw.
    
    Args:
        pose_landmarks: MediaPipe pose landmarks object
        hand_landmarks: MediaPipe hand landmarks list
        face_landmarks: MediaPipe face landmarks list
    """
    global _current_pose_landmarks, _current_hand_landmarks, _current_face_landmarks
    _current_pose_landmarks = pose_landmarks
    _current_hand_landmarks = hand_landmarks
    _current_face_landmarks = face_landmarks


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


def draw_pose_landmarks_2d():
    """Draw MediaPipe pose landmarks as 2D overlay with depth-based sizing."""
    global _current_pose_landmarks, _camera_texture
    
    if _current_pose_landmarks is None:
        return
    
    try:
        from ..runtime.trackers import POSE_CONNECTIONS, DISABLED_POSE_LANDMARKS, DEPTH_CONFIG, DRAW_CONFIG
        
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
        
        # Prepare vertices for landmarks - single pass
        landmark_positions = []
        landmark_depths = []
        visible_indices = []  # Only store indices of visible landmarks
        
        try:
            for idx, landmark in enumerate(_current_pose_landmarks):
                # Skip disabled landmarks early
                if idx in DISABLED_POSE_LANDMARKS:
                    landmark_positions.append(None)
                    landmark_depths.append(0)
                    continue
                
                # Skip if not visible enough
                visibility = landmark.visibility if hasattr(landmark, 'visibility') else 1.0
                if visibility < 0.5:
                    landmark_positions.append(None)
                    landmark_depths.append(0)
                    continue
                
                # Convert normalized coordinates to screen space
                x = margin + (landmark.x * feed_width)
                y = margin + ((1.0 - landmark.y) * feed_height)
                
                # Check bounds before clamping (faster)
                if not (margin <= x <= margin + feed_width and margin <= y <= margin + feed_height):
                    landmark_positions.append(None)
                    landmark_depths.append(0)
                    continue
                
                z_depth = landmark.z if hasattr(landmark, 'z') else 0.0
                
                landmark_positions.append((x, y))
                landmark_depths.append(z_depth)
                visible_indices.append(idx)
                
        except (TypeError, AttributeError) as e:
            print(f"ERROR: Cannot iterate landmarks: {e}")
            return
        
        if not visible_indices:
            return
        
        # Filter connections to exclude disabled landmarks - build once
        line_vertices = []
        for connection in POSE_CONNECTIONS:
            idx1, idx2 = connection[0], connection[1]
            if (idx1 not in DISABLED_POSE_LANDMARKS and idx2 not in DISABLED_POSE_LANDMARKS and
                idx1 < len(landmark_positions) and idx2 < len(landmark_positions) and
                landmark_positions[idx1] is not None and landmark_positions[idx2] is not None):
                line_vertices.append(landmark_positions[idx1])
                line_vertices.append(landmark_positions[idx2])
        
        # Draw all connections in one batch
        if line_vertices:
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {"pos": line_vertices})
            
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(DRAW_CONFIG['pose']['connection']['thickness'])
            
            shader.bind()
            color = tuple(c / 255.0 for c in DRAW_CONFIG['pose']['connection']['color']) + (0.9,)
            shader.uniform_float("color", color)
            batch.draw(shader)
            gpu.state.blend_set('NONE')
        
        # Draw landmarks with depth-based sizing - batch by size for efficiency
        if visible_indices:
            # Calculate depth normalization once
            visible_depths = [landmark_depths[idx] for idx in visible_indices]
            z_min = min(visible_depths)
            z_max = max(visible_depths)
            z_range = z_max - z_min if z_max != z_min else 1
            
            # Get config values once
            radius_min, radius_max = DEPTH_CONFIG['radius_range']
            landmark_color = DRAW_CONFIG['pose']['landmark']['color']
            color = tuple(c / 255.0 for c in landmark_color) + (1.0,)
            
            gpu.state.blend_set('ALPHA')
            shader = gpu.shader.from_builtin('SMOOTH_COLOR')
            shader.bind()
            
            # Group landmarks by size (3 size categories for batching)
            size_groups = [[], [], []]  # small, medium, large
            
            for idx in visible_indices:
                pos = landmark_positions[idx]
                depth = landmark_depths[idx]
                
                # Normalize z value
                normalized_z = 1 - ((depth - z_min) / z_range)
                circle_radius = (radius_min + (normalized_z * (radius_max - radius_min))) * 2
                
                # Categorize by size
                if circle_radius < 6:
                    size_groups[0].append(pos)
                elif circle_radius < 10:
                    size_groups[1].append(pos)
                else:
                    size_groups[2].append(pos)
            
            # Draw each size group in batch
            sizes = [4, 8, 12]
            for group_idx, positions in enumerate(size_groups):
                if positions:
                    colors = [color] * len(positions)
                    batch = batch_for_shader(shader, 'POINTS', {
                        "pos": positions,
                        "color": colors
                    })
                    gpu.state.point_size_set(sizes[group_idx])
                    batch.draw(shader)
            
            gpu.state.blend_set('NONE')
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to draw pose landmarks: {str(e)}")


def draw_hand_landmarks_2d():
    """Draw MediaPipe hand landmarks as 2D overlay."""
    global _current_hand_landmarks, _camera_texture
    
    if _current_hand_landmarks is None:
        return
    
    try:
        from ..runtime.dependency_check import safe_import_mediapipe
        mp = safe_import_mediapipe()
        if mp is None:
            return
        
        from ..runtime.trackers import DRAW_CONFIG
        
        # Get viewport dimensions
        if _camera_texture and 'width' in _camera_texture and 'height' in _camera_texture:
            cam_width = _camera_texture['width']
            cam_height = _camera_texture['height']
            aspect_ratio = cam_width / cam_height if cam_height > 0 else 4/3
        else:
            aspect_ratio = 4 / 3
        
        feed_height = 240
        feed_width = int(feed_height * aspect_ratio)
        margin = 10
        
        # Pre-calculate hand connections once
        hand_connections = mp.solutions.hands.HAND_CONNECTIONS
        
        # Draw each hand
        for hand_idx, hand_landmarks in enumerate(_current_hand_landmarks):
            # Determine if left or right hand
            config_key = 'left_hand' if hand_idx % 2 == 0 else 'right_hand'
            
            landmark_positions = []
            try:
                for landmark in hand_landmarks.landmark:
                    x = margin + (landmark.x * feed_width)
                    y = margin + ((1.0 - landmark.y) * feed_height)
                    # Only add if within bounds
                    if margin <= x <= margin + feed_width and margin <= y <= margin + feed_height:
                        landmark_positions.append((x, y))
                    else:
                        landmark_positions.append(None)
            except (TypeError, AttributeError):
                continue
            
            if not any(landmark_positions):
                continue
            
            # Draw hand connections in one batch
            line_vertices = []
            for connection in hand_connections:
                idx1, idx2 = connection[0], connection[1]
                if (idx1 < len(landmark_positions) and idx2 < len(landmark_positions) and
                    landmark_positions[idx1] is not None and landmark_positions[idx2] is not None):
                    line_vertices.append(landmark_positions[idx1])
                    line_vertices.append(landmark_positions[idx2])
            
            if line_vertices:
                shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {"pos": line_vertices})
                gpu.state.blend_set('ALPHA')
                gpu.state.line_width_set(DRAW_CONFIG[config_key]['connection']['thickness'])
                shader.bind()
                color = tuple(c / 255.0 for c in DRAW_CONFIG[config_key]['connection']['color']) + (0.9,)
                shader.uniform_float("color", color)
                batch.draw(shader)
                gpu.state.blend_set('NONE')
            
            # Draw hand landmarks in one batch
            valid_positions = [pos for pos in landmark_positions if pos is not None]
            if valid_positions:
                gpu.state.blend_set('ALPHA')
                shader = gpu.shader.from_builtin('SMOOTH_COLOR')
                shader.bind()
                landmark_color = DRAW_CONFIG[config_key]['landmark']['color']
                color = tuple(c / 255.0 for c in landmark_color) + (1.0,)
                colors = [color] * len(valid_positions)
                circle_radius = DRAW_CONFIG[config_key]['landmark']['circle_radius'] * 2
                
                batch = batch_for_shader(shader, 'POINTS', {
                    "pos": valid_positions,
                    "color": colors
                })
                gpu.state.point_size_set(circle_radius)
                batch.draw(shader)
                gpu.state.blend_set('NONE')
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to draw hand landmarks: {str(e)}")


def draw_face_landmarks_2d():
    """Draw MediaPipe face landmarks as 2D overlay (optimized for 468 landmarks)."""
    global _current_face_landmarks, _camera_texture
    
    if _current_face_landmarks is None:
        return
    
    try:
        from ..runtime.dependency_check import safe_import_mediapipe
        mp = safe_import_mediapipe()
        if mp is None:
            return
        
        from ..runtime.trackers import DRAW_CONFIG
        
        # Get viewport dimensions
        if _camera_texture and 'width' in _camera_texture and 'height' in _camera_texture:
            cam_width = _camera_texture['width']
            cam_height = _camera_texture['height']
            aspect_ratio = cam_width / cam_height if cam_height > 0 else 4/3
        else:
            aspect_ratio = 4 / 3
        
        feed_height = 240
        feed_width = int(feed_height * aspect_ratio)
        margin = 10
        
        # Pre-calculate face mesh connections once (only get contours for performance)
        # FACEMESH_TESSELATION has too many connections, use FACEMESH_CONTOURS instead
        try:
            face_connections = mp.solutions.face_mesh.FACEMESH_CONTOURS
        except:
            # Fallback to tesselation if contours not available
            face_connections = mp.solutions.face_mesh.FACEMESH_TESSELATION
        
        # Draw each face
        for face_landmarks in _current_face_landmarks:
            # Convert all landmarks in one pass
            landmark_positions = []
            try:
                for landmark in face_landmarks.landmark:
                    x = margin + (landmark.x * feed_width)
                    y = margin + ((1.0 - landmark.y) * feed_height)
                    # Only add if within bounds
                    if margin <= x <= margin + feed_width and margin <= y <= margin + feed_height:
                        landmark_positions.append((x, y))
                    else:
                        landmark_positions.append(None)
            except (TypeError, AttributeError):
                continue
            
            if not any(landmark_positions):
                continue
            
            # Draw face mesh connections in one batch
            line_vertices = []
            for connection in face_connections:
                idx1, idx2 = connection[0], connection[1]
                if (idx1 < len(landmark_positions) and idx2 < len(landmark_positions) and
                    landmark_positions[idx1] is not None and landmark_positions[idx2] is not None):
                    line_vertices.append(landmark_positions[idx1])
                    line_vertices.append(landmark_positions[idx2])
            
            if line_vertices:
                shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {"pos": line_vertices})
                gpu.state.blend_set('ALPHA')
                gpu.state.line_width_set(1)  # Thin lines for face
                shader.bind()
                color = tuple(c / 255.0 for c in DRAW_CONFIG['face']['connection']['color']) + (0.3,)  # More transparent
                shader.uniform_float("color", color)
                batch.draw(shader)
                gpu.state.blend_set('NONE')
            
            # Skip drawing individual face landmarks (468 points is too much)
            # Only draw connections for performance
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to draw face landmarks: {str(e)}")


def draw_callback():
    """Main draw callback function."""
    try:
        # Draw camera feed
        draw_camera_feed()
        
        # Draw all landmark overlays
        draw_pose_landmarks_2d()
        draw_hand_landmarks_2d()
        draw_face_landmarks_2d()
        
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
    global _draw_handler, _camera_texture, _current_frame
    global _current_pose_landmarks, _current_hand_landmarks, _current_face_landmarks
    
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
    _current_pose_landmarks = None
    _current_hand_landmarks = None
    _current_face_landmarks = None


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
