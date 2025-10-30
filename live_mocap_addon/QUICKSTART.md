# Quick Setup Guide

## 1. Install Dependencies (5 minutes)

### Find Your Blender Python

**Windows:**
```cmd
cd "C:\Program Files\Blender Foundation\Blender 4.x\4.x\python\bin"
```

**macOS:**
```bash
cd /Applications/Blender.app/Contents/Resources/4.x/python/bin
```

**Linux:**
```bash
cd /path/to/blender/4.x/python/bin
```

### Install Packages

```bash
# Windows
python.exe -m pip install opencv-python mediapipe

# macOS/Linux
./python3.11 -m pip install opencv-python mediapipe
```

**Expected output:**
```
Successfully installed opencv-python-4.x.x.x mediapipe-0.x.x.x
```

## 2. Install Add-on (2 minutes)

### Option A: Install as Folder
1. Copy the entire `live_mocap_addon` folder to Blender's add-ons directory:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\4.x\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/4.x/scripts/addons/`
   - **Linux**: `~/.config/blender/4.x/scripts/addons/`

2. Restart Blender

3. **Edit → Preferences → Add-ons**

4. Search for "mocap"

5. Enable **Animation: Live Mocap (MediaPipe)**

### Option B: Install as ZIP
1. Zip the `live_mocap_addon` folder

2. In Blender: **Edit → Preferences → Add-ons → Install**

3. Select the `.zip` file

4. Enable **Animation: Live Mocap (MediaPipe)**

5. Restart Blender (recommended)

## 3. Verify Installation (1 minute)

1. Open Blender

2. In 3D Viewport, press `N` to open sidebar

3. Look for **Mocap** tab

4. Click **Help / Dependency Check**

5. Verify:
   - ✓ OpenCV: Installed
   - ✓ MediaPipe: Installed

If you see ✗ Missing, dependencies were not installed correctly. Re-run step 1.

## 4. Test With Default Cube (5 minutes)

Let's do a quick test without even setting up a rig:

1. **Add an armature:**
   - `Shift+A` → Armature → Single Bone

2. **Select the armature, enter Pose Mode:**
   - Select the armature
   - Press `Ctrl+Tab` (or switch to Pose Mode in header)

3. **In Mocap panel:**
   - Click **Select Target**
   - Click **Auto-Fill Bone Map** (it will map what it can)
   - Add a manual mapping:
     - Click **+** in the mapping list
     - Set Landmark: `NOSE`
     - Set Bone: `Bone` (the default bone name)
     - Enable the checkbox

4. **Start capture:**
   - Click **Start Capture**
   - Move in front of your webcam
   - The bone should follow your nose!

5. **Stop:**
   - Click **Stop Capture**

**Success!** You've verified the add-on works.

## 5. Try With a Rigify Rig (10 minutes)

1. **Add a Rigify rig:**
   - Enable the Rigify add-on first (Edit → Preferences → Add-ons → search "Rigify")
   - `Shift+A` → Armature → Basic → Basic Human (MetaRig)
   - Select the armature
   - In armature properties panel (right side), click **Generate Rig**
   - This creates a full human rig

2. **Select the generated rig:**
   - Select the rig object (the one with DEF- bones)
   - Enter Pose Mode

3. **In Mocap panel:**
   - Click **Select Target**
   - Click **Auto-Fill Bone Map**
   - You should see many mappings created automatically

4. **Start capture:**
   - Stand back from your webcam so your full body is visible
   - Good lighting helps!
   - Click **Start Capture**
   - Move around - your rig should mimic you!

5. **Record animation:**
   - Go to frame 1 in timeline
   - Click **Record**
   - Perform a motion (wave, squat, etc.)
   - Click **Stop Recording**
   - Click **Stop Capture**
   - Click **Bake to Action**

6. **Play back:**
   - Go to frame 1
   - Press `Space` to play
   - Your motion is now an animation!

## Troubleshooting

### "Missing Dependencies"
- Re-run the pip install commands
- Make sure you're using Blender's Python, not system Python
- Restart Blender after installing

### Camera not opening
- Try camera index `1` or `2` if `0` doesn't work
- Close other apps using the camera (Zoom, Skype, etc.)
- Check camera permissions (especially on macOS)

### No bones moving
- Make sure you're in Pose Mode
- Verify bone names match in the mapping list
- Check that your body is visible in the camera
- Try increasing lighting

### Laggy/slow
- Lower FPS to 24
- Disable "Use Hands" and "Use Face"
- Close other applications

## Next Steps

- Read the full **README.md** for detailed features
- Review **STRUCTURE.md** to understand the code
- Save bone mappings for your rigs (Save Map button)
- Experiment with smoothing and filters
- Try recording full performances!

## Need Help?

1. Click **Help / Dependency Check** in the panel
2. Check the **README.md** troubleshooting section
3. Review STRUCTURE.md for technical details

---

**Have fun with motion capture! 🎬🎭**
