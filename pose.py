# Install dependencies
# For GPU support, you'll also need: pip install mediapipe-gpu
# !pip install opencv-python mediapipe

# Import required libraries
import mediapipe as mp
import cv2
import sys

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions

# ============================================================================
# GPU/CPU CONFIGURATION
# ============================================================================
PROCESSING_CONFIG = {
    'use_gpu': False,  # Set to True to use GPU, False for CPU
    'gpu_device': 0    # GPU device ID (if multiple GPUs available)
}

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

# Controls which body parts and landmarks to draw
ENABLE_DRAWING = {
    # Pose: 33 landmarks (0-32)
    'pose': True,
    # Face: 468 landmarks (0-468)
    'face': False,
    # Hand: 21 landmarks (0-21)
    'right_hand': True,
    'left_hand': True
}

# MediaPipe Model Configuration
MODEL_CONFIG = {
    'min_detection_confidence': 0.5,   # Minimum confidence for pose detection (0.0 - 1.0)
    'min_tracking_confidence': 0.5,    # Minimum confidence for pose tracking (0.0 - 1.0)
    'model_complexity': 2,             # Model complexity: 0 (Lite), 1 (Full), 2 (Heavy)
    'enable_segmentation': False,      # Enable/disable segmentation mask
    'smooth_landmarks': True,          # Enable/disable landmark smoothing
}

CAMERA_CONFIG = {
    'fps': 60,           # Target frames per second
    'width': 1280,       # Camera width (optional, comment out to use default)
    'height': 720        # Camera height (optional, comment out to use default)
}


def setup_gpu_environment():
    """
    Configure GPU settings for MediaPipe.
    Returns True if GPU setup successful, False otherwise.
    """
    if not PROCESSING_CONFIG['use_gpu']:
        print("Running on CPU")
        return False
    
    try:
        # Try to import TensorFlow to check GPU availability
        import tensorflow as tf
        
        # List available GPUs
        gpus = tf.config.list_physical_devices('GPU')
        
        if not gpus:
            print("WARNING: GPU requested but no GPU devices found. Falling back to CPU.")
            return False
        
        print(f"Found {len(gpus)} GPU(s):")
        for gpu in gpus:
            print(f"  - {gpu.name}")
        
        # Configure GPU memory growth to avoid allocating all GPU memory at once
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        
        # Set specific GPU device if specified
        if PROCESSING_CONFIG['gpu_device'] < len(gpus):
            tf.config.set_visible_devices(gpus[PROCESSING_CONFIG['gpu_device']], 'GPU')
            print(f"Using GPU device {PROCESSING_CONFIG['gpu_device']}")
        
        print("GPU setup successful")
        return True
        
    except ImportError:
        print("WARNING: TensorFlow not found. GPU acceleration requires TensorFlow.")
        print("Install with: pip install tensorflow")
        return False
    except Exception as e:
        print(f"WARNING: GPU setup failed: {e}")
        print("Falling back to CPU")
        return False


