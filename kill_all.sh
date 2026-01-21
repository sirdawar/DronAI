#!/bin/bash

# Kill all ProjectAirSim simulation processes

echo "Killing all simulation processes..."

# Kill PX4
pkill -f "px4.*sitl" && echo "✓ Killed PX4" || echo "⊘ PX4 not running"

# Kill Unreal
pkill -f "UnrealEditor.*Blocks" && echo "✓ Killed Unreal" || echo "⊘ Unreal not running"

# Kill QGroundControl
pkill -f "QGroundControl" && echo "✓ Killed QGC" || echo "⊘ QGC not running"

# Kill any Python scripts
pkill -f "px4_quadrotor" && echo "✓ Killed Python scripts" || echo "⊘ Python not running"

echo ""
echo "All processes stopped."
echo "You can now run: ./start_simulation_correct.sh"
