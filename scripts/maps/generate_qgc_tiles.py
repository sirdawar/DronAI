#!/usr/bin/env python3
"""Generate XYZ/slippy map tiles from the UE5 master map for QGroundControl."""
import math
import os
import sys
from PIL import Image

# --- Coordinate constants (from grid_overlay.py / restitch.py) ---
WORLD_MIN = -55000   # UE centimeters
WORLD_MAX = 55000
WORLD_SIZE = WORLD_MAX - WORLD_MIN  # 110000 cm = 1100 m
TILE_COVER = 18000
GRID = math.ceil(WORLD_SIZE / TILE_COVER)  # 7
STEP = WORLD_SIZE / GRID
TILE_RES = 1024
crop_px = int(round((TILE_COVER - STEP) / 2 / TILE_COVER * TILE_RES))
inner = TILE_RES - 2 * crop_px  # 894
full_res = GRID * inner  # 6258

# --- Geo-reference ---
HOME_LAT = 47.641468
HOME_LON = -122.140165
# Meters per degree at this latitude
M_PER_DEG_LAT = 111320.0
M_PER_DEG_LON = 111320.0 * math.cos(math.radians(HOME_LAT))  # ~75004

# --- Paths ---
MAP_PATH = '/home/davor/.openclaw/workspace-drone/output/topdown_v2_master.png'
OUT_DIR = '/home/davor/.openclaw/workspace-drone/output/qgc_tiles'

ZOOM_MIN = 15
ZOOM_MAX = 20
TILE_SIZE = 256


def latlon_to_world(lat, lon):
    """Convert lat/lon to UE world coordinates (centimeters)."""
    wx = (lat - HOME_LAT) * M_PER_DEG_LAT * 100.0  # UE +X = North
    wy = (lon - HOME_LON) * M_PER_DEG_LON * 100.0  # UE +Y = East
    return wx, wy


def world_to_pixel(wx, wy):
    """Convert UE world coords to pixel coords on the master map."""
    px_x = (wy - WORLD_MIN) / WORLD_SIZE * full_res
    px_y = (1 - (wx - WORLD_MIN) / WORLD_SIZE) * full_res
    return px_x, px_y


def latlon_to_pixel(lat, lon):
    """Convert lat/lon directly to pixel coords on master map."""
    wx, wy = latlon_to_world(lat, lon)
    return world_to_pixel(wx, wy)


def tile_bounds(z, x, y):
    """Return (north_lat, south_lat, west_lon, east_lon) for tile (z, x, y)."""
    n = 2 ** z
    west = x / n * 360.0 - 180.0
    east = (x + 1) / n * 360.0 - 180.0
    north = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    south = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return north, south, west, east


def latlon_to_tile(lat, lon, z):
    """Convert lat/lon to tile x, y at zoom z."""
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def get_tile_range(z):
    """Get min/max tile x, y that cover the map area at zoom z."""
    # Bounding box of the UE world in lat/lon
    half_m = WORLD_SIZE / 2.0 / 100.0  # 550 m
    north = HOME_LAT + half_m / M_PER_DEG_LAT
    south = HOME_LAT - half_m / M_PER_DEG_LAT
    east = HOME_LON + half_m / M_PER_DEG_LON
    west = HOME_LON - half_m / M_PER_DEG_LON

    x_min, y_min = latlon_to_tile(north, west, z)
    x_max, y_max = latlon_to_tile(south, east, z)
    return x_min, x_max, y_min, y_max


def generate_tiles(master_img):
    """Generate all tiles for zoom levels ZOOM_MIN to ZOOM_MAX."""
    total = 0
    for z in range(ZOOM_MIN, ZOOM_MAX + 1):
        x_min, x_max, y_min, y_max = get_tile_range(z)
        count = (x_max - x_min + 1) * (y_max - y_min + 1)
        total += count
        print(f'  z={z}: tiles x=[{x_min}..{x_max}] y=[{y_min}..{y_max}] → {count} tiles')

    print(f'Total tiles to generate: {total}')
    generated = 0

    for z in range(ZOOM_MIN, ZOOM_MAX + 1):
        x_min, x_max, y_min, y_max = get_tile_range(z)

        for tx in range(x_min, x_max + 1):
            for ty in range(y_min, y_max + 1):
                north, south, west, east = tile_bounds(z, tx, ty)

                # Convert tile corners to pixel coords on master map
                px_left, px_top = latlon_to_pixel(north, west)
                px_right, px_bottom = latlon_to_pixel(south, east)

                # Ensure correct ordering (left < right, top < bottom)
                if px_left > px_right:
                    px_left, px_right = px_right, px_left
                if px_top > px_bottom:
                    px_top, px_bottom = px_bottom, px_top

                # Crop region on master map (may extend beyond image bounds)
                src_width = px_right - px_left
                src_height = px_bottom - px_top

                if src_width < 1 or src_height < 1:
                    continue

                # Create tile with transparent background for areas outside map
                tile = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))

                # Calculate overlap between tile region and master map
                clip_left = max(0, px_left)
                clip_top = max(0, px_top)
                clip_right = min(full_res, px_right)
                clip_bottom = min(full_res, px_bottom)

                if clip_left >= clip_right or clip_top >= clip_bottom:
                    # Tile is entirely outside master map — skip
                    continue

                # Crop from master
                crop = master_img.crop((
                    int(clip_left), int(clip_top),
                    int(clip_right), int(clip_bottom)
                ))

                # Scale crop to tile size, accounting for partial overlap
                # Where does the clipped region sit within the full tile?
                dest_left = (clip_left - px_left) / src_width * TILE_SIZE
                dest_top = (clip_top - px_top) / src_height * TILE_SIZE
                dest_right = (clip_right - px_left) / src_width * TILE_SIZE
                dest_bottom = (clip_bottom - px_top) / src_height * TILE_SIZE

                dest_w = int(round(dest_right - dest_left))
                dest_h = int(round(dest_bottom - dest_top))
                if dest_w < 1 or dest_h < 1:
                    continue

                crop_resized = crop.resize((dest_w, dest_h), Image.LANCZOS)
                tile.paste(crop_resized, (int(round(dest_left)), int(round(dest_top))))

                # Save tile
                tile_dir = os.path.join(OUT_DIR, str(z), str(tx))
                os.makedirs(tile_dir, exist_ok=True)
                tile_path = os.path.join(tile_dir, f'{ty}.png')
                tile.save(tile_path, 'PNG')
                generated += 1

        print(f'  z={z} done ({generated} tiles so far)')

    return generated


def main():
    print(f'Loading master map: {MAP_PATH}')
    master = Image.open(MAP_PATH).convert('RGBA')
    assert master.size == (full_res, full_res), f'Expected {full_res}x{full_res}, got {master.size}'
    print(f'Master map: {full_res}x{full_res}')
    print(f'Home: {HOME_LAT}, {HOME_LON}')
    print(f'Resolution: {M_PER_DEG_LAT:.0f} m/deg lat, {M_PER_DEG_LON:.0f} m/deg lon')
    print(f'Generating tiles for zoom {ZOOM_MIN}-{ZOOM_MAX}...')

    count = generate_tiles(master)
    print(f'\nDone! Generated {count} tiles in {OUT_DIR}')

    # Print a sample center tile URL for verification
    cx, cy = latlon_to_tile(HOME_LAT, HOME_LON, 17)
    print(f'Center tile at z=17: http://localhost:8844/17/{cx}/{cy}.png')


if __name__ == '__main__':
    main()
