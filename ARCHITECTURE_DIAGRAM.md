# System Architecture Diagram

## Component Overview

```
┌────────────────────────────────────────────────────────────────┐
│                     BLENDER 3D VIEWPORT                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                                                        │    │
│  │            3D Scene Rendering                         │    │
│  │                                                        │    │
│  │                                                        │    │
│  │  ┌───────────────────────────────┐                   │    │
│  │  │  POST_PIXEL Draw Handler     │                   │    │
│  │  │  ┌─────────────────────┐     │                   │    │
│  │  │  │ ┌──────────────┐   │     │                   │    │
│  │  │  │ │              │   │     │                   │    │
│  │  │  │ │ Camera Feed  │   │     │                   │    │
│  │  │  │ │   🔴─🟢─🔴   │   │     │                   │    │
│  │  │  │ │   │  │  │   │   │     │                   │    │
│  │  │  │ │   🔴─🟢─🔴   │   │     │                   │    │
│  │  │  │ │   │  │  │   │   │     │                   │    │
│  │  │  │ │   🔴─🟢─🔴   │   │     │                   │    │
│  │  │  │ └──────────────┘   │     │                   │    │
│  │  │  │  viewport_draw.py  │     │                   │    │
│  │  │  └─────────────────────┘     │                   │    │
│  │  └───────────────────────────────┘                   │    │
│  └──────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────┐
│   Camera    │  OpenCV captures frame
│  (Hardware) │
└──────┬──────┘
       │ BGR Frame (numpy array)
       ↓
┌─────────────────┐
│ CameraCapture   │  Reads frame, converts BGR→RGB
│   (capture.py)  │
└──────┬──────────┘
       │ BGR Frame + RGB Frame
       ↓
┌─────────────────┐
│ capture_start   │  Modal operator - main loop
│  (operator)     │
└──┬───────────┬──┘
   │           │
   │           └──────────────┐
   │                          │
   │ RGB Frame                │ BGR Frame
   ↓                          ↓
┌──────────────┐      ┌──────────────────┐
│ MediaPipe    │      │ viewport_draw    │
│  Trackers    │      │ update_camera    │
│ (trackers.py)│      │     _frame()     │
└──────┬───────┘      └──────────────────┘
       │                      
       │ Landmarks            
       ↓                      
┌──────────────┐              
│ viewport_draw│              
│ update_land  │              
│   marks()    │              
└──────────────┘              
       │                      
       │                      
       ↓                      
┌──────────────────────┐      
│  Draw Callback       │  ← Blender calls during viewport render
│  draw_callback()     │
│                      │
│  1. draw_camera_feed()  → Background box + border
│  2. draw_landmarks_2d() → Points + lines
│                      │
└──────────────────────┘
       │
       ↓
┌──────────────────────┐
│  GPU Rendering       │
│  - Shaders           │
│  - Batch rendering   │
│  - Alpha blending    │
└──────────────────────┘
       │
       ↓
┌──────────────────────┐
│  Viewport Display    │
└──────────────────────┘
```

## Module Structure

```
live_mocap_addon/
│
├── runtime/
│   │
│   ├── viewport_draw.py          ← NEW! Drawing system
│   │   ├── register_draw_handler()
│   │   ├── unregister_draw_handler()
│   │   ├── update_camera_frame()
│   │   ├── update_landmarks()
│   │   ├── draw_camera_feed()
│   │   ├── draw_landmarks_2d()
│   │   └── draw_callback()       ← Main entry point
│   │
│   ├── capture.py                 ← Camera capture
│   │   └── CameraCapture.read_frame()
│   │
│   ├── trackers.py                ← MODIFIED: Added POSE_CONNECTIONS
│   │   ├── POSE_LANDMARK_NAMES
│   │   ├── POSE_CONNECTIONS      ← NEW!
│   │   └── MediaPipeTrackers
│   │
│   └── __init__.py                ← MODIFIED: Import viewport_draw
│
├── operators/
│   │
│   ├── capture_start.py           ← MODIFIED: Integrated drawing
│   │   ├── invoke()              → Register handler
│   │   ├── process_frame()       → Update viewport
│   │   └── cancel()              → Unregister handler
│   │
│   ├── toggle_camera_feed.py     ← NEW! Toggle operator
│   │   └── MOCAP_OT_ToggleCameraFeed
│   │
│   └── __init__.py                ← MODIFIED: Import new operator
│
├── properties.py                  ← MODIFIED: Added show_camera_feed
│   └── MOCAP_PG_Settings
│       └── show_camera_feed      ← NEW!
│
├── panels/
│   └── main.py                    ← MODIFIED: Added UI toggle
│       └── draw_capture_section()
│           └── "Show Camera Feed" checkbox
│
└── __init__.py                    ← MODIFIED: Register operator
```

## State Machine

```
┌─────────────┐
│   IDLE      │
│ (Not        │
│ Capturing)  │
└──────┬──────┘
       │
       │ User clicks "Start Capture"
       ↓
┌─────────────┐
│  STARTING   │
│             │
│ - Check     │
│ - Setup     │
│ - Register  │  ← register_draw_handler() if show_camera_feed=True
└──────┬──────┘
       │
       │ Success
       ↓
┌─────────────┐
│  CAPTURING  │ ← Modal operator running
│             │
│ Every frame:│
│ 1. Read     │ → camera.read_frame()
│ 2. Process  │ → trackers.process_frame()
│ 3. Update   │ → viewport_draw.update_*()
│ 4. Retarget │ → Apply to bones
│ 5. Redraw   │ → area.tag_redraw()
└──────┬──────┘
       │          ↑
       │          │
       └──────────┘ Loop (timer event)
       │
       │ User presses ESC or "Stop"
       ↓
┌─────────────┐
│  STOPPING   │
│             │
│ - Release   │
│ - Cleanup   │
│ - Unreg     │  ← unregister_draw_handler()
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   IDLE      │
└─────────────┘
```

