# 🎯 Final Solution - Working Startup

## The Problem

The issue was with **timing and order**:
- Python waits for PX4 to connect on TCP:4560
- PX4 waits to connect to TCP:4560
- They need to start **simultaneously** to connect to each other!

## ✅ The Solution

```bash
# Kill any stuck processes
./kill_all.sh

# Start everything (RECOMMENDED)
./start_parallel.sh
```

## What This Does

1. **Unreal** - Starts and waits for you to press Play
2. **Python + PX4** - Start at the SAME TIME (2 second gap)
   - Python opens TCP:4560 and waits
   - PX4 connects to TCP:4560
   - They shake hands and connect!
3. **QGC** - Starts for monitoring

## Scripts Comparison

| Script | Best For | Timing Checks | Works? |
|--------|----------|---------------|--------|
| `start_parallel.sh` | **RECOMMENDED** | Minimal | ✅ |
| `start_simple.sh` | Alternative | Some | ✅ |
| `start_simulation_correct.sh` | Complex | Too many | ❌ Hangs |
| `start_simulation_v2.sh` | Complex | Too many | ❌ Hangs |

## Why Previous Scripts Failed

**Problem:** They tried to wait for ports/connections that only appear AFTER both components start:

```bash
# Wrong approach:
Start Python → Wait for TCP:4560 → Start PX4
                ↑
                This hangs! Python is waiting for PX4 to connect,
                but PX4 hasn't started yet!
```

**Solution:** Start them together:

```bash
# Right approach:
Start Python (opens TCP:4560, waits for connection)
  ↓ (2 seconds later)
Start PX4 (connects to TCP:4560)
  ↓
They connect!
```

## The Handshake Process

```
┌──────────────┐                    ┌──────────────┐
│    Python    │                    │     PX4      │
│              │                    │              │
│  Opens       │                    │              │
│  TCP:4560    │◄───────────────────│  Connects    │
│              │   TCP Connection   │  to 4560     │
│              │                    │              │
│  Waits for   │                    │  Sends       │
│  data...     │◄───────────────────│  sensor data │
│              │                    │              │
│  Scene       │────────────────────►│  Receives    │
│  loaded!     │   Motor commands   │  commands    │
│              │                    │              │
│  ✓ Ready     │                    │  ✓ Ready     │
└──────────────┘                    └──────────────┘
```

## Manual Steps (If Scripts Don't Work)

### Terminal 1: Unreal
```bash
$UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject
```
**Press Play button and wait 3 seconds**

### Terminal 2: Python
```bash
cd /home/davor/projects/DronAI/ProjectAirSim/client/python/projectairsim
poetry run bash -c "cd ../example_user_scripts && python px4_quadrotor_extended.py sitl"
```

### Terminal 3: PX4 (start 2 seconds after Python)
```bash
cd /home/davor/projects/DronAI/PX4/PX4-Autopilot
make px4_sitl none_iris
```

### Terminal 4: QGC (optional, after PX4 connects)
```bash
/home/davor/QGroundControl.AppImage --udp-port 18570
```

## Success Indicators

### Python Terminal ✅
```
Loading scene config: scene_px4_sitl.jsonc
Waiting 5 seconds for PX4 sensors to stabilize...
Enabling API control
Arming drone
Taking off...
```

### PX4 Terminal ✅
```
Waiting for simulator to accept connection on TCP port 4560
Connected to simulator
INFO [mavlink] mode: Onboard, data rate: 4000000 B/s
INFO [mavlink] ready
```

### Unreal Window ✅
- Drone spawns
- Takes off
- Flies around following the script

## Troubleshooting

### "Python hangs at 'Loading scene config'"
**Cause:** PX4 not started yet
**Fix:** Start PX4 within 5 seconds of Python

### "PX4 stuck at 'Waiting for simulator on TCP:4560'"
**Cause:** Python not started yet
**Fix:** Start Python first, then PX4

### "Both running but not connecting"
**Cause:** Unreal not in Play mode
**Fix:** Press Play in Unreal Editor!

### Check connectivity
```bash
./check_connectivity.sh

# Should show:
# ✓ Unreal running
# ✓ PX4 running
# ✓ Port 4560 active
# ✓ Port 14540 active
```

## Why 2 Second Gap?

- **0 seconds:** Too fast, Python might not have opened port yet
- **2 seconds:** Perfect, Python opens port, PX4 can connect
- **5+ seconds:** Can work, but Python might timeout or retry
- **30+ seconds:** Usually times out

## Port Summary

| Port | Protocol | Opened By | Used By | Purpose |
|------|----------|-----------|---------|---------|
| 4560 | TCP | Python/ProjectAirSim | PX4 → Unreal | Simulator connection |
| 14540 | UDP | Unreal | Python → PX4 | MAVLink control |
| 18570 | UDP | PX4 | QGC ↔ PX4 | MAVLink telemetry |

## Quick Reference

```bash
# Start simulation
./start_parallel.sh

# Stop everything
./kill_all.sh

# Check what's running
./check_connectivity.sh

# View logs (if using logging version)
ls -la /tmp/projectairsim/
```

That's it! The key is starting Python and PX4 together (with a small gap). 🚁
