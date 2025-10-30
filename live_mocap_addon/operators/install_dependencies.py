"""Install dependencies operator using Rokoko-style library manager."""
import bpy
from bpy.types import Operator
import traceback


class MOCAP_OT_InstallDependencies(Operator):
    """Install missing dependencies (opencv-python and mediapipe)"""
    bl_idname = "mocap.install_dependencies"
    bl_label = "Install Dependencies"
    bl_description = "Automatically install opencv-python and mediapipe"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from ..runtime import library_manager, dependency_check
        
        # Install the libraries using library manager
        try:
            print("\n" + "=" * 70)
            print("Installing dependencies for Live Mocap ...")
            print("=" * 70)
            
            missing = library_manager.lib_manager.install_libraries(
                dependency_check.REQUIRED_LIBRARIES
            )
            
            if missing:
                error_str = (
                    f"Failed to install the following libraries: {', '.join(missing)}"
                    f"\nTry running Blender as an admin and install the libraries again."
                    f"\nSee console for more information."
                )
                self.report({'ERROR'}, error_str)
                return {'CANCELLED'}
            
        except Exception as e:
            trace = traceback.format_exc()
            error_str = (
                f"Unable to install the libraries!"
                f"\nTry running Blender as an admin and install the libraries again."
                f"\n\nFull Error: \n\n{trace}"
            )
            self.report({'ERROR'}, error_str)
            return {'CANCELLED'}
        
        # Note: Don't try to import the libraries here - they won't be available until Blender restarts
        # The dependency check will run automatically on next startup
        
        self.report({'WARNING'}, 'Dependencies installed! Please RESTART Blender to use the add-on.')
        print("\n" + "=" * 70)
        print("IMPORTANT: Please restart Blender to complete installation!")
        print("=" * 70 + "\n")
        
        return {'FINISHED'}
