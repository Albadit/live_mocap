"""Show help operator."""
import bpy
from bpy.types import Operator
import subprocess
import sys

from ..runtime import dependency_check


class MOCAP_OT_ShowHelp(Operator):
    """Show help and dependency information"""
    bl_idname = "mocap.show_help"
    bl_label = "Help / Dependency Check"
    bl_description = "Show installation help and check dependencies"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Live Mocap - Help", icon='INFO')
        layout.separator()
        
        # Dependency status
        box = layout.box()
        box.label(text="Dependencies:", icon='PACKAGE')
        
        dep_info = dependency_check.get_dependency_info()
        
        for pkg, (available, version) in dep_info.items():
            row = box.row()
            pkg_name = "OpenCV" if pkg == "cv2" else "MediaPipe"
            row.label(text=f"{pkg_name}:")
            
            if available:
                row.label(text=f"✓ {version}", icon='CHECKMARK')
            else:
                row.label(text="✗ Missing", icon='ERROR')
        
        # Installation instructions
        if not dependency_check.all_dependencies_available():
            layout.separator()
            box = layout.box()
            box.label(text="Installation Instructions:", icon='IMPORT')
            
            msg_lines = dependency_check.get_install_instructions().split('\n')
            for line in msg_lines:
                if line.strip():
                    box.label(text=line)
        
        # Usage instructions
        layout.separator()
        box = layout.box()
        box.label(text="Quick Start:", icon='PLAY')
        box.label(text="1. Select an armature and click 'Select Target'")
        box.label(text="2. Click 'Auto-Fill Bone Map' to map bones")
        box.label(text="3. Click 'Start Capture' to begin tracking")
        box.label(text="4. Click 'Record' to start keyframing")
        box.label(text="5. Click 'Bake to Action' when done")
