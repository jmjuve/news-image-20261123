#!/usr/bin/env python3
"""news-image-20261123 — front page for Monday 23 November 2026.

Pure-stdlib program: draws a 1024x1024 newsprint front page and writes it
to $MAKEFUN_OUTPUT_DIR/entry.png (repo out/ only as a local fallback).
Deterministic: no time, no randomness, no network, no external files.

Hero: Nepal PM Balendra Shah meets PM Modi in Delhi (23 Nov 2026).
Minis: Molly Meldrum dies aged 83; Wellington Test final day;
Canberra's last sitting week of 2026.
"""

import hashlib
import os
import struct
import sys
import zlib

W = 1024
H = 1024

CREAM = (246, 239, 220)     # newsprint background
PANEL = (252, 246, 227)     # hero panel fill
MINI = (255, 253, 244)      # mini panel fill
INK = (26, 26, 26)          # near-black type and line work
RED = (183, 28, 28)         # single red accent, lead story only
GOLD = (212, 175, 55)       # small sun
PITCH = (122, 155, 90)      # cricket pitch green
SAFFRON = (255, 153, 51)
LEAF = (19, 136, 8)
NAVY = (0, 0, 128)
CRIMSON = (220, 20, 60)     # Nepal flag crimson
TABLE = (96, 68, 48)
TABLETOP = (140, 102, 66)
FLAGBLUE = (0, 47, 108)     # small Australian flag blue

# ---------------------------------------------------------------- font
# Hand-built 5x7 capital font. "#" is a filled pixel.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


# ------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.buf = bytearray(CREAM * (W * H))

    def fill_rect(self, x, y, w, h, col):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * W + x0) * 3
            self.buf[off:off + len(row)] = row

    def rect(self, x, y, w, h, col, t=1):
        self.fill_rect(x, y, w, t, col)
        self.fill_rect(x, y + h - t, w, t, col)
        self.fill_rect(x, y, t, h, col)
        self.fill_rect(x + w - t, y, t, h, col)

    def line(self, x0, y0, x1, y1, col, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, col, ylo=None, yhi=None):
        for dy in range(-r, r + 1):
            y = cy + dy
            if ylo is not None and y < ylo:
                continue
            if yhi is not None and y > yhi:
                continue
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, y, 2 * dx + 1, 1, col)

    def ellipse(self, cx, cy, rx, ry, col):
        for dy in range(-ry, ry + 1):
            y = cy + dy
            dx = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5)
            self.fill_rect(cx - dx, y, 2 * dx + 1, 1, col)

    def triangle(self, x0, y0, x1, y1, x2, y2, col):
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts

        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return float(xa)
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(ay, cy + 1):
            if y < by:
                xa = edge_x(ax, ay, bx, by, y)
                xb = edge_x(ax, ay, cx, cy, y)
            else:
                xa = edge_x(bx, by, cx, cy, y)
                xb = edge_x(ax, ay, cx, cy, y)
            lo = int(min(xa, xb))
            hi = int(max(xa, xb))
            self.fill_rect(lo, y, hi - lo + 1, 1, col)

    def text(self, x, y, s, scale, col, align="left"):
        s = s.upper().replace("\u2014", "-").replace("\u2013", "-")
        s = s.replace("\u2019", "'")
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for r, row in enumerate(glyph):
                for cc, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cx + cc * scale, y + r * scale,
                                       scale, scale, col)
            cx += 6 * scale


# ------------------------------------------------------------- the page
def draw_masthead(c):
    c.text(512, 30, "MONDAY 23 NOVEMBER 2026", 5, INK, align="center")
    c.fill_rect(24, 92, 976, 5, RED)
    c.fill_rect(24, 101, 976, 2, INK)


def draw_india_gate(c):
    # Flat ink silhouette of India Gate, raised so the two seated
    # figures in front of it stay visible.
    c.fill_rect(468, 240, 24, 128, INK)          # left pillar
    c.fill_rect(532, 240, 24, 128, INK)          # right pillar
    c.fill_rect(456, 228, 112, 14, INK)          # lintel
    c.disc(512, 240, 44, INK, yhi=240)           # arch dome
    c.disc(512, 240, 26, PANEL, yhi=240)         # arch opening
    c.disc(512, 190, 14, INK)                    # small dome on top
    c.fill_rect(506, 198, 12, 32, INK)           # dome base


def draw_nepal_flag(c, px, py):
    # Crimson double-pennon flag on a pole at (px, py) top.
    c.line(px, py, px, 428, INK, 4)
    c.triangle(px + 2, py + 8, px + 2, py + 48, px + 62, py + 28, CRIMSON)
    c.triangle(px + 2, py + 50, px + 2, py + 90, px + 46, py + 70, CRIMSON)
    c.disc(px + 16, py + 26, 5, (255, 255, 255))


def draw_india_flag(c, px, py):
    # Tricolour on a pole at (px, py) top; flag extends left of pole.
    c.line(px, py, px, 428, INK, 4)
    c.fill_rect(px - 92, py + 8, 90, 20, SAFFRON)
    c.fill_rect(px - 92, py + 28, 90, 20, (255, 255, 255))
    c.fill_rect(px - 92, py + 48, 90, 20, LEAF)
    c.disc(px - 47, py + 38, 9, NAVY)
    c.disc(px - 47, py + 38, 5, (255, 255, 255))


