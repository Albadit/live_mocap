"""Start capture modal operator."""
import bpy
from bpy.types import Operator
import time

from ..runtime.capture import CameraCapture
from ..runtime.trackers import MediaPipeTrackers
from ..runtime.retarget import (
    landmarks_to_positions, normalize_skeleton_scale,
    compute_spine_position, compute_bone_rotation_from_chain
)
from ..runtime.mapping import get_next_landmark_in_chain
from ..runtime.filters import MultiFilter
from ..runtime import dependency_check
from ..runtime import viewport_draw


class MOCAP_OT_CaptureStart(Operator):
    """Start live motion capture from webcam"""
    bl_idname = "mocap.capture_start"
    bl_label = "Start Capture"
    bl_description = "Start capturing motion from webcam (requires at least one camera)"
    bl_options = {'REGISTER'}
    
    _timer = None
    _camera = None
    _trackers = None
    _filters = {}
    _frame_interval = 1.0 / 30.0
    
    @classmethod
    def poll(cls, context):
        """Check if operator can run."""
        settings = context.scene.mocap_settings
        # Require at least one camera and at least one bone mapping in the list
        return len(settings.camera_indices) > 0 and len(settings.bone_mappings) > 0
    
    def modal(self, context, event):
        settings = context.scene.mocap_settings
        
        if event.type == 'ESC' or not settings.is_capturing:
            self.cancel(context)
            return {'CANCELLED'}
        
        if event.type == 'TIMER':
            self.process_frame(context)
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        settings = context.scene.mocap_settings
        
        # Check dependencies
        if not dependency_check.all_dependencies_available():
            self.report({'ERROR'}, "Missing dependencies. Check panel for details.")
            return {'CANCELLED'}
        
        # Check target
        if not settings.target_armature:
            self.report({'ERROR'}, "No target armature selected")
            return {'CANCELLED'}
        
        # Switch to Pose Mode with the target armature
        armature = settings.target_armature
        if armature:
            # Make sure we're in object mode first
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            # Select and make active the target armature
            armature.select_set(True)
            context.view_layer.objects.active = armature
            # Switch to Pose Mode
            bpy.ops.object.mode_set(mode='POSE')
        
        # Get camera index (use first camera from list, or default to 0)
        camera_index = 0
        if len(settings.camera_indices) > 0:
            camera_index = settings.camera_indices[0].index
        
        # Initialize camera
        self._camera = CameraCapture(camera_index, settings.target_fps)
        if not self._camera.open():
            self.report({'ERROR'}, f"Failed to open camera {camera_index}")
            return {'CANCELLED'}
        
        # Initialize trackers
        self._trackers = MediaPipeTrackers(
            use_pose=settings.use_pose,
            use_hands=settings.use_hands,
            use_face=settings.use_face,
            min_confidence=settings.min_confidence
        )
        
        if not self._trackers.initialize():
            self._camera.release()
            self.report({'ERROR'}, "Failed to initialize MediaPipe")
            return {'CANCELLED'}
        
        # Initialize filters for each bone
        self._filters = {}
        for mapping in settings.bone_mappings:
            if mapping.enabled and mapping.bone_name:
                self._filters[mapping.bone_name] = MultiFilter(
                    smoothing_alpha=settings.smoothing,
                    min_confidence=settings.min_confidence,
                    foot_lock_threshold=settings.foot_lock_threshold
                )
        
        # Register viewport draw handler if enabled
        if settings.show_camera_feed:
            print(f"INFO: show_camera_feed is True, registering draw handler...")
            viewport_draw.register_draw_handler()
            
            # Create camera texture for viewport
            width, height = self._camera.get_resolution()
            print(f"INFO: Camera resolution: {width}x{height}")
            if width > 0 and height > 0:
                viewport_draw.create_camera_texture(width, height)
        else:
            print(f"INFO: show_camera_feed is False, skipping draw handler")
        
        # Setup
        settings.is_capturing = True
        settings.status_message = "Capturing..."
        settings.dropped_frames = 0
        self._frame_interval = 1.0 / settings.target_fps
        
        # Add timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(self._frame_interval, window=context.window)
        wm.modal_handler_add(self)
        
        self.report({'INFO'}, "Motion capture started")
        return {'RUNNING_MODAL'}
    
    def process_frame(self, context):
        """Process a single frame."""
        settings = context.scene.mocap_settings
        
        try:
            # Read frame
            frame_result = self._camera.read_frame()
            if not frame_result:
                settings.dropped_frames += 1
                return
            
            success, frame, frame_rgb = frame_result
            
            # Update viewport with camera frame if enabled
            if settings.show_camera_feed:
                viewport_draw.update_camera_frame(frame)
            
            # Process with MediaPipe
            landmarks_result = self._trackers.process_frame(frame_rgb)
            
            # Retarget if we have pose landmarks
            if landmarks_result.pose_landmarks:
                # Update viewport with landmarks if enabled
                if settings.show_camera_feed:
                    viewport_draw.update_landmarks(landmarks_result.pose_landmarks)
                
                self.retarget_pose(context, landmarks_result.pose_landmarks)
            
            # Force viewport redraw if camera feed is enabled
            if settings.show_camera_feed:
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
            
            # Update status
            fps = self._camera.get_average_fps()
            latency = self._camera.get_average_latency()
            settings.avg_latency = latency
            settings.status_message = f"Tracking | FPS: {fps:.1f} | Latency: {latency:.1f}ms"
            
        except Exception as e:
            print(f"Frame processing error: {str(e)}")
            settings.dropped_frames += 1
    
    def retarget_pose(self, context, landmarks):
        """Retarget pose landmarks to bones."""
        settings = context.scene.mocap_settings
        armature = settings.target_armature
        
        if not armature or armature.type != 'ARMATURE':
            print(f"DEBUG: No armature or wrong type: armature={armature}, type={armature.type if armature else None}")
            return
        
        print(f"DEBUG: Retargeting to armature '{armature.name}' with {len(settings.bone_mappings)} mappings")
        
        # Convert to positions
        positions = landmarks_to_positions(
            landmarks,
            scale=settings.motion_scale,
            z_offset=settings.z_offset
        )
        
        # Normalize scale
        if len(positions) > 12:
            scale_factor = normalize_skeleton_scale(positions, (11, 12))
            positions = [p * scale_factor for p in positions]
        
        # Build landmark dict
        from ..runtime.trackers import POSE_LANDMARK_NAMES
        landmark_positions = {}
        for idx, name in POSE_LANDMARK_NAMES.items():
            if idx < len(positions):
                landmark_positions[name] = positions[idx]
        
        # Add computed landmarks
        spine_pos = compute_spine_position(positions)
        if spine_pos:
            landmark_positions["SPINE_PROXY"] = spine_pos
        
        # Apply to bones
        bones_updated = 0
        for mapping in settings.bone_mappings:
            if not mapping.enabled or not mapping.bone_name:
                print(f"DEBUG: Skipping mapping - enabled={mapping.enabled}, bone_name={mapping.bone_name}")
                continue
            
            if mapping.bone_name not in armature.pose.bones:
                print(f"DEBUG: Bone '{mapping.bone_name}' not found in armature")
                continue
            
            bone = armature.pose.bones[mapping.bone_name]
            landmark_name = mapping.landmark_name
            
            if landmark_name not in landmark_positions:
                print(f"DEBUG: Landmark '{landmark_name}' not found in landmark_positions")
                continue
            
            print(f"DEBUG: Updating bone '{mapping.bone_name}' with landmark '{landmark_name}'")
            
            position = landmark_positions[landmark_name]
            
            # Apply filter
            if mapping.bone_name in self._filters:
                is_foot = "ankle" in mapping.bone_name.lower() or "foot" in mapping.bone_name.lower()
                confidence = landmarks[list(POSE_LANDMARK_NAMES.keys())[list(POSE_LANDMARK_NAMES.values()).index(landmark_name)]].visibility if hasattr(landmarks[0], 'visibility') else 1.0
                position = self._filters[mapping.bone_name].filter_position(
                    position, confidence, is_foot
                )
            
            if position is None:
                continue
            
            # ROTATION ONLY - Do not set location to prevent bone stretching
            # bone.location = position  # DISABLED - causes stretching
            
            # Compute rotation from chain
            next_landmark = get_next_landmark_in_chain(landmark_name)
            if next_landmark and next_landmark in landmark_positions:
                end_pos = landmark_positions[next_landmark]
                rotation = compute_bone_rotation_from_chain(position, end_pos)
                
                if rotation:
                    # Apply smoothing only (skip confidence gate to avoid slerp error)
                    if mapping.bone_name in self._filters:
                        try:
                            rotation = self._filters[mapping.bone_name].smoothing.filter(rotation)
                        except Exception as e:
                            print(f"DEBUG: Filter error for {mapping.bone_name}: {e}")
                    
                    # Set rotation only
                    bone.rotation_quaternion = rotation
                    bones_updated += 1
                    print(f"DEBUG: Set rotation for '{mapping.bone_name}'")
            
            # Insert keyframes if recording
            if settings.is_recording:
                # Only keyframe rotation, not location
                bone.keyframe_insert(data_path="rotation_quaternion", frame=context.scene.frame_current)
        
        print(f"DEBUG: Updated {bones_updated} bones this frame")
        
        # Advance frame if recording
        if settings.is_recording:
            context.scene.frame_set(context.scene.frame_current + 1)
            settings.recorded_frames += 1
    
    def cancel(self, context):
        """Cleanup."""
        settings = context.scene.mocap_settings
        
        # Remove timer
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            self._timer = None
        
        # Cleanup camera
        if self._camera:
            self._camera.release()
            self._camera = None
        
        # Cleanup trackers
        if self._trackers:
            self._trackers.cleanup()
            self._trackers = None
        
        # Unregister viewport draw handler
        viewport_draw.unregister_draw_handler()
        
        # Force viewport redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        # Update status
        settings.is_capturing = False
        settings.is_recording = False
        settings.status_message = "Stopped"
        
        self.report({'INFO'}, "Motion capture stopped")