def draw_pose(image, results, mp_holistic, mp_drawing):
    """
    Optimized pose landmark drawing with dynamic circle size based on depth (z-coordinate).
    Closer landmarks appear larger, farther landmarks appear smaller.
    Respects ENABLE_DRAWING['pose'] configuration.
    """
    # Check ENABLE_DRAWING configuration
    enable_config = ENABLE_DRAWING['pose']
    
    # If False, don't draw at all
    if enable_config is False:
        return image
    
    if not results.pose_landmarks:
        return image
    
    landmarks = results.pose_landmarks.landmark
    
    # If True, show all landmarks (empty disabled set)
    # If set/dict, use it as disabled landmarks
    disabled_set = set() if enable_config is True else enable_config
    
    # Pre-compute image dimensions (avoid repeated access)
    h, w = image.shape[:2]
    
    # Cache config values to avoid dictionary lookups in loop
    radius_min, radius_max = DEPTH_CONFIG['radius_range']
    pose_color = DRAW_CONFIG['pose']['landmark']['color']
    conn_color = DRAW_CONFIG['pose']['connection']['color']
    conn_thickness = DRAW_CONFIG['pose']['connection']['thickness']
    
    # Vectorized z-value extraction and normalization
    z_values = [lm.z for lm in landmarks]
    z_min, z_max = min(z_values), max(z_values)
    z_range = z_max - z_min if z_max - z_min > 1e-6 else 1
    z_range_inv = 1.0 / z_range  # Pre-compute division
    
    # Pre-filter connections (cache if this list doesn't change)
    filtered_connections = [
        conn for conn in mp_holistic.POSE_CONNECTIONS
        if conn[0] not in disabled_set and conn[1] not in disabled_set
    ]
    
    # Draw connections first (single draw call)
    mp_drawing.draw_landmarks(
        image, 
        results.pose_landmarks, 
        filtered_connections,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing.DrawingSpec(color=conn_color, thickness=conn_thickness)
    )
    
    # Optimized landmark drawing loop
    radius_range = radius_max - radius_min
    for idx, landmark in enumerate(landmarks):
        # Combined conditional check for early exit
        if idx in disabled_set or landmark.visibility < 0.5:
            continue
        
        # Optimized z normalization (reduced operations)
        normalized_z = 1.0 - ((landmark.z - z_min) * z_range_inv)
        
        # Direct radius calculation
        circle_radius = int(radius_min + normalized_z * radius_range)
        
        # Convert coordinates to pixels (combined operation)
        cx, cy = int(landmark.x * w), int(landmark.y * h)
        
        # Draw landmark (filled circle)
        cv2.circle(image, (cx, cy), circle_radius, pose_color, -1)
    
    return image


def draw_face(image, results, mp_holistic, mp_drawing):
    """
    Draw face landmarks with support for disabled landmarks.
    Respects ENABLE_DRAWING['face'] configuration.
    """
    # Check ENABLE_DRAWING configuration
    enable_config = ENABLE_DRAWING['face']
    
    # If False, don't draw at all
    if enable_config is False:
        return image
    
    if not results.face_landmarks:
        return image
    
    # If True, show all landmarks (empty disabled set)
    # If set/dict, use it as disabled landmarks
    disabled_set = set() if enable_config is True else enable_config
    
    if not disabled_set:
        # If no landmarks are disabled, use the standard drawing method
        mp_drawing.draw_landmarks(
            image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION, 
            mp_drawing.DrawingSpec(**DRAW_CONFIG['face']['landmark']),
            mp_drawing.DrawingSpec(**DRAW_CONFIG['face']['connection'])
        )
    else:
        # Filter connections to exclude disabled landmarks
        filtered_connections = [
            conn for conn in mp_holistic.FACEMESH_TESSELATION
            if conn[0] not in disabled_set and conn[1] not in disabled_set
        ]
        
        # Draw filtered connections
        mp_drawing.draw_landmarks(
            image, results.face_landmarks, filtered_connections,
            mp_drawing.DrawingSpec(**DRAW_CONFIG['face']['landmark']),
            mp_drawing.DrawingSpec(**DRAW_CONFIG['face']['connection'])
        )
    
    return image


