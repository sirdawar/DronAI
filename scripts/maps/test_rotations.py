#!/usr/bin/env python3
"""
Re-stitch existing tiles with 4 rotation variants (k=0,1,2,3)
to find which rotation makes roads connect across tile boundaries.
No UE capture needed — uses cached EXR tiles.
"""
import os, numpy as np, OpenEXR, Imath
from PIL import Image

TILE_DIR = '/home/davor/.openclaw/workspace-drone/output/final_tiles_v2'
OUT_DIR = '/home/davor/.openclaw/workspace-drone/output/rotation_test'
os.makedirs(OUT_DIR, exist_ok=True)

GRID = 7
TILE_RES = 1024
FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

# Load all tiles once
tiles = {}
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
            tiles[(row, col)] = np.stack([r, g, b], axis=2)
        except Exception as e:
            print(f'Error loading {row},{col}: {e}')

print(f'Loaded {len(tiles)} tiles')

full_res = GRID * TILE_RES

for k in range(4):
    print(f'Stitching rotation k={k} ({k*90}° CCW)...')
    canvas = np.zeros((full_res, full_res, 3), dtype=np.float32)

    for (row, col), tile in tiles.items():
        rotated = np.rot90(tile, k=k)
        y_start = (GRID - 1 - row) * TILE_RES
        x_start = col * TILE_RES
        canvas[y_start:y_start + TILE_RES, x_start:x_start + TILE_RES] = rotated

    # Tone map
    canvas = np.clip(canvas, 0, None)
    if canvas.max() > 1.5:
        canvas = canvas / (1 + canvas)
    canvas = np.clip(canvas, 0, 1)
    rgb = (canvas * 255).astype(np.uint8)

    # Save 1024px preview (enough to see road continuity)
    im = Image.fromarray(rgb)
    preview = im.resize((1024, 1024), Image.LANCZOS)
    out_path = f'{OUT_DIR}/rot_k{k}_{k*90}deg.jpg'
    preview.save(out_path, 'JPEG', quality=93)
    print(f'  -> {out_path} ({os.path.getsize(out_path) // 1024} KB)')

print(f'\nDone. Compare the 4 images in {OUT_DIR}/')
