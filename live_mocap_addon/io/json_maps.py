"""
JSON bone map loading and saving.
"""

import json
import os
from typing import Dict, List

from ..utils.logging_utils import get_logger


def get_default_map_directory(blend_filepath: str) -> str:
    """
    Get the default map directory path.
    
    Args:
        blend_filepath: Path to the .blend file
    
    Returns:
        Path to mocap_maps directory
    """
    if not blend_filepath:
        return "mocap_maps"
    
    blend_dir = os.path.dirname(blend_filepath)
    return os.path.join(blend_dir, "mocap_maps")


def save_bone_map(mappings: List[Dict], filepath: str) -> bool:
    """
    Save bone mappings to JSON file.
    
    Args:
        mappings: List of mapping dicts with 'landmark', 'bone', 'enabled'
        filepath: Path to save to
    
    Returns:
        True if successful
    """
    logger = get_logger()
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write JSON
        with open(filepath, 'w') as f:
            json.dump(mappings, f, indent=2)
        
        logger.info(f"Saved bone map to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save bone map: {str(e)}")
        return False


def load_bone_map(filepath: str) -> List[Dict]:
    """
    Load bone mappings from JSON file.
    
    Args:
        filepath: Path to load from
    
    Returns:
        List of mapping dicts, or empty list if failed
    """
    logger = get_logger()
    
    try:
        with open(filepath, 'r') as f:
            mappings = json.load(f)
        
        logger.info(f"Loaded {len(mappings)} mappings from {filepath}")
        return mappings
        
    except Exception as e:
        logger.error(f"Failed to load bone map: {str(e)}")
        return []
