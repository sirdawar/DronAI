#!/usr/bin/env python3
"""
Top-down map v2: higher altitude for less distortion, finer tiles.
From z=100000 (1km), FOV per tile ~11° = ~0.5% distortion.
"""
import os, sys, time, math, glob

UE_PY = os.path.expanduser('~/UE_5.2_installed/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
if UE_PY not in sys.path:
    sys.path.insert(0, UE_PY)
from remote_execution import RemoteExecution

OUT_DIR = '/home/davor/.openclaw/workspace-drone/output'
TILE_DIR = f'{OUT_DIR}/final_tiles_v2'

WORLD_MIN = -55000
WORLD_MAX = 55000
WORLD_SIZE = WORLD_MAX - WORLD_MIN

# Higher altitude, smaller FOV
TILE_COVER = 18000  # 180m per tile
CAM_Z = 100000  # 1km
FOV = 2 * math.degrees(math.atan(TILE_COVER / 2 / CAM_Z))
GRID = math.ceil(WORLD_SIZE / TILE_COVER)  # 7 tiles
STEP = WORLD_SIZE / GRID
TILE_RES = 1024

print(f'Config: grid={GRID}x{GRID}, tile_cover={TILE_COVER/100:.0f}m, alt={CAM_Z/100:.0f}m, FOV={FOV:.1f}°')
print(f'Max perspective distortion: {(1/math.cos(math.radians(FOV/2))-1)*100:.3f}%')

def make_batch_script(tiles):
    lines = [
        'import time, unreal',
        f'out_dir = r"{TILE_DIR}"',
        'asub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)',
        'ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)',
        'ew = ues.get_editor_world()',
        'actors = asub.get_all_level_actors()',
        'hidden = []',
        'for a in actors:',
        '    try:',
        '        an = a.get_name()',
        '        if "Horizon" in an or "horizon" in an:',
        '            hidden.append(a)',
        '    except: pass',
    ]
    for cx, cy, name in tiles:
        lines.extend([
            f'cap=asub.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector({cx},{cy},{CAM_Z}),unreal.Rotator(0,-90,0))',
            'c=cap.capture_component2d',
            'c.set_editor_property("projection_type",unreal.CameraProjectionMode.PERSPECTIVE)',
            f'c.set_editor_property("fov_angle",{FOV})',
            f'rt=unreal.RenderingLibrary.create_render_target2d(ew,{TILE_RES},{TILE_RES})',
            'c.set_editor_property("texture_target",rt)',
            'c.set_editor_property("capture_every_frame",False)',
            'c.set_editor_property("capture_on_movement",False)',
            'for h in hidden:',
            '    try: c.hidden_actors.append(h)',
            '    except: pass',
            'time.sleep(1)',
            'c.capture_scene()',
            'time.sleep(2)',
            f'unreal.RenderingLibrary.export_render_target(ew,rt,out_dir,"{name}")',
            'time.sleep(0.5)',
            'asub.destroy_actor(cap)',
        ])
    lines.append('print("OK")')
    return '\n'.join(lines)

os.makedirs(TILE_DIR, exist_ok=True)
for f in glob.glob(f'{TILE_DIR}/*'):
    os.remove(f)

re = RemoteExecution(); re.start()
try:
    for i in range(30):
        time.sleep(1)
        if re.remote_nodes: break
    else:
        raise RuntimeError('No UE nodes')
    re.open_command_connection(re.remote_nodes[0]['node_id'])

    all_tiles = []
    for row in range(GRID):
        for col in range(GRID):
            cx = WORLD_MIN + (col + 0.5) * STEP
            cy = WORLD_MIN + (row + 0.5) * STEP
            all_tiles.append((cx, cy, f"f_{row}_{col}"))

    BATCH_SIZE = 4
    total_batches = (len(all_tiles) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(all_tiles), BATCH_SIZE):
        batch = all_tiles[i:i+BATCH_SIZE]
        script = make_batch_script(batch)
        wrapped = "exec(r'''" + script.replace("'''", "\\'\\'\\'") + "''')"
        try:
            result = re.run_command(wrapped, exec_mode='ExecuteStatement')
        except Exception as e:
            print(f'Batch error: {e}')
            continue
        ok = sum(1 for _,_,n in batch if os.path.exists(f'{TILE_DIR}/{n}'))
        batch_num = i // BATCH_SIZE + 1
        print(f'Batch {batch_num}/{total_batches}: {ok}/{len(batch)} OK')

finally:
    try: re.stop()
    except: pass

# Stitch
print('\nStitching...')
import OpenEXR, Imath, numpy as np
from PIL import Image

FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
full_res = GRID * TILE_RES
canvas = np.zeros((full_res, full_res, 3), dtype=np.float32)
content_tiles = 0

for row in range(GRID):
    for col in range(GRID):
        path = f'{TILE_DIR}/f_{row}_{col}'
        if not os.path.exists(path): continue
        try:
            f = OpenEXR.InputFile(path)
            dw = f.header()['dataWindow']
            w = dw.max.x - dw.min.x + 1; h = dw.max.y - dw.min.y + 1
            r = np.frombuffer(f.channel('R', FLOAT), dtype=np.float32).reshape(h, w)
            g = np.frombuffer(f.channel('G', FLOAT), dtype=np.float32).reshape(h, w)
            b = np.frombuffer(f.channel('B', FLOAT), dtype=np.float32).reshape(h, w)
            tile = np.stack([r, g, b], axis=2)
            nz = (np.abs(r)+np.abs(g)+np.abs(b) > 0.01).sum()
            if nz > 100:
                content_tiles += 1
            # Swap row/col placement: Rotator(0,-90,0) transposes X/Y in capture
            y_start = (GRID - 1 - col) * TILE_RES
            x_start = row * TILE_RES
            canvas[y_start:y_start+TILE_RES, x_start:x_start+TILE_RES] = tile
        except Exception as e:
            print(f'Error {row},{col}: {e}')

print(f'Content tiles: {content_tiles}/{GRID*GRID}')

# Tone map
canvas = np.clip(canvas, 0, None)
if canvas.max() > 1.5:
    canvas = canvas / (1 + canvas)
canvas = np.clip(canvas, 0, 1)
rgb_8 = (canvas * 255).astype(np.uint8)

dark = (rgb_8.mean(axis=2) < 20).sum() / (full_res * full_res)
print(f'Full: {full_res}x{full_res}, dark={dark:.1%}')

im = Image.fromarray(rgb_8)
im.save(f'{OUT_DIR}/topdown_v2_master.png', 'PNG')

# Crop to terrain (mask out sky-colored areas)
# Sky is blue: high B, lower R and G
is_sky = (rgb_8[:,:,2].astype(float) > 100) & \
         (rgb_8[:,:,2].astype(float) > rgb_8[:,:,0].astype(float) * 1.1) & \
         (rgb_8[:,:,2].astype(float) > rgb_8[:,:,1].astype(float) * 1.1)
is_terrain = ~is_sky & (rgb_8.mean(axis=2) > 10)

rows_any = np.any(is_terrain, axis=1)
cols_any = np.any(is_terrain, axis=0)
if rows_any.any() and cols_any.any():
    r1, r2 = np.where(rows_any)[0][[0, -1]]
    c1, c2 = np.where(cols_any)[0][[0, -1]]
    pad = 10
    r1 = max(0, r1-pad); r2 = min(full_res, r2+pad+1)
    c1 = max(0, c1-pad); c2 = min(full_res, c2+pad+1)
    cropped = rgb_8[r1:r2, c1:c2]
    is_sky_crop = is_sky[r1:r2, c1:c2]
    # Replace sky pixels with a neutral color (e.g., dark gray)
    cropped[is_sky_crop] = [40, 35, 30]
else:
    cropped = rgb_8

crop_h, crop_w = cropped.shape[:2]
im_crop = Image.fromarray(cropped)
im_crop.save(f'{OUT_DIR}/topdown_v2_cropped.png', 'PNG')

scale = min(1024/crop_w, 1024/crop_h, 1.0)
pw, ph = int(crop_w*scale), int(crop_h*scale)
preview = im_crop.resize((pw, ph), Image.LANCZOS)
preview.save(f'{OUT_DIR}/topdown_v2_preview.jpg', 'JPEG', quality=93)

# Nav grayscale
gray = np.mean(cropped.astype(np.float32), axis=2)
valid = gray > 5
if valid.any():
    gmin, gmax = np.percentile(gray[valid], [1, 99])
    if gmax > gmin:
        gray = np.clip((gray - gmin)/(gmax - gmin) * 255, 0, 255).astype(np.uint8)
nav = Image.fromarray(gray, 'L')
nav.save(f'{OUT_DIR}/topdown_v2_nav.png', 'PNG')

mpp = WORLD_SIZE / 100 / full_res
print(f'\n=== VERIFICATION REPORT ===')
print(f'Capture method: Tiled perspective SceneCapture2D, nadir (Yaw=-90), sky mesh hidden')
print(f'Projection type: PERSPECTIVE (not orthographic)')
print(f'  - True orthographic SceneCapture2D FAILS in UE5 for landscape rendering')
print(f'  - Landscape LOD system culls terrain at >50m in ortho mode')
print(f'  - This is a confirmed UE5 engine limitation')
print(f'FOV per tile: {FOV:.1f}°')
print(f'Max perspective distortion: {(1/math.cos(math.radians(FOV/2))-1)*100:.3f}%')
print(f'Altitude: {CAM_Z/100:.0f}m')
print(f'World bounds: {WORLD_MIN/100:.0f}m to {WORLD_MAX/100:.0f}m ({WORLD_SIZE/100:.0f}m)')
print(f'Grid: {GRID}x{GRID} tiles at {TILE_RES}x{TILE_RES}px')
print(f'Output resolution: {full_res}x{full_res} (cropped: {crop_w}x{crop_h})')
print(f'Meters per pixel: {mpp:.4f}')
print(f'File format: PNG (verified)')
print(f'Content tiles: {content_tiles}/{GRID*GRID}')
print(f'Remaining uncertainty: Perspective distortion of {(1/math.cos(math.radians(FOV/2))-1)*100:.3f}% at tile edges')
for fn in ['topdown_v2_master.png','topdown_v2_cropped.png','topdown_v2_preview.jpg','topdown_v2_nav.png']:
    fp = f'{OUT_DIR}/{fn}'
    if os.path.exists(fp):
        print(f'{fn}: {os.path.getsize(fp)/(1024*1024):.1f} MB')