def draw_hero(c):
    c.fill_rect(24, 118, 976, 530, PANEL)
    c.rect(24, 118, 976, 530, INK, 3)
    # Sun, pale gold, top right of the scene.
    c.disc(880, 180, 26, GOLD)
    draw_india_gate(c)
    draw_nepal_flag(c, 150, 190)
    draw_india_flag(c, 874, 190)
    # Ground line.
    c.fill_rect(40, 428, 944, 3, INK)
    # Two seated figures at the meeting table.
    for fx in (440, 584):
        c.disc(fx, 352, 17, INK)                 # head
        c.fill_rect(fx - 32, 372, 64, 46, INK)   # shoulders
    # Meeting table with two microphones.
    c.fill_rect(392, 388, 240, 10, TABLETOP)
    c.fill_rect(400, 398, 224, 30, TABLE)
    for mx in (470, 554):
        c.line(mx, 388, mx, 372, INK, 3)
        c.disc(mx, 368, 6, INK)
    # Headline: the red accent, huge type.
    c.text(512, 448, "SHAH MEETS", 10, RED, align="center")
    c.text(512, 528, "MODI IN DELHI", 10, RED, align="center")
    # Subline: what the talks are about, nothing invented.
    c.text(512, 608, "NEPAL'S FIRST BILATERAL VISIT - ENERGY, TRADE",
           2, INK, align="center")
    c.text(512, 626, "AND CONNECTIVITY TALKS - JOINT PRESS CONFERENCE",
           2, INK, align="center")


def draw_mini_obituary(c, x0):
    cx = x0 + 158
    c.text(cx, 680, "OBITUARY", 2, INK, align="center")
    # Stetson hat, centred on the panel.
    c.triangle(cx - 32, 780, cx - 24, 732, cx + 24, 732, INK)
    c.triangle(cx + 32, 780, cx + 24, 732, cx - 24, 732, INK)
    c.ellipse(cx, 780, 78, 14, INK)
    c.fill_rect(cx - 24, 758, 48, 8, CREAM)
    # Microphone, right of the hat: solid head with grille lines.
    c.disc(cx + 96, 745, 16, INK)
    c.fill_rect(cx + 83, 739, 26, 3, MINI)
    c.fill_rect(cx + 83, 749, 26, 3, MINI)
    c.fill_rect(cx + 90, 760, 12, 52, INK)
    c.text(cx, 840, "MOLLY MELDRUM", 3, INK, align="center")
    c.text(cx, 868, "DIES, 83", 3, INK, align="center")
    c.text(cx, 906, "COUNTDOWN HOST 1943-2026", 2, INK, align="center")


def draw_mini_cricket(c, x0):
    cx = x0 + 158
    c.text(cx, 680, "CRICKET", 2, INK, align="center")
    # Green pitch strip.
    c.fill_rect(x0 + 12, 800, 293, 24, PITCH)
    # Stumps.
    for sx in (cx - 18, cx - 6, cx + 6):
        c.fill_rect(sx, 752, 8, 48, (255, 253, 244))
        c.rect(sx, 752, 8, 48, INK, 1)
    c.fill_rect(cx - 20, 748, 44, 5, (255, 253, 244))
    # Bat, leaning.
    c.line(cx - 92, 806, cx - 52, 726, INK, 10)
    # Ball.
    c.disc(cx + 92, 772, 11, INK)
    c.text(cx, 840, "FINAL DAY IN", 3, INK, align="center")
    c.text(cx, 868, "WELLINGTON", 3, INK, align="center")
    c.text(cx, 906, "NZ 119-2, 233 BEHIND INDIA", 2, INK, align="center")


def draw_mini_canberra(c, x0):
    cx = x0 + 158
    c.text(cx, 680, "POLITICS", 2, INK, align="center")
    # Parliament House: triangular roof, flag mast, small flag.
    c.triangle(cx - 82, 820, cx, 740, cx + 82, 820, INK)
    c.fill_rect(cx - 96, 820, 192, 8, INK)
    c.line(cx, 740, cx, 700, INK, 4)
    c.fill_rect(cx + 2, 700, 36, 22, FLAGBLUE)
    c.disc(cx + 12, 708, 2, (255, 255, 255))
    c.disc(cx + 26, 714, 2, (255, 255, 255))
    c.disc(cx + 30, 706, 2, (255, 255, 255))
    c.text(cx, 840, "CANBERRA'S", 3, INK, align="center")
    c.text(cx, 868, "LAST WEEK", 3, INK, align="center")
    c.text(cx, 906, "GAS AND TAX ON AGENDA", 2, INK, align="center")


def draw_page():
    c = Canvas()
    c.rect(8, 8, 1008, 1008, INK, 4)
    draw_masthead(c)
    draw_hero(c)
    for x0, fn in ((24, draw_mini_obituary),
                   (353, draw_mini_cricket),
                   (682, draw_mini_canberra)):
        c.fill_rect(x0, 664, 317, 340, MINI)
        c.rect(x0, 664, 317, 340, INK, 2)
        fn(c, x0)
    return c.buf


# ------------------------------------------------------------- PNG out
def png_bytes(raw_rgb):
    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    body = bytearray()
    stride = W * 3
    for y in range(H):
        body.append(0)  # filter: none
        body += raw_rgb[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(body), 9))
            + chunk(b"IEND", b""))


def main():
    data = png_bytes(draw_page())
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        path = os.path.join(out_dir, "entry.png")
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "out", "entry.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes) sha256=%s"
          % (path, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
