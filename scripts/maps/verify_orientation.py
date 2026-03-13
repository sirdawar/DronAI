#!/usr/bin/env python3
"""Verify map orientation by marking the UE origin (drone spawn point) and cardinal directions."""
import math
from PIL import Image, ImageDraw, ImageFont

MAP_PATH = '/home/davor/.openclaw/workspace-drone/output/topdown_v2_master.png'
OUT_PATH = '/home/davor/.openclaw/workspace-drone/output/topdown_v2_verify.png'

# Constants from restitch.py
WORLD_MIN = -55000
WORLD_MAX = 55000
WORLD_SIZE = WORLD_MAX - WORLD_MIN
TILE_COVER = 18000
CAM_Z = 100000
GRID = math.ceil(WORLD_SIZE / TILE_COVER)  # 7
STEP = WORLD_SIZE / GRID
TILE_RES = 1024
crop_px = int(round((TILE_COVER - STEP) / 2 / TILE_COVER * TILE_RES))
inner = TILE_RES - 2 * crop_px  # 894
full_res = GRID * inner  # 6258


def world_to_pixel(wx, wy):
    """Convert UE world coords (wx=X, wy=Y) to pixel coords on the master map.

    From restitch.py placement logic:
    - Tile (row, col) has UE center: cx = f(col), cy = f(row)
    - Canvas placement: x_start = row * inner, y_start = (GRID-1-col) * inner
    - So UE Y (cy, varies with row) maps to pixel X
    - And UE X (cx, varies with col) maps to pixel Y (inverted)
    """
    px_x = (wy - WORLD_MIN) / WORLD_SIZE * full_res
    px_y = (1 - (wx - WORLD_MIN) / WORLD_SIZE) * full_res
    return int(round(px_x)), int(round(px_y))


def main():
    print(f'Loading {MAP_PATH}...')
    img = Image.open(MAP_PATH).convert('RGB')
    assert img.size == (full_res, full_res), f'Expected {full_res}x{full_res}, got {img.size}'

    draw = ImageDraw.Draw(img)

    # Try to get a reasonable font
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
        font_sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    # Mark origin (0, 0) — drone spawn point
    ox, oy = world_to_pixel(0, 0)
    print(f'Origin (0,0) -> pixel ({ox}, {oy})')
    cross_size = 80
    line_w = 4

    # Crosshair
    draw.line([(ox - cross_size, oy), (ox + cross_size, oy)], fill='red', width=line_w)
    draw.line([(ox, oy - cross_size), (ox, oy + cross_size)], fill='red', width=line_w)
    # Circle
    r = 30
    draw.ellipse([(ox - r, oy - r), (ox + r, oy + r)], outline='red', width=line_w)
    # Label
    draw.text((ox + cross_size + 10, oy - 20), 'ORIGIN (0,0)', fill='red', font=font_sm)
    draw.text((ox + cross_size + 10, oy + 15), 'Drone Spawn', fill='yellow', font=font_sm)

    # Mark some reference points for orientation check
    ref_points = [
        (20000, 0, '+200m X, 0'),
        (-20000, 0, '-200m X, 0'),
        (0, 20000, '0, +200m Y'),
        (0, -20000, '0, -200m Y'),
    ]
    for wx, wy, label in ref_points:
        px, py = world_to_pixel(wx, wy)
        draw.ellipse([(px - 15, py - 15), (px + 15, py + 15)], outline='cyan', width=3)
        draw.text((px + 20, py - 12), label, fill='cyan', font=font_sm)

    # Cardinal direction labels at map edges
    # In UE: X = forward (typically "North" in game), Y = right (typically "East")
    # On our map: UE +X maps to pixel Y decreasing (top), UE +Y maps to pixel X increasing (right)
    margin = 20
    cx, cy = full_res // 2, full_res // 2

    labels = [
        (cx, margin + 30, '+X (UE Forward)'),           # top center
        (cx, full_res - margin - 30, '-X (UE Back)'),    # bottom center
        (full_res - margin - 10, cy, '+Y (UE Right)'),   # right center
        (margin + 10, cy, '-Y (UE Left)'),                # left center
    ]
    for lx, ly, text in labels:
        # Center text approximately
        draw.text((lx - 100, ly - 15), text, fill='yellow', font=font)

    # Draw thin axis lines through origin
    draw.line([(0, oy), (full_res, oy)], fill=(255, 255, 0, 128), width=2)
    draw.line([(ox, 0), (ox, full_res)], fill=(255, 255, 0, 128), width=2)

    # Info box
    info = [
        f'Map: {full_res}x{full_res}px',
        f'World: {WORLD_MIN/100:.0f}m to {WORLD_MAX/100:.0f}m',
        f'Meters/pixel: {WORLD_SIZE/100/full_res:.4f}',
        f'Origin pixel: ({ox}, {oy})',
    ]
    y_off = full_res - 200
    for line in info:
        draw.text((30, y_off), line, fill='white', font=font_sm)
        y_off += 40

    img.save(OUT_PATH, 'PNG')
    print(f'Saved: {OUT_PATH}')
    print(f'\nVerification checklist:')
    print(f'  1. Red crosshair at ({ox},{oy}) should be on/near the drone landing pad')
    print(f'  2. +X label at top, -X at bottom (UE forward direction)')
    print(f'  3. +Y label at right, -Y at left (UE right direction)')
    print(f'  4. Roads should run in visually correct directions')


if __name__ == '__main__':
    main()
