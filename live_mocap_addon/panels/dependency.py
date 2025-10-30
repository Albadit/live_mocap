"""
Dependency status panel for Live Mocap addon.
"""

import bpy
from bpy.types import Panel


class MOCAP_PT_DependencyPanel(Panel):
    """Dependency status panel in the 3D Viewport sidebar."""
    
    bl_label = "Dependencies"
    bl_idname = "MOCAP_PT_dependency_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mocap'
    bl_parent_id = "MOCAP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        from ..runtime import dependency_check
        
        # Re-check dependencies on each draw to ensure fresh status
        dependency_check.check_dependencies()
        
        layout = self.layout
        box = layout.box()
        
        if dependency_check.all_dependencies_available():
            row = box.row()
            row.label(text="✓ All installed", icon='CHECKMARK')
            
            dep_info = dependency_check.get_dependency_info()
            for pkg, (available, version) in dep_info.items():
                if available:
                    row = box.row()
                    pkg_display = "OpenCV" if pkg == "cv2" else "MediaPipe"
                    row.label(text=f"  {pkg_display}: v{version}")
        else:
            row = box.row()
            row.alert = True
            row.label(text="Missing dependencies!", icon='ERROR')
            row = box.row()
            row.label(text=dependency_check.get_error_message())
            
            row = box.row()
            row.operator("mocap.show_help", icon='HELP', text="Installation Guide")
