# Quick Startup Guide

## Easy One-Command Startup

### Auto-Play Version (Recommended)
```bash
./start_simulation_auto.sh
```
- Unreal starts automatically in game mode
- No Play button needed!
- All terminals open automatically

### Manual Version (if auto-play doesn't work)
```bash
./start_simulation.sh
```
- Opens Unreal Editor
- You need to press Play button manually
- Useful for debugging/editing

### Editor Mode (for development)
```bash
./start_simulation_auto.sh editor
```
- Opens full Unreal Editor
- Allows level editing and debugging
- Requires pressing Play button

---

## What Gets Started

1. **Unreal Engine** - The 3D simulation environment
2. **PX4 SITL** - Flight controller simulation (ports 18570, 14540, etc.)
3. **Python Script** - Your drone control logic (connects to port 14540)
4. **QGroundControl** (optional) - Monitoring only (port 18570)

---

## Port Configuration

| Component | Port | Purpose |
|-----------|------|---------|
| QGroundControl | 18570 | GCS monitoring/telemetry |
| Python Script | 14540 | Offboard API control |
| Payload Link | 14030 | Camera/sensors |
| Gimbal Link | 13280 | Gimbal control |

**Important**: QGC and Python use different ports to avoid conflicts!

---

## Stopping the Simulation

Close all terminal windows or press `Ctrl+C` in each terminal.

---

## Troubleshooting

### Script says "UE_ROOT not set"
Add to your `~/.bashrc`:
```bash
export UE_ROOT=/path/to/UnrealEngine
```

### Unreal doesn't start automatically
Use manual version: `./start_simulation.sh`

### Drone doesn't move
1. Check PX4 shows "INFO [mavlink] ready"
2. Verify Python script connected successfully
3. Make sure Unreal is running (check Play button pressed)
4. If QGC is open, verify it's on port 18570

### QGC interferes with control
Make sure QGC is launched with `--udp-port 18570`

---

## More Information

- [STARTUP_FIXED.md](STARTUP_FIXED.md) - Detailed manual startup guide
- [UNREAL_AUTOPLAY_GUIDE.md](UNREAL_AUTOPLAY_GUIDE.md) - Explanation of auto-play modes
