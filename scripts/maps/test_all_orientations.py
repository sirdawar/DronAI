#!/usr/bin/env python3
"""
Test all 8 possible tile orientations (4 rotations × 2 flip states)
and also test swapping row/col in grid placement.
Generates 16 variants total.
"""
import os, numpy as np, OpenEXR, Imath
from PIL import Image

TILE_DIR = '/home/davor/.openclaw/workspace-drone/output/final_tiles_v2'
OUT_DIR = '/home/davor/.openclaw/workspace-drone/output/orientation_test'
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


def tone_map(canvas):
    canvas = np.clip(canvas, 0, None)
    if canvas.max() > 1.5:
        canvas = canvas / (1 + canvas)
    canvas = np.clip(canvas, 0, 1)
    return (canvas * 255).astype(np.uint8)


def stitch(transform_fn, swap_rc=False):
    """Stitch tiles with a given per-tile transform and optional row/col swap in placement."""
    canvas = np.zeros((full_res, full_res, 3), dtype=np.float32)
    for (row, col), tile in tiles.items():
        t = transform_fn(tile)
        if swap_rc:
            # Swap which grid position this tile is placed at
            y_start = (GRID - 1 - col) * TILE_RES
            x_start = row * TILE_RES
        else:
            y_start = (GRID - 1 - row) * TILE_RES
            x_start = col * TILE_RES
        canvas[y_start:y_start + TILE_RES, x_start:x_start + TILE_RES] = t
    return tone_map(canvas)


transforms = {
    'k0':        lambda t: t,
    'k1':        lambda t: np.rot90(t, 1),
    'k2':        lambda t: np.rot90(t, 2),
    'k3':        lambda t: np.rot90(t, 3),
    'k0_flipH':  lambda t: np.fliplr(t),
    'k1_flipH':  lambda t: np.fliplr(np.rot90(t, 1)),
    'k2_flipH':  lambda t: np.fliplr(np.rot90(t, 2)),
    'k3_flipH':  lambda t: np.fliplr(np.rot90(t, 3)),
    'k0_flipV':  lambda t: np.flipud(t),
    'k1_flipV':  lambda t: np.flipud(np.rot90(t, 1)),
    'k2_flipV':  lambda t: np.flipud(np.rot90(t, 2)),
    'k3_flipV':  lambda t: np.flipud(np.rot90(t, 3)),
}

# Also test with row/col swap for the most promising rotations
swap_variants = {
    'k0_swap':   lambda t: t,
    'k1_swap':   lambda t: np.rot90(t, 1),
    'k2_swap':   lambda t: np.rot90(t, 2),
    'k3_swap':   lambda t: np.rot90(t, 3),
}

for name, fn in transforms.items():
    print(f'Stitching {name}...')
    rgb = stitch(fn, swap_rc=False)
    im = Image.fromarray(rgb)
    preview = im.resize((1024, 1024), Image.LANCZOS)
    preview.save(f'{OUT_DIR}/{name}.jpg', 'JPEG', quality=93)

for name, fn in swap_variants.items():
    print(f'Stitching {name}...')
    rgb = stitch(fn, swap_rc=True)
    im = Image.fromarray(rgb)
    preview = im.resize((1024, 1024), Image.LANCZOS)
    preview.save(f'{OUT_DIR}/{name}.jpg', 'JPEG', quality=93)

print(f'\nDone — {len(transforms) + len(swap_variants)} variants in {OUT_DIR}/')
