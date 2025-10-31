# 🔧 Troubleshooting: No Skeleton Overlay Visible

## Quick Checklist

Before diving into details, verify these:

- [ ] **Addon is enabled** (Edit → Preferences → Add-ons → Live Mocap)
- [ ] **"Show Camera Feed" is checked** (in Mocap panel)
- [ ] **Capture is running** (Status shows "Tracking")
- [ ] **You're in front of the camera** (move into frame)
- [ ] **3D Viewport is visible** (not minimized or covered)

---

## Step-by-Step Diagnosis

### Step 1: Run the Debug Script

1. In Blender, go to **Scripting** workspace
2. Click **Text** → **Open** → Select `debug_viewport.py`
3. Click **Run Script** (▶ button or Alt+P)
4. Check the output in the **System Console** (Window → Toggle System Console)

**Expected output:**
```
CAMERA FEED VIEWPORT DEBUG TEST
================================
Handler active: True
Connections count: 35
show_camera_feed: True
...
```

### Step 2: Check System Console

Open the **System Console** (Window → Toggle System Console) and look for:

#### ✅ Good signs:
```
SUCCESS: Viewport draw handler registered
DEBUG: Updated landmarks, count: 33
DEBUG: Drawing 33 landmarks
DEBUG: Drawing 35 connections
```

#### ❌ Bad signs:
```
ERROR: Failed to register draw handler
ImportError: cannot import name 'POSE_CONNECTIONS'
AttributeError: 'list' object has no attribute 'landmark'
```

### Step 3: Verify Registration

Run this in **Python Console** (Scripting workspace, bottom panel):

```python
from live_mocap_addon.runtime import viewport_draw
print("Handler active:", viewport_draw.is_draw_handler_active())
```

**If False:**
```python
# Try registering manually
viewport_draw.register_draw_handler()
print("Handler active now:", viewport_draw.is_draw_handler_active())

# Force redraw
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.tag_redraw()
```

### Step 4: Check Property Value

```python
import bpy
settings = bpy.context.scene.mocap_settings
print("Show camera feed:", settings.show_camera_feed)

# If False, enable it
settings.show_camera_feed = True
```

### Step 5: Verify Data is Being Updated

```python
from live_mocap_addon.runtime import viewport_draw

print("Frame:", viewport_draw._current_frame is not None)
print("Landmarks:", viewport_draw._current_landmarks is not None)

if viewport_draw._current_landmarks:
    landmarks = viewport_draw._current_landmarks
    if isinstance(landmarks, list):
        print(f"Landmark count: {len(landmarks)}")
        if len(landmarks) > 0:
            lm = landmarks[0]
            print(f"First: x={lm.x:.3f}, y={lm.y:.3f}, z={lm.z:.3f}")
```

---

## Common Issues & Fixes

### Issue 1: Draw Handler Not Registered

**Symptoms:**
- No overlay at all
- Console shows: `Handler active: False`

**Fix:**
```python
from live_mocap_addon.runtime import viewport_draw
viewport_draw.register_draw_handler()

import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.tag_redraw()
```

### Issue 2: Landmarks Not Being Updated

**Symptoms:**
- Box visible but no dots/lines
- Console shows: `Landmarks: None`

**Cause:** Capture might not be running, or no person detected

**Fix:**
1. Start capture (click ▶ Start Capture)
2. Move in front of camera
3. Check "Use Pose" is enabled
4. Lower "Min Confidence" to 0.3

### Issue 3: Wrong Landmark Format

**Symptoms:**
- Console error: `AttributeError: 'list' object has no attribute 'landmark'`

**Fix:** This is already handled in the code. If you see this, the fix is in viewport_draw.py:
```python
# Landmarks come as a list from trackers.py
if isinstance(_current_landmarks, list):
    for landmark in _current_landmarks:
        # Process landmark
```

### Issue 4: POSE_CONNECTIONS Not Found

**Symptoms:**
- Console error: `ImportError: cannot import name 'POSE_CONNECTIONS'`

**Fix:** Reload the addon:
1. Edit → Preferences → Add-ons
2. Disable "Live Mocap"
3. Re-enable "Live Mocap"
4. Restart Blender if still failing

### Issue 5: Nothing Visible Despite No Errors

**Symptoms:**
- Handler active: True
- Landmarks updated
- No errors in console
- Still nothing visible

**Possible causes:**

#### A. Viewport Not Refreshing
```python
import bpy
# Force ALL viewports to redraw
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
```

#### B. Drawing Off-Screen
Check if the camera feed box is visible:
- Feed position: Bottom-left corner
- Coordinates: x=10, y=10
- Size: 320×240 pixels
- Make sure viewport is large enough (at least 350×270)

#### C. OpenGL State Issues
```python
# Check GPU module
import gpu
print("GPU module:", gpu)
print("Shader available:", gpu.shader.from_builtin('UNIFORM_COLOR'))
```

### Issue 6: Blender Crashes

**Symptoms:**
- Blender freezes or crashes when starting capture

**Immediate fix:**
1. Disable "Show Camera Feed"
2. Start capture without visualization
3. Update GPU drivers