## Draw Handler Lifecycle

```
Addon Registration
       ↓
   [Handler: None]
       │
       │ capture_start.invoke()
       │ if show_camera_feed:
       ↓
┌──────────────────┐
│ register_draw_   │
│    handler()     │
└────────┬─────────┘
         │
         │ Create handler
         ↓
┌──────────────────┐
│ SpaceView3D.     │
│ draw_handler_add │
│ (draw_callback,  │
│  'WINDOW',       │
│  'POST_PIXEL')   │
└────────┬─────────┘
         │
         ↓
   [Handler: Active]
         │
         │ Blender renders viewport
         ↓
┌──────────────────┐
│ draw_callback()  │  ← Called automatically by Blender
│                  │
│ 1. Check data    │
│ 2. Draw feed     │
│ 3. Draw landmarks│
└────────┬─────────┘
         │
         │ Loop every frame
         ↑─────────┘
         │
         │ capture_start.cancel()
         ↓
┌──────────────────┐
│ unregister_draw_ │
│    handler()     │
└────────┬─────────┘
         │
         │ Remove handler
         ↓
┌──────────────────┐
│ SpaceView3D.     │
│ draw_handler_    │
│    remove()      │
└────────┬─────────┘
         │
         ↓
   [Handler: None]
         │
         ↓
   Addon Cleanup
```

## Coordinate Systems

### Camera Space (OpenCV)
```
(0,0) ─────────────→ X (width=640)
│
│  Camera Image
│  BGR format
│
↓ Y (height=480)
```

### Normalized Landmark Space (MediaPipe)
```
(0.0, 0.0) ────────→ X (1.0)
│
│  Landmarks
│  x, y, z all 0.0-1.0
│
↓ Y (1.0)
```

### Screen Space (Viewport Drawing)
```
     Y (viewport height)
     ↑
     │
     │  3D Viewport
     │
     │
(0,0)└────────────→ X (viewport width)
Bottom-left origin

Camera feed box:
  x = 10 (margin)
  y = 10 (margin)
  width = 320
  height = 240
```

### Landmark to Screen Conversion
```python
# Normalized (0-1) → Screen pixels
screen_x = margin + (landmark.x * feed_width)
screen_y = margin + ((1.0 - landmark.y) * feed_height)  # Flip Y
#                     └── Flip because OpenGL Y is up, MediaPipe Y is down
```

## GPU Rendering Pipeline

```
┌─────────────────┐
│  Python Data    │
│  - vertices     │
│  - colors       │
│  - indices      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ batch_for_      │
│   shader()      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  GPU Batch      │
│  (optimized)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Shader         │
│  - UNIFORM_COLOR│
│  - IMAGE        │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  GPU State      │
│  - Blend mode   │
│  - Line width   │
│  - Point size   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Draw           │
│  batch.draw()   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Framebuffer    │
│  (Viewport)     │
└─────────────────┘
```

## Threading Model

```
┌──────────────────────┐
│   Main Thread        │
│   (Blender)          │
│                      │
│  ┌────────────────┐ │
│  │ Modal Operator │ │
│  │ (Timer Event)  │ │
│  └────────┬───────┘ │
│           │         │
│           │ Read    │
│           ↓         │
│  ┌────────────────┐ │
│  │ Camera Capture │ │
│  └────────┬───────┘ │
│           │         │
│           │ Process │
│           ↓         │
│  ┌────────────────┐ │
│  │ MediaPipe      │ │
│  └────────┬───────┘ │
│           │         │
│           │ Update  │
│           ↓         │
│  ┌────────────────┐ │
│  │ viewport_draw  │ │
│  │ (Update data)  │ │
│  └────────┬───────┘ │
│           │         │
│           │ Redraw  │
│           ↓         │
│  ┌────────────────┐ │
│  │ Viewport       │ │
│  │ Render         │ │
│  └────────┬───────┘ │
│           │         │
│           │ Callback│
│           ↓         │
│  ┌────────────────┐ │
│  │ draw_callback  │ │
│  │ (GPU Draw)     │ │
│  └────────────────┘ │
│                      │
│  All on main thread! │
└──────────────────────┘

No threading issues - everything sequential
```

## Memory Management

```
Global Variables (viewport_draw.py)
├── _draw_handler       : DrawHandler | None
├── _camera_texture     : dict | None
├── _current_frame      : np.ndarray | None (H×W×4 RGBA)
└── _current_landmarks  : Landmarks | None

Lifecycle:
1. register_draw_handler()    → Create _draw_handler
2. create_camera_texture()    → Store dimensions in _camera_texture
3. update_camera_frame()      → Store frame in _current_frame
4. update_landmarks()         → Store landmarks in _current_landmarks
5. draw_callback()            → Read from _current_frame/_current_landmarks
6. unregister_draw_handler()  → Clear all to None

Memory: ~300KB per frame (640×480×4 bytes)
```

---

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Easy to maintain and extend
- ✅ Minimal performance overhead
- ✅ Safe cleanup on shutdown
- ✅ No threading issues
- ✅ GPU-accelerated rendering
