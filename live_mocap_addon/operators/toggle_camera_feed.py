"""Toggle camera feed visibility operator."""
import bpy
from bpy.types import Operator


class MOCAP_OT_ToggleCameraFeed(Operator):
    """Toggle camera feed visibility in viewport"""
    bl_idname = "mocap.toggle_camera_feed"
    bl_label = "Toggle Camera Feed"
    bl_description = "Show/hide camera feed and landmarks in 3D Viewport"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        
        # Toggle the property
        settings.show_camera_feed = not settings.show_camera_feed
        
        # Update viewport
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        status = "shown" if settings.show_camera_feed else "hidden"
        self.report({'INFO'}, f"Camera feed {status}")
        
        return {'FINISHED'}
