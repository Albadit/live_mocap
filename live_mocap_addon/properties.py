"""
Property groups for addon state and bone mappings.
"""

import bpy
from bpy.props import (
    StringProperty, IntProperty, FloatProperty, BoolProperty,
    EnumProperty, CollectionProperty, PointerProperty
)
from bpy.types import PropertyGroup, UIList


class MOCAP_PG_BoneMapping(PropertyGroup):
    """Single bone mapping entry (MediaPipe landmark → Armature bone)."""
    
    rig_bone_name: StringProperty(
        name="Rig Bone",
        description="Rig bone name (e.g., Head, LeftUpperArm)",
        default=""
    )
    
    landmark_name: StringProperty(
        name="Landmark",
        description="MediaPipe landmark name (auto-linked from rig bone)",
        default=""
    )
    
    bone_name: StringProperty(
        name="Bone",
        description="Target armature bone name",
        default=""
    )
    
    enabled: BoolProperty(
        name="Enabled",
        description="Enable this mapping",
        default=True
    )


class MOCAP_PG_CameraIndex(PropertyGroup):
    """Single camera index entry for multi-camera support."""
    
    index: IntProperty(
        name="Camera Index",
        description="Webcam device index",
        default=0,
        min=0,
        max=10
    )


class MOCAP_PG_Settings(PropertyGroup):
    """Main settings property group for the mocap addon."""
    
    # ========== Source Selection ==========
    source_model: EnumProperty(
        name="Source",
        description="MediaPipe model to use for tracking",
        items=[
            ('POSE', "Pose Landmarks", "Track body pose (33 landmarks)"),
            ('HAND', "Hand Landmarks", "Track hands (21 landmarks per hand)"),
            ('FACE', "Face Landmarks", "Track face (468 landmarks)"),
            ('ALL', "All Landmarks", "Track pose, hands, and face"),
        ],
        default='POSE'
    )
    
    # ========== Target ==========
    target_armature: PointerProperty(
        type=bpy.types.Object,
        name="Target Armature",
        description="Armature to apply motion capture to",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    
    coord_space: EnumProperty(
        name="Coordinate Space",
        items=[
            ('WORLD', "World", "World space coordinates"),
            ('ARMATURE_LOCAL', "Armature Local", "Armature local space"),
            ('BONE_LOCAL', "Bone Local", "Bone local space"),
        ],
        default='WORLD'
    )
    
    motion_scale: FloatProperty(
        name="Scale",
        description="Overall motion scale multiplier",
        default=1.0,
        min=0.01,
        max=10.0
    )
    
    z_offset: FloatProperty(
        name="Z-Up Offset",
        description="Vertical offset for retargeting",
        default=0.0,
        min=-5.0,
        max=5.0
    )
    
    # ========== Bone Mapping ==========
    bone_mappings: CollectionProperty(type=MOCAP_PG_BoneMapping)
    bone_mapping_index: IntProperty(default=0)
    
    # ========== Capture Settings ==========
    camera_indices: CollectionProperty(type=MOCAP_PG_CameraIndex)
    camera_index_active: IntProperty(default=0)
    
    target_fps: IntProperty(
        name="FPS",
        description="Target frames per second",
        default=30,
        min=1,
        max=120
    )
    
    use_pose: BoolProperty(
        name="Use Pose",
        description="Enable pose tracking (body landmarks)",
        default=True
    )
    
    use_hands: BoolProperty(
        name="Use Hands",
        description="Enable hand tracking",
        default=False
    )
    
    use_face: BoolProperty(
        name="Use Face",
        description="Enable face tracking",
        default=False
    )
    
    # ========== Status ==========
    is_capturing: BoolProperty(
        name="Is Capturing",
        description="Whether capture is currently active",
        default=False
    )
    
    is_recording: BoolProperty(
        name="Is Recording",
        description="Whether keyframe recording is active",
        default=False
    )
    
    status_message: StringProperty(
        name="Status Message",
        description="Current status message",
        default="Ready"
    )
    
    # ========== Filters ==========
    smoothing: FloatProperty(
        name="Smoothing",
        description="EWMA smoothing factor (0=no smoothing, 1=max smoothing)",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    min_confidence: FloatProperty(
        name="Min Confidence",
        description="Minimum confidence threshold for landmarks",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    foot_lock_threshold: FloatProperty(
        name="Foot Lock Threshold",
        description="Threshold for foot locking (0=disabled)",
        default=0.0,
        min=0.0,
        max=0.5
    )
    
    # ========== Recording ==========
    start_frame: IntProperty(
        name="Start Frame",
        description="Frame where recording started",
        default=1
    )
    
    recorded_frames: IntProperty(
        name="Recorded Frames",
        description="Number of frames recorded",
        default=0
    )
    
    # ========== Performance ==========
    dropped_frames: IntProperty(
        name="Dropped Frames",
        description="Number of dropped frames",
        default=0
    )
    
    avg_latency: FloatProperty(
        name="Average Latency",
        description="Average frame processing latency in milliseconds",
        default=0.0
    )


class MOCAP_UL_BoneMappingList(UIList):
    """UI List for bone mappings."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        """Draw a single list item."""
        settings = context.scene.mocap_settings
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            # First column: Show rig bone name (e.g., "Head", "LeftUpperArm")
            row.label(text=item.rig_bone_name if item.rig_bone_name else item.landmark_name, icon='ARMATURE_DATA')
            
            # Second column: Show bone selector if target armature is set
            if settings.target_armature and settings.target_armature.type == 'ARMATURE':
                row.prop_search(item, "bone_name", settings.target_armature.data, "bones", text="", icon='BONE_DATA')
            else:
                row.prop(item, "bone_name", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.rig_bone_name if item.rig_bone_name else item.landmark_name)