**Long-term fix:**
```python
# Test GPU drawing separately
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

def test_draw():
    vertices = [(10, 10), (100, 10), (100, 100), (10, 100)]
    indices = [(0, 1, 2), (0, 2, 3)]
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    shader.bind()
    shader.uniform_float("color", (1, 0, 0, 1))
    batch.draw(shader)

handle = bpy.types.SpaceView3D.draw_handler_add(test_draw, (), 'WINDOW', 'POST_PIXEL')
# If this crashes, it's a GPU/driver issue
```

---

## Manual Test with Fake Data

If capture isn't working but you want to test the overlay:

```python
from live_mocap_addon.runtime import viewport_draw
import bpy

# 1. Register handler
viewport_draw.register_draw_handler()

# 2. Create fake landmarks
class FakeLandmark:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = 1.0

fake_landmarks = []
for i in range(33):
    x = 0.3 + (i % 7) * 0.1
    y = 0.2 + (i // 7) * 0.15
    fake_landmarks.append(FakeLandmark(x, y, 0.0))

# 3. Update with fake data
viewport_draw.update_landmarks(fake_landmarks)

# 4. Force redraw
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.tag_redraw()

print("Check viewport bottom-left corner!")
```

**You should see:**
- Dark box in bottom-left
- Grid of red dots
- Green lines connecting them

---

## Verification Checklist

Run through this to confirm everything works:

```python
# Complete verification script
import bpy
from live_mocap_addon.runtime import viewport_draw
from live_mocap_addon.runtime.trackers import POSE_CONNECTIONS

print("\n=== VERIFICATION CHECKLIST ===\n")

# 1. Module imports
try:
    print("✓ viewport_draw imported")
except:
    print("✗ viewport_draw import failed")

# 2. POSE_CONNECTIONS
try:
    assert len(POSE_CONNECTIONS) > 0
    print(f"✓ POSE_CONNECTIONS available ({len(POSE_CONNECTIONS)} connections)")
except:
    print("✗ POSE_CONNECTIONS missing or empty")

# 3. Property exists
try:
    settings = bpy.context.scene.mocap_settings
    _ = settings.show_camera_feed
    print("✓ show_camera_feed property exists")
except:
    print("✗ show_camera_feed property missing")

# 4. Handler functions
try:
    viewport_draw.register_draw_handler()
    assert viewport_draw.is_draw_handler_active()
    print("✓ Draw handler registration works")
    viewport_draw.unregister_draw_handler()
    assert not viewport_draw.is_draw_handler_active()
    print("✓ Draw handler unregistration works")
except Exception as e:
    print(f"✗ Draw handler issue: {e}")

# 5. Update functions
try:
    viewport_draw.update_camera_frame(None)
    viewport_draw.update_landmarks(None)
    print("✓ Update functions work")
except Exception as e:
    print(f"✗ Update functions issue: {e}")

print("\n=== END CHECKLIST ===\n")
```

---

## Still Not Working?

### Last Resort Steps:

1. **Full Addon Reload:**
   ```python
   import sys
   # Remove all addon modules from cache
   keys_to_remove = [k for k in sys.modules.keys() if 'live_mocap_addon' in k]
   for key in keys_to_remove:
       del sys.modules[key]
   ```
   Then disable and re-enable the addon.

2. **Restart Blender:**
   - Save your work
   - Close Blender completely
   - Reopen and test again

3. **Check Blender Version:**
   ```python
   import bpy
   print(bpy.app.version)  # Should be (3, 6, 0) or higher
   ```

4. **Test in Clean Blend File:**
   - File → New → General
   - Enable addon
   - Test with just default cube

5. **System Console Monitoring:**
   - Keep System Console open
   - Watch for ANY error messages
   - Screenshot and report errors

---

## Reporting Issues

If nothing works, collect this info:

```python
# Diagnostic dump
import bpy
from live_mocap_addon.runtime import viewport_draw
from live_mocap_addon.runtime.trackers import POSE_CONNECTIONS

print("\n=== DIAGNOSTIC INFO ===")
print(f"Blender version: {bpy.app.version}")
print(f"Python version: {sys.version}")
print(f"GPU: {bpy.context.preferences.system.gpu_backend}")
print(f"Handler active: {viewport_draw.is_draw_handler_active()}")
print(f"POSE_CONNECTIONS: {len(POSE_CONNECTIONS)}")
print(f"Current landmarks: {viewport_draw._current_landmarks is not None}")
print(f"Current frame: {viewport_draw._current_frame is not None}")

settings = bpy.context.scene.mocap_settings
print(f"show_camera_feed: {settings.show_camera_feed}")
print(f"is_capturing: {settings.is_capturing}")
print("======================\n")
```

Take a screenshot of:
1. System Console output
2. 3D Viewport
3. Mocap panel settings

---

## Success Indicators

**You'll know it's working when you see:**

✅ System Console shows:
```
SUCCESS: Viewport draw handler registered
DEBUG: Updated landmarks, count: 33
DEBUG: Drawing 33 landmarks
DEBUG: Drawing 35 connections
```

✅ 3D Viewport shows:
- Dark box with gray border (bottom-left)
- Red dots when person is in frame
- Green lines connecting the dots
- Updates in real-time

✅ Panel shows:
- Status: "Tracking | FPS: XX.X | Latency: XX.Xms"
- Dropped frames stays low
- Everything responsive

---

**Need more help? Run `debug_viewport.py` and check the output!**
