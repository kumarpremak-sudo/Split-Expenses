"""Generate PWA icon PNG files from the SVG source."""
import struct
import zlib
import os


def create_png_icon(width, height, output_path):
    """
    Create a simple PNG icon with the app's brand colors.
    Dark navy background with a teal currency symbol.
    """
    bg_r, bg_g, bg_b = 15, 23, 42
    teal_r, teal_g, teal_b = 20, 184, 166
    amber_r, amber_g, amber_b = 245, 158, 11

    pixels = []
    cx, cy = width // 2, height // 2
    radius = int(min(width, height) * 0.35)

    for y in range(height):
        row = [0]
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = (dx * dx + dy * dy) ** 0.5

            ring_outer = radius
            ring_inner = radius * 0.78
            ring_width = (ring_outer - ring_inner)

            if ring_inner <= dist <= ring_outer:
                row.extend([teal_r, teal_g, teal_b, 255])
            elif dist < ring_inner:
                sym_cx = cx
                sym_top = cy - int(radius * 0.5)
                sym_bot = cy + int(radius * 0.5)
                sym_w = int(radius * 0.3)

                in_vertical = (sym_cx - 3 <= x <= sym_cx + 3) and (sym_top <= y <= sym_bot)
                in_top_h = (sym_cx - sym_w <= x <= sym_cx + sym_w) and (sym_top - 2 <= y <= sym_top + 6)
                in_mid_h = (sym_cx - sym_w <= x <= sym_cx + sym_w) and (cy - 4 <= y <= cy + 4)
                in_bot_h = (sym_cx - sym_w <= x <= sym_cx + sym_w) and (sym_bot - 6 <= y <= sym_bot + 2)

                curve_y_start = cy
                curve_y_end = sym_bot - 6
                if curve_y_start <= y <= curve_y_end and sym_cx + 3 < x <= sym_cx + sym_w:
                    progress = (y - curve_y_start) / max(1, curve_y_end - curve_y_start)
                    curve_x = sym_cx + 3 + progress * (sym_w - 3)
                    if abs(x - curve_x) < 5:
                        row.extend([amber_r, amber_g, amber_b, 255])
                        continue

                if in_vertical or in_top_h or in_mid_h or in_bot_h:
                    row.extend([teal_r, teal_g, teal_b, 255])
                else:
                    row.extend([bg_r, bg_g, bg_b, 255])
            else:
                row.extend([bg_r, bg_g, bg_b, 255])

        pixels.append(bytes(row))

    raw_data = b''.join(pixels)

    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

    signature = b'\x89PNG\r\n\x1a\n'

    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)

    compressed = zlib.compress(raw_data, 9)
    idat = make_chunk(b'IDAT', compressed)

    iend = make_chunk(b'IEND', b'')

    with open(output_path, 'wb') as f:
        f.write(signature + ihdr + idat + iend)

    print(f"Created {output_path} ({width}x{height})")


if __name__ == '__main__':
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    create_png_icon(192, 192, os.path.join(icons_dir, 'icon-192.png'))
    create_png_icon(512, 512, os.path.join(icons_dir, 'icon-512.png'))

    print("Done!")
