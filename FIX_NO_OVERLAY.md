# 🎯 QUICK FIX: No Skeleton Overlay Visible

## Immediate Actions (Do These Now!)

### 1. Open Blender's System Console
```
Window → Toggle System Console
```
Leave this open to see debug messages!

### 2. Run the Debug Script

**In Blender:**
1. Switch to **Scripting** workspace (top tabs)
2. Click **Text** → **Open**
3. Navigate to: `c:\Users\Albadit\Documents\GitHub\live_mocap\debug_viewport.py`
4. Click **Run Script** (▶ button or press Alt+P)
5. Watch the System Console for output

### 3. Look for These Messages

**GOOD** (means it's working):
```
SUCCESS: Viewport draw handler registered
DEBUG: Updated landmarks, count: 33
DEBUG: Drawing 33 landmarks
```

**BAD** (means there's an error):
```
ERROR: Failed to register draw handler
AttributeError: ...
ImportError: ...
```

---

## If You See Errors:

### Error: "Handler already registered"
**Fix:**
```python
# In Python Console (Scripting workspace, bottom):
from live_mocap_addon.runtime import viewport_draw
viewport_draw.unregister_draw_handler()
viewport_draw.register_draw_handler()
```

### Error: "Cannot import POSE_CONNECTIONS"
**Fix:** Reload the addon:
1. Edit → Preferences → Add-ons
2. Uncheck "Live Mocap"
3. Check "Live Mocap" again
4. Close preferences

### Error: "AttributeError: 'list' has no attribute 'landmark'"
**This should be fixed now!** If you still see it, the code needs the latest changes.

---

## If NO Errors But Still No Overlay:

### Test with Fake Data

Run this in **Python Console**:

```python
from live_mocap_addon.runtime import viewport_draw
import bpy

# Create fake landmarks
class FL:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y  
        self.z = z

fake = [FL(0.3+i*0.02, 0.2+i*0.02, 0) for i in range(33)]

# Update and redraw
viewport_draw.update_landmarks(fake)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.tag_redraw()

print("Check bottom-left corner of viewport!")
```

**Expected:** You should see a grid of red dots with green lines.

---

## Checklist

Run through this:

- [ ] System Console is open and visible
- [ ] Debug script has been run
- [ ] No errors in console
- [ ] "Show Camera Feed" is checked in panel
- [ ] Capture is started (Status: "Tracking")
- [ ] 3D Viewport is at least 400x300 pixels
- [ ] Looking at bottom-left corner of viewport
- [ ] Tested with fake data (see above)

---

## What You Should See

```
┌─────────────────────────────────┐
│  3D Viewport                    │
│                                 │
│                                 │
│                                 │
│  ┌──────────┐                  │
│  │  ⬛⬛⬛  │ ← Dark box        │
│  │  🔴─🟢  │ ← Red dots        │
│  │  │  │  │ ← Green lines      │
│  │  🔴─🟢  │                    │
│  └──────────┘                  │
│  (Bottom-left corner)          │
└─────────────────────────────────┘
```

---

## If Still Nothing:

### Copy & Paste This Full Test:

```python
import bpy
from live_mocap_addon.runtime import viewport_draw

print("\n" + "="*50)
print("FULL DIAGNOSTIC TEST")
print("="*50)

# 1. Unregister any existing handler
viewport_draw.unregister_draw_handler()
print("1. Cleaned up old handler")

# 2. Register fresh
viewport_draw.register_draw_handler()
print("2. Registered new handler")

# 3. Check status
active = viewport_draw.is_draw_handler_active()
print(f"3. Handler active: {active}")

# 4. Create and set fake landmarks
class FakeLandmark:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

landmarks = []
for i in range(33):
    x = 0.2 + (i % 8) * 0.1
    y = 0.2 + (i // 8) * 0.1
    landmarks.append(FakeLandmark(x, y, 0.0))

viewport_draw.update_landmarks(landmarks)
print(f"4. Set {len(landmarks)} fake landmarks")

# 5. Force redraw of ALL viewports
count = 0
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
            count += 1
print(f"5. Redrawn {count} viewport(s)")

print("="*50)
print("CHECK VIEWPORT BOTTOM-LEFT CORNER NOW!")
print("="*50 + "\n")
```

---

## Next Steps

1. **If you see the overlay with fake data:**
   - Problem is with camera/capture, not drawing
   - Check camera is working
   - Check MediaPipe is detecting you

2. **If you DON'T see overlay even with fake data:**
   - GPU/driver issue
   - Blender version issue  
   - Send me the console output

---

## Send Me This Info:

If nothing works, copy this output and send it:

```python
import bpy
import sys
from live_mocap_addon.runtime import viewport_draw

print("\n=== DIAGNOSTIC INFO ===")
print(f"Blender: {bpy.app.version}")
print(f"Python: {sys.version_info[:3]}")
print(f"Handler active: {viewport_draw.is_draw_handler_active()}")
print(f"Landmarks set: {viewport_draw._current_landmarks is not None}")

try:
    from live_mocap_addon.runtime.trackers import POSE_CONNECTIONS
    print(f"POSE_CONNECTIONS: {len(POSE_CONNECTIONS)} items")
except Exception as e:
    print(f"POSE_CONNECTIONS error: {e}")

try:
    settings = bpy.context.scene.mocap_settings
    print(f"show_camera_feed: {settings.show_camera_feed}")
    print(f"is_capturing: {settings.is_capturing}")
except Exception as e:
    print(f"Settings error: {e}")

print("======================\n")
```

---

**Let me know what you see in the console after running these tests!**
