# ✅ The CORRECT Startup Order

## The Problem You Discovered

You were right! **PX4 needs the Python script to start BEFORE it can initialize.**

Here's why:

## The Connection Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Unreal Engine (Press Play)                          │
│     └─> ProjectAirSim plugin loads (but waits)          │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  2. Python Script Starts                                 │
│     └─> Loads scene_px4_sitl.jsonc                      │
│         └─> Tells ProjectAirSim to start TCP server     │
│             on port 4560                                 │
│     └─> Python waits for PX4 to connect                 │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  3. PX4 SITL Starts                                      │
│     └─> Tries to connect to TCP port 4560               │
│     └─> SUCCESS! Connects to ProjectAirSim              │
│     └─> Initializes MAVLink (ports 14540, 18570, etc)   │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  4. QGroundControl (optional)                            │
│     └─> Connects to port 18570 for monitoring           │
└─────────────────────────────────────────────────────────┘
```

## What Was Wrong Before

**Incorrect Order:**
1. Unreal ✓
2. PX4 ← **Gets stuck waiting for TCP:4560**
3. Python ← Never starts because we're waiting for PX4

**The issue:** PX4 log showed:
```
INFO [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
```

Port 4560 only opens when Python loads the scene config!

## The Correct Order

1. **Unreal Engine** - Start and press Play
2. **Python Script** - Loads scene → Opens TCP:4560
3. **PX4 SITL** - Connects to TCP:4560 → Initializes MAVLink
4. **QGroundControl** - Monitoring on port 18570

## Using the Correct Script

```bash
./start_simulation_correct.sh
```

This script:
- ✓ Starts Unreal and waits for Play
- ✓ Starts Python and waits for TCP:4560 to open
- ✓ Only then starts PX4
- ✓ Waits for PX4 to connect before starting QGC

## Key Configuration

From `robot_quadrotor_px4_sitl.jsonc`:

```json
"controller": {
  "id": "PX4_Controller",
  "type": "px4-api",
  "px4-settings": {
    "lock-step": true,
    "use-tcp": true,
    "tcp-port": 4560,        ← PX4 connects here
    "control-port": 14540,   ← MAVLink offboard API
    "qgc-port": 14550
  }
}
```

## Port Summary

| Port | Direction | Purpose | Opened By |
|------|-----------|---------|-----------|
| 4560 | PX4 → Unreal | Simulator connection (TCP) | Python/ProjectAirSim |
| 14540 | Python → PX4 | MAVLink offboard control | PX4 |
| 18570 | QGC ↔ PX4 | MAVLink GCS telemetry | PX4 |
| 14580 | Internal | MAVLink offboard local | PX4 |

## Why This Matters

**ProjectAirSim is different from standard AirSim:**
- Standard AirSim: Simulator starts TCP server immediately
- ProjectAirSim: Simulator starts TCP server only when scene is loaded by client

This is why the startup order matters!

## Manual Verification

You can check if ports are ready:

```bash
# Check if TCP:4560 is listening (should be after Python starts)
ss -tunl | grep 4560

# Check if MAVLink ports are active (should be after PX4 connects)
ss -tunl | grep -E "(14540|18570)"

# Or use the diagnostic script
./check_connectivity.sh
```

## What Success Looks Like

**Python terminal:**
```
INFO [projectairsim] Loading scene config: scene_px4_sitl.jsonc
INFO [projectairsim] Starting TCP server on port 4560
INFO [projectairsim] Waiting for PX4 connection...
INFO [projectairsim] PX4 connected!
```

**PX4 terminal:**
```
INFO [simulator_mavlink] Waiting for simulator on TCP:4560
INFO [simulator_mavlink] Connected to simulator
INFO [mavlink] mode: Onboard, data rate: 4000000 B/s
INFO [mavlink] ready
```

Now everything connects properly! 🎉
