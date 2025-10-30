"""
Export utilities for baked actions (e.g., FBX).
"""

import bpy
from ..utils.logging_utils import get_logger


def export_action_to_fbx(armature, filepath: str) -> bool:
    """
    Export armature with action to FBX.
    
    Args:
        armature: Armature object with action
        filepath: Output FBX path
    
    Returns:
        True if successful
    """
    logger = get_logger()
    
    try:
        # Select only the armature
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        
        # Export FBX
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            bake_anim=True,
            add_leaf_bones=False
        )
        
        logger.info(f"Exported action to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"FBX export failed: {str(e)}")
        return False
