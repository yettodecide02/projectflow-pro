#!/usr/bin/env python3
"""
Generate PWA icons for ProjectFlow Pro.
Uses only Python stdlib (no Pillow needed).
Outputs valid PNG files with the PF logo.
"""

import os
import struct
import zlib

def make_png(size):
    """Generate a PNG icon with a gradient background and 'PF' text rendered as pixels."""
    width = height = size

    # Colors
    bg1 = (79, 142, 247)   # accent blue
    bg2 = (139, 92, 246)   # purple
    text_color = (255, 255, 255)

    # Build pixel data
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            # Gradient: top-left blue → bottom-right purple
            t = (x + y) / (width + height)
            r = int(bg1[0] + (bg2[0] - bg1[0]) * t)
            g = int(bg1[1] + (bg2[1] - bg1[1]) * t)
            b = int(bg1[2] + (bg2[2] - bg1[2]) * t)

            # Rounded rect mask (rounded corners)
            radius = size * 0.22
            cx, cy = width / 2, height / 2
            dx = abs(x - cx) - (width / 2 - radius)
            dy = abs(y - cy) - (height / 2 - radius)
            if dx > 0 and dy > 0 and (dx * dx + dy * dy) > radius * radius:
                row.extend([0, 0, 0, 0])  # transparent outside
            else:
                row.extend([r, g, b, 255])
        pixels.append(row)

    # Draw "PF" using a simple pixel font scaled to icon size
    scale = max(1, size // 48)
    font_P = [
        [1,1,1,0],
        [1,0,0,1],
        [1,1,1,0],
        [1,0,0,0],
        [1,0,0,0],
    ]
    font_F = [
        [1,1,1,1],
        [1,0,0,0],
        [1,1,1,0],
        [1,0,0,0],
        [1,0,0,0],
    ]

    char_w = 4 * scale
    char_h = 5 * scale
    gap = 1 * scale
    total_w = char_w * 2 + gap
    total_h = char_h
    start_x = (width - total_w) // 2
    start_y = (height - total_h) // 2

    def draw_char(font, ox, oy):
        for fy, row in enumerate(font):
            for fx, pixel in enumerate(row):
                if pixel:
                    for sy in range(scale):
                        for sx in range(scale):
                            px = ox + fx * scale + sx
                            py = oy + fy * scale + sy
                            if 0 <= px < width and 0 <= py < height:
                                base = py * (width * 4) + px * 4
                                # flat index into pixels list
                                pixels[py][px * 4] = text_color[0]
                                pixels[py][px * 4 + 1] = text_color[1]
                                pixels[py][px * 4 + 2] = text_color[2]
                                pixels[py][px * 4 + 3] = 255

    # Adjust pixel addressing (row is a flat list per row)
    # Redo pixel storage as list of lists of RGBA tuples
    px_grid = []
    for y in range(height):
        row = []
        for x in range(width):
            t = (x + y) / (width + height)
            r = int(bg1[0] + (bg2[0] - bg1[0]) * t)
            g = int(bg1[1] + (bg2[1] - bg1[1]) * t)
            b = int(bg1[2] + (bg2[2] - bg1[2]) * t)

            radius = size * 0.22
            cx2, cy2 = width / 2, height / 2
            dx2 = abs(x - cx2) - (width / 2 - radius)
            dy2 = abs(y - cy2) - (height / 2 - radius)
            if dx2 > 0 and dy2 > 0 and (dx2 * dx2 + dy2 * dy2) > radius * radius:
                row.append((0, 0, 0, 0))
            else:
                row.append((r, g, b, 255))
        px_grid.append(row)

    def draw_char2(font, ox, oy):
        for fy, frow in enumerate(font):
            for fx, pixel in enumerate(frow):
                if pixel:
                    for sy in range(scale):
                        for sx in range(scale):
                            px2 = ox + fx * scale + sx
                            py2 = oy + fy * scale + sy
                            if 0 <= px2 < width and 0 <= py2 < height:
                                px_grid[py2][px2] = (*text_color, 255)

    draw_char2(font_P, start_x, start_y)
    draw_char2(font_F, start_x + char_w + gap, start_y)

    # Encode PNG
    def encode_png(grid, w, h):
        def make_chunk(chunk_type, data):
            c = chunk_type + data
            return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

        sig = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)  # 8-bit RGBA
        ihdr = make_chunk(b'IHDR', ihdr_data)

        raw = b''
        for row in grid:
            raw += b'\x00'  # filter type None
            for px in row:
                raw += bytes(px)

        idat = make_chunk(b'IDAT', zlib.compress(raw, 9))
        iend = make_chunk(b'IEND', b'')
        return sig + ihdr + idat + iend

    return encode_png(px_grid, width, height)


sizes = [72, 96, 128, 144, 152, 192, 384, 512]
out_dir = os.path.join(os.path.dirname(__file__), 'icons')
os.makedirs(out_dir, exist_ok=True)

for s in sizes:
    data = make_png(s)
    path = os.path.join(out_dir, f'icon-{s}.png')
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Generated {path} ({len(data)} bytes)')

print('All icons generated!')
