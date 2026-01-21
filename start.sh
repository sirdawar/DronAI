#!/bin/bash
# Super simple startup - just opens terminals, YOU control the timing

if [ -z "$UE_ROOT" ]; then
    echo "ERROR: Set UE_ROOT first!"
    exit 1
fi

echo "Opening terminals..."
echo ""
echo "ORDER:"
echo "  1. Wait for Unreal to load"
echo "  2. Press PLAY in Unreal"
echo "  3. Wait 5 seconds"
echo "  4. Python will start automatically"
echo "  5. PX4 will start automatically"
echo ""
read -p "Press Enter to start..."

# Terminal 1: Unreal
gnome-terminal --title="1-Unreal" -- bash -c "
    echo 'Starting Unreal...'
    echo 'REMEMBER: Press PLAY after it loads!'
    echo ''
    $UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
      /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject
" &

echo "Unreal starting..."
echo ""
echo "WAITING FOR YOU TO PRESS PLAY IN UNREAL..."
read -p "Press Enter AFTER you pressed Play and waited 5 seconds... "

# Terminal 2: Python
gnome-terminal --title="2-Python" -- bash -c "
    cd /home/davor/projects/DronAI/ProjectAirSim/client/python/projectairsim
    echo 'Starting Python...'
    echo ''
    poetry run bash -c 'cd ../example_user_scripts && python px4_quadrotor_extended.py sitl'
    read -p 'Done. Press Enter to close...'
" &

echo "Python starting, waiting 2 seconds..."
sleep 2

# Terminal 3: PX4
gnome-terminal --title="3-PX4" -- bash -c "
    cd /home/davor/projects/DronAI/PX4/PX4-Autopilot
    echo 'Starting PX4...'
    echo ''
    make px4_sitl none_iris
" &

echo "PX4 starting, waiting 2 seconds..."
sleep 2

# Terminal 4: QGC (start early so it's ready when drone flies)
if [ -f "/home/davor/QGroundControl.AppImage" ]; then
    gnome-terminal --title="4-QGC" -- bash -c "
        /home/davor/QGroundControl.AppImage --udp-port 18570
    " &
    echo "QGC started"
fi

echo "All systems starting up..."
sleep 1

echo ""
echo "All terminals opened!"
echo "Watch the Python terminal - drone should be flying!"
