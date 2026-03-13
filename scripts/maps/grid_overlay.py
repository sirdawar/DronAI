#!/usr/bin/env python3
"""Overlay UE world coordinate grid on the master map."""
import math
from PIL import Image, ImageDraw, ImageFont

MAP_PATH = '/home/davor/.openclaw/workspace-drone/output/topdown_v2_master.png'
OUT_PATH = '/home/davor/.openclaw/workspace-drone/output/topdown_v2_grid.png'

# Constants from restitch.py
WORLD_MIN = -55000
WORLD_MAX = 55000
WORLD_SIZE = WORLD_MAX - WORLD_MIN
TILE_COVER = 18000
GRID = math.ceil(WORLD_SIZE / TILE_COVER)  # 7
STEP = WORLD_SIZE / GRID
TILE_RES = 1024
crop_px = int(round((TILE_COVER - STEP) / 2 / TILE_COVER * TILE_RES))
inner = TILE_RES - 2 * crop_px  # 894
full_res = GRID * inner  # 6258

# Grid spacing in UE units (10000 = 100m)
GRID_SPACING = 10000


def world_to_pixel(wx, wy):
    """Convert UE world coords to pixel coords on the master map."""
    px_x = (wy - WORLD_MIN) / WORLD_SIZE * full_res
    px_y = (1 - (wx - WORLD_MIN) / WORLD_SIZE) * full_res
    return int(round(px_x)), int(round(px_y))


def main():
    print(f'Loading {MAP_PATH}...')
    img = Image.open(MAP_PATH).convert('RGBA')
    assert img.size == (full_res, full_res), f'Expected {full_res}x{full_res}, got {img.size}'

    # Create semi-transparent overlay for grid lines
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        font_sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    grid_color = (255, 255, 255, 80)       # semi-transparent white
    origin_color = (255, 50, 50, 160)       # semi-transparent red
    label_color = (255, 255, 200, 220)      # near-opaque cream

    # Generate grid coordinates from WORLD_MIN to WORLD_MAX at GRID_SPACING
    coords = list(range(WORLD_MIN, WORLD_MAX + 1, GRID_SPACING))

    # Draw vertical grid lines (constant UE Y values → constant pixel X)
    for wy in coords:
        px_x, _ = world_to_pixel(0, wy)
        if 0 <= px_x < full_res:
            color = origin_color if wy == 0 else grid_color
            width = 3 if wy == 0 else 1
            draw.line([(px_x, 0), (px_x, full_res)], fill=color, width=width)
            # Label at top
            meters = wy / 100
            label = f'{meters:+.0f}m' if wy != 0 else 'Y=0'
            draw.text((px_x + 4, 5), label, fill=label_color, font=font_sm)

    # Draw horizontal grid lines (constant UE X values → constant pixel Y)
    for wx in coords:
        _, px_y = world_to_pixel(wx, 0)
        if 0 <= px_y < full_res:
            color = origin_color if wx == 0 else grid_color
            width = 3 if wx == 0 else 1
            draw.line([(0, px_y), (full_res, px_y)], fill=color, width=width)
            # Label at left
            meters = wx / 100
            label = f'{meters:+.0f}m' if wx != 0 else 'X=0'
            draw.text((5, px_y + 4), label, fill=label_color, font=font_sm)

    # Mark origin with a crosshair
    ox, oy = world_to_pixel(0, 0)
    r = 25
    draw.ellipse([(ox - r, oy - r), (ox + r, oy + r)], outline=(255, 50, 50, 200), width=3)
    draw.text((ox + r + 8, oy - 15), 'ORIGIN', fill=(255, 80, 80, 240), font=font)

    # Axis labels in corners
    draw.text((full_res // 2 - 80, 50), 'UE +X', fill=(255, 200, 50, 220), font=font)
    draw.text((full_res // 2 - 80, full_res - 80), 'UE -X', fill=(255, 200, 50, 220), font=font)
    draw.text((full_res - 180, full_res // 2 - 15), 'UE +Y', fill=(255, 200, 50, 220), font=font)
    draw.text((10, full_res // 2 - 15), 'UE -Y', fill=(255, 200, 50, 220), font=font)

    # Composite
    result = Image.alpha_composite(img, overlay).convert('RGB')
    result.save(OUT_PATH, 'PNG')
    print(f'Saved: {OUT_PATH}')
    print(f'Grid spacing: {GRID_SPACING} UE units = {GRID_SPACING/100:.0f}m')
    print(f'Grid lines: {len(coords)} per axis')
    print(f'Origin at pixel: ({ox}, {oy})')


if __name__ == '__main__':
    main()
