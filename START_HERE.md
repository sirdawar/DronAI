# 🚁 ProjectAirSim Startup Guide

## Quick Start (Recommended)

```bash
./start_simulation_v2.sh
```

This will:
1. Open Unreal Engine Editor
2. **WAIT FOR YOUR INPUT** - You must press Play!
3. Launch PX4 SITL and wait for it to be ready
4. Start Python control script
5. Open QGroundControl for monitoring

---

## Why Python Gets Stuck

The Python script hangs at `client.connect()` because:

### ❌ Problem
- **ProjectAirSim plugin only starts its network server when Unreal is in PLAY mode**
- If you start Python before pressing Play, it will hang forever
- The script can't connect to a server that isn't running yet

### ✅ Solution
The new script (`start_simulation_v2.sh`) fixes this by:
1. Starting Unreal
2. **Waiting for you to press Play** (shows big warning)
3. Waiting 5 seconds for ProjectAirSim plugin to initialize
4. Checking that MAVLink ports are active
5. Only then starting the Python script

---

## Startup Scripts Comparison

| Script | Best For | Manual Steps | Auto-waits |
|--------|----------|--------------|------------|
| `start_simulation_v2.sh` | **RECOMMENDED** | Press Play button | ✓ Waits for everything |
| `start_simulation_fixed.sh` | Basic use | Press Play button | Partial waits |
| `start_simulation_auto.sh` | Experimental | None (tries `-game`) | ✓ But may not work |
| `check_connectivity.sh` | Diagnostics | - | N/A |

---

## Troubleshooting Tools

### Check if everything is ready
```bash
./check_connectivity.sh
```

This shows:
- ✓/✗ Is Unreal running?
- ✓/✗ Is PX4 running?
- ✓/✗ Are MAVLink ports active?
- ✓/✗ Is ProjectAirSim server port open?

### View logs
```bash
ls -la /tmp/projectairsim/
cat /tmp/projectairsim/python.log
cat /tmp/projectairsim/px4.log
```

---

## Why Manual "Play" Button is Needed

### In AirSim's Blocks.sh
- Launches **standalone packaged game** (pre-built binary)
- Simulation starts immediately
- No editor, no Play button needed

### In Your Setup
- Opens **Unreal Editor** (for development)
- Editor starts in Edit mode (not Play mode)
- ProjectAirSim plugin **only activates in Play mode**
- You must press Play to start the simulation

### The `-game` Flag
- Command: `UnrealEditor Blocks.uproject -game`
- Should start Unreal in game mode directly
- **Sometimes doesn't work reliably** with all projects
- If it works, use `start_simulation_auto.sh`
- If it fails, use `start_simulation_v2.sh` (manual Play)

---

## Common Issues

### "Python script hangs at 'Connecting to simulation server'"
**Cause:** Unreal is not in Play mode yet
**Fix:** Make sure you pressed Play in Unreal Editor

### "Connection opened" but then hangs
**Cause:** PX4 not ready yet
**Fix:** The script should wait automatically, but you can wait longer

### "Port 14540 not found"
**Cause:** PX4 didn't start properly
**Fix:** Check PX4 terminal for errors

### "ProjectAirSim server port not detected"
**Cause:**
- Unreal not in Play mode, OR
- ProjectAirSim plugin didn't load

**Fix:**
1. Check Unreal Editor Output Log for plugin errors
2. Make sure you're in Play mode
3. Wait a few more seconds after pressing Play

---

## Port Reference

| Port | Component | Purpose |
|------|-----------|---------|
| 41451 | ProjectAirSim | Simulation API (Unreal ↔ Python) |
| 14540 | PX4 MAVLink | Offboard control (Python → PX4) |
| 18570 | PX4 MAVLink | GCS telemetry (QGC monitoring) |
| 14580 | PX4 MAVLink | Offboard local |

---

## Advanced Usage

### Start without QGroundControl
Edit the script and comment out Step 4, or just close the QGC terminal.

### Use different Python script
Edit `start_simulation_v2.sh` line with `python px4_quadrotor_extended.py` and change the script name.

### Run manually (step by step)
See [STARTUP_FIXED.md](STARTUP_FIXED.md) for manual instructions.

---

## Need Help?

1. Run `./check_connectivity.sh` to diagnose
2. Check logs in `/tmp/projectairsim/`
3. Look at individual terminal windows for error messages
4. Make sure you pressed Play in Unreal!

---

**Remember:** The key is **Unreal must be in PLAY mode before Python starts!** 🎮
