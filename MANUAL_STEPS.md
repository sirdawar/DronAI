# Manual Startup Steps (Guaranteed to Work)

## DO THIS IN ORDER - ONE STEP AT A TIME

### Step 1: Start Unreal
```bash
$UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject
```

**WAIT:** Let Unreal fully load (30-60 seconds)

**ACTION:** Click the **PLAY** button (▶) in the toolbar

**WAIT:** 5 seconds after pressing Play

---

### Step 2: Start Python (in a new terminal)
```bash
cd /home/davor/projects/DronAI/ProjectAirSim/client/python/projectairsim
poetry run bash -c "cd ../example_user_scripts && python px4_quadrotor_extended.py sitl"
```

**You should see:**
```
INFO Using scene "scene_px4_sitl.jsonc"
INFO Connecting to simulation server at 127.0.0.1
INFO Connection opened.
INFO Started the pub-sub topic receiving thread.
INFO Loading scene config: scene_px4_sitl.jsonc
```

**WAIT:** 3-5 seconds for it to load the scene

---

### Step 3: Start PX4 (in a new terminal)
```bash
cd /home/davor/projects/DronAI/PX4/PX4-Autopilot
make px4_sitl none_iris
```

**You should see:**
```
Waiting for simulator to accept connection on TCP port 4560
Connected to simulator
INFO [mavlink] mode: Onboard
INFO [mavlink] ready
```

**WAIT:** Until you see "mavlink ready"

---

### Step 4: Start QGC (optional, in a new terminal)
```bash
/home/davor/QGroundControl.AppImage --udp-port 18570
```

---

## What Should Happen

1. **Unreal (in Play mode):** Shows the Blocks environment
2. **Python:** Loads scene, waits for PX4, then starts controlling drone
3. **PX4:** Connects to Unreal, starts MAVLink
4. **Drone:** Takes off and flies in Unreal!

---

## If Python Gets Stuck at "Loading scene config"

**Problem:** Unreal is NOT in Play mode

**Solution:**
1. Press Ctrl+C to stop Python
2. Go to Unreal window
3. Press the PLAY button (▶)
4. Wait 5 seconds
5. Run Python command again

---

## If PX4 Gets Stuck at "Waiting for simulator on TCP:4560"

**Problem:** Python hasn't opened the port yet

**Solution:**
1. Make sure Python is running and past "Loading scene config"
2. Wait a few more seconds
3. If still stuck after 30s, restart:
   - Kill PX4 (Ctrl+C)
   - Check Python is still running
   - Start PX4 again

---

## The Critical Requirement

**UNREAL MUST BE IN PLAY MODE BEFORE PYTHON LOADS THE SCENE!**

The ProjectAirSim plugin only activates and accepts connections when Unreal is playing.

If you try to run Python before pressing Play, it will hang at "Loading scene config" forever.

---

## Quick Check Before Starting

```bash
# Make sure nothing is running
ps aux | grep -E "(UnrealEditor.*Blocks|px4.*sitl|python.*px4)" | grep -v grep

# If anything shows up, kill it:
killall -9 UnrealEditor px4 python
```

---

## Success Indicators

### Unreal Window
- Shows Blocks environment
- You see a drone spawn
- Drone takes off and flies

### Python Terminal
```
Waiting 5 seconds for PX4 sensors to stabilize...
Enabling API control
Arming drone
Taking off...
Takeoff complete
Hovering for 3 seconds...
```

### PX4 Terminal
```
Connected to simulator
INFO [mavlink] ready
[Lots of sensor data scrolling]
```

---

## Why Automated Scripts Don't Work Well

The scripts can't reliably detect when:
1. Unreal is fully loaded
2. You've pressed Play
3. ProjectAirSim plugin is ready

That's why manual steps work better - YOU know when Unreal is ready!

---

## After It's Working

Once you've done this manually a few times and it's working reliably, THEN you can try to automate with scripts. But for now, just do it manually step by step.
