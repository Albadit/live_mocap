"""
Installation Verification Script

Run this in Blender's Python console to verify the add-on is properly installed.
Instructions:
1. Open Blender
2. Go to Scripting workspace
3. Paste this script in the console
4. Press Enter to run
"""

import sys

print("=" * 70)
print("Live Mocap - Installation Verification")
print("=" * 70)

# Check Blender version
import bpy
blender_version = bpy.app.version_string
print(f"\n✓ Blender Version: {blender_version}")

# Check if add-on is enabled
addon_name = "live_mocap_addon"
is_enabled = addon_name in bpy.context.preferences.addons
print(f"{'✓' if is_enabled else '✗'} Add-on Enabled: {is_enabled}")

if not is_enabled:
    print("  → Enable: Edit → Preferences → Add-ons → Search 'mocap'")
    sys.exit()

# Check dependencies
print("\n--- Dependencies ---")

# OpenCV
try:
    import cv2
    print(f"✓ OpenCV: {cv2.__version__}")
except ImportError:
    print("✗ OpenCV: NOT INSTALLED")
    print(f"  → Install: \"{sys.executable}\" -m pip install opencv-python")

# MediaPipe
try:
    import mediapipe as mp
    print(f"✓ MediaPipe: {mp.__version__}")
except ImportError:
    print("✗ MediaPipe: NOT INSTALLED")
    print(f"  → Install: \"{sys.executable}\" -m pip install mediapipe")

# Check scene properties
print("\n--- Scene Properties ---")
if hasattr(bpy.types.Scene, 'mocap_settings'):
    print("✓ Scene properties registered")
    settings = bpy.context.scene.mocap_settings
    print(f"  - Camera Index: {settings.camera_index}")
    print(f"  - Target FPS: {settings.target_fps}")
    print(f"  - Smoothing: {settings.smoothing}")
else:
    print("✗ Scene properties NOT registered")

# Check panel
print("\n--- UI Panel ---")
panel_found = False
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for region in area.regions:
            if region.type == 'UI':
                panel_found = True
                break

if panel_found:
    print("✓ 3D Viewport sidebar available")
    print("  → Press 'N' in 3D Viewport to open sidebar")
    print("  → Look for 'Mocap' tab")
else:
    print("? 3D Viewport sidebar status unknown")

# Check operators
print("\n--- Operators ---")
operators_to_check = [
    "mocap.select_target",
    "mocap.autofill_bone_map",
    "mocap.capture_start",
    "mocap.record_start",
    "mocap.bake_action"
]

for op_id in operators_to_check:
    # Check if operator exists
    try:
        op_name = op_id.split('.')[1]
        exists = hasattr(bpy.ops.mocap, op_name)
        print(f"{'✓' if exists else '✗'} {op_id}")
    except:
        print(f"✗ {op_id}")

# Final summary
print("\n" + "=" * 70)
print("Installation Check Complete!")
print("=" * 70)

all_deps = True
try:
    import cv2
    import mediapipe
except ImportError:
    all_deps = False

if is_enabled and all_deps:
    print("\n🎉 SUCCESS! Add-on is ready to use.")
    print("\nNext steps:")
    print("1. Press 'N' in 3D Viewport")
    print("2. Click 'Mocap' tab")
    print("3. Click 'Help / Dependency Check' for more info")
    print("4. Follow QUICKSTART.md for a test run")
elif is_enabled:
    print("\n⚠️  Add-on enabled but dependencies missing!")
    print("Install opencv-python and mediapipe (see above)")
else:
    print("\n⚠️  Add-on not enabled!")
    print("Enable in: Edit → Preferences → Add-ons")

print()
