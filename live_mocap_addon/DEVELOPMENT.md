# Development Guide

Guide for developers who want to understand, modify, or extend the Live Mocap add-on.

## Architecture Overview

The add-on follows a clean modular architecture with clear separation of concerns:

### Layer 1: Blender Integration
- `__init__.py` (root): Entry point for Blender
- `src/__init__.py`: Registration and initialization
- `src/addon_prefs.py`: User preferences
- `src/properties.py`: Data models (PropertyGroups)
- `src/panel.py`: UI presentation

### Layer 2: Operations
- `src/ops/`: All user-triggered actions (operators)
- Each operator in its own file for maintainability
- Modal operator pattern for non-blocking real-time operations

### Layer 3: Runtime Systems
- `src/runtime/`: Live capture, tracking, and processing
- Isolated from Blender-specific code where possible
- Easy to test and mock

### Layer 4: Utilities
- `src/utils/`: Pure functions for common operations
- No Blender dependencies (except `mathutils`)
- Reusable across modules

### Layer 5: I/O
- `src/io/`: File operations and exports
- JSON serialization for bone maps
- Optional format exports (FBX, etc.)

## Key Design Patterns

### 1. Modal Operator Pattern
Used in `op_capture_start.py` for non-blocking real-time capture:

```python
class MOCAP_OT_CaptureStart(Operator):
    _timer = None  # Timer for frame updates
    
    def invoke(self, context, event):
        # Initialize resources (camera, trackers)
        # Add modal timer
        wm.event_timer_add(...)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            self.process_frame(context)  # Do work
        return {'PASS_THROUGH'}  # Don't block Blender
    
    def cancel(self, context):
        # Cleanup resources
        self._camera.release()
```

### 2. Safe Dependency Import
Used in `dependency_check.py` to handle missing packages gracefully:

```python
def safe_import_cv2():
    try:
        import cv2
        return cv2
    except ImportError:
        return None

# Usage:
cv2 = safe_import_cv2()
if cv2 is None:
    # Handle gracefully
```

### 3. Filter Chain
Used in `filters.py` for composable data processing:

```python
class MultiFilter:
    def __init__(self):
        self.smoothing = SmoothingFilter(alpha)
        self.confidence_gate = ConfidenceGate(threshold)
        self.foot_lock = FootLockFilter(threshold)
    
    def filter_position(self, pos, confidence, is_foot):
        pos = self.confidence_gate.filter(pos, confidence)
        pos = self.smoothing.filter(pos)
        if is_foot:
            pos = self.foot_lock.filter(pos)
        return pos
```

### 4. Data-Driven Bone Mapping
Used in `mapping.py` for flexible rig support:

```python
DEFAULT_BONE_MAP = {
    "NOSE": ["head", "Head"],
    "LEFT_SHOULDER": ["shoulder.L", "upper_arm.L"],
    # ...
}

def auto_map_bones(armature_bones):
    for landmark, candidates in DEFAULT_BONE_MAP.items():
        bone = find_bone_in_armature(armature_bones, candidates)
        if bone:
            mapping[landmark] = bone
```

## Core Subsystems

### Camera Capture (`runtime/capture.py`)

**Responsibilities:**
- Open/close OpenCV camera
- Read frames at target FPS
- Track performance metrics (FPS, latency, dropped frames)

**Key Methods:**
```python
camera = CameraCapture(index=0, fps=30)
camera.open()
success, frame, frame_rgb = camera.read_frame()
camera.release()
```

**Metrics:**
- `get_average_fps()`: Actual capture FPS
- `get_average_latency()`: Frame processing time
- `get_dropped_frames()`: Frames that failed to read

### MediaPipe Tracking (`runtime/trackers.py`)

**Responsibilities:**
- Initialize MediaPipe Pose/Hands/Face
- Process frames and extract landmarks
- Manage tracker lifecycle

**Key Methods:**
```python
trackers = MediaPipeTrackers(use_pose=True, use_hands=False)
trackers.initialize()
result = trackers.process_frame(frame_rgb)
# result.pose_landmarks, result.hand_landmarks, result.face_landmarks
trackers.cleanup()
```

**MediaPipe Modules:**
- **Pose**: 33 body landmarks (required)
- **Hands**: 21 landmarks per hand (optional)
- **Face**: 468 facial landmarks (optional)

### Retargeting (`runtime/retarget.py`)

**Responsibilities:**
- Convert MediaPipe normalized coords → Blender 3D positions
- Compute bone rotations from landmark pairs
- Scale normalization

**Key Functions:**
```python
# Convert landmarks to positions
positions = landmarks_to_positions(landmarks, scale, z_offset)

# Normalize scale (e.g., shoulder width)
scale_factor = normalize_skeleton_scale(positions, (11, 12))

# Compute rotation from landmark chain
rotation = compute_bone_rotation_from_chain(start_pos, end_pos)
```

**Coordinate Conversion:**
```
MediaPipe (normalized [0,1]):        Blender (world space):
  X: 0 (left) → 1 (right)              X: -n ← 0 → +n
  Y: 0 (top) → 1 (bottom)              Y: -n (back) ↔ +n (forward)
  Z: depth (relative)                  Z: -n (down) ↔ +n (up)
```

