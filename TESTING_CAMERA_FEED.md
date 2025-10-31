# Testing Camera Feed Visualization

## Quick Test Steps

### 1. Check Dependencies
```python
# Run this in Blender's Python Console:
import bpy
settings = bpy.context.scene.mocap_settings
print("Dependencies installed:", bpy.ops.mocap.install_dependencies.poll())
```

### 2. Test Draw Handler Registration
```python
# In Blender's Python Console:
from live_mocap_addon.runtime import viewport_draw

# Register handler
viewport_draw.register_draw_handler()
print("Handler active:", viewport_draw.is_draw_handler_active())

# Unregister handler
viewport_draw.unregister_draw_handler()
print("Handler active:", viewport_draw.is_draw_handler_active())
```

### 3. Check Property
```python
# In Blender's Python Console:
import bpy
settings = bpy.context.scene.mocap_settings
print("Show camera feed:", settings.show_camera_feed)

# Toggle it
settings.show_camera_feed = not settings.show_camera_feed
print("Now:", settings.show_camera_feed)
```

### 4. Full Integration Test

**Manual Test:**
1. Open Blender
2. Go to Edit → Preferences → Add-ons
3. Search for "Live Mocap"
4. Enable the addon
5. In 3D Viewport, press `N` to open sidebar
6. Go to **Mocap** tab
7. Set up a basic scene:
   - Add an armature (Shift+A → Armature)
   - In Mocap panel: Select armature as Target
   - Click "Add" to add a camera (index 0)
   - Check "Show Camera Feed"
   - Click "Build Bone List"
8. Click **▶ Start Capture**
9. Look at bottom-left corner of viewport
10. You should see a dark box with border
11. Move in front of camera to see landmarks

**Expected Result:**
- ✅ Dark box appears in bottom-left corner
- ✅ Red dots appear when body is detected
- ✅ Green lines connect the landmarks
- ✅ Status shows "Tracking | FPS: X.X | Latency: X.Xms"

**If Problems:**
- ❌ No box appearing → Check console for errors
- ❌ Box but no landmarks → Check camera is working, move into frame
- ❌ Capture won't start → Check dependencies are installed
- ❌ Blender crashes → Check GPU drivers, try disabling feed

### 5. Performance Test

```python
# Run during capture to check performance:
import bpy
settings = bpy.context.scene.mocap_settings

print(f"FPS: {settings.avg_latency:.1f}ms")
print(f"Dropped frames: {settings.dropped_frames}")
print(f"Recording: {settings.is_recording}")

# Toggle feed on/off to compare performance
settings.show_camera_feed = False  # Disable
# ... capture for a bit ...
settings.show_camera_feed = True   # Re-enable
```

### 6. Check for Errors

**In Blender Console (Window → Toggle System Console):**
```
Look for any error messages starting with:
- "Failed to register draw handler"
- "Failed to update camera frame"
- "Draw callback error"
- "Failed to draw..."
```

**Common Errors and Fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError: No module named 'cv2'` | OpenCV not installed | Click "Install Dependencies" |
| `ImportError: No module named 'mediapipe'` | MediaPipe not installed | Click "Install Dependencies" |
| `Failed to open camera` | Camera in use / wrong index | Change camera index, close other apps |
| `Draw handler already registered` | Previous session not cleaned up | Restart Blender |
| GPU errors | Driver issues | Update graphics drivers |

## Developer Testing

### Unit Test Draw Functions

```python
# Test drawing utilities (safe even without capture running):
from live_mocap_addon.runtime import viewport_draw
from mathutils import Vector

# Test landmark data structure
class FakeLandmark:
    def __init__(self, x, y, z, visibility=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

class FakeLandmarks:
    def __init__(self):
        self.landmark = [
            FakeLandmark(0.5, 0.5, 0.0),  # Nose
            FakeLandmark(0.4, 0.4, 0.0),  # Left eye
            FakeLandmark(0.6, 0.4, 0.0),  # Right eye
            # ... add more as needed
        ]

# Update with fake landmarks
fake_landmarks = FakeLandmarks()
viewport_draw.update_landmarks(fake_landmarks)
print("Landmarks updated")

# Register and force redraw
import bpy
viewport_draw.register_draw_handler()
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.tag_redraw()

# Should see landmarks drawn (if registered properly)
```

### Debug Drawing

Add debug prints to `viewport_draw.py`:

```python
def draw_callback():
    """Main draw callback function."""
    print("DEBUG: draw_callback called")  # Add this
    try:
        draw_camera_feed()
        draw_landmarks_2d()
    except Exception as e:
        logger = get_logger()
        logger.error(f"Draw callback error: {str(e)}")
```

### Verify POSE_CONNECTIONS

```python
from live_mocap_addon.runtime.trackers import POSE_CONNECTIONS
print(f"Total connections: {len(POSE_CONNECTIONS)}")
print(f"Connections: {POSE_CONNECTIONS[:5]}")  # First 5
```

Expected output:
```
Total connections: 35
Connections: [(0, 1), (1, 2), (2, 3), (3, 7), (0, 4)]
```

## Automated Test Script

Save this as `test_camera_feed.py` and run from Blender's Text Editor:

```python
import bpy
from live_mocap_addon.runtime import viewport_draw
from live_mocap_addon.runtime.trackers import POSE_CONNECTIONS

def test_camera_feed():
    print("\n" + "="*50)
    print("Testing Camera Feed Visualization")
    print("="*50 + "\n")
    
    # Test 1: Check property exists
    try:
        settings = bpy.context.scene.mocap_settings
        print(f"✓ Property 'show_camera_feed' exists: {settings.show_camera_feed}")
    except Exception as e:
        print(f"✗ Property error: {e}")
        return False
    
    # Test 2: Check POSE_CONNECTIONS
    try:
        assert len(POSE_CONNECTIONS) > 0
        print(f"✓ POSE_CONNECTIONS defined: {len(POSE_CONNECTIONS)} connections")
    except Exception as e:
        print(f"✗ POSE_CONNECTIONS error: {e}")
        return False
    
    # Test 3: Check draw handler registration
    try:
        viewport_draw.register_draw_handler()
        is_active = viewport_draw.is_draw_handler_active()
        print(f"✓ Draw handler registration: {is_active}")
        viewport_draw.unregister_draw_handler()
        is_inactive = not viewport_draw.is_draw_handler_active()
        print(f"✓ Draw handler unregistration: {is_inactive}")
    except Exception as e:
        print(f"✗ Draw handler error: {e}")
        return False
    
    # Test 4: Check camera texture creation
    try:
        texture = viewport_draw.create_camera_texture(640, 480)
        if texture and 'width' in texture and 'height' in texture:
            print(f"✓ Camera texture created: {texture['width']}x{texture['height']}")
        else:
            print(f"✗ Camera texture creation failed")
            return False
    except Exception as e:
        print(f"✗ Texture error: {e}")
        return False
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50 + "\n")
    return True

# Run the test
test_camera_feed()
```

## CI/CD Considerations

For automated testing environments:
- Mock `bpy` module for unit tests
- Test draw functions without OpenGL context
- Verify imports and module structure
- Check property definitions
- Validate connections data

## Next Steps After Testing

If all tests pass:
1. ✓ Test with real camera and motion capture
2. ✓ Verify performance (FPS, latency)
3. ✓ Test with different armature types
4. ✓ Record and bake animations
5. ✓ Document any issues found

If tests fail:
1. Check Blender version (3.6+ required)
2. Verify dependencies installed
3. Check Python version compatibility
4. Review console errors
5. Test with minimal scene (default cube only)
