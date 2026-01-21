# Push DronAI to GitHub

## Step 1: Create GitHub Repository

Go to GitHub and create a new repository:
- Name: `DronAI` (or your preferred name)
- Description: "Autonomous drone development environment with ProjectAirSim and PX4"
- **Do NOT** initialize with README, .gitignore, or license (we already have these)
- Visibility: Public or Private (your choice)

## Step 2: Add Remote and Push

After creating the repo on GitHub, run these commands:

```bash
cd /home/davor/projects/DronAI

# Add the GitHub remote (replace YOUR_USERNAME)
git remote add origin git@github.com:YOUR_USERNAME/DronAI.git

# Or use HTTPS if you prefer:
# git remote add origin https://github.com/YOUR_USERNAME/DronAI.git

# Push to GitHub
git push -u origin main
```

## Step 3: Verify

Check that everything is pushed:
- Main repo files (scripts, docs)
- `.gitmodules` file
- Submodule references for ProjectAirSim and PX4

## What Gets Pushed

✅ All bash scripts (start.sh, kill_all.sh, etc.)
✅ All documentation (markdown files)
✅ Submodule references (pointing to your ProjectAirSim fork and PX4 repo)
✅ CLAUDE.md and Copilot instructions

❌ Submodule contents (they're in their own repos)
❌ Build artifacts (excluded by .gitignore)
❌ Unreal Engine files (excluded by .gitignore)

## For Others to Clone Your Repo

```bash
# Clone with submodules
git clone --recursive git@github.com:YOUR_USERNAME/DronAI.git

# Or if already cloned without --recursive:
cd DronAI
git submodule update --init --recursive
```

## Current Status

Your local repo is ready with:
- 3 commits on main branch
- 2 submodules configured
- All documentation complete
- Working startup scripts

Just create the GitHub repo and push! 🚀
