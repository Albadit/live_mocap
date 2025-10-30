Perfect — here’s the **clean, improved version** of your prompt with the `live_mocap_mediapipe` folder **removed**, so all source modules live **directly inside `src/`** (simpler import path, easier Blender packaging).
It keeps the same modular design and structure clarity.

---

# Blender Add-on (Multi-File): Live Mocap with MediaPipe + OpenCV

## 🎯 Goal

Create a **modular Blender add-on** that uses **OpenCV (cv2)** for webcam capture and **MediaPipe** for real-time motion tracking (Pose + optional Hands/Face), then **retargets** tracked landmarks to a **selected armature’s bones** and allows **recording and baking animations**.

The add-on must use a **multi-file structure under `src/`** — not one giant script — with clean separation of UI, operators, runtime logic, and utilities.

---

## 🧱 Project Layout

```
addon-root/
├─ __init__.py                # Blender add-on entry (bl_info, imports, register/unregister)
├─ src/
│  ├─ __init__.py             # Root package initializer (setup, logger, constants)
│  ├─ addon_prefs.py          # Add-on preferences (default paths, debug)
│  ├─ properties.py           # bpy.props PropertyGroups (panel state, bone mapping)
│  ├─ panel.py                # N-panel UI layout
│  ├─ ops/                    # All operator classes
│  │  ├─ __init__.py
│  │  ├─ op_select_target.py
│  │  ├─ op_autofill_map.py
│  │  ├─ op_clear_map.py
│  │  ├─ op_save_map.py
│  │  ├─ op_load_map.py
│  │  ├─ op_capture_start.py
│  │  ├─ op_capture_stop.py
│  │  ├─ op_record_start.py
│  │  ├─ op_record_stop.py
│  │  ├─ op_bake_action.py
│  │  ├─ op_zero_pose.py
│  │  └─ op_apply_rest_offset.py
│  ├─ runtime/                # Live systems and retargeting
│  │  ├─ __init__.py
│  │  ├─ dependency_check.py   # Safe imports for cv2/mediapipe, version reporting
│  │  ├─ capture.py            # Camera management (cv2 + frame loop)
│  │  ├─ trackers.py           # MediaPipe trackers setup and landmark extraction
│  │  ├─ retarget.py           # Landmark → bone retarget math (vectors → quaternions)
│  │  ├─ mapping.py            # Bone-landmark mapping models and auto-matching
│  │  ├─ recording.py          # Keyframe writing, bake, cleanup
│  │  └─ filters.py            # Smoothing, confidence gating, optional IK/foot lock
│  ├─ io/                     # File I/O and exports
│  │  ├─ __init__.py
│  │  ├─ json_maps.py          # Load/save JSON bone maps (//mocap_maps/)
│  │  └─ export.py             # Optional FBX exporter for baked actions
│  └─ utils/                   # Helpers and shared utilities
│     ├─ __init__.py
│     ├─ logging_utils.py
│     ├─ naming.py             # Canonical bone name patterns & fuzzy matching
│     └─ coords.py             # Coordinate transforms (world/local/bone space)
└─ README.md                   # Setup, usage, and dependency instructions
```

> ✅ **Key rule:** `__init__.py` at the addon root is the **only** file Blender directly loads.
> It should just define `bl_info`, import from `src`, and call `register()` / `unregister()`.

---

## 🧩 UI (N-Panel: “Live Mocap (MediaPipe)”)

**Sections & Controls**

**🎯 Target**

* **Select Target** → sets active armature as the mocap target.
* Shows current target name (or “None”).
* Enum: **Coordinate Space** → `WORLD` / `ARMATURE_LOCAL` / `BONE_LOCAL`
* Float: **Scale**, **Z-Up Offset**

**🦴 Bone Mapping**

* **Auto-Fill Map** → tries to auto-link MediaPipe landmarks to bones.
* Editable UIList: **Landmark → Bone name**.
* **Clear Map**, **Save Map**, **Load Map** (stored in `//mocap_maps/` as JSON).

**📷 Capture**

* Int: **Camera Index** (default 0)
* Int: **Target FPS** (default 30)
* Toggles: **Use Pose**, **Use Hands**, **Use Face**
* **Start Capture** / **Stop Capture** buttons
* Status label: (Tracking / Idle / Missing deps / Camera error)

**🎬 Record**

