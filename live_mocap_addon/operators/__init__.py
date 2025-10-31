"""
Operators package.
"""

first_startup = "bpy" not in locals()

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
from . import select_target
from . import autofill_map
from . import clear_map
from . import save_map
from . import load_map
from . import add_mapping
from . import remove_mapping
from . import add_camera_index
from . import remove_camera_index
from . import capture_start
from . import capture_stop
from . import record_start
from . import record_stop
from . import bake_action
from . import zero_pose
from . import apply_rest_offset
from . import show_help
from . import install_dependencies
from . import toggle_camera_feed

if first_startup:
    pass
else:
    import importlib
    importlib.reload(select_target)
    importlib.reload(autofill_map)
    importlib.reload(clear_map)
    importlib.reload(save_map)
    importlib.reload(load_map)
    importlib.reload(add_mapping)
    importlib.reload(remove_mapping)
    importlib.reload(add_camera_index)
    importlib.reload(remove_camera_index)
    importlib.reload(capture_start)
    importlib.reload(capture_stop)
    importlib.reload(record_start)
    importlib.reload(record_stop)
    importlib.reload(bake_action)
    importlib.reload(zero_pose)
    importlib.reload(apply_rest_offset)
    importlib.reload(show_help)
    importlib.reload(install_dependencies)
    importlib.reload(toggle_camera_feed)