def draw_hand(image, results_landmarks, mp_holistic, mp_drawing, hand_type='right'):
    """
    Draw hand landmarks with support for disabled landmarks.
    Respects ENABLE_DRAWING configuration.
    
    Args:
        image: Image to draw on
        results_landmarks: Either results.right_hand_landmarks or results.left_hand_landmarks
        mp_holistic: MediaPipe holistic object
        mp_drawing: MediaPipe drawing utilities
        hand_type: 'right' or 'left'
    """
    # Select the appropriate keys
    config_key = 'right_hand' if hand_type == 'right' else 'left_hand'
    
    # Check ENABLE_DRAWING configuration
    enable_config = ENABLE_DRAWING[config_key]
    
    # If False, don't draw at all
    if enable_config is False:
        return image
    
    if not results_landmarks:
        return image
    
    # If True, show all landmarks (empty disabled set)
    # If set/dict, use it as disabled landmarks
    disabled_set = set() if enable_config is True else enable_config
    
    if not disabled_set:
        # If no landmarks are disabled, use the standard drawing method
        mp_drawing.draw_landmarks(
            image, results_landmarks, mp_holistic.HAND_CONNECTIONS, 
            mp_drawing.DrawingSpec(**DRAW_CONFIG[config_key]['landmark']),
            mp_drawing.DrawingSpec(**DRAW_CONFIG[config_key]['connection'])
        )
    else:
        # Filter connections to exclude disabled landmarks
        filtered_connections = [
            conn for conn in mp_holistic.HAND_CONNECTIONS
            if conn[0] not in disabled_set and conn[1] not in disabled_set
        ]
        
        # Draw filtered connections
        mp_drawing.draw_landmarks(
            image, results_landmarks, filtered_connections,
            mp_drawing.DrawingSpec(**DRAW_CONFIG[config_key]['landmark']),
            mp_drawing.DrawingSpec(**DRAW_CONFIG[config_key]['connection'])
        )
    
    return image


def main():
    """
    Main function to run pose detection with GPU/CPU support.
    """
    # Setup GPU environment if requested
    gpu_available = setup_gpu_environment()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['fps'])
    if 'width' in CAMERA_CONFIG:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG['width'])
    if 'height' in CAMERA_CONFIG:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG['height'])
    
    # Verify actual FPS (some cameras may not support requested FPS)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"\nCamera Configuration:")
    print(f"Requested FPS: {CAMERA_CONFIG['fps']}")
    print(f"Actual FPS: {actual_fps}")
    print(f"Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"Processing Mode: {'GPU' if PROCESSING_CONFIG['use_gpu'] and gpu_available else 'CPU'}")
    print("\nPress 'q' to quit\n")
    
    # Calculate wait time for display (in milliseconds)
    wait_time = max(1, int(1000 / CAMERA_CONFIG['fps']))
    
    # Initiate holistic model with configuration variables
    with mp_holistic.Holistic(
        min_detection_confidence=MODEL_CONFIG['min_detection_confidence'],
        min_tracking_confidence=MODEL_CONFIG['min_tracking_confidence'],
        model_complexity=MODEL_CONFIG['model_complexity'],
        enable_segmentation=MODEL_CONFIG['enable_segmentation'],
        smooth_landmarks=MODEL_CONFIG['smooth_landmarks']
    ) as holistic:
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret: 
                print("Failed to grab frame")
                break
    
            # Recolor Feed
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False        
            
            # Make Detections
            results = holistic.process(image)
            
            # Recolor image back to BGR for rendering
            image.flags.writeable = True   
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Draw landmarks using custom functions that respect disabled landmarks
            # 1. Draw face landmarks
            image = draw_face(image, results, mp_holistic, mp_drawing)
            
            # 2. Right hand
            image = draw_hand(image, results.right_hand_landmarks, mp_holistic, mp_drawing, 'right')
    
            # 3. Left Hand
            image = draw_hand(image, results.left_hand_landmarks, mp_holistic, mp_drawing, 'left')
    
            # 4. Pose Detections with Dynamic Depth-based Size
            image = draw_pose(image, results, mp_holistic, mp_drawing)
            
            # Add processing mode indicator on frame
            mode_text = f"Mode: {'GPU' if PROCESSING_CONFIG['use_gpu'] and gpu_available else 'CPU'}"
            cv2.putText(image, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2, cv2.LINE_AA)
                            
            cv2.imshow('MediaPipe Holistic', image)
    
            # Calculate wait time based on target FPS (waitKey expects milliseconds)
            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break
            
            frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessed {frame_count} frames")


if __name__ == "__main__":
    main()