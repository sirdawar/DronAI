#!/bin/bash

# Test script to diagnose launch issues

echo "=== Testing Unreal Launch ==="
echo ""

# Test 1: Normal editor launch
echo "Test 1: Launching Unreal Editor (normal mode)"
echo "Command: $UE_ROOT/Engine/Binaries/Linux/UnrealEditor /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject"
echo ""
read -p "Press Enter to test normal editor launch (will open Unreal)..."

$UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject &

UNREAL_PID=$!
echo "Unreal PID: $UNREAL_PID"
echo "Waiting 10 seconds for Unreal to start..."
sleep 10

if ps -p $UNREAL_PID > /dev/null; then
    echo "✓ Unreal is running (PID $UNREAL_PID)"
    echo ""
    read -p "Did Unreal Editor open? (y/n): " answer
    if [ "$answer" = "y" ]; then
        echo "✓ Normal editor launch works"
    else
        echo "✗ Normal editor launch failed"
    fi

    echo ""
    echo "Killing Unreal..."
    kill $UNREAL_PID
    sleep 2
else
    echo "✗ Unreal process died"
fi

echo ""
echo "==================================="
echo ""

# Test 2: Game mode launch
echo "Test 2: Launching Unreal in -game mode"
echo "Command: $UE_ROOT/Engine/Binaries/Linux/UnrealEditor /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject -game -WINDOWED"
echo ""
read -p "Press Enter to test -game mode launch..."

$UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject \
  -game -WINDOWED -ResX=1280 -ResY=720 &

UNREAL_PID=$!
echo "Unreal PID: $UNREAL_PID"
echo "Waiting 15 seconds for Unreal to start..."
sleep 15

if ps -p $UNREAL_PID > /dev/null; then
    echo "✓ Unreal is running in game mode (PID $UNREAL_PID)"
    echo ""
    read -p "Did Unreal game window open and start playing? (y/n): " answer
    if [ "$answer" = "y" ]; then
        echo "✓ Game mode launch works!"
        echo "  This means auto-play should work"
    else
        echo "✗ Game mode launch opened but didn't auto-play"
        echo "  You may need to use editor mode with manual Play"
    fi

    echo ""
    read -p "Press Enter to kill Unreal and continue..."
    kill $UNREAL_PID
    sleep 2
else
    echo "✗ Unreal process died in game mode"
    echo "  -game flag may not work with this project"
fi

echo ""
echo "==================================="
echo ""
echo "Test complete. Results:"
echo "- If Test 1 worked but Test 2 didn't: Use start_simulation.sh (manual Play)"
echo "- If Test 2 worked: Use start_simulation_auto.sh"
echo "- If neither worked: Check Unreal project and logs"
