#!/bin/bash

# Check connectivity status for ProjectAirSim simulation

echo "=== ProjectAirSim Connectivity Check ==="
echo ""

# Check if Unreal is running
if pgrep -f "UnrealEditor.*Blocks" > /dev/null; then
    echo "✓ Unreal Engine is running"
else
    echo "✗ Unreal Engine is NOT running"
fi

# Check if PX4 is running
if pgrep -f "px4.*sitl" > /dev/null; then
    echo "✓ PX4 SITL is running"
else
    echo "✗ PX4 SITL is NOT running"
fi

echo ""
echo "=== Network Ports ==="
echo ""

# Check ProjectAirSim port (usually 41451 or similar)
echo "Checking for ProjectAirSim server ports:"
netstat -an 2>/dev/null | grep LISTEN | grep -E ":(414[0-9]{2}|415[0-9]{2})" || echo "  No ProjectAirSim ports detected"

echo ""
echo "Checking for MAVLink ports:"

# Check MAVLink ports
if netstat -an 2>/dev/null | grep -q ":14540 "; then
    echo "  ✓ Port 14540 (Offboard API) - ACTIVE"
else
    echo "  ✗ Port 14540 (Offboard API) - NOT ACTIVE"
fi

if netstat -an 2>/dev/null | grep -q ":18570 "; then
    echo "  ✓ Port 18570 (GCS) - ACTIVE"
else
    echo "  ✗ Port 18570 (GCS) - NOT ACTIVE"
fi

if netstat -an 2>/dev/null | grep -q ":14580 "; then
    echo "  ✓ Port 14580 (Offboard Local) - ACTIVE"
else
    echo "  ✗ Port 14580 (Offboard Local) - NOT ACTIVE"
fi

echo ""
echo "=== All UDP Listening Ports ==="
netstat -anup 2>/dev/null | grep LISTEN || echo "Need sudo for process names"

echo ""
echo "=== Diagnosis ==="
echo ""

UNREAL_OK=false
PX4_OK=false
MAVLINK_OK=false
PROJECTAIRSIM_OK=false

if pgrep -f "UnrealEditor.*Blocks" > /dev/null; then
    UNREAL_OK=true
fi

if pgrep -f "px4.*sitl" > /dev/null; then
    PX4_OK=true
fi

if netstat -an 2>/dev/null | grep -q ":14540 "; then
    MAVLINK_OK=true
fi

if netstat -an 2>/dev/null | grep -qE ":(414[0-9]{2}|415[0-9]{2}).*LISTEN"; then
    PROJECTAIRSIM_OK=true
fi

if [ "$UNREAL_OK" = false ]; then
    echo "❌ Unreal is not running - Start Unreal first!"
elif [ "$PROJECTAIRSIM_OK" = false ]; then
    echo "❌ ProjectAirSim plugin server not detected"
    echo "   Possible causes:"
    echo "   1. Unreal is running but you haven't pressed PLAY yet"
    echo "   2. ProjectAirSim plugin didn't load"
    echo "   3. Unreal is still starting up"
    echo ""
    echo "   Solution: Make sure Unreal is in PLAY mode!"
fi

if [ "$PX4_OK" = false ]; then
    echo "❌ PX4 is not running - Start PX4 SITL!"
elif [ "$MAVLINK_OK" = false ]; then
    echo "❌ MAVLink ports not ready - Wait for PX4 to fully initialize"
fi

if [ "$UNREAL_OK" = true ] && [ "$PROJECTAIRSIM_OK" = true ] && [ "$PX4_OK" = true ] && [ "$MAVLINK_OK" = true ]; then
    echo "✅ All systems appear ready!"
    echo "   You can now run the Python control script"
fi

echo ""
