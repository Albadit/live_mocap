# Quick Start: Camera Feed Visualization

## What's New? 🎥

You can now see your camera feed and MediaPipe tracking directly in Blender's 3D Viewport!

## How to Use

### 1. Enable the Feature
- Open the **3D Viewport** sidebar (press `N` if hidden)
- Go to the **Mocap** tab
- In the **Capture** section, check **☑ Show Camera Feed**

### 2. Start Capturing
- Click the **▶ Start Capture** button
- Look at the **bottom-left corner** of your 3D Viewport
- You'll see:
  - 📹 Live camera preview (320x240 pixels)
  - 🔴 Red dots showing detected body landmarks
  - 🟢 Green lines connecting the landmarks (your skeleton!)

### 3. What You'll See

```
┌──────────────────────────┐
│  [Camera Feed Preview]   │
│                          │
│    🔴─🟢─🔴            │ ← Your pose tracked live!
│    │    │    │          │
│    🔴─🟢─🔴            │
│    │    │    │          │
│    🔴─🟢─🔴            │
│                          │
└──────────────────────────┘
```

### 4. Toggle On/Off
- **During capture**: Uncheck "Show Camera Feed" to hide
- **Benefits of disabling**: 
  - Slightly better performance
  - Less visual clutter
  - Still tracks your motion!

## Visual Guide

### Landmark Colors:
- 🔴 **Red Points** = Individual body landmarks (eyes, shoulders, hips, etc.)
- 🟢 **Green Lines** = Skeleton connections between landmarks
- ⬛ **Dark Box** = Camera feed background

### What Gets Tracked:
- ✅ Full body pose (33 points)
- ✅ Head and face position
- ✅ Arms, elbows, wrists
- ✅ Torso and hips
- ✅ Legs, knees, ankles, feet

## Tips & Tricks

### 📸 Better Tracking:
1. **Good lighting** - Make sure you're well-lit
2. **Full body visible** - Step back from the camera
3. **Contrast** - Wear different color than background
4. **Movement** - Face the camera for best results

### ⚡ Better Performance:
1. **Disable when not needed** - Uncheck "Show Camera Feed"
2. **Lower FPS** - Reduce target FPS in settings
3. **Close other overlays** - Hide other viewport elements

### 🎯 Checking Tracking Quality:
- **Solid red points** = Good tracking
- **Missing lines** = Landmarks not detected
- **Jittery motion** = Increase smoothing filter
- **Laggy** = Reduce FPS or disable feed

## Keyboard Shortcuts

While capturing:
- `ESC` - Stop capture immediately
- `N` - Toggle sidebar (show/hide panel)
- `Spacebar` - Play/pause timeline (if recording)

## Common Questions

**Q: Can I move the feed to a different position?**
A: Currently it's fixed to bottom-left. Future updates may add customization.

**Q: Does it affect capture performance?**
A: Minimal impact (~1-2ms per frame). Can disable if needed.

**Q: Can I record the camera feed?**
A: Not yet, but it's planned for future versions!

**Q: Why are some landmarks missing?**
A: Body parts out of frame, poor lighting, or low confidence. Check camera position.

**Q: Can I see hand/face details?**
A: Enable "Use Hands" or "Use Face" in Capture settings (landmarks will show if detected).

## Troubleshooting

### No overlay showing?
- ✓ Check "Show Camera Feed" is enabled
- ✓ Verify capture is running (Status: "Tracking")
- ✓ Ensure camera is working (check dropped frames)

### Landmarks not visible?
- ✓ Stand in front of camera
- ✓ Improve lighting
- ✓ Enable "Use Pose" in settings
- ✓ Lower "Min Confidence" threshold

### Feed looks wrong?
- ✓ Make sure Blender is up to date (3.6+)
- ✓ Check GPU drivers are current
- ✓ Try disabling and re-enabling the feed

## Next Steps

Once you can see yourself tracking properly:
1. **Map bones** - Use "Build Bone List" to setup your rig
2. **Adjust filters** - Tune smoothing for better motion
3. **Start recording** - Click Record to capture keyframes
4. **Bake action** - Convert to animation curves

Enjoy real-time motion capture with visual feedback! 🎬✨
