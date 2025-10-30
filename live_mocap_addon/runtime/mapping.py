"""
Bone-landmark mapping models and auto-matching.
"""

from typing import List, Dict, Optional
from ..utils.naming import find_bone_in_armature, BONE_PATTERNS

# Default landmark-to-bone mapping suggestions
# Format: "Rig Bone Name": {"landmark": "MEDIAPIPE_LANDMARK", "bones": ["alternative_bone_names", ...]}
DEFAULT_BONE_MAP = {
    # Head and face
    "Head": {"landmark": "NOSE", "bones": ["head", "spine.006"]},
    # "LeftEye": {"landmark": "LEFT_EYE", "bones": ["eye.L"]},
    # "RightEye": {"landmark": "RIGHT_EYE", "bones": ["eye.R"]},
    # "LeftEar": {"landmark": "LEFT_EAR", "bones": ["ear.L"]},
    # "RightEar": {"landmark": "RIGHT_EAR", "bones": ["ear.R"]},
    # "Mouth": {"landmark": "MOUTH_LEFT", "bones": ["jaw", "chin"]},
    
    # Spine/Torso
    # "Hips": {"landmark": "LEFT_HIP", "bones": ["spine", "pelvis", "hips"]},
    # "Spine": {"landmark": "LEFT_HIP", "bones": ["spine"]},
    # "Spine1": {"landmark": "LEFT_HIP", "bones": ["spine.001"]},
    # "Spine2": {"landmark": "LEFT_SHOULDER", "bones": ["spine.002"]},
    # "Spine3": {"landmark": "LEFT_SHOULDER", "bones": ["spine.003"]},
    # "Spine4": {"landmark": "LEFT_SHOULDER", "bones": ["spine.004"]},
    # "Spine5": {"landmark": "LEFT_SHOULDER", "bones": ["spine.005"]},
    
    # Left arm
    # "LeftShoulder": {"landmark": "LEFT_SHOULDER", "bones": ["upper_arm_fk.L", "upper_arm.L", "shoulder.L"]},
    "LeftUpperArm": {"landmark": "LEFT_SHOULDER", "bones": ["upper_arm_fk.L", "upper_arm.L"]},
    # "LeftElbow": {"landmark": "LEFT_ELBOW", "bones": ["forearm_fk.L", "forearm.L"]},
    "LeftForearm": {"landmark": "LEFT_ELBOW", "bones": ["forearm_fk.L", "forearm.L"]},
    # "LeftWrist": {"landmark": "LEFT_WRIST", "bones": ["hand_fk.L", "hand.L"]},
    "LeftHand": {"landmark": "LEFT_WRIST", "bones": ["hand_fk.L", "hand.L"]},
    
    # Left hand fingers
    "LeftThumb": {"landmark": "LEFT_THUMB", "bones": ["f_thumb.01.L", "thumb.01.L"]},
    "LeftIndex": {"landmark": "LEFT_INDEX", "bones": ["f_index.01.L", "finger_index.01.L"]},
    "LeftPinky": {"landmark": "LEFT_PINKY", "bones": ["f_pinky.03.L", "finger_pinky.03.L"]},
    # "LeftPalm1": {"landmark": "LEFT_PINKY", "bones": ["palm.01.L"]},
    # "LeftPalm2": {"landmark": "LEFT_PINKY", "bones": ["palm.02.L"]},
    # "LeftPalm3": {"landmark": "LEFT_INDEX", "bones": ["palm.03.L"]},
    # "LeftPalm4": {"landmark": "LEFT_THUMB", "bones": ["palm.04.L"]},
    # "LeftThumb1": {"landmark": "LEFT_THUMB", "bones": ["f_thumb.01.L", "thumb.01.L"]},
    # "LeftThumb2": {"landmark": "LEFT_THUMB", "bones": ["f_thumb.02.L", "thumb.02.L"]},
    # "LeftThumb3": {"landmark": "LEFT_THUMB", "bones": ["f_thumb.03.L", "thumb.03.L"]},
    # "LeftIndex1": {"landmark": "LEFT_INDEX", "bones": ["f_index.01.L", "finger_index.01.L"]},
    # "LeftIndex2": {"landmark": "LEFT_INDEX", "bones": ["f_index.02.L", "finger_index.02.L"]},
    # "LeftIndex3": {"landmark": "LEFT_INDEX", "bones": ["f_index.03.L", "finger_index.03.L"]},
    # "LeftMiddle1": {"landmark": "LEFT_INDEX", "bones": ["f_middle.01.L", "finger_middle.01.L"]},
    # "LeftMiddle2": {"landmark": "LEFT_INDEX", "bones": ["f_middle.02.L", "finger_middle.02.L"]},
    # "LeftMiddle3": {"landmark": "LEFT_INDEX", "bones": ["f_middle.03.L", "finger_middle.03.L"]},
    # "LeftRing1": {"landmark": "LEFT_PINKY", "bones": ["f_ring.01.L", "finger_ring.01.L"]},
    # "LeftRing2": {"landmark": "LEFT_PINKY", "bones": ["f_ring.02.L", "finger_ring.02.L"]},
    # "LeftRing3": {"landmark": "LEFT_PINKY", "bones": ["f_ring.03.L", "finger_ring.03.L"]},
    # "LeftPinky1": {"landmark": "LEFT_PINKY", "bones": ["f_pinky.01.L", "finger_pinky.01.L"]},
    # "LeftPinky2": {"landmark": "LEFT_PINKY", "bones": ["f_pinky.02.L", "finger_pinky.02.L"]},
    # "LeftPinky3": {"landmark": "LEFT_PINKY", "bones": ["f_pinky.03.L", "finger_pinky.03.L"]},
    
    # Right arm
    # "RightShoulder": {"landmark": "RIGHT_SHOULDER", "bones": ["upper_arm_fk.R", "upper_arm.R", "shoulder.R"]},
    "RightUpperArm": {"landmark": "RIGHT_SHOULDER", "bones": ["upper_arm_fk.R", "upper_arm.R"]},
    # "RightElbow": {"landmark": "RIGHT_ELBOW", "bones": ["forearm_fk.R", "forearm.R"]},
    "RightForearm": {"landmark": "RIGHT_ELBOW", "bones": ["forearm_fk.R", "forearm.R"]},
    # "RightWrist": {"landmark": "RIGHT_WRIST", "bones": ["hand_fk.R", "hand.R"]},
    "RightHand": {"landmark": "RIGHT_WRIST", "bones": ["hand_fk.R", "hand.R"]},
    
    # Right hand fingers
    "RightThumb": {"landmark": "RIGHT_THUMB", "bones": ["f_thumb.01.R", "thumb.01.R"]},
    "RightPinky": {"landmark": "RIGHT_PINKY", "bones": ["f_pinky.01.R", "finger_pinky.01.R"]},
    "RightIndex": {"landmark": "RIGHT_INDEX", "bones": ["f_index.01.R", "finger_index.01.R"]},
    # "RightPalm1": {"landmark": "RIGHT_PINKY", "bones": ["palm.01.R"]},
    # "RightPalm2": {"landmark": "RIGHT_PINKY", "bones": ["palm.02.R"]},
    # "RightPalm3": {"landmark": "RIGHT_INDEX", "bones": ["palm.03.R"]},
    # "RightPalm4": {"landmark": "RIGHT_THUMB", "bones": ["palm.04.R"]},
    # "RightThumb1": {"landmark": "RIGHT_THUMB", "bones": ["f_thumb.01.R", "thumb.01.R"]},
    # "RightThumb2": {"landmark": "RIGHT_THUMB", "bones": ["f_thumb.02.R", "thumb.02.R"]},
    # "RightThumb3": {"landmark": "RIGHT_THUMB", "bones": ["f_thumb.03.R", "thumb.03.R"]},
    # "RightIndex1": {"landmark": "RIGHT_INDEX", "bones": ["f_index.01.R", "finger_index.01.R"]},
    # "RightIndex2": {"landmark": "RIGHT_INDEX", "bones": ["f_index.02.R", "finger_index.02.R"]},
    # "RightIndex3": {"landmark": "RIGHT_INDEX", "bones": ["f_index.03.R", "finger_index.03.R"]},
    # "RightMiddle1": {"landmark": "RIGHT_INDEX", "bones": ["f_middle.01.R", "finger_middle.01.R"]},
    # "RightMiddle2": {"landmark": "RIGHT_INDEX", "bones": ["f_middle.02.R", "finger_middle.02.R"]},
    # "RightMiddle3": {"landmark": "RIGHT_INDEX", "bones": ["f_middle.03.R", "finger_middle.03.R"]},
    # "RightRing1": {"landmark": "RIGHT_PINKY", "bones": ["f_ring.01.R", "finger_ring.01.R"]},
    # "RightRing2": {"landmark": "RIGHT_PINKY", "bones": ["f_ring.02.R", "finger_ring.02.R"]},
    # "RightRing3": {"landmark": "RIGHT_PINKY", "bones": ["f_ring.03.R", "finger_ring.03.R"]},
    # "RightPinky1": {"landmark": "RIGHT_PINKY", "bones": ["f_pinky.01.R", "finger_pinky.01.R"]},
    # "RightPinky2": {"landmark": "RIGHT_PINKY", "bones": ["f_pinky.02.R", "finger_pinky.02.R"]},
    # "RightPinky3": {"landmark": "RIGHT_PINKY", "bones": ["f_pinky.03.R", "finger_pinky.03.R"]},
    
    # Left leg
    # "LeftPelvis": {"landmark": "LEFT_HIP", "bones": ["pelvis.L"]},
    # "LeftHip": {"landmark": "LEFT_HIP", "bones": ["thigh_fk.L", "thigh.L"]},
    "LeftThigh": {"landmark": "LEFT_HIP", "bones": ["thigh_fk.L", "thigh.L"]},
    # "LeftKnee": {"landmark": "LEFT_KNEE", "bones": ["shin_fk.L", "shin.L"]},
    "LeftShin": {"landmark": "LEFT_KNEE", "bones": ["shin_fk.L", "shin.L"]},
    # "LeftAnkle": {"landmark": "LEFT_ANKLE", "bones": ["foot_fk.L", "foot.L"]},
    "LeftFoot": {"landmark": "LEFT_ANKLE", "bones": ["foot_fk.L", "foot.L"]},
    "LeftHeel": {"landmark": "LEFT_HEEL", "bones": ["heel.02.L"]},
    "LeftToe": {"landmark": "LEFT_FOOT_INDEX", "bones": ["toe_fk.L", "toe.L"]},
    
    # Right leg
    # "RightPelvis": {"landmark": "RIGHT_HIP", "bones": ["pelvis.R"]},
    # "RightHip": {"landmark": "RIGHT_HIP", "bones": ["thigh_fk.R", "thigh.R"]},
    "RightThigh": {"landmark": "RIGHT_HIP", "bones": ["thigh_fk.R", "thigh.R"]},
    # "RightKnee": {"landmark": "RIGHT_KNEE", "bones": ["shin_fk.R", "shin.R"]},
    "RightShin": {"landmark": "RIGHT_KNEE", "bones": ["shin_fk.R", "shin.R"]},
    # "RightAnkle": {"landmark": "RIGHT_ANKLE", "bones": ["foot_fk.R", "foot.R"]},
    "RightFoot": {"landmark": "RIGHT_ANKLE", "bones": ["foot_fk.R", "foot.R"]},
    "RightHeel": {"landmark": "RIGHT_HEEL", "bones": ["heel.02.R"]},
    "RightToe": {"landmark": "RIGHT_FOOT_INDEX", "bones": ["toe_fk.R", "toe.R"]},
}


