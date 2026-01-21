# DronAI - Autonomous Drone Development Environment

Complete setup for autonomous drone simulation using ProjectAirSim, PX4, and Unreal Engine.

## 🚁 Quick Start

```bash
./start.sh
```

See [START_HERE.md](START_HERE.md) for detailed instructions.

## 📦 Components

- **ProjectAirSim** - Unreal Engine plugin for drone simulation (submodule)
- **PX4-Autopilot** - Flight controller firmware (submodule)
- **QGroundControl** - Ground control station
- **Startup Scripts** - Automated launch scripts

## 📚 Documentation

- [START_HERE.md](START_HERE.md) - Main startup guide
- [MANUAL_STEPS.md](MANUAL_STEPS.md) - Step-by-step manual instructions
- [FINAL_SOLUTION.md](FINAL_SOLUTION.md) - Technical details and troubleshooting
- [CORRECT_STARTUP_ORDER.md](CORRECT_STARTUP_ORDER.md) - Understanding the startup sequence

## 🛠️ Setup

### Prerequisites
- Unreal Engine 5.2 (set `$UE_ROOT` environment variable)
- Python 3.8+ with Poetry
- Build tools (cmake, gcc, etc.)

### Clone with Submodules

```bash
git clone --recursive <your-repo-url>
cd DronAI
```

Or if already cloned:

```bash
git submodule update --init --recursive
```

### Build Components

1. **Build PX4:**
   ```bash
   cd PX4/PX4-Autopilot
   make px4_sitl_default
   ```

2. **Install Python dependencies:**
   ```bash
   cd ProjectAirSim/client/python/projectairsim
   poetry install
   ```

3. **Open Unreal Project:**
   ```bash
   $UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
     ProjectAirSim/unreal/Blocks/Blocks.uproject
   ```

## 🚀 Running the Simulation

### Automated Startup (Recommended)

```bash
./start.sh
```

This will:
1. Open Unreal Engine (you press Play)
2. Start Python control script
3. Start PX4 SITL
4. Start QGroundControl

### Manual Startup

See [MANUAL_STEPS.md](MANUAL_STEPS.md) for step-by-step instructions.

## 🔧 Utility Scripts

- `./start.sh` - Main startup script
- `./kill_all.sh` - Stop all simulation processes
- `./check_connectivity.sh` - Diagnostic tool

## 📁 Project Structure

```
DronAI/
├── ProjectAirSim/          # Simulation framework (git submodule)
├── PX4/PX4-Autopilot/      # Flight controller (git submodule)
├── start.sh                # Main startup script
├── kill_all.sh             # Cleanup script
├── check_connectivity.sh   # Diagnostics
└── docs/                   # Documentation files
```

## 🐛 Troubleshooting

Run the connectivity checker:
```bash
./check_connectivity.sh
```

Common issues:
- **Python hangs:** Make sure Unreal is in Play mode
- **PX4 can't connect:** Start Python before PX4
- **QGC conflicts:** Make sure it's using port 18570

## 📝 License

- ProjectAirSim: See [ProjectAirSim/LICENSE](ProjectAirSim/LICENSE)
- PX4-Autopilot: BSD 3-Clause (see PX4 repo)
- Custom scripts: MIT

## 🤝 Contributing

This is a personal development environment. For issues with:
- ProjectAirSim: Report to [iamaisim/ProjectAirSim](https://github.com/iamaisim/ProjectAirSim)
- PX4: Report to [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