* **Record** → start inserting keyframes at scene FPS
* **Stop Recording** → stop keyframe writing
* **Bake to Action** → creates finalized action on target armature (`Mediapipe_Capture_YYYYMMDD_HHMM`)

**⚙️ Filters**

* Float: **Smoothing (0–1)**
* Float: **Min Confidence (0–1)**
* Float: **Foot Lock Threshold**

**🛠 Utilities**

* **Zero Pose** (reset mapped bones to rest)
* **Apply Rest Offset** (compute rest offsets)
* **Help / Dependency Check** → displays dependency info & install command

---

## 🧠 Core Features

### MediaPipe → Bone Mapping

* Built-in canonical mapping suggestions (case-insensitive, `.L/.R` ignored):

  ```
  NOSE → head
  LEFT_SHOULDER → shoulder.L
  RIGHT_SHOULDER → shoulder.R
  LEFT_ELBOW → forearm.L
  RIGHT_ELBOW → forearm.R
  LEFT_WRIST → hand.L
  RIGHT_WRIST → hand.R
  LEFT_HIP → thigh.L
  RIGHT_HIP → thigh.R
  LEFT_KNEE → shin.L
  RIGHT_KNEE → shin.R
  LEFT_ANKLE → foot.L
  RIGHT_ANKLE → foot.R
  ```
* Optional hands mapping (thumb/index/pinky tips).

**Auto-Fill Logic**

1. Scan armature bone names.
2. Fuzzy-match canonical names.
3. Fill best matches automatically.
4. User can correct or save as JSON.

---

## ⚙️ Runtime & Retargeting Logic

* Modal operator using `wm.timer`:

  1. Capture webcam frame (cv2).
  2. Run MediaPipe → get landmarks.
  3. Normalize to Blender coordinates (rooted, scaled, oriented).
  4. Convert limb vectors → bone quaternions.
  5. Apply filters & confidence thresholds.
  6. If recording → insert keyframes; else → preview live pose.

* Supports:

  * Rotation-only mode
  * Root translation scaling/clamping
  * Coordinate spaces (`WORLD`, `ARMATURE_LOCAL`, `BONE_LOCAL`)
  * EWMA smoothing and optional foot locking

---

## 🧾 Recording & Baking

* Record inserts `rotation_quaternion` and optional `location` per frame.
* Stop recording cleanly without halting capture.
* Bake creates new action with timestamp name, cleans jitter keys.

---

## 🔍 Dependency Management

* `runtime/dependency_check.py`:

  * Import `cv2`, `mediapipe`, record version info.
  * Expose `HAS_CV2`, `HAS_MEDIAPIPE` flags.
* Panel shows install guide if missing:

  ```bash
  "C:\Program Files\Blender\4.2\python\bin\python.exe" -m pip install opencv-python mediapipe
  ```

---

## 🧩 Registration Rules

* `__init__.py` at addon root:

  * Contains `bl_info`
  * Imports `register`, `unregister` from `src`
* `src/__init__.py`:

  * Aggregates all classes (from props, ops, panels)
  * Handles registration order
  * Initializes logging and state

---

## 💡 Coding Standards

* Type hints, docstrings, descriptive logging.
* No blocking UI; modal timers only.
* Resources (camera, mediapipe graph) always released on stop/error.
* No globals beyond minimal runtime context.

---

## ✅ Acceptance Criteria

1. Add-on installs, “Live Mocap (MediaPipe)” panel visible.
2. Selecting armature works.
3. Auto-Fill populates a usable bone map.
4. Live capture runs smoothly (no UI freeze).
5. Record & Bake produce usable keyframed animation.
6. Missing dependencies trigger helpful install hint, not crash.
7. Camera released safely on stop or exception.

---

## 🌟 Optional Features

* L/R mirroring
* Latency/dropped frame counter
* Hand/finger mapping UI
* Action export (FBX)
* Simple calibration for root offset

---

## 📦 Deliverables

* Complete modular folder structure (`src/` layout above).
* Ready-to-zip Blender add-on (root `__init__.py` + `src/`).
* `README.md` with:

  * Installation steps
  * Dependency setup for all OS
  * Example mapping JSON
  * Usage tutorial

---

Would you like me to generate the **starter folder structure with Python file stubs** (each containing class/register scaffolds) next?
That would give you a working base add-on that loads cleanly in Blender and is ready to fill in MediaPipe logic.


----

todo

- fix error install
- add 1 default camera cant be remove
- show window of camera