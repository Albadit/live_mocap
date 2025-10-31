"""
Debug script for camera feed visualization.
Run this in Blender's Text Editor to test the viewport drawing.
"""

import bpy
from live_mocap_addon.runtime import viewport_draw
from live_mocap_addon.runtime.trackers import POSE_CONNECTIONS

def test_viewport_draw():
    """Test the viewport drawing system."""
    print("\n" + "="*60)
    print("CAMERA FEED VIEWPORT DEBUG TEST")
    print("="*60)
    
    # Test 1: Check if handler is registered
    print("\n1. Checking draw handler status...")
    is_active = viewport_draw.is_draw_handler_active()
    print(f"   Handler active: {is_active}")
    
    # Test 2: Check POSE_CONNECTIONS
    print("\n2. Checking POSE_CONNECTIONS...")
    print(f"   Connections count: {len(POSE_CONNECTIONS)}")
    print(f"   First 5: {POSE_CONNECTIONS[:5]}")
    
    # Test 3: Check property
    print("\n3. Checking 'show_camera_feed' property...")
    try:
        settings = bpy.context.scene.mocap_settings
        print(f"   show_camera_feed: {settings.show_camera_feed}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 4: Check if capturing
    print("\n4. Checking capture status...")
    try:
        settings = bpy.context.scene.mocap_settings
        print(f"   is_capturing: {settings.is_capturing}")
        print(f"   status_message: {settings.status_message}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 5: Check current data
    print("\n5. Checking current data...")
    print(f"   _current_frame: {viewport_draw._current_frame is not None}")
    print(f"   _current_landmarks: {viewport_draw._current_landmarks is not None}")
    
    if viewport_draw._current_landmarks is not None:
        landmarks = viewport_draw._current_landmarks
        if isinstance(landmarks, list):
            print(f"   Landmarks type: list")
            print(f"   Landmarks count: {len(landmarks)}")
            if len(landmarks) > 0:
                print(f"   First landmark: x={landmarks[0].x:.3f}, y={landmarks[0].y:.3f}, z={landmarks[0].z:.3f}")
        else:
            print(f"   Landmarks type: {type(landmarks)}")
    
    # Test 6: Manual registration test
    print("\n6. Testing manual handler registration...")
    if not is_active:
        print("   Registering handler...")
        viewport_draw.register_draw_handler()
        is_active = viewport_draw.is_draw_handler_active()
        print(f"   Handler active now: {is_active}")
    else:
        print("   Handler already active")
    
    # Test 7: Force viewport redraw
    print("\n7. Forcing viewport redraw...")
    count = 0
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
            count += 1
    print(f"   Tagged {count} viewport(s) for redraw")
    
    # Test 8: Create fake landmarks for testing
    print("\n8. Creating test landmarks...")
    class FakeLandmark:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = 1.0
    
    fake_landmarks = [
        FakeLandmark(0.5, 0.3, 0.0),  # Nose
        FakeLandmark(0.4, 0.2, 0.0),  # Left eye
        FakeLandmark(0.6, 0.2, 0.0),  # Right eye
        FakeLandmark(0.3, 0.5, 0.0),  # Left shoulder
        FakeLandmark(0.7, 0.5, 0.0),  # Right shoulder
        FakeLandmark(0.3, 0.7, 0.0),  # Left elbow
        FakeLandmark(0.7, 0.7, 0.0),  # Right elbow
    ]
    
    # Fill to 33 landmarks
    while len(fake_landmarks) < 33:
        fake_landmarks.append(FakeLandmark(0.5, 0.5, 0.0))
    
    viewport_draw.update_landmarks(fake_landmarks)
    print(f"   Updated with {len(fake_landmarks)} fake landmarks")
    
    # Force redraw again
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nLook at the bottom-left corner of your 3D Viewport.")
    print("You should see:")
    print("  - A dark box with border (camera feed background)")
    print("  - Red dots (fake landmarks)")
    print("  - Green lines connecting them")
    print("\nIf you don't see anything, check the System Console")
    print("(Window -> Toggle System Console) for error messages.")
    print("="*60 + "\n")

# Run the test
test_viewport_draw()
