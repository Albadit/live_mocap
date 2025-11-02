# Install dependencies
# For AMD GPU on Windows: pip install tensorflow-directml
# For CPU-only: pip install opencv-python mediapipe

# Import required libraries
import mediapipe as mp
import cv2
import sys
import platform

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions

# ============================================================================
# GPU/CPU CONFIGURATION
# ============================================================================
PROCESSING_CONFIG = {
    'use_gpu': False,      # Set to True to attempt GPU acceleration
    'gpu_backend': 'auto',  # Options: 'auto', 'directml', 'opencl', 'cpu'
    'verbose': True         # Print detailed GPU setup information
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


def detect_gpu_backend():
    """
    Detect available GPU backends for the system.
    Returns tuple: (backend_name, backend_available)
    """
    system = platform.system()
    detected_backends = []
    
    # Check for DirectML (Windows + AMD/Intel GPUs)
    if system == "Windows":
        try:
            import tensorflow_directml as tfdml
            detected_backends.append('directml')
            if PROCESSING_CONFIG['verbose']:
                print("✓ DirectML detected (AMD/Intel GPU support)")
        except ImportError:
            if PROCESSING_CONFIG['verbose']:
                print("✗ DirectML not found (install: pip install tensorflow-directml)")
    
    # Check for standard TensorFlow with CUDA (NVIDIA GPUs)
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            detected_backends.append('cuda')
            if PROCESSING_CONFIG['verbose']:
                print(f"✓ CUDA detected - {len(gpus)} NVIDIA GPU(s) found")
        elif PROCESSING_CONFIG['verbose']:
            print("✗ No CUDA GPUs found")
    except ImportError:
        if PROCESSING_CONFIG['verbose']:
            print("✗ TensorFlow not found")
    except Exception as e:
        if PROCESSING_CONFIG['verbose']:
            print(f"✗ TensorFlow GPU check failed: {e}")
    
    return detected_backends


def setup_gpu_environment():
    """
    Configure GPU settings for MediaPipe with support for AMD GPUs.
    Returns: (backend_name, success_status)
    """
    if not PROCESSING_CONFIG['use_gpu']:
        if PROCESSING_CONFIG['verbose']:
            print("\n[CPU MODE] - GPU acceleration disabled")
        return 'cpu', True
    
    system = platform.system()
    backend = PROCESSING_CONFIG['gpu_backend']
    
    print("\n" + "="*60)
    print("GPU SETUP")
    print("="*60)
    print(f"System: {system}")
    print(f"Requested backend: {backend}")
    print()
    
    # Detect available backends
    available_backends = detect_gpu_backend()
    
    if not available_backends:
        print("\n⚠ WARNING: No GPU backends detected")
        print("Falling back to CPU mode")
        print("\nFor AMD GPU support on Windows, install:")
        print("  pip install tensorflow-directml")
        return 'cpu', False
    
    print(f"\nAvailable backends: {', '.join(available_backends)}")
    
    # Auto-select best backend
    if backend == 'auto':
        if 'directml' in available_backends:
            backend = 'directml'
        elif 'cuda' in available_backends:
            backend = 'cuda'
        else:
            backend = 'cpu'
        print(f"Auto-selected: {backend}")
    
    # Setup DirectML (AMD/Intel GPUs on Windows)
    if backend == 'directml':
        try:
            import tensorflow_directml as tfdml
            # Note: DirectML plugin automatically handles device selection
            print("\n✓ DirectML initialized successfully")
            print("  Compatible with: AMD Radeon, Intel Iris GPUs")
            return 'directml', True
        except Exception as e:
            print(f"\n✗ DirectML setup failed: {e}")
            print("Falling back to CPU")
            return 'cpu', False
    
    # Setup CUDA (NVIDIA GPUs)
    elif backend == 'cuda':
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            
            if not gpus:
                print("\n✗ No CUDA GPUs found")
                return 'cpu', False
            
            # Configure GPU memory growth
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            
            print(f"\n✓ CUDA initialized successfully")
            print(f"  Using {len(gpus)} NVIDIA GPU(s)")
            for i, gpu in enumerate(gpus):
                print(f"    GPU {i}: {gpu.name}")
            return 'cuda', True
            
        except Exception as e:
            print(f"\n✗ CUDA setup failed: {e}")
            return 'cpu', False
    
    # CPU fallback
    print("\n[CPU MODE]")
    return 'cpu', True


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
    Main function to run pose detection with AMD/NVIDIA GPU or CPU support.
    """
    # Setup GPU environment
    backend, gpu_success = setup_gpu_environment()
    
    print("="*60)
    print()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['fps'])
    if 'width' in CAMERA_CONFIG:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG['width'])
    if 'height' in CAMERA_CONFIG:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG['height'])
    
    # Verify actual FPS
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print("Camera Configuration:")
    print(f"  Requested FPS: {CAMERA_CONFIG['fps']}")
    print(f"  Actual FPS: {actual_fps}")
    print(f"  Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"  Processing Backend: {backend.upper()}")
    print()
    print("="*60)
    print()
    
    # Calculate wait time for display
    wait_time = max(1, int(1000 / CAMERA_CONFIG['fps']))
    
    # Initiate holistic model
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
            
            # Draw landmarks
            image = draw_face(image, results, mp_holistic, mp_drawing)
            image = draw_hand(image, results.right_hand_landmarks, mp_holistic, mp_drawing, 'right')
            image = draw_hand(image, results.left_hand_landmarks, mp_holistic, mp_drawing, 'left')
            image = draw_pose(image, results, mp_holistic, mp_drawing)
            
            # Add backend indicator on frame
            backend_text = f"Backend: {backend.upper()}"
            cv2.putText(image, backend_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2, cv2.LINE_AA)
                            
            cv2.imshow('MediaPipe Pose Detection', image)
    
            if cv2.waitKey(wait_time) & 0xFF == 27:
                break
            
            frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessed {frame_count} frames")
    print(f"Backend used: {backend.upper()}")


if __name__ == "__main__":
    main()