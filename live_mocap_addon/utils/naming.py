"""
Bone naming utilities and fuzzy matching for automatic bone mapping.
"""

import re
from typing import List, Optional


# Canonical bone name patterns (lowercase)
BONE_PATTERNS = {
    # Head/Neck
    "head": ["head", "neck_01", "neck1"],
    "neck": ["neck", "neck_00", "neck0"],
    
    # Arms (Left)
    "shoulder.L": ["shoulder.l", "upper_arm.l", "upperarm.l", "arm.l", "clavicle.l"],
    "elbow.L": ["forearm.l", "elbow.l", "lowerarm.l"],
    "wrist.L": ["hand.l", "wrist.l"],
    
    # Arms (Right)
    "shoulder.R": ["shoulder.r", "upper_arm.r", "upperarm.r", "arm.r", "clavicle.r"],
    "elbow.R": ["forearm.r", "elbow.r", "lowerarm.r"],
    "wrist.R": ["hand.r", "wrist.r"],
    
    # Legs (Left)
    "hip.L": ["thigh.l", "upper_leg.l", "upperleg.l", "leg.l", "hip.l"],
    "knee.L": ["shin.l", "lower_leg.l", "lowerleg.l", "calf.l"],
    "ankle.L": ["foot.l", "ankle.l"],
    
    # Legs (Right)
    "hip.R": ["thigh.r", "upper_leg.r", "upperleg.r", "leg.r", "hip.r"],
    "knee.R": ["shin.r", "lower_leg.r", "lowerleg.r", "calf.r"],
    "ankle.R": ["foot.r", "ankle.r"],
    
    # Spine
    "spine": ["spine", "spine.000", "spine_00", "spine0"],
    "chest": ["chest", "spine.001", "spine_01", "spine1", "spine.002", "spine2"],
    "pelvis": ["pelvis", "hips", "root"],
}


def normalize_bone_name(name: str) -> str:
    """
    Normalize a bone name for comparison.
    
    Args:
        name: Bone name to normalize
    
    Returns:
        Normalized bone name (lowercase, stripped)
    """
    return name.lower().strip()


def fuzzy_match_bone(bone_name: str, candidate_names: List[str]) -> Optional[str]:
    """
    Find the best matching bone from a list of candidates.
    
    Args:
        bone_name: Target bone name from the armature
        candidate_names: List of candidate patterns to match against
    
    Returns:
        Best matching candidate name, or None if no match
    """
    normalized = normalize_bone_name(bone_name)
    
    # Try exact match first
    for candidate in candidate_names:
        if normalized == normalize_bone_name(candidate):
            return candidate
    
    # Try contains match
    for candidate in candidate_names:
        if normalize_bone_name(candidate) in normalized:
            return candidate
    
    # Try substring match (candidate in bone_name)
    for candidate in candidate_names:
        if candidate.lower() in normalized:
            return candidate
    
    return None


def find_bone_in_armature(armature_bones: List[str], patterns: List[str]) -> Optional[str]:
    """
    Find a bone in an armature that matches one of the patterns.
    
    Args:
        armature_bones: List of bone names from the armature
        patterns: List of pattern names to search for
    
    Returns:
        Matching bone name from armature, or None
    """
    for bone_name in armature_bones:
        if fuzzy_match_bone(bone_name, patterns):
            return bone_name
    return None


def extract_side_suffix(bone_name: str) -> Optional[str]:
    """
    Extract side suffix (.L/.R, _L/_R, etc.) from bone name.
    
    Args:
        bone_name: Bone name to analyze
    
    Returns:
        Side suffix (.L or .R), or None if not found
    """
    # Common patterns: .L, .R, _L, _R, -L, -R, .l, .r
    pattern = r'[._-]([LRlr])$'
    match = re.search(pattern, bone_name)
    if match:
        side = match.group(1).upper()
        return f".{side}"
    return None


def get_mirrored_bone_name(bone_name: str) -> Optional[str]:
    """
    Get the mirrored version of a bone name (L ↔ R).
    
    Args:
        bone_name: Bone name to mirror
    
    Returns:
        Mirrored bone name, or None if no side suffix found
    """
    side = extract_side_suffix(bone_name)
    if not side:
        return None
    
    opposite_side = ".L" if side == ".R" else ".R"
    
    # Replace the suffix
    pattern = r'[._-][LRlr]$'
    mirrored = re.sub(pattern, opposite_side, bone_name)
    return mirrored


def get_canonical_name(bone_name: str) -> Optional[str]:
    """
    Get the canonical name for a bone (e.g., "UpperArm.L" → "shoulder.L").
    
    Args:
        bone_name: Bone name to canonicalize
    
    Returns:
        Canonical name, or None if not found
    """
    normalized = normalize_bone_name(bone_name)
    
    for canonical, patterns in BONE_PATTERNS.items():
        for pattern in patterns:
            if pattern in normalized:
                return canonical
    
    return None
