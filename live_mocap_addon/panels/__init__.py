"""
Panels package for Live Mocap addon.
"""

first_startup = "bpy" not in locals()

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
from . import main
from . import dependency
from . import info

if first_startup:
    pass
else:
    import importlib
    importlib.reload(main)
    importlib.reload(dependency)
    importlib.reload(info)
