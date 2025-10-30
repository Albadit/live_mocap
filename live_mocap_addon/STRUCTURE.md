# Live Mocap (MediaPipe) - Project Structure

## Directory Tree

```
live_mocap_addon/
│
├── __init__.py                      # 🔹 BLENDER ENTRY POINT
│                                    #    - bl_info metadata
│                                    #    - Imports src package
│                                    #    - register()/unregister()
│
├── README.md                        # 📖 Complete documentation
│
└── src/                             # 📦 Main source package
    │
    ├── __init__.py                  # 🔹 Package registration
    │                                #    - Collects all classes
    │                                #    - Registers with Blender
    │                                #    - Scene property setup
    │
    ├── addon_prefs.py               # ⚙️ Add-on preferences
    │                                #    - Default map folder
    │                                #    - Debug mode
    │                                #    - Advanced settings
    │
    ├── properties.py                # 📊 Property groups
    │                                #    - MOCAP_PG_BoneMapping
    │                                #    - MOCAP_PG_Settings
    │                                #    - MOCAP_UL_BoneMappingList (UIList)
    │
    ├── panel.py                     # 🎨 N-panel UI
    │                                #    - MOCAP_PT_MainPanel
    │                                #    - All UI sections (Target, Mapping, etc.)
    │
    ├── ops/                         # 🎬 Operator classes
    │   ├── __init__.py              #    - get_operator_classes()
    │   ├── op_select_target.py      #    - Select armature
    │   ├── op_autofill_map.py       #    - Auto-fill bone mappings
    │   ├── op_clear_map.py          #    - Clear mappings
    │   ├── op_save_map.py           #    - Save to JSON
    │   ├── op_load_map.py           #    - Load from JSON
    │   ├── op_add_mapping.py        #    - Add UIList item
    │   ├── op_remove_mapping.py     #    - Remove UIList item
    │   ├── op_capture_start.py      #    ⭐ MAIN MODAL OPERATOR
    │   ├── op_capture_stop.py       #    - Stop capture
    │   ├── op_record_start.py       #    - Start keyframing
    │   ├── op_record_stop.py        #    - Stop keyframing
    │   ├── op_bake_action.py        #    - Bake to Action
    │   ├── op_zero_pose.py          #    - Reset bones
    │   ├── op_apply_rest_offset.py  #    - Rest offset (placeholder)
    │   └── op_show_help.py          #    - Help dialog
    │
    ├── runtime/                     # 🚀 Live capture systems
    │   ├── __init__.py              #    - initialize()/cleanup()
    │   ├── dependency_check.py      #    - Safe imports for cv2/mediapipe
    │   │                            #    - Version checking
    │   │                            #    - Install instructions
    │   ├── capture.py               #    - CameraCapture class
    │   │                            #    - OpenCV camera management
    │   │                            #    - Frame reading & timing
    │   ├── trackers.py              #    - MediaPipeTrackers class
    │   │                            #    - Pose/Hands/Face initialization
    │   │                            #    - Landmark extraction
    │   ├── retarget.py              #    - Landmark → bone math
    │   │                            #    - landmarks_to_positions()
    │   │                            #    - compute_bone_rotation_from_chain()
    │   ├── mapping.py               #    - auto_map_bones()
    │   │                            #    - DEFAULT_BONE_MAP
    │   │                            #    - LANDMARK_CHAINS
    │   ├── recording.py             #    - KeyframeRecorder class
    │   │                            #    - create_action()
    │   │                            #    - bake_action()
    │   └── filters.py               #    - SmoothingFilter (EWMA)
    │                                #    - ConfidenceGate
    │                                #    - FootLockFilter
    │                                #    - MultiFilter
    │
    ├── io/                          # 💾 File I/O
    │   ├── __init__.py
    │   ├── json_maps.py             #    - save_bone_map()
    │   │                            #    - load_bone_map()
    │   │                            #    - get_default_map_directory()
    │   └── export.py                #    - export_action_to_fbx()
    │
    └── utils/                       # 🛠️ Shared utilities
        ├── __init__.py
        ├── logging_utils.py         #    - AddonLogger
        │                            #    - get_logger()
        ├── naming.py                #    - Bone name fuzzy matching
        │                            #    - BONE_PATTERNS
        │                            #    - normalize_bone_name()
        │                            #    - find_bone_in_armature()
        └── coords.py                #    - mediapipe_to_blender()
                                     #    - direction_to_quaternion()
                                     #    - world_to_local() transforms
```

## Data Flow

