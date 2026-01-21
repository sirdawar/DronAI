# Claude Instructions for DronAI Project

## Project Vision

This is a **GPS-denied navigation and surveillance system for drones with defense applications**. The project combines cutting-edge simulation with real-world autonomous navigation research.

### Core Mission
Developing autonomous drone capabilities for:

1. **GPS-Denied Navigation**
   - Visual-Inertial Odometry (VIO) using camera + IMU fusion
   - LiDAR-based navigation for obstacle avoidance and 3D mapping
   - SLAM algorithms for indoor/underground environments
   - Sensor fusion combining multiple positioning methods

2. **ISR (Intelligence, Surveillance, Reconnaissance)**
   - Computer vision for vehicle/object detection (YOLO)
   - Vision-Language Models (GPT-4V/Claude Vision/LLaVA) for scene description
   - Automated surveillance with AI-driven target identification
   - Matching camera views to satellite imagery

### Learning Platform
This simulation environment serves as a **safe prototyping platform** for testing autonomous navigation algorithms before real-world deployment. Engages with open-source community (PX4 Discord, r/diydrones, ArduPilot forums) to leverage existing work and contribute back.

## Project Overview

**Development Environment:**
- **OS**: Ubuntu Linux
- **Python**: Poetry for dependency management
- **Simulation**: Unreal Engine 5.2 with photorealistic environments
- **Flight Control**: PX4 SITL (Software-in-the-Loop)

**Technology Stack:**
- **ProjectAirSim**: Unreal Engine 5 simulation plugin (fork of Microsoft AirSim successor) - submodule
- **PX4-Autopilot**: Industry-standard open-source flight controller firmware - submodule
- **Python Scripts**: AI integration and autonomous control
- **Custom Utilities**: Startup automation and diagnostics

## Project Structure

```
DronAI/                          # Main repo (this one)
├── ProjectAirSim/               # Git submodule (sirdawar/Project_AirSim_AI)
│   ├── unreal/Blocks/          # Unreal Engine project
│   └── client/python/          # Python control scripts
├── PX4/PX4-Autopilot/          # Git submodule (PX4/PX4-Autopilot)
├── start.sh                     # Main startup script
├── kill_all.sh                  # Cleanup script
└── docs/                        # Various markdown documentation
```

## Critical Requirements

### Startup Order
**The order is CRITICAL and must be preserved:**
1. **Unreal Engine** - Must be in PLAY mode before Python connects
2. **Python Script** - Loads scene config, opens TCP:4560
3. **PX4 SITL** - Connects to TCP:4560 (opened by Python)
4. **QGroundControl** - Monitoring only on port 18570

**Why:** Python opens TCP port 4560 when loading the scene. PX4 needs this port to connect. Starting PX4 before Python will cause it to hang waiting for port 4560.

### Port Configuration
| Port  | Protocol | Purpose | Opened By | Used By |
|-------|----------|---------|-----------|---------|
| 4560  | TCP | Simulator connection | Python/ProjectAirSim | PX4 → Unreal |
| 14540 | UDP | MAVLink offboard control | Unreal/PX4 | Python → PX4 |
| 18570 | UDP | MAVLink GCS telemetry | PX4 | QGC ↔ PX4 |
| 14580 | UDP | MAVLink offboard local | PX4 | Internal |

**QGC Port Warning:** QGroundControl MUST use port 18570, not the default 14550, to avoid conflicts with Python control.

## Code Modification Guidelines

### When Modifying Startup Scripts
- **NEVER** add complex port checking loops - they cause hangs
- **KEEP** timing simple: 2-3 second delays are sufficient
- **TEST** the entire sequence after any changes
- The `start.sh` script works because it's simple and waits for user confirmation

### When Modifying Python Scripts
- Python scripts are in `ProjectAirSim/client/python/example_user_scripts/`
- After modifying, commit to the ProjectAirSim submodule first
- Then update the submodule reference in the main repo
- The 10-second QGC wait in `px4_quadrotor_extended.py` is intentional

