# GitHub Copilot Instructions for DronAI Project

## Project Context

**Mission**: GPS-denied navigation and ISR (Intelligence, Surveillance, Reconnaissance) system for drones with defense applications.

**Research Focus**:
- GPS-Denied Navigation: VIO (Visual-Inertial Odometry), LiDAR, SLAM, sensor fusion
- ISR Capabilities: Computer vision (YOLO), Vision-Language Models (GPT-4V/Claude/LLaVA), satellite imagery matching
- Autonomous target identification and surveillance

**Environment**: Ubuntu Linux, Unreal Engine 5.2, Python with Poetry, PX4 SITL

**Purpose**: Safe prototyping platform for autonomous navigation algorithms before real-world deployment. Learning from open-source community (PX4 Discord, r/diydrones, ArduPilot forums).

## Critical Startup Order (Never Change)

```bash
1. Unreal (user presses Play)
2. Python (opens TCP:4560) → sleep 2
3. PX4 (connects to TCP:4560) → sleep 2
4. QGC (monitoring on port 18570)
```

## Port Configuration

- 4560: TCP - PX4 → Unreal simulator
- 14540: UDP - Python → PX4 control
- 18570: UDP - QGC ↔ PX4 telemetry

## Code Patterns

### Bash Scripts
```bash
gnome-terminal --title="Name" -- bash -c "command" &
sleep 2  # Simple delays only, no complex checks
```

### Python (ProjectAirSim)
```python
async def main(scenefile):
    client = ProjectAirSimClient()
    client.connect()
    world = World(client, scenefile)
    drone = Drone(client, world, "Drone1")

    await asyncio.sleep(5)  # Sensor stabilization
    drone.enable_api_control()
    await drone.takeoff_async()
```

## Anti-Patterns

❌ Complex port checking loops (causes hangs)
❌ Starting PX4 before Python (port 4560 not ready)
❌ Blocking drone operations (use async/await)

✅ Simple sleep delays
✅ Python before PX4
✅ Async drone control

## Submodule Workflow

```bash
# Modify in submodule
cd ProjectAirSim
git commit -m "change"
git push

# Update parent
cd ..
git add ProjectAirSim
git commit -m "Update submodule"
```

## Keep It Simple

This project values reliability over automation. Working solution uses manual Play button + simple delays.
