# Why Manual "Play" is Needed and How to Auto-Start

## Why You Need to Press Play

When you open an Unreal Engine project using the **Editor**, it starts in **Edit Mode** by default. This mode is for:
- Level design
- Asset placement
- Blueprint editing
- Configuration

The simulation only runs when you press **Play** (or PIE - Play In Editor).

## Why AirSim's Blocks Example Starts Automatically

AirSim's `Blocks.sh` script doesn't open the **Unreal Editor** - instead, it launches the **Standalone Game** (packaged binary). This is a pre-built executable that starts in play mode immediately.

**The difference:**
- `UnrealEditor Blocks.uproject` → Opens **Editor** (requires Play button)
- `Blocks.sh` or packaged game → Runs **Standalone Game** (auto-starts)

## Solutions to Auto-Start

### Option 1: Launch as Standalone Game (Recommended for Automation)

You can package your Blocks project as a standalone binary:

1. Open Unreal Editor with your Blocks project
2. Go to **Platforms** → **Linux** → **Package Project**
3. Wait for packaging to complete
4. Run the generated executable directly (like Blocks.sh does)

**Pros:**
- Starts automatically
- Faster startup
- No editor overhead

**Cons:**
- Takes time to package
- Harder to debug
- Need to repackage after changes

### Option 2: Use Command-Line Arguments to Auto-Play

Unreal Engine supports command-line arguments to start in play mode:

```bash
$UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject \
  -game -WINDOWED -ResX=1280 -ResY=720
```

**Key arguments:**
- `-game`: Launch directly into game mode (no editor UI)
- `-WINDOWED`: Run in windowed mode instead of fullscreen
- `-ResX=1280 -ResY=720`: Set window resolution

**Pros:**
- No manual interaction needed
- Faster than editor mode
- Easier to automate

**Cons:**
- Still loads editor executable (heavier than standalone)
- Limited debugging compared to full editor

### Option 3: Use Unreal Automation Commands

You can use the `-ExecCmds` flag to execute console commands on startup:

```bash
$UE_ROOT/Engine/Binaries/Linux/UnrealEditor \
  /home/davor/projects/DronAI/ProjectAirSim/unreal/Blocks/Blocks.uproject \
  -ExecCmds="AutomationList;StartGame"
```

This is more experimental and may require custom setup.

### Option 4: Modify Project Settings (Partial Solution)

You can set the project to start in "Standalone Game" mode by default:

1. Open Project Settings → Maps & Modes
2. Set **Editor Startup Map** to your Blocks map
3. Enable **Start in VR/Standalone Game Mode**

But this still requires pressing Play - just changes what happens when you do.

## Recommended Approach for Your Setup

For automated simulation runs, I recommend **Option 2** (command-line `-game` flag). Let me create an updated startup script with this option.

## Comparison Table

| Method | Auto-Start | Speed | Debug Capability | Rebuild Needed |
|--------|-----------|-------|------------------|----------------|
| Editor (current) | ❌ Manual Play | Slow | Full Editor | No |
| `-game` flag | ✅ Auto | Medium | Console only | No |
| Standalone Package | ✅ Auto | Fast | Minimal | After changes |
| Blocks.sh style | ✅ Auto | Fast | Minimal | Provided by AirSim |

## Why AirSim Provides Blocks.sh

AirSim's pre-built Blocks environment comes with a packaged standalone binary specifically for this reason - to make it easy to run automated simulations without manual interaction. Your custom Blocks project is opened via the Editor, which is why you need the Play button.