### When Suggesting Changes
1. **Consider the startup order** - will this break the sequence?
2. **Check port conflicts** - does this introduce new port usage?
3. **Test in isolation first** - don't modify multiple components at once
4. **Keep scripts simple** - automation complexity causes more problems

## Common Issues & Solutions

### "Python hangs at 'Loading scene config'"
- **Cause:** Unreal is not in Play mode
- **Fix:** User must press Play in Unreal before Python can connect
- **Don't:** Try to automate Play button - it's unreliable

### "PX4 hangs at 'Waiting for simulator on TCP:4560'"
- **Cause:** Python hasn't opened port 4560 yet
- **Fix:** Ensure Python starts before PX4 (2-3 second gap)
- **Don't:** Add complex port checking - just use sleep

### "QGC interferes with drone control"
- **Cause:** QGC is using default port 14540 (same as Python)
- **Fix:** Always start QGC with `--udp-port 18570`
- **Already fixed in:** `start.sh` script

## Git Submodule Workflow

### Making Changes in Submodules
```bash
# 1. Make changes in submodule (e.g., ProjectAirSim)
cd ProjectAirSim
git add <files>
git commit -m "Your message"
git push origin main

# 2. Update main repo to reference new commit
cd ..
git add ProjectAirSim
git commit -m "Update ProjectAirSim submodule"
git push
```

### Pulling Updates
```bash
# Update all submodules to latest committed versions
git submodule update --remote

# Or update specific submodule
cd ProjectAirSim
git pull origin main
cd ..
git add ProjectAirSim
git commit -m "Update ProjectAirSim"
```

## Environment Setup

### Required Environment Variables
- `UE_ROOT`: Path to Unreal Engine installation (e.g., `/home/user/UE_5.2_installed`)

### Python Environment
- Uses Poetry for dependency management
- Install: `cd ProjectAirSim/client/python/projectairsim && poetry install`

### Build Requirements
- PX4 needs to be built once: `cd PX4/PX4-Autopilot && make px4_sitl_default`

## User Preferences

### Automation Philosophy
- **Prefer simple over complex** - the working `start.sh` is simple by design
- **Manual steps are OK** - user pressing Play in Unreal is acceptable
- **Don't over-engineer** - previous attempts at full automation failed

### Documentation Style
- Keep markdown files up to date
- Use clear step-by-step instructions
- Include "Why" explanations, not just "How"
- Troubleshooting sections are important

### Testing Approach
- Always test the full startup sequence after changes
- Use `kill_all.sh` to clean up between tests
- Use `check_connectivity.sh` for diagnostics

## Files to Never Modify Automatically
- Unreal Engine project files (.uproject, .uasset, .umap)
- PX4 core configuration (let user modify if needed)
- Git submodule URLs (these point to specific repos)

## Files Safe to Modify
- `start.sh` and other bash scripts in root
- Documentation markdown files
- Python scripts in ProjectAirSim (with submodule commit)
- Scene configs in `example_user_scripts/sim_config/`

## When User Asks for New Features

1. **Understand impact on startup sequence** - will it change the order?
2. **Check if it affects ports** - are we opening new connections?
3. **Consider submodule boundaries** - which repo should this go in?
4. **Keep it simple** - can this be done without complex automation?
5. **Document thoroughly** - add to appropriate markdown file

## Testing Checklist After Changes

- [ ] `./start.sh` completes without hanging
- [ ] Unreal loads and waits for Play button
- [ ] Python connects after Play is pressed
- [ ] PX4 connects to simulator (sees "Connected to simulator")
- [ ] QGC shows telemetry data
- [ ] Drone takes off and flies
- [ ] All four terminals stay open and responsive

## Remember

The current working solution is **simple and manual**. The user presses Play in Unreal, then the script handles the rest with basic delays. This works reliably. Previous attempts at full automation with port checking and health checks all failed because ProjectAirSim's plugin behavior is hard to detect programmatically.

**Keep it simple, keep it working.**
