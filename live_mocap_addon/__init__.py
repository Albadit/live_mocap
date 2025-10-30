"""
Live Motion Capture with MediaPipe + OpenCV for Blender
========================================================
Real-time motion capture using webcam, MediaPipe, and OpenCV with bone retargeting.

Main add-on entry point - Blender loads this file directly.
"""

# Important plugin info for Blender
bl_info = {
    "name": "Live Mocap",
    "author": "AI Assistant",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Mocap",
    "description": "Real-time motion capture using MediaPipe and OpenCV",
    "doc_url": "https://github.com/your-repo/live-mocap-addon#readme",
    "category": "Animation",
}

first_startup = "bpy" not in locals()
import bpy
import sys

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
# This lets you do adjustments to the plugin on the fly without having to restart Blender
from . import addon_prefs
from . import properties
from . import panels
from . import operators
from . import runtime
from . import io
from . import utils

if first_startup:
    pass
else:
    import importlib
    importlib.reload(addon_prefs)
    importlib.reload(properties)
    importlib.reload(panels)
    importlib.reload(operators)
    importlib.reload(runtime)
    importlib.reload(io)
    importlib.reload(utils)


absolute_min_ver = (3, 6, 0)
soft_min_ver = (4, 0, 0)


# List of all classes to register
classes_panels = [
    panels.main.MOCAP_PT_MainPanel,
    panels.dependency.MOCAP_PT_DependencyPanel,
    panels.info.MOCAP_PT_InfoPanel,
]

classes_properties = [
    properties.MOCAP_PG_BoneMapping,
    properties.MOCAP_PG_CameraIndex,
    properties.MOCAP_PG_Settings,
    properties.MOCAP_UL_BoneMappingList,
]

classes_operators = [
    operators.select_target.MOCAP_OT_SelectTarget,
    operators.autofill_map.MOCAP_OT_AutoFillBoneMap,
    operators.clear_map.MOCAP_OT_ClearBoneMap,
    operators.save_map.MOCAP_OT_SaveBoneMap,
    operators.load_map.MOCAP_OT_LoadBoneMap,
    operators.add_mapping.MOCAP_OT_AddBoneMapping,
    operators.remove_mapping.MOCAP_OT_RemoveBoneMapping,
    operators.add_camera_index.MOCAP_OT_AddCameraIndex,
    operators.remove_camera_index.MOCAP_OT_RemoveCameraIndex,
    operators.capture_start.MOCAP_OT_CaptureStart,
    operators.capture_stop.MOCAP_OT_CaptureStop,
    operators.record_start.MOCAP_OT_RecordStart,
    operators.record_stop.MOCAP_OT_RecordStop,
    operators.bake_action.MOCAP_OT_BakeAction,
    operators.zero_pose.MOCAP_OT_ZeroPose,
    operators.apply_rest_offset.MOCAP_OT_ApplyRestOffset,
    operators.show_help.MOCAP_OT_ShowHelp,
    operators.install_dependencies.MOCAP_OT_InstallDependencies,
]

classes_preferences = [
    addon_prefs.MOCAP_AP_Preferences,
]

# Combine all classes
classes_all = classes_preferences + classes_properties + classes_operators + classes_panels


def register_classes(classes):
    """Register a list of classes."""
    register_count = 0
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            register_count += 1
        except ValueError:
            print(f"Error: Failed to register class {cls}")
            pass
    
    if register_count < len(classes):
        print(f'Skipped {len(classes) - register_count} MOCAP classes.')


def unregister_classes(classes):
    """Unregister a list of classes."""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            print(f"Error: Failed to unregister class {cls}")
            pass


def check_unsupported_blender_versions():
    """Check for unsupported Blender versions."""
    # Don't allow Blender versions older than 3.6
    if bpy.app.version < absolute_min_ver:
        unregister()
        sys.tracebacklimit = 0
        raise ImportError(
            '\n\nBlender versions older than 3.6 are not supported by Live Mocap. '
            '\nPlease use Blender 3.6 or later.'
            '\n'
        )


def register():
    """Register all addon components."""
    print("\n### Loading Live Mocap for Blender...")
    
    # Check for unsupported Blender versions
    check_unsupported_blender_versions()
    
    # Register all classes
    register_classes(classes_all)
    
    # Register scene properties
    bpy.types.Scene.mocap_settings = bpy.props.PointerProperty(
        type=properties.MOCAP_PG_Settings
    )
    
    # Initialize runtime
    runtime.initialize()
    
    print("### Loaded Live Mocap for Blender successfully!\n")


def unregister():
    """Unregister all addon components."""
    print("### Unloading Live Mocap for Blender...")
    
    # Cleanup runtime
    runtime.cleanup()
    
    # Unregister scene properties
    if hasattr(bpy.types.Scene, 'mocap_settings'):
        del bpy.types.Scene.mocap_settings
    
    # Unregister all classes
    unregister_classes(classes_all)
    
    print("### Unloaded Live Mocap for Blender successfully!\n")


if __name__ == "__main__":
    register()