# Landmark chains for computing rotations
LANDMARK_CHAINS = {
    # Arms
    "LEFT_SHOULDER": "LEFT_ELBOW",
    "LEFT_ELBOW": "LEFT_WRIST",
    "LEFT_WRIST": "LEFT_INDEX",
    "RIGHT_SHOULDER": "RIGHT_ELBOW",
    "RIGHT_ELBOW": "RIGHT_WRIST",
    "RIGHT_WRIST": "RIGHT_INDEX",
    
    # Legs
    "LEFT_HIP": "LEFT_KNEE",
    "LEFT_KNEE": "LEFT_ANKLE",
    "LEFT_ANKLE": "LEFT_FOOT_INDEX",
    "RIGHT_HIP": "RIGHT_KNEE",
    "RIGHT_KNEE": "RIGHT_ANKLE",
    "RIGHT_ANKLE": "RIGHT_FOOT_INDEX",
    
    # Fingers - Left
    "LEFT_THUMB": "LEFT_INDEX",
    "LEFT_INDEX": "LEFT_PINKY",
    
    # Fingers - Right
    "RIGHT_THUMB": "RIGHT_INDEX",
    "RIGHT_INDEX": "RIGHT_PINKY",
}


def auto_map_bones(armature_bones: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Automatically map MediaPipe landmarks to armature bones.
    First checks for exact matches from the candidate patterns,
    then falls back to fuzzy matching if no exact match is found.
    Skips entries with empty/None landmarks.
    
    Args:
        armature_bones: List of bone names from the armature
    
    Returns:
        Dict mapping rig bone names to {"landmark": landmark_name, "bone": matched_bone}
        Example: {"Head": {"landmark": "NOSE", "bone": "head"}}
    """
    mapping = {}
    
    for rig_bone_name, bone_config in DEFAULT_BONE_MAP.items():
        # bone_config format: {"landmark": "MEDIAPIPE_LANDMARK", "bones": ["bone1", "bone2", ...]}
        landmark_name = bone_config.get("landmark")
        candidate_patterns = bone_config.get("bones", [])
        
        # Skip if landmark is None or empty
        if not landmark_name:
            continue
        
        # Skip if no candidate patterns
        if not candidate_patterns:
            continue
        
        # First, check for exact matches
        matched_bone = None
        for pattern in candidate_patterns:
            if pattern in armature_bones:
                matched_bone = pattern
                break
        
        # If no exact match, use fuzzy matching
        if not matched_bone:
            matched_bone = find_bone_in_armature(armature_bones, candidate_patterns)
        
        if matched_bone:
            mapping[rig_bone_name] = {
                "landmark": landmark_name,
                "bone": matched_bone
            }
    
    return mapping


def get_next_landmark_in_chain(landmark_name: str) -> Optional[str]:
    """Get the next landmark in a bone chain."""
    return LANDMARK_CHAINS.get(landmark_name)
