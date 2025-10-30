"""
Add-on preferences for Live Mocap.
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty

from .runtime import dependency_check


class MOCAP_AP_Preferences(AddonPreferences):
    """Preferences for Live Mocap addon."""
    
    bl_idname = __package__.split('.')[0]  # Get root package name
    
    default_map_folder: StringProperty(
        name="Default Map Folder",
        description="Default folder for saving/loading bone maps",
        default="/mocap_maps/",
        subtype='DIR_PATH'
    )
    
    debug_mode: BoolProperty(
        name="Debug Mode",
        description="Enable debug logging",
        default=False
    )
    
    show_advanced: BoolProperty(
        name="Show Advanced Settings",
        description="Show advanced retargeting options in panel",
        default=False
    )
    
    def draw(self, context):
        layout = self.layout
        
        # Re-check dependencies on each draw to ensure fresh status
        dependency_check.check_dependencies()
        
        # General preferences header
        layout.label(text="General", icon='PREFERENCES')
        
        # Other preferences
        layout.prop(self, "default_map_folder")
        layout.prop(self, "debug_mode")
        layout.prop(self, "show_advanced")
        
        layout.separator()

        # Dependencies header
        layout.label(text="Dependencies", icon='PLUGIN')
        
        # Dependency status section
        box = layout.box()
        
        if dependency_check.all_dependencies_available():
            row = box.row()
            row.label(text="All dependencies installed", icon='CHECKMARK')
            
            # Show versions
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
            row.operator("mocap.install_dependencies", icon='IMPORT')
            row.operator("mocap.show_help", icon='HELP')