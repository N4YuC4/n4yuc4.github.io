#!/usr/bin/env python3
"""Pure-PIL rasterizer for the N4YuC4 mark (no cairo dependency)."""
from PIL import Image, ImageDraw

INK_DARK_BG = "#EDF2F7"
INK_LIGHT_BG = "#0D0D0D"
ACCENT_A = (0x00, 0x7C, 0xF0)
ACCENT_B = (0x00, 0xD4, 0xFF)
BG_TILE = "#0D0D0D"

TL = (148, 136)
BL = (148, 376)
TR = (364, 136)
BR = (364, 376)


def _lerp(c1, c2, t):
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def draw_mark(size, ink, accent="gradient", bg=None, bold=False,
              tile_rx=112, ss=4):
    """Render the mark at `size` px. accent: 'gradient' | hex string."""
    SW, R, RA = (56, 55, 60) if bold else (36, 40, 47)
    S = size * ss
    k = S / 512.0
    ink_rgb = _hex2rgb(ink)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if bg:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=tile_rx * k,
                            fill=_hex2rgb(bg) + (255,))

    def line(p1, p2, color, width):
        d.line([p1[0] * k, p1[1] * k, p2[0] * k, p2[1] * k],
               fill=color + (255,), width=round(width * k))

    def dot(p, r, color):
        d.ellipse([ (p[0] - r) * k, (p[1] - r) * k,
                    (p[0] + r) * k, (p[1] + r) * k], fill=color + (255,))

    # vertical edges
    line(TL, BL, ink_rgb, SW)
    line(TR, BR, ink_rgb, SW)
    # round caps for verticals (mostly hidden under nodes)
    for p in (TL, BL, TR, BR):
        dot(p, SW / 2, ink_rgb)

    # diagonal edge
    if accent == "gradient":
        n = 240
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            p0 = (TL[0] + (BR[0] - TL[0]) * t0, TL[1] + (BR[1] - TL[1]) * t0)
            p1 = (TL[0] + (BR[0] - TL[0]) * t1, TL[1] + (BR[1] - TL[1]) * t1)
            col = _lerp(ACCENT_A, ACCENT_B, (t0 + t1) / 2)
            line(p0, p1, col, SW)
            dot(p0, SW / 2, col)
        dot(BR, SW / 2, ACCENT_B)
        accent_rgb = None
    else:
        line(TL, BR, ink_rgb, SW)
        accent_rgb = _hex2rgb(accent)

    # nodes
    dot(TL, R, ink_rgb)
    dot(BL, R, ink_rgb)
    dot(TR, R, ink_rgb)
    if accent == "gradient":
        # gradient-filled activated node: approximate with radial blend of end colour
        dot(BR, RA, ACCENT_B)
    else:
        dot(BR, RA, accent_rgb)

    return img.resize((size, size), Image.LANCZOS)
