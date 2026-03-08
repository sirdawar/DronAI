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

# 0. Hard cleanup to avoid stale PX4 instance conflicts
pkill -f 'PX4-Autopilot/build/.*/bin/px4' >/dev/null 2>&1 || true
pkill -f 'px4_sitl none_iris' >/dev/null 2>&1 || true
pkill -f px4_quadrotor_extended.py >/dev/null 2>&1 || true
rm -f /tmp/px4.log /tmp/airsim_client.log

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

PORT_4560_READY=0
if ss -tlnp | grep -q 4560; then
  PORT_4560_READY=1
fi

if [ "$PORT_4560_READY" -eq 0 ]; then
  echo "⚠️ Port 4560 did not open after Play. Continuing with fallback startup..."
fi

wait_for_px4_ready() {
  local attempts=${1:-60}
  local sleep_sec=${2:-2}
  for i in $(seq 1 "$attempts"); do
    if grep -q "Simulator connected on TCP port 4560\|Ready for takeoff" /tmp/px4.log 2>/dev/null; then
      echo "✅ PX4 reports simulator link/ready"
      return 0
    fi
    if ! pgrep -f 'PX4-Autopilot/build/.*/bin/px4' >/dev/null 2>&1; then
      echo "❌ PX4 process is not running"
      return 1
    fi
    sleep "$sleep_sec"
  done
  echo "❌ PX4 ready timeout"
  return 1
}

# 4. Start PX4 SITL first and ensure readiness before mission script
echo "[3/4] Starting PX4 SITL..."
cd "$PX4_DIR"
nohup make px4_sitl none_iris > /tmp/px4.log 2>&1 &
PX4_MAKE_PID=$!
echo "PX4 make PID: $PX4_MAKE_PID"

if ! wait_for_px4_ready 60 2; then
  echo "⚠️ First PX4 startup not ready, restarting once..."
  pkill -f 'PX4-Autopilot/build/.*/bin/px4' || true
  sleep 2
  : > /tmp/px4.log
  nohup make px4_sitl none_iris > /tmp/px4.log 2>&1 &
  PX4_MAKE_PID=$!
  echo "PX4 restart make PID: $PX4_MAKE_PID"

  if ! wait_for_px4_ready 60 2; then
    echo "ERROR: PX4 failed readiness check after restart"
    exit 1
  fi
fi

# 5. Start Python mission only after PX4 readiness is confirmed
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
