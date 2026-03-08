#!/bin/bash
# Full automated drone sim startup - fixes PX4 timing issue
# Usage: ./start_full_auto.sh

set -e
export UE_ROOT="$HOME/UE_5.2_installed"

AIRSIM_PY="/home/davor/.cache/pypoetry/virtualenvs/projectairsim-UMFaqgh7-py3.10/bin/python"
SCRIPTS_DIR="/home/davor/projects/DronAI/ProjectAirSim/client/python/example_user_scripts"
PX4_DIR="/home/davor/projects/DronAI/PX4/PX4-Autopilot"
UE_REMOTE="/home/davor/UE_5.2_installed/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python"

echo "=== Starting Drone Simulation ==="

# 1. Start UE
echo "[1/4] Starting Unreal Editor..."
nohup $UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject \
  > /tmp/ue.log 2>&1 &

echo "Waiting 70s for UE to load..."
sleep 70

# 2. Press Play via UE Python remote API
echo "[2/4] Pressing Play in UE..."
python3 -c "
import sys, time
sys.path.insert(0, '$UE_REMOTE')
from remote_execution import RemoteExecution
re = RemoteExecution()
re.start()
time.sleep(3)
nodes = re.remote_nodes
if not nodes:
    print('ERROR: No UE nodes found')
    re.stop()
    sys.exit(1)
re.open_command_connection(nodes[0]['node_id'])
result = re.run_command(
    'import unreal; unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()',
    exec_mode='ExecuteStatement', raise_on_failure=False)
print('Play result:', result['success'])
re.close_command_connection()
re.stop()
"

# 3. Wait for port 4560 to open (means UE sim is ready)
echo "Waiting for simulation to be ready (port 4560)..."
for i in $(seq 1 20); do
  if ss -tlnp | grep -q 4560; then
    echo "✅ Port 4560 open — simulation ready!"
    break
  fi
  echo "  Attempt $i/20..."
  sleep 3
done

if ! ss -tlnp | grep -q 4560; then
  echo "ERROR: Port 4560 never opened"
  exit 1
fi

# 4. Start PX4 first (avoids Python timeout race)
echo "[3/4] Starting PX4 SITL first..."
cd "$PX4_DIR"
nohup make px4_sitl none_iris > /tmp/px4.log 2>&1 &
PX4_PID=$!
echo "PX4 PID: $PX4_PID"

# Wait for PX4 boot progress
echo "Waiting for PX4 to initialize..."
for i in $(seq 1 30); do
  if grep -q "Ready for takeoff\|INFO  \[px4\]\|INFO  \[simulator\]" /tmp/px4.log 2>/dev/null; then
    echo "✅ PX4 booting/ready"
    break
  fi
  sleep 2
done

# 5. Start Python client after PX4 is up
echo "[4/4] Starting AirSim Python client..."
cd "$SCRIPTS_DIR"
nohup $AIRSIM_PY px4_quadrotor_extended.py sitl > /tmp/airsim_client.log 2>&1 &
PYTHON_PID=$!
echo "Python client PID: $PYTHON_PID"

# If Python exits too early, retry once after short delay
sleep 8
if ! kill -0 $PYTHON_PID 2>/dev/null; then
  echo "⚠️ Python client exited early; retrying once..."
  nohup $AIRSIM_PY px4_quadrotor_extended.py sitl >> /tmp/airsim_client.log 2>&1 &
  PYTHON_PID=$!
  echo "Python retry PID: $PYTHON_PID"
fi

# Wait and check full connection
sleep 12
echo ""
echo "=== Status ==="
echo "UE:     $(pgrep -c UnrealEditor 2>/dev/null && echo running || echo DEAD)"
echo "Python: $(pgrep -c -f px4_quadrotor 2>/dev/null && echo running || echo DEAD)"  
echo "PX4:    $(pgrep -c -f 'bin/px4' 2>/dev/null && echo running || echo DEAD)"
echo ""
echo "Last Python log:"
tail -5 /tmp/airsim_client.log
echo ""
echo "Last PX4 log:"
tail -5 /tmp/px4.log
