"""
Info panel for Live Mocap addon.
"""

import bpy
from bpy.types import Panel


class MOCAP_PT_InfoPanel(Panel):
    """Information and help panel in the 3D Viewport sidebar."""
    
    bl_label = "Info"
    bl_idname = "MOCAP_PT_info_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mocap'
    bl_parent_id = "MOCAP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Live Mocap with MediaPipe", icon='INFO')
        
        col = box.column(align=True)
        col.label(text="Real-time motion capture using:")
        col.label(text="• Webcam input")
        col.label(text="• MediaPipe landmarks")
        col.label(text="• Automatic bone retargeting")
        
        box.separator()
        
        col = box.column(align=True)
        col.label(text="Supported tracking:")
        col.label(text="• Pose (33 landmarks)")
        col.label(text="• Hands (21 per hand)")
        col.label(text="• Face (468 landmarks)")
        
        box.separator()
        
        row = box.row()
        row.operator("mocap.show_help", icon='HELP', text="View Documentation")