### Filtering (`runtime/filters.py`)

**Three filter types:**

1. **SmoothingFilter (EWMA)**
   ```python
   smoothed = prev * (1 - α) + current * α
   ```
   - Works with Vector, Quaternion, float
   - Uses `lerp` for vectors, `slerp` for quaternions

2. **ConfidenceGate**
   ```python
   if confidence >= threshold:
       return value
   else:
       return last_valid_value
   ```
   - Rejects low-confidence landmarks
   - Returns last known good value

3. **FootLockFilter**
   ```python
   if foot_height < threshold and velocity < 0.1:
       locked = True
       return Vector(x, y, locked_height)
   ```
   - Simple ground plane locking
   - Prevents foot sliding

### Recording (`runtime/recording.py`)

**Responsibilities:**
- Insert keyframes during live capture
- Create timestamped actions
- Optional keyframe cleanup

**Key Classes:**
```python
recorder = KeyframeRecorder(armature)
recorder.start(frame=1)
recorder.insert_keyframe("bone_name", location=True, rotation=True)
recorder.stop()

# Bake final action
action = create_action(armature, name="Capture_20241029")
bake_action(armature, start_frame, end_frame, clean=True)
```

## Extending the Add-on

### Adding a New Tracker Module

1. **Add to `runtime/trackers.py`:**
```python
class MediaPipeTrackers:
    def __init__(self, ..., use_custom=False):
        self.use_custom = use_custom
        self.custom = None
    
    def initialize(self):
        if self.use_custom:
            mp_custom = mp.solutions.custom
            self.custom = mp_custom.Custom(...)
    
    def process_frame(self, frame_rgb):
        result = LandmarkResult()
        if self.custom:
            custom_results = self.custom.process(frame_rgb)
            result.custom_landmarks = custom_results.landmarks
        return result
```

2. **Add property to `properties.py`:**
```python
use_custom: BoolProperty(
    name="Use Custom",
    description="Enable custom tracking",
    default=False
)
```

3. **Add toggle to `panel.py`:**
```python
row.prop(settings, "use_custom", toggle=True)
```

### Adding a New Filter

1. **Create filter class in `runtime/filters.py`:**
```python
class CustomFilter:
    def __init__(self, param=1.0):
        self.param = param
    
    def filter(self, value):
        # Your filtering logic
        return filtered_value
    
    def reset(self):
        # Reset internal state
        pass
```

2. **Add to `MultiFilter`:**
```python
class MultiFilter:
    def __init__(self, ..., custom_param=1.0):
        self.custom_filter = CustomFilter(custom_param)
    
    def filter_position(self, pos, ...):
        pos = self.custom_filter.filter(pos)
        return pos
```

### Adding a New Bone Mapping Preset

In `runtime/mapping.py`:

```python
DEFAULT_BONE_MAP = {
    # Existing mappings...
    
    # Add your rig's bone names
    "LEFT_ELBOW": ["forearm.L", "elbow.L", "YourRig_LeftElbow"],
    "CUSTOM_LANDMARK": ["your_bone_name", "alternate_name"],
}

# For computed landmarks:
def compute_custom_landmark(positions):
    # Calculate from existing landmarks
    custom_pos = (positions[1] + positions[2]) / 2
    return custom_pos
```

### Adding a New Operator

1. **Create `src/ops/op_your_feature.py`:**
```python
import bpy
from bpy.types import Operator

class MOCAP_OT_YourFeature(Operator):
    """Tooltip description"""
    bl_idname = "mocap.your_feature"
    bl_label = "Your Feature"
    bl_description = "Detailed description"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mocap_settings
        # Your logic here
        self.report({'INFO'}, "Success message")
        return {'FINISHED'}
```

2. **Add to `src/ops/__init__.py`:**
```python
from . import your_feature

def get_operator_classes():
    return [
        # ... existing operators
        your_feature.MOCAP_OT_YourFeature,
    ]
```

3. **Add button to `src/panel.py`:**
```python
def draw_your_section(self, layout, settings):
    box = layout.box()
    box.label(text="Your Section", icon='ICON_NAME')
    box.operator("mocap.your_feature", icon='ICON')
```

### Adding a New Export Format

In `src/io/export.py`:

```python
def export_action_to_custom(armature, filepath):
    """Export to custom format."""
    try:
        # Your export logic
        with open(filepath, 'w') as f:
            # Write data
            pass
        return True
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return False
```

## Testing Strategies

### 1. Manual Testing Checklist

- [ ] Install dependencies
- [ ] Enable add-on
- [ ] Open help dialog - verify versions
- [ ] Select target armature
- [ ] Auto-fill bone map
- [ ] Start capture - verify camera opens
- [ ] Move in frame - verify bones move
- [ ] Adjust smoothing - verify effect
- [ ] Start recording
- [ ] Stop recording - verify frame count
- [ ] Bake action - verify action created
- [ ] Play timeline - verify animation plays
- [ ] Save/load bone map - verify persistence
- [ ] Stop capture - verify cleanup

