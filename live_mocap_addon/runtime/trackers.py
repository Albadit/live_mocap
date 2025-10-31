"""
MediaPipe tracker setup and landmark extraction.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass

from ..utils.logging_utils import get_logger


# Unified drawing configuration
DRAW_CONFIG = {
    # Face
    'face': {
        'landmark': {'color': (80, 110, 10), 'thickness': 1, 'circle_radius': 1},
        'connection': {'color': (255, 255, 255), 'thickness': 1, 'circle_radius': 1}
    },
    # Right hand
    'right_hand': {
        'landmark': {'color': (80, 22, 10), 'thickness': 2, 'circle_radius': 4},
        'connection': {'color': (255, 255, 255), 'thickness': 2, 'circle_radius': 2}
    },
    # Left hand
    'left_hand': {
        'landmark': {'color': (121, 22, 76), 'thickness': 2, 'circle_radius': 4},
        'connection': {'color': (255, 255, 255), 'thickness': 2, 'circle_radius': 2}
    },
    # Pose
    'pose': {
        'landmark': {'color': (245, 117, 66), 'thickness': 2, 'circle_radius': 4},
        'connection': {'color': (255, 255, 255), 'thickness': 2}
    }
}

# Depth-based sizing configuration for pose landmarks
DEPTH_CONFIG = {
    'radius_range': (2, 8),      # (min, max) radius in pixels based on depth
    'thickness_range': (1, 3)    # (min, max) thickness in pixels based on depth
}

# Pose landmarks to disable (skip drawing)
DISABLED_POSE_LANDMARKS = {
    0,   # nose
    1,   # left eye (inner)
    2,   # left eye
    3,   # left eye (outer)
    4,   # right eye (inner)
    5,   # right eye
    6,   # right eye (outer)
    7,   # left ear
    8,   # right ear
    9,   # mouth (left)
    10,  # mouth (right)
    17,  # left pinky
    18,  # right pinky
    19,  # left index
    20,  # right index
    21,  # left thumb
    22   # right thumb
}

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

# MediaPipe pose connections (bones)
POSE_CONNECTIONS = [
    # Face
    (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye to ear
    (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye to ear
    (9, 10),  # Mouth
    # Shoulders
    (11, 12),  # Shoulder line
    # Left arm
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    # Right arm
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
    # Torso
    (11, 23), (12, 24), (23, 24),  # Hip line
    # Left leg
    (23, 25), (25, 27), (27, 29), (27, 31),
    # Right leg
    (24, 26), (26, 28), (28, 30), (28, 32),
]


def draw_pose(image, results, mp_holistic, mp_drawing):
    """
    Draw pose landmarks with dynamic circle size based on depth (z-coordinate).
    Closer landmarks appear larger, farther landmarks appear smaller.
    """
    from ..runtime.dependency_check import safe_import_cv2
    cv2 = safe_import_cv2()
    if cv2 is None:
        return image
    
    if results.pose_landmarks:
        # Get all pose landmarks
        landmarks = results.pose_landmarks.landmark
        
        # Find min and max z values for normalization
        z_values = [lm.z for lm in landmarks]
        z_min, z_max = min(z_values), max(z_values)
        z_range = z_max - z_min if z_max != z_min else 1
        
        # Filter connections to exclude disabled landmarks
        filtered_connections = [
            connection for connection in mp_holistic.POSE_CONNECTIONS
            if connection[0] not in DISABLED_POSE_LANDMARKS and connection[1] not in DISABLED_POSE_LANDMARKS
        ]
        
        # Draw connections first (white lines) - only for enabled landmarks
        mp_drawing.draw_landmarks(
            image, 
            results.pose_landmarks, 
            filtered_connections,
            landmark_drawing_spec=None,  # We'll draw landmarks manually
            connection_drawing_spec=mp_drawing.DrawingSpec(
                color=DRAW_CONFIG['pose']['connection']['color'], 
                thickness=DRAW_CONFIG['pose']['connection']['thickness']
            )
        )
        
        # Draw each landmark with dynamic size based on depth
        h, w, c = image.shape
        for idx, landmark in enumerate(landmarks):
            # Skip disabled landmarks
            if idx in DISABLED_POSE_LANDMARKS:
                continue
                
            if landmark.visibility < 0.5:  # Skip if not visible enough
                continue
                
            # Normalize z value (inverse: closer = larger)
            # z is negative for closer points, so we invert it
            normalized_z = 1 - ((landmark.z - z_min) / z_range)
            
            # Get depth ranges from config
            radius_min, radius_max = DEPTH_CONFIG['radius_range']
            thickness_min, thickness_max = DEPTH_CONFIG['thickness_range']
            
            # Map normalized_z to the configured ranges
            circle_radius = int(radius_min + (normalized_z * (radius_max - radius_min)))
            circle_thickness = int(thickness_min + (normalized_z * (thickness_max - thickness_min)))
            
            # Calculate pixel coordinates
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            
            # Draw the landmark circle (filled)
            cv2.circle(image, (cx, cy), circle_radius, DRAW_CONFIG['pose']['landmark']['color'], -1)
    
    return image


@dataclass
class LandmarkResult:
    """Container for landmark detection results."""
    pose_landmarks: Optional[List] = None
    hand_landmarks: Optional[List] = None
    face_landmarks: Optional[List] = None


class MediaPipeTrackers:
    """Manages MediaPipe trackers for pose, hands, and face."""
    
    def __init__(self, use_pose: bool = True, use_hands: bool = False, 
                 use_face: bool = False, min_confidence: float = 0.5,
                 model_complexity: int = 2, min_tracking_confidence: float = 0.5,
                 smooth_landmarks: bool = True):
        """
        Initialize MediaPipe trackers.
        
        Args:
            use_pose: Enable pose tracking
            use_hands: Enable hand tracking
            use_face: Enable face tracking
            min_confidence: Minimum detection confidence
            model_complexity: Model complexity (0=Lite, 1=Full, 2=Heavy)
            min_tracking_confidence: Minimum tracking confidence
            smooth_landmarks: Enable landmark smoothing
        """
        self.use_pose = use_pose
        self.use_hands = use_hands
        self.use_face = use_face
        self.min_confidence = min_confidence
        self.model_complexity = model_complexity
        self.min_tracking_confidence = min_tracking_confidence
        self.smooth_landmarks = smooth_landmarks
        
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
                    min_tracking_confidence=self.min_tracking_confidence,
                    model_complexity=self.model_complexity,
                    smooth_landmarks=self.smooth_landmarks
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


def get_landmark_name(index: int) -> str:
    """Get landmark name from index."""
    return POSE_LANDMARK_NAMES.get(index, f"LANDMARK_{index}")


def get_landmark_by_name(landmarks: List, name: str) -> Optional[object]:
    """Get landmark by name from landmark list."""
    for idx, landmark_name in POSE_LANDMARK_NAMES.items():
        if landmark_name == name and idx < len(landmarks):
            return landmarks[idx]
    return None
