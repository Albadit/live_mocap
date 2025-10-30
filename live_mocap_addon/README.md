# Live Mocap (MediaPipe) - Blender Add-on

Real-time motion capture for Blender using MediaPipe and OpenCV. Capture body, hand, and face motion directly from your webcam and retarget it to any armature in real-time.

## Features

✅ **Real-time Tracking**
- Body pose tracking (33 landmarks)
- Optional hand tracking (21 landmarks per hand)
- Optional face tracking (468 landmarks)
- Live preview without blocking Blender

✅ **Flexible Retargeting**
- Auto-mapping for common rig types (Rigify, Unity, etc.)
- Custom bone mapping with save/load
- Multiple coordinate space options
- Configurable scale and offset

✅ **Recording & Animation**
- Live keyframe recording at scene FPS
- Bake to timestamped actions
- Clean, non-destructive workflow

✅ **Filters & Smoothing**
- EWMA smoothing for positions and rotations
- Confidence-based gating
- Optional foot locking
- Performance metrics (FPS, latency, dropped frames)

## Installation

### 1. Install Dependencies

The add-on requires `opencv-python` and `mediapipe` to be installed in Blender's Python environment.

**Windows:**
```cmd
"C:\Program Files\Blender Foundation\Blender 4.x\4.x\python\bin\python.exe" -m pip install opencv-python mediapipe
```

**macOS:**
```bash
/Applications/Blender.app/Contents/Resources/4.x/python/bin/python3.11 -m pip install opencv-python mediapipe
```

**Linux:**
```bash
/path/to/blender/4.x/python/bin/python3.11 -m pip install opencv-python mediapipe
```

### 2. Install Add-on

1. Download or clone this repository
2. In Blender: **Edit → Preferences → Add-ons**
3. Click **Install** and select the `live_mocap_addon` folder (or zip it first)
4. Enable **Animation: Live Mocap (MediaPipe)**
5. Restart Blender (recommended)

## Quick Start

### Basic Workflow

1. **Prepare Your Rig**
   - Open or create a scene with an armature
   - Select the armature
   - Open the **N-panel** (press `N` in 3D Viewport)
   - Go to the **Mocap** tab

2. **Set Target**
   - Click **Select Target** to bind the active armature
   - Adjust **Scale** and **Z-Offset** if needed

3. **Map Bones**
   - Click **Auto-Fill Bone Map** to automatically map bones
   - Review the mapping in the list (edit if needed)
   - Optionally **Save Map** for reuse

4. **Start Capture**
   - Ensure your webcam is connected
   - Click **Start Capture**
   - You should see live motion applied to your rig

5. **Record Animation**
   - Set your timeline to the start frame
   - Click **Record** to begin keyframe insertion
   - Perform your motion
   - Click **Stop Recording** when done

6. **Bake Action**
   - Click **Bake to Action** to finalize
   - Your animation is now saved as an Action (e.g., `Mediapipe_Capture_20251029_143022`)
   - Play back in the timeline!

## UI Overview

### Target Section
- **Select Target**: Bind active armature
- **Coordinate Space**: World/Armature/Bone local space
- **Scale**: Overall motion scale multiplier
- **Z-Up Offset**: Vertical offset adjustment

### Bone Mapping Section
- **Auto-Fill Bone Map**: Automatically match landmarks to bones
- **Clear Map**: Remove all mappings
- **Save/Load Map**: Persist mappings to JSON files in `/mocap_maps/`
- **UIList**: Edit landmark → bone mappings
- **+/-**: Add/remove custom mappings

### Capture Section
- **Camera Index**: Webcam device index (usually 0)
- **FPS**: Target frame rate (30 recommended)
- **Use Pose/Hands/Face**: Toggle tracking modules
- **Start/Stop Capture**: Control live capture
- **Status**: Live FPS, latency, and dropped frames

### Record Section
- **Record/Stop Recording**: Control keyframe insertion
- **Bake to Action**: Finalize recording as an Action
- **Frame Counter**: Shows recorded frame count

### Filters Section
- **Smoothing**: EWMA filter strength (0=none, 1=max)
- **Min Confidence**: Minimum landmark confidence threshold
- **Foot Lock Threshold**: Simple foot IK locking

### Utilities Section
- **Zero Pose**: Reset all mapped bones to rest pose
- **Apply Rest Offset**: Compute rest pose offsets (placeholder)
- **Help**: Show dependency status and installation instructions

## Default Bone Mapping

The add-on auto-maps these MediaPipe landmarks to common bone names:

| Landmark | Common Bone Names |
|----------|-------------------|
| NOSE | head, Head |
| LEFT_SHOULDER | shoulder.L, upper_arm.L, UpperArm.L |
| RIGHT_SHOULDER | shoulder.R, upper_arm.R, UpperArm.R |
| LEFT_ELBOW | forearm.L, elbow.L, LowerArm.L |
| RIGHT_ELBOW | forearm.R, elbow.R, LowerArm.R |
| LEFT_WRIST | hand.L, Hand.L |
| RIGHT_WRIST | hand.R, Hand.R |
| LEFT_HIP | thigh.L, upper_leg.L, UpperLeg.L |
| RIGHT_HIP | thigh.R, upper_leg.R, UpperLeg.R |
| LEFT_KNEE | shin.L, lower_leg.L, LowerLeg.L |
| RIGHT_KNEE | shin.R, lower_leg.R, LowerLeg.R |
| LEFT_ANKLE | foot.L, Foot.L |
| RIGHT_ANKLE | foot.R, Foot.R |
| SPINE_PROXY | spine, spine.001, Spine, chest |

## Project Structure

```
live_mocap_addon/
├── __init__.py              # Blender entry point (bl_info, register/unregister)
├── src/
│   ├── __init__.py          # Package root, registration
│   ├── addon_prefs.py       # Add-on preferences
│   ├── properties.py        # PropertyGroups for UI state
│   ├── panel.py             # N-panel UI layout
│   ├── ops/                 # Operator classes
│   │   ├── op_select_target.py
│   │   ├── op_autofill_map.py
│   │   ├── op_capture_start.py  # Main modal operator
│   │   ├── op_record_start.py
│   │   ├── op_bake_action.py
│   │   └── ...
│   ├── runtime/             # Live systems
│   │   ├── dependency_check.py  # Safe imports, version checks
│   │   ├── capture.py       # OpenCV camera management
│   │   ├── trackers.py      # MediaPipe trackers
│   │   ├── retarget.py      # Landmark → bone math
│   │   ├── mapping.py       # Auto-mapping logic
│   │   ├── recording.py     # Keyframe insertion
│   │   └── filters.py       # Smoothing, confidence gating
│   ├── io/                  # File I/O
│   │   ├── json_maps.py     # Save/load bone maps
│   │   └── export.py        # FBX export (optional)
│   └── utils/               # Shared utilities
│       ├── logging_utils.py # Logger
│       ├── naming.py        # Bone name fuzzy matching
│       └── coords.py        # Coordinate transforms
└── README.md
```

## Troubleshooting

### "Missing Dependencies" Error
- Ensure `opencv-python` and `mediapipe` are installed in Blender's Python
- Run the install command from **Installation** section
- Restart Blender after installation
- Click **Help** button in the panel to verify installation

### Camera Not Opening
- Check camera index (usually 0 for built-in webcam, 1+ for external)
- Ensure no other application is using the camera
- Try different camera index values

### Poor Tracking Quality
- Ensure good lighting
- Stand/sit centered in frame with full body visible
- Increase **Min Confidence** threshold
- Reduce **Smoothing** if motion is too sluggish

### Bones Not Moving
- Verify bone mappings are correct (check bone names in UIList)
- Ensure mapped bones exist in your armature
- Check that **Use Pose** is enabled
- Verify armature is in Pose Mode or has pose bones

### Performance Issues
- Lower **FPS** target (e.g., 24 instead of 30)
- Disable **Use Hands** and **Use Face** if not needed
- Close other applications
- Use lower MediaPipe complexity (code modification required)

## Technical Details

### Coordinate System Conversion

MediaPipe outputs normalized coordinates [0, 1]:
- **X**: 0 (left) → 1 (right)
- **Y**: 0 (top) → 1 (bottom)
- **Z**: Depth (relative scale)

Converted to Blender:
- **X**: Left/right (centered at 0)
- **Y**: Depth (forward/back)
- **Z**: Up/down (flipped from MediaPipe Y)

### Retargeting Pipeline

1. **Capture**: OpenCV reads webcam frame
2. **Detect**: MediaPipe extracts landmarks
3. **Convert**: Landmarks → Blender positions
4. **Normalize**: Scale based on shoulder width
5. **Filter**: Apply smoothing and confidence gating
6. **Compute**: Calculate bone rotations from landmark pairs
7. **Apply**: Set bone transforms
8. **Record**: Insert keyframes (if recording)

### Smoothing (EWMA)

Exponential Weighted Moving Average with configurable alpha:
- `smoothed = prev * (1 - α) + current * α`
- For quaternions: uses slerp instead of lerp
- Per-bone filters maintain state across frames

## Advanced Usage

### Custom Bone Mappings

1. Add a new mapping with **+** button
2. Set **Landmark** name (e.g., `LEFT_ELBOW`)
3. Set **Bone** name (exact name from your armature)
4. Enable the checkbox
5. Save with **Save Map** for reuse

### JSON Map Format

```json
[
  {
    "landmark": "LEFT_SHOULDER",
    "bone": "upper_arm.L",
    "enabled": true
  },
  ...
]
```

Maps are saved to `/mocap_maps/` relative to your .blend file.

### Exporting Animation

After baking:
1. Select the armature
2. **File → Export → FBX**
3. Enable **Bake Animation**
4. Choose frame range
5. Export

Or use the built-in export utility (if implemented in `io/export.py`).

## Known Limitations

- **2.5D Tracking**: MediaPipe Z-depth is relative, not absolute
- **Single Person**: Tracks only one person at a time
- **Lighting Dependent**: Requires good lighting for accurate tracking
- **No IK Solving**: Direct bone transforms (IK chains may need adjustment)
- **Foot Sliding**: Foot lock filter is basic (threshold-based)

## Future Enhancements

- [ ] True 3D pose estimation with camera calibration
- [ ] Advanced IK solving for foot/hand contact
- [ ] Multi-person tracking support
- [ ] Face rig retargeting (blendshapes/shape keys)
- [ ] Hand finger retargeting to finger chains
- [ ] Latency optimization
- [ ] Recording pause/resume
- [ ] Keyframe cleanup/simplification
- [ ] Real-time visualization overlay

## Credits

- **Blender**: https://www.blender.org
- **MediaPipe**: https://google.github.io/mediapipe/
- **OpenCV**: https://opencv.org

## License

This add-on is provided as-is for educational and personal use.

## Support

For issues, questions, or contributions:
- Check the **Help** dialog in the add-on panel
- Review this README thoroughly
- Verify dependencies are installed correctly

---

**Happy Motion Capturing! 🎬**