### 2. Edge Cases to Test

- No camera available
- Camera index out of range
- No armature selected
- Empty bone mappings
- Landmarks not detected (poor lighting)
- Very fast motion (dropped frames)
- Long recording sessions (memory)
- Multiple armatures in scene
- Rig with custom bone names

### 3. Performance Profiling

Add timing to critical sections:

```python
import time

start = time.perf_counter()
# ... code to profile ...
elapsed = time.perf_counter() - start
print(f"Operation took {elapsed*1000:.2f}ms")
```

Monitor in `op_capture_start.py`:
- Frame read time
- MediaPipe processing time
- Retargeting time
- Filter time
- Keyframe insertion time

## Debugging Tips

### Enable Debug Logging

In `addon_prefs.py`, set:
```python
debug_mode: BoolProperty(default=True)
```

Then use:
```python
from ..utils.logging_utils import get_logger

logger = get_logger()
logger.debug("Detailed debug info")
logger.info("General info")
logger.warning("Warning message")
logger.error("Error details")
```

### Print Landmark Data

In `op_capture_start.retarget_pose()`:
```python
# Print first few landmarks
for i in range(min(5, len(landmarks))):
    lm = landmarks[i]
    print(f"Landmark {i}: x={lm.x:.3f}, y={lm.y:.3f}, z={lm.z:.3f}")
```

### Visualize in Console

```python
# Print bone transforms
for bone_name in ["upper_arm.L", "forearm.L"]:
    bone = armature.pose.bones[bone_name]
    print(f"{bone_name}: loc={bone.location}, rot={bone.rotation_quaternion}")
```

### Blender Console

Access Python console in Blender:
- **Workspace → Scripting**
- Or: **Window → Toggle System Console** (Windows)

## Code Style

### Formatting
- **Indentation**: 4 spaces
- **Line length**: ~100 characters (flexible)
- **Imports**: Group stdlib, third-party, local

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `CameraCapture`)
- **Functions**: `snake_case` (e.g., `get_logger`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_BONE_MAP`)
- **Private**: `_leading_underscore` (e.g., `_timer`)
- **Operator IDs**: `mocap.operator_name`

### Documentation
- **Docstrings**: All classes and public methods
- **Type hints**: Where helpful (especially utilities)
- **Comments**: Explain "why", not "what"

Example:
```python
def compute_bone_rotation(start_pos: Vector, end_pos: Vector) -> Quaternion:
    """
    Compute quaternion rotation from start to end position.
    
    Args:
        start_pos: Bone head position
        end_pos: Bone tail position
    
    Returns:
        Quaternion representing the rotation
    """
    direction = end_pos - start_pos
    # ... implementation
    return rotation
```

## Common Pitfalls

### 1. Blender API Thread Safety
**Problem**: Blender's API is not thread-safe.
**Solution**: Always do Blender operations in the main thread (modal operator).

### 2. MediaPipe Resource Leaks
**Problem**: MediaPipe objects must be explicitly closed.
**Solution**: Always call `.close()` in cleanup/cancel.

### 3. Camera Not Released
**Problem**: Camera stays locked if not released.
**Solution**: Use try/finally or ensure `cancel()` always runs.

### 4. PropertyGroup Defaults
**Problem**: PropertyGroup instances share default mutable objects.
**Solution**: Use `CollectionProperty` for lists, never default `[]`.

### 5. Operator Re-registration
**Problem**: Changing operator `bl_idname` breaks existing code.
**Solution**: Keep IDs stable, add new operators instead.

## Performance Optimization

### 1. Reduce Landmark Processing
```python
# Only process landmarks that have mappings
active_landmarks = set(m.landmark_name for m in settings.bone_mappings if m.enabled)

for idx, name in POSE_LANDMARK_NAMES.items():
    if name not in active_landmarks:
        continue  # Skip unused landmarks
```

### 2. Batch Keyframe Insertion
```python
# Instead of:
for frame in range(start, end):
    bone.keyframe_insert("location", frame=frame)

# Use:
bone.keyframe_insert("location", frame=start)
bone.keyframe_insert("location", frame=end)
# Blender interpolates between
```

### 3. Reduce Filter Overhead
```python
# Cache filter instances per bone
if bone_name not in self._filters:
    self._filters[bone_name] = MultiFilter(...)

filtered = self._filters[bone_name].filter_position(pos)
```

## Future Development Ideas

- [ ] 3D pose estimation with camera calibration
- [ ] IK solver integration for better foot placement
- [ ] Blendshape/shape key facial animation
- [ ] Multi-person tracking with selector UI
- [ ] Motion library browser
- [ ] Auto-retargeting between different rig types
- [ ] GPU acceleration for filtering
- [ ] Network streaming (receive mocap from another machine)
- [ ] Recording to custom formats (BVH, etc.)
- [ ] Real-time confidence visualization overlay

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (use checklist above)
5. Document your changes (docstrings, README updates)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

**Happy coding! 🚀**
