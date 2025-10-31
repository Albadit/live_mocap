# 📸 Camera Feed - Quick Reference Card

## 🎯 What You Get
Real-time camera preview + skeleton tracking overlay in your 3D Viewport!

---

## ⚡ Quick Setup (30 seconds)

1. **Enable in Panel**
   ```
   3D Viewport → N key → Mocap tab
   Capture section → ☑ Show Camera Feed
   ```

2. **Start Capture**
   ```
   Click ▶ Start Capture button
   ```

3. **Look at Bottom-Left**
   ```
   You'll see a small video preview with your skeleton!
   ```

---

## 🎨 What You See

```
┌─────────────────┐
│ ⬛ Dark Box    │ ← Camera preview background
│                 │
│  🔴 Red Dots   │ ← Your body landmarks (33 points)
│   │            │
│  🟢 Green Lines│ ← Skeleton connections
│                 │
└─────────────────┘
  320×240 pixels
  Bottom-left corner
```

---

## 🎛️ Controls

| Action | How |
|--------|-----|
| **Show feed** | Check "Show Camera Feed" |
| **Hide feed** | Uncheck "Show Camera Feed" |
| **Move view** | Can't move (fixed position) |
| **Resize** | Can't resize (fixed 320×240) |
| **Toggle during capture** | Just check/uncheck the box! |

---

## 💡 Tips

### Better Tracking
- ✅ **Good lighting** - Bright, even light
- ✅ **Full body** - Step back from camera
- ✅ **Face camera** - Front view works best
- ✅ **Contrast** - Wear different color than background

### Better Performance
- ⚡ **Disable when not needed** - Uncheck "Show Camera Feed"
- ⚡ **Lower FPS** - Reduce target FPS to 15-24
- ⚡ **Close overlays** - Hide other viewport elements

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| **No box showing** | Check "Show Camera Feed" is enabled |
| **Box but no landmarks** | Move in front of camera |
| **Red dots but no green lines** | Body parts out of frame |
| **Jittery motion** | Increase smoothing filter |
| **Low FPS** | Disable feed or lower target FPS |
| **Capture won't start** | Install dependencies first |

---

## 📊 Status Info

Watch the status text during capture:
```
Status: Tracking | FPS: 28.5 | Latency: 35.2ms
        ↑         ↑           ↑
    Working    Camera     Processing
               speed      time
```

### Good Values:
- **FPS**: 25-30 (smooth)
- **Latency**: <50ms (responsive)
- **Dropped frames**: <5%

---

## 🎮 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `ESC` | Stop capture immediately |
| `N` | Toggle sidebar (show/hide panel) |
| `Space` | Play/pause (when recording) |

---

## 📈 Performance Impact

| Setting | FPS Impact |
|---------|-----------|
| Feed **ON** | ~1-2ms per frame |
| Feed **OFF** | 0ms (no overhead) |

**Recommendation**: Leave on for setup, turn off for final recording.

---

## 🎯 Landmark Detection

### What Gets Tracked:
```
Face:    👤 Nose, eyes, ears, mouth
Arms:    💪 Shoulders, elbows, wrists
Hands:   👋 Thumb, index, pinky
Torso:   🦴 Shoulders, hips
Legs:    🦵 Hips, knees, ankles, feet

Total: 33 body points
```

### Color Coding:
- 🔴 **Red** = Individual landmarks
- 🟢 **Green** = Connections (skeleton)

---

## 🚦 Quality Indicators

### Good Tracking:
- ✅ All landmarks visible
- ✅ Smooth green lines
- ✅ Steady red dots
- ✅ High FPS (>25)

### Poor Tracking:
- ❌ Missing landmarks
- ❌ Broken connections
- ❌ Flickering dots
- ❌ Low FPS (<15)

**Fix**: Improve lighting, camera position, or settings.

---

## 🔧 Settings to Adjust

### For Better Tracking:
```
Min Confidence: 0.3-0.5  (lower = more sensitive)
Smoothing: 0.3-0.7       (higher = smoother)
```

### For Better Performance:
```
Target FPS: 15-24        (lower = faster)
Show Camera Feed: OFF    (disable visualization)
```

---

## 📝 Common Scenarios

### Setup Phase:
1. ✅ Enable camera feed
2. ✅ Test tracking
3. ✅ Adjust position
4. ✅ Tune settings

### Recording Phase:
1. ✅ Disable feed (performance)
2. ✅ Start recording
3. ✅ Perform motion
4. ✅ Stop and bake

### Debugging:
1. ✅ Enable feed
2. ✅ Watch landmarks
3. ✅ Identify issues
4. ✅ Fix and retry

---

## 🎓 Learning Mode

### First Time:
1. Start with default settings
2. Enable camera feed
3. Just move around and watch
4. Get comfortable with tracking

### Once Familiar:
1. Adjust settings for your needs
2. Toggle feed as needed
3. Focus on your performance
4. Record great animations!

---

## 🆘 Quick Help

**It's working if you see:**
- Small dark box in bottom-left corner
- Red dots when you're in frame
- Green lines connecting the dots
- Status showing "Tracking"

**Get help if:**
- Nothing shows up at all
- Blender crashes or freezes
- Camera never opens
- No dependencies installed

→ Check `TESTING_CAMERA_FEED.md` for detailed troubleshooting

---

## 📚 More Info

| Document | Purpose |
|----------|---------|
| `CAMERA_FEED_QUICKSTART.md` | User guide with examples |
| `CAMERA_FEED_VISUALIZATION.md` | Technical documentation |
| `TESTING_CAMERA_FEED.md` | Testing and validation |
| `ARCHITECTURE_DIAGRAM.md` | System architecture |

---

## ✨ Pro Tips

1. **Use feed for setup, disable for recording**
2. **Check tracking quality before recording**
3. **Adjust smoothing while watching the feed**
4. **Lower FPS if you need more performance**
5. **Full body in frame = best results**

---

**Happy Motion Capturing! 🎬✨**

*Created for Live Mocap Addon - Oct 2025*
