"""
MediaPipe tracker setup and landmark extraction.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass

from ..utils.logging_utils import get_logger


@dataclass
class LandmarkResult:
    """Container for landmark detection results."""
    pose_landmarks: Optional[List] = None
    hand_landmarks: Optional[List] = None
    face_landmarks: Optional[List] = None


class MediaPipeTrackers:
    """Manages MediaPipe trackers for pose, hands, and face."""
    
    def __init__(self, use_pose: bool = True, use_hands: bool = False, 
                 use_face: bool = False, min_confidence: float = 0.5):
        """
        Initialize MediaPipe trackers.
        
        Args:
            use_pose: Enable pose tracking
            use_hands: Enable hand tracking
            use_face: Enable face tracking
            min_confidence: Minimum detection/tracking confidence
        """
        self.use_pose = use_pose
        self.use_hands = use_hands
        self.use_face = use_face
        self.min_confidence = min_confidence
        
        self.pose = None
        self.hands = None
        self.face = None
        
        self.logger = get_logger()
    
    def initialize(self) -> bool:
        """
        Initialize MediaPipe solutions.
        
        Returns:
            True if initialization successful
        """
        from ..runtime.dependency_check import safe_import_mediapipe
        mp = safe_import_mediapipe()
        
        if mp is None:
            self.logger.error("MediaPipe not available")
            return False
        
        try:
            # Initialize pose
            if self.use_pose:
                mp_pose = mp.solutions.pose
                self.pose = mp_pose.Pose(
                    min_detection_confidence=self.min_confidence,
                    min_tracking_confidence=self.min_confidence,
                    model_complexity=1,  # 0=Lite, 1=Full, 2=Heavy
                    smooth_landmarks=True
                )
                self.logger.info("Pose tracker initialized")
            
            # Initialize hands
            if self.use_hands:
                mp_hands = mp.solutions.hands
                self.hands = mp_hands.Hands(
                    min_detection_confidence=self.min_confidence,
                    min_tracking_confidence=self.min_confidence,
                    max_num_hands=2
                )
                self.logger.info("Hand tracker initialized")
            
            # Initialize face
            if self.use_face:
                mp_face = mp.solutions.face_mesh
                self.face = mp_face.FaceMesh(
                    min_detection_confidence=self.min_confidence,
                    min_tracking_confidence=self.min_confidence,
                    max_num_faces=1,
                    refine_landmarks=False
                )
                self.logger.info("Face tracker initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"MediaPipe initialization failed: {str(e)}")
            return False
    
    def process_frame(self, frame_rgb) -> LandmarkResult:
        """
        Process a frame and extract landmarks.
        
        Args:
            frame_rgb: RGB frame from camera
        
        Returns:
            LandmarkResult containing detected landmarks
        """
        result = LandmarkResult()
        
        try:
            # Process pose
            if self.pose is not None:
                pose_results = self.pose.process(frame_rgb)
                if pose_results.pose_landmarks:
                    result.pose_landmarks = pose_results.pose_landmarks.landmark
            
            # Process hands
            if self.hands is not None:
                hand_results = self.hands.process(frame_rgb)
                if hand_results.multi_hand_landmarks:
                    result.hand_landmarks = hand_results.multi_hand_landmarks
            
            # Process face
            if self.face is not None:
                face_results = self.face.process(frame_rgb)
                if face_results.multi_face_landmarks:
                    result.face_landmarks = face_results.multi_face_landmarks
        
        except Exception as e:
            self.logger.error(f"Frame processing error: {str(e)}")
        
        return result
    
    def cleanup(self):
        """Cleanup MediaPipe resources."""
        if self.pose is not None:
            self.pose.close()
            self.pose = None
        
        if self.hands is not None:
            self.hands.close()
            self.hands = None
        
        if self.face is not None:
            self.face.close()
            self.face = None
        
        self.logger.info("MediaPipe trackers cleaned up")
    
    def update_confidence(self, min_confidence: float):
        """
        Update confidence threshold (requires re-initialization).
        
        Args:
            min_confidence: New confidence threshold
        """
        self.min_confidence = min_confidence
        self.cleanup()
        self.initialize()


# MediaPipe landmark indices and names
POSE_LANDMARK_NAMES = {
    0: "NOSE",
    1: "LEFT_EYE_INNER", 2: "LEFT_EYE", 3: "LEFT_EYE_OUTER",
    4: "RIGHT_EYE_INNER", 5: "RIGHT_EYE", 6: "RIGHT_EYE_OUTER",
    7: "LEFT_EAR", 8: "RIGHT_EAR",
    9: "MOUTH_LEFT", 10: "MOUTH_RIGHT",
    11: "LEFT_SHOULDER", 12: "RIGHT_SHOULDER",
    13: "LEFT_ELBOW", 14: "RIGHT_ELBOW",
    15: "LEFT_WRIST", 16: "RIGHT_WRIST",
    17: "LEFT_PINKY", 18: "RIGHT_PINKY",
    19: "LEFT_INDEX", 20: "RIGHT_INDEX",
    21: "LEFT_THUMB", 22: "RIGHT_THUMB",
    23: "LEFT_HIP", 24: "RIGHT_HIP",
    25: "LEFT_KNEE", 26: "RIGHT_KNEE",
    27: "LEFT_ANKLE", 28: "RIGHT_ANKLE",
    29: "LEFT_HEEL", 30: "RIGHT_HEEL",
    31: "LEFT_FOOT_INDEX", 32: "RIGHT_FOOT_INDEX",
}


def get_landmark_name(index: int) -> str:
    """Get landmark name from index."""
    return POSE_LANDMARK_NAMES.get(index, f"LANDMARK_{index}")


def get_landmark_by_name(landmarks: List, name: str) -> Optional:
    """Get landmark by name from landmark list."""
    for idx, landmark_name in POSE_LANDMARK_NAMES.items():
        if landmark_name == name and idx < len(landmarks):
            return landmarks[idx]
    return None
