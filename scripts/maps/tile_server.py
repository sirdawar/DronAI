#!/usr/bin/env python3
"""Minimal tile server for QGroundControl custom map tiles.

Serves XYZ tiles from the qgc_tiles directory on port 8844.
URL pattern: http://localhost:8844/{z}/{x}/{y}.png
"""
import http.server
import os
import sys

PORT = 8844
TILE_DIR = '/home/davor/.openclaw/workspace-drone/output/qgc_tiles'


class TileHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=TILE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Only log errors, not every request
        if '404' in str(args) or '500' in str(args):
            super().log_message(format, *args)

    def end_headers(self):
        # Allow QGC to fetch tiles without CORS issues
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def main():
    if not os.path.isdir(TILE_DIR):
        print(f'ERROR: Tile directory not found: {TILE_DIR}')
        print('Run generate_qgc_tiles.py first.')
        sys.exit(1)

    server = http.server.HTTPServer(('0.0.0.0', PORT), TileHandler)
    print(f'Tile server running on http://localhost:{PORT}/')
    print(f'Serving tiles from: {TILE_DIR}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        server.shutdown()


if __name__ == '__main__':
    main()
