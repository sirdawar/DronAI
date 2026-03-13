#!/usr/bin/env python3
"""Re-stitch from cached EXR tiles with row/col swap + overlap crop. No UE needed."""
import os, math, numpy as np, OpenEXR, Imath
from PIL import Image

TILE_DIR = '/home/davor/.openclaw/workspace-drone/output/final_tiles_v2'
OUT_DIR = '/home/davor/.openclaw/workspace-drone/output'

WORLD_MIN = -55000
WORLD_MAX = 55000
WORLD_SIZE = WORLD_MAX - WORLD_MIN
TILE_COVER = 18000
CAM_Z = 100000
FOV = 2 * math.degrees(math.atan(TILE_COVER / 2 / CAM_Z))
GRID = math.ceil(WORLD_SIZE / TILE_COVER)
STEP = WORLD_SIZE / GRID
TILE_RES = 1024
FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

# Each tile captures TILE_COVER but grid step is STEP < TILE_COVER
# Crop the overlap from each edge so tiles butt together correctly
crop_px = int(round((TILE_COVER - STEP) / 2 / TILE_COVER * TILE_RES))
inner = TILE_RES - 2 * crop_px
full_res = GRID * inner

print(f'Grid: {GRID}x{GRID}, crop: {crop_px}px/edge, inner tile: {inner}x{inner}px')
print(f'Output: {full_res}x{full_res}px')

canvas = np.zeros((full_res, full_res, 3), dtype=np.float32)
content_tiles = 0

for row in range(GRID):
    for col in range(GRID):
        path = f'{TILE_DIR}/f_{row}_{col}'
        if not os.path.exists(path):
            continue
        try:
            f = OpenEXR.InputFile(path)
            dw = f.header()['dataWindow']
            w = dw.max.x - dw.min.x + 1
            h = dw.max.y - dw.min.y + 1
            r = np.frombuffer(f.channel('R', FLOAT), dtype=np.float32).reshape(h, w)
            g = np.frombuffer(f.channel('G', FLOAT), dtype=np.float32).reshape(h, w)
            b = np.frombuffer(f.channel('B', FLOAT), dtype=np.float32).reshape(h, w)
            tile = np.stack([r, g, b], axis=2)
            nz = (np.abs(r) + np.abs(g) + np.abs(b) > 0.01).sum()
            if nz > 100:
                content_tiles += 1
            # Crop overlap edges
            tile = tile[crop_px:crop_px + inner, crop_px:crop_px + inner]
            # Swap row/col placement: Rotator(0,-90,0) transposes X/Y in capture
            y_start = (GRID - 1 - col) * inner
            x_start = row * inner
            canvas[y_start:y_start + inner, x_start:x_start + inner] = tile
        except Exception as e:
            print(f'Error {row},{col}: {e}')

print(f'Content tiles: {content_tiles}/{GRID * GRID}')

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
print(f'Saved master: {os.path.getsize(f"{OUT_DIR}/topdown_v2_master.png") / (1024*1024):.1f} MB')

# Crop to terrain
is_sky = (rgb_8[:, :, 2].astype(float) > 100) & \
         (rgb_8[:, :, 2].astype(float) > rgb_8[:, :, 0].astype(float) * 1.1) & \
         (rgb_8[:, :, 2].astype(float) > rgb_8[:, :, 1].astype(float) * 1.1)
is_terrain = ~is_sky & (rgb_8.mean(axis=2) > 10)

rows_any = np.any(is_terrain, axis=1)
cols_any = np.any(is_terrain, axis=0)
if rows_any.any() and cols_any.any():
    r1, r2 = np.where(rows_any)[0][[0, -1]]
    c1, c2 = np.where(cols_any)[0][[0, -1]]
    pad = 10
    r1 = max(0, r1 - pad)
    r2 = min(full_res, r2 + pad + 1)
    c1 = max(0, c1 - pad)
    c2 = min(full_res, c2 + pad + 1)
    cropped = rgb_8[r1:r2, c1:c2]
    is_sky_crop = is_sky[r1:r2, c1:c2]
    cropped[is_sky_crop] = [40, 35, 30]
else:
    cropped = rgb_8

crop_h, crop_w = cropped.shape[:2]
im_crop = Image.fromarray(cropped)
im_crop.save(f'{OUT_DIR}/topdown_v2_cropped.png', 'PNG')

scale = min(1024 / crop_w, 1024 / crop_h, 1.0)
pw, ph = int(crop_w * scale), int(crop_h * scale)
preview = im_crop.resize((pw, ph), Image.LANCZOS)
preview.save(f'{OUT_DIR}/topdown_v2_preview.jpg', 'JPEG', quality=93)

# Nav grayscale
gray = np.mean(cropped.astype(np.float32), axis=2)
valid = gray > 5
if valid.any():
    gmin, gmax = np.percentile(gray[valid], [1, 99])
    if gmax > gmin:
        gray = np.clip((gray - gmin) / (gmax - gmin) * 255, 0, 255).astype(np.uint8)
nav = Image.fromarray(gray, 'L')
nav.save(f'{OUT_DIR}/topdown_v2_nav.png', 'PNG')

mpp = WORLD_SIZE / 100 / full_res
print(f'\nCropped: {crop_w}x{crop_h}')
print(f'Meters per pixel: {mpp:.4f}')
for fn in ['topdown_v2_master.png', 'topdown_v2_cropped.png', 'topdown_v2_preview.jpg', 'topdown_v2_nav.png']:
    fp = f'{OUT_DIR}/{fn}'
    if os.path.exists(fp):
        print(f'{fn}: {os.path.getsize(fp) / (1024 * 1024):.1f} MB')
