"""
Main panel for Live Mocap addon.
"""

import bpy
from bpy.types import Panel


class MOCAP_PT_MainPanel(Panel):
    """Main panel for Live Mocap in the 3D Viewport sidebar."""
    
    bl_label = "Live Mocap"
    bl_idname = "MOCAP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mocap'
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.mocap_settings
        
        # ========== Armature Mapping Section ==========
        self.draw_armature_mapping_section(layout, settings)
        
        # ========== MediaPipe Settings Section ==========
        self.draw_mediapipe_settings_section(layout, settings)
        
        # ========== Capture Section ==========
        self.draw_capture_section(layout, settings, context)
        
        # ========== Record Section ==========
        self.draw_record_section(layout, settings)
    
    def draw_armature_mapping_section(self, layout, settings):
        """Draw the Armature Mapping section."""
        box = layout.box()
        box.label(text="Armature Mapping", icon='ARMATURE_DATA')
        
        # Source and Target selection
        row = box.row()
        row.prop(settings, "source_model", text="Source")
        
        row = box.row(align=True)
        row.prop(settings, "target_armature", text="Target")
        
        # Show mapping controls only when both source and target are selected
        if settings.source_model and settings.target_armature:
            box.separator()
            
            # Additional settings
            row = box.row()
            row.prop(settings, "coord_space")

            row = box.row(align=True)
            row.prop(settings, "motion_scale")
            row.prop(settings, "z_offset")

            row = box.row(align=True)
            row.operator("mocap.autofill_bone_map", text="Build Bone List", icon='BONE_DATA')
            row.operator("mocap.clear_bone_map", text="", icon='X')
            
            box.separator()

            # Bone mapping list (only show if bones have been built)
            if len(settings.bone_mappings) > 0:
                row = box.row()
                row.template_list(
                    "MOCAP_UL_BoneMappingList", "Bone List",
                    settings, "bone_mappings",
                    settings, "bone_mapping_index",
                    rows=1, maxrows=10
                )

                # Utilities
                row = box.row(align=True)
                row.operator("mocap.zero_pose", icon='LOOP_BACK')
                row.operator("mocap.apply_rest_offset", icon='ORIENTATION_GIMBAL')

                box.separator()

                row = box.row(align=True)
                row.label(text="Bone mapping:")
                row.operator("mocap.save_bone_map", icon='EXPORT')
                row.operator("mocap.load_bone_map", icon='IMPORT')
    
    def draw_mediapipe_settings_section(self, layout, settings):
        """Draw the MediaPipe Advanced Settings section."""
        box = layout.box()
        box.label(text="MediaPipe Settings", icon='SETTINGS')
        
        row = box.row()
        row.prop(settings, "mp_delegate")
        
        row = box.row()
        row.prop(settings, "mp_model_complexity")
        
        row = box.row()
        row.prop(settings, "mp_num_poses")
        
        box.separator()
        box.label(text="Confidence Thresholds:", icon='SHADERFX')

        row = box.row()
        row.prop(settings, "mp_min_detection_confidence", slider=True)
        
        row = box.row()
        row.prop(settings, "mp_min_presence_confidence", slider=True)
        
        row = box.row()
        row.prop(settings, "mp_min_tracking_confidence", slider=True)
        
        box.separator()
        box.label(text="Smoothing:", icon='SMOOTHCURVE')
        
        row = box.row()
        row.prop(settings, "smoothing", slider=True)

    def draw_capture_section(self, layout, settings, context):
        """Draw the Capture section."""
        from ..runtime import dependency_check
        
        # Re-check dependencies to ensure fresh status
        dependency_check.check_dependencies()
        
        box = layout.box()
        box.label(text="Capture", icon='CAMERA_DATA')
        
        # Camera indices list
        row = box.row()
        row.label(text="Camera Indices:")
        row.operator("mocap.add_camera_index", text="", icon='ADD')
        
        if len(settings.camera_indices) > 0:
            for idx, cam in enumerate(settings.camera_indices):
                row = box.row(align=True)
                row.prop(cam, "index", text=f"Camera {idx+1}")
                op = row.operator("mocap.remove_camera_index", text="", icon='X')
                op.index = idx
        else:
            row = box.row()
            row.label(text="No cameras added", icon='INFO')
        
        box.separator()
        
        row = box.row()
        row.prop(settings, "target_fps")
        
        row = box.row()
        row.prop(settings, "show_camera_feed")
        
        row = box.row(align=True)
        row.prop(settings, "use_pose", toggle=True)
        row.prop(settings, "use_hands", toggle=True)
        row.prop(settings, "use_face", toggle=True)
        
        row = box.row(align=True)
        
        if not settings.is_capturing:
            op = row.operator("mocap.capture_start", icon='PLAY')
            # Button is enabled if dependencies are available, target armature is set,
            # at least one camera is added, and at least one bone mapping exists
            row.enabled = (
                dependency_check.all_dependencies_available() and 
                settings.target_armature is not None and
                len(settings.camera_indices) > 0 and
                len(settings.bone_mappings) > 0
            )
        else:
            row.operator("mocap.capture_stop", icon='PAUSE')
        
        # Status display
        if settings.is_capturing:
            status_box = box.box()
            status_box.label(text=settings.status_message, icon='INFO')
            
            row = status_box.row()
            row.label(text=f"Dropped: {settings.dropped_frames}")
            row.label(text=f"Latency: {settings.avg_latency:.1f}ms")
    
    def draw_record_section(self, layout, settings):
        """Draw the Record section."""
        box = layout.box()
        box.label(text="Record", icon='REC')
        
        row = box.row(align=True)
        
        if not settings.is_recording:
            row.operator("mocap.record_start", icon='RADIOBUT_OFF')
            row.enabled = settings.is_capturing
        else:
            row.operator("mocap.record_stop", icon='RADIOBUT_ON')
        
        row.operator("mocap.bake_action", icon='ACTION')
        
        if settings.is_recording:
            row = box.row()
            row.label(text=f"Frames: {settings.recorded_frames}", icon='KEYFRAME')