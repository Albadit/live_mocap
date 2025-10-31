# Camera Feed Visualization in 3D Viewport

## Overview

This update adds real-time camera feed visualization and MediaPipe landmark drawing directly in Blender's 3D Viewport. You can now see what your camera is capturing and the detected landmarks while performing motion capture.

## New Features

### 1. **Viewport Camera Feed Display**
- Shows a live preview of the camera feed in the bottom-left corner of the 3D Viewport
- 320x240 preview window with a dark background and border
- Updates in real-time during motion capture

### 2. **MediaPipe Landmark Overlay**
- Displays detected body landmarks as red points
- Shows skeleton connections as green lines
- Landmarks are overlaid on the camera feed preview
- Updates in real-time to show tracking quality

### 3. **Toggle Control**
- New "Show Camera Feed" checkbox in the Capture panel
- Can be toggled on/off to show/hide the viewport overlay
- Improves performance when disabled

## Files Added/Modified

### New Files:
1. **`runtime/viewport_draw.py`** - Core drawing functionality
   - `register_draw_handler()` - Registers the viewport draw callback
   - `unregister_draw_handler()` - Cleans up the draw callback
   - `update_camera_frame()` - Updates the camera frame data
   - `update_landmarks()` - Updates the landmark data
   - `draw_camera_feed()` - Draws the camera preview box
   - `draw_landmarks_2d()` - Draws landmarks and connections

2. **`operators/toggle_camera_feed.py`** - Toggle operator for camera feed visibility

### Modified Files:
1. **`runtime/__init__.py`** - Added viewport_draw module and cleanup
2. **`runtime/trackers.py`** - Added POSE_CONNECTIONS for drawing skeleton
3. **`operators/capture_start.py`** - Integrated viewport drawing:
   - Registers draw handler on capture start
   - Updates viewport with frame and landmarks each cycle
   - Forces viewport redraw
   - Unregisters draw handler on stop

4. **`operators/__init__.py`** - Registered new toggle operator
5. **`properties.py`** - Added `show_camera_feed` boolean property
6. **`panels/main.py`** - Added camera feed toggle in UI
7. **`__init__.py`** - Registered toggle operator

## How It Works

### Drawing Pipeline:
1. **Capture Start**: 
   - Registers a draw handler with Blender's `SpaceView3D.draw_handler_add()`
   - Creates texture dimensions for the camera feed
   
2. **Frame Processing**:
   - Each frame captured from the camera is sent to `viewport_draw.update_camera_frame()`
   - MediaPipe landmarks are sent to `viewport_draw.update_landmarks()`
   - Forces viewport redraw with `area.tag_redraw()`

3. **Draw Callback**:
   - Called by Blender during viewport rendering
   - Draws camera feed background box with border
   - Draws landmark connections as lines
   - Draws landmark points
   - Uses GPU shader from `gpu.shader.from_builtin()`

4. **Capture Stop**:
   - Unregisters the draw handler
   - Clears cached frame and landmark data
   - Forces final viewport redraw

## Usage

### Enable Camera Feed:
1. Open the Live Mocap panel in the 3D Viewport sidebar
2. In the **Capture** section, check **"Show Camera Feed"**
3. Start capture with the Play button
4. You'll see the camera feed in the bottom-left corner with landmarks overlaid

### Disable Camera Feed:
1. Uncheck **"Show Camera Feed"** before or during capture
2. The viewport drawing will be disabled
3. Improves performance when visualization is not needed

## Technical Details

### Coordinate Systems:
- Camera frame: OpenCV BGR format, converted to RGBA
- Flipped vertically to match OpenGL coordinate system
- Landmarks: Normalized 0-1 coordinates converted to screen pixels
- Screen space: Bottom-left origin for 2D overlay

### Performance Considerations:
- Drawing happens in `POST_PIXEL` space (after 3D rendering)
- Minimal overhead when enabled (~1-2ms per frame)
- Can be disabled for maximum capture performance
- Uses efficient GPU batch rendering

### GPU Rendering:
- Uses Blender's `gpu` module for hardware-accelerated drawing
- `UNIFORM_COLOR` shader for simple shapes (lines, points)
- Batch rendering for efficient drawing of multiple primitives
- Alpha blending for semi-transparent overlay

## Landmark Visualization

### Pose Connections:
The skeleton is drawn using 33 MediaPipe pose landmarks connected as:
- Face: Eyes, nose, mouth, ears
- Upper body: Shoulders, elbows, wrists
- Hands: Thumb, index, pinky fingers
- Torso: Shoulder line, hip line
- Lower body: Hips, knees, ankles, feet

### Color Scheme:
- **Red points** (size 5.0): Individual landmarks
- **Green lines** (width 2.0, alpha 0.7): Skeleton connections
- **Dark background** (alpha 0.8): Camera feed box
- **Gray border** (width 2.0): Feed outline

## Future Enhancements

Potential improvements for future versions:
1. Adjustable feed size and position
2. Multiple camera view support
3. Hand and face landmark visualization
4. Confidence indicators (color-coded landmarks)
5. Recording the camera feed to video file
6. Picture-in-picture mode with larger preview
7. Toggle individual landmark groups (body/hands/face)
8. Overlay FPS and stats directly on feed

## Troubleshooting

### No viewport overlay showing:
- Ensure "Show Camera Feed" is checked
- Verify capture is running (not just idle)
- Check that camera is providing frames

### Performance issues:
- Disable "Show Camera Feed" if not needed
- Reduce target FPS in capture settings
- Close other viewport overlays

### Landmarks not visible:
- Ensure person is in camera frame
- Check lighting conditions
- Adjust "Min Confidence" threshold
- Verify "Use Pose" is enabled