```
┌─────────────┐
│   WEBCAM    │
└──────┬──────┘
       │
       ↓
┌────────────────────────────────────────────────────┐
│  op_capture_start.py (Modal Operator)              │
│  ┌──────────────────────────────────────────────┐  │
│  │  1. Camera Capture (capture.py)              │  │
│  │     └→ OpenCV reads frame                    │  │
│  │  2. MediaPipe Tracking (trackers.py)         │  │
│  │     └→ Extract pose/hand/face landmarks      │  │
│  │  3. Retargeting (retarget.py)                │  │
│  │     └→ Convert landmarks → Blender positions │  │
│  │     └→ Compute bone rotations                │  │
│  │  4. Filtering (filters.py)                   │  │
│  │     └→ Smooth, confidence gate, foot lock    │  │
│  │  5. Apply to Bones                           │  │
│  │     └→ Set bone.location & rotation          │  │
│  │  6. Recording (recording.py) [if enabled]    │  │
│  │     └→ Insert keyframes                      │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────┐
│  Animation  │  (Keyframes in timeline)
│   Action    │
└─────────────┘
```

## Key Classes

### Properties (`properties.py`)
- `MOCAP_PG_BoneMapping`: Single landmark → bone mapping
- `MOCAP_PG_Settings`: Main settings (target, fps, filters, status)
- `MOCAP_UL_BoneMappingList`: UIList for editing mappings

### Runtime Systems
- `CameraCapture`: OpenCV webcam management
- `MediaPipeTrackers`: MediaPipe Pose/Hands/Face
- `SmoothingFilter`: EWMA filter
- `MultiFilter`: Combined filtering system
- `KeyframeRecorder`: Keyframe insertion

### Operators
- `MOCAP_OT_CaptureStart`: ⭐ Main modal operator (frame loop)
- `MOCAP_OT_AutoFillBoneMap`: Auto-map bones
- `MOCAP_OT_RecordStart`: Start keyframing
- `MOCAP_OT_BakeAction`: Create final action

## Module Dependencies

```
__init__.py (root)
    └── src.__init__
        ├── addon_prefs
        ├── properties
        ├── panel
        │   └── runtime.dependency_check
        ├── ops
        │   ├── op_capture_start
        │   │   ├── runtime.capture
        │   │   ├── runtime.trackers
        │   │   ├── runtime.retarget
        │   │   ├── runtime.filters
        │   │   └── runtime.dependency_check
        │   ├── op_autofill_map
        │   │   └── runtime.mapping
        │   ├── op_save_map
        │   │   └── io.json_maps
        │   └── ...
        ├── runtime
        │   ├── dependency_check
        │   ├── capture
        │   │   └── utils.logging_utils
        │   ├── trackers
        │   │   └── utils.logging_utils
        │   ├── retarget
        │   │   └── utils.coords
        │   ├── mapping
        │   │   └── utils.naming
        │   ├── recording
        │   │   └── utils.logging_utils
        │   └── filters
        ├── io
        │   ├── json_maps
        │   │   └── utils.logging_utils
        │   └── export
        │       └── utils.logging_utils
        └── utils
            ├── logging_utils
            ├── naming
            └── coords
```

## Critical Files for Understanding

1. **`__init__.py` (root)**: Entry point - shows Blender what to load
2. **`src/__init__.py`**: Registration logic - collects all classes
3. **`src/ops/op_capture_start.py`**: Main capture loop - the heart of the system
4. **`src/runtime/retarget.py`**: Math for landmark → bone conversion
5. **`src/panel.py`**: UI layout - what users see

## Usage Pattern

```python
# 1. User clicks "Start Capture"
#    → op_capture_start.invoke()
#       → Opens camera (capture.py)
#       → Initializes MediaPipe (trackers.py)
#       → Sets up filters (filters.py)
#       → Adds timer for modal loop

# 2. Timer fires every frame
#    → op_capture_start.modal()
#       → process_frame()
#          → camera.read_frame()
#          → trackers.process_frame()
#          → retarget_pose()
#             → landmarks_to_positions()
#             → filter.filter_position()
#             → bone.location = position
#             → compute_rotation()
#             → bone.rotation_quaternion = rotation
#             → IF recording: keyframe_insert()

# 3. User clicks "Stop Capture"
#    → op_capture_stop.execute()
#       → settings.is_capturing = False
#       → modal() returns CANCELLED
#       → cancel() cleanup: camera.release(), trackers.cleanup()
```

## Extension Points

Want to add features? Here are the best places:

- **New tracking module**: Add to `runtime/trackers.py`
- **New filter**: Add class to `runtime/filters.py`
- **New coordinate transform**: Add to `utils/coords.py`
- **New bone mapping preset**: Add to `runtime/mapping.py` DEFAULT_BONE_MAP
- **New export format**: Add function to `io/export.py`
- **New operator**: Create `src/ops/op_your_feature.py`, add to `ops/__init__.py`

---

**Note**: The lint errors about `bpy` and `mathutils` imports are expected - these modules are provided by Blender at runtime.
