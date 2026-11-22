#!/usr/bin/env python3
"""THE WORLD TODAY - Sunday 22 November 2026.

A one-page newspaper image summing up the day's world news.
Pure Python 3 standard library: draws every pixel itself (bitmap font,
procedural scenes, stylised world map) and writes a PNG with zlib/struct.
No network, no fonts on disk, no third-party packages. Deterministic:
two runs write byte-identical output.

Run:  python3 main.py        (writes $MAKEFUN_OUTPUT_DIR/entry.png,
                               default /output/entry.png)
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (255, 255, 255)
INK = (17, 17, 17)
RED = (200, 16, 46)
GREY = (102, 102, 102)
LGREY = (232, 232, 232)
MGREY = (208, 208, 208)
BLUE = (31, 78, 121)
LBLUE = (174, 214, 241)
GREEN = (46, 125, 50)
LGREEN = (165, 214, 167)
SAND = (232, 217, 160)
SKY = (135, 206, 235)
SEA = (36, 110, 160)
ORANGE = (230, 126, 34)
YELLOW = (241, 196, 15)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows; each row is 5 bits, bit 4 = left.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    'a': (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    'b': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    'c': (0x00, 0x00, 0x0E, 0x10, 0x10, 0x10, 0x0E),
    'd': (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    'e': (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    'f': (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    'k': (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm': (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    'n': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'o': (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    'p': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    'q': (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    'r': (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    's': (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    't': (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    'u': (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v': (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w': (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'x': (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    'y': (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'z': (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '*': (0x04, 0x15, 0x0E, 0x15, 0x04, 0, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
}

# Normalise fancy punctuation to what the font holds.
NORM = {
    '\u2014': '-', '\u2013': '-', '\u2019': "'", '\u2018': "'",
    '\u201c': '"', '\u201d': '"', '\u00b7': '.', '\u2022': '.',
    '\u00d7': 'x', '\u2192': '>', '\u00b0': 'o', '\u2011': '-',
}


def clean(s):
    return ''.join(NORM.get(ch, ch) for ch in s)


def text_w(s, scale):
    return len(clean(s)) * 6 * scale


def wrap(s, max_chars):
    """Greedy word wrap to at most max_chars per line."""
    words = clean(s).split(' ')
    lines, cur = [], ''
    for wd in words:
        if not cur:
            cur = wd
        elif len(cur) + 1 + len(wd) <= max_chars:
            cur += ' ' + wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)
        self.clip = (0, 0, w, h)  # x0, y0, x1, y1 (exclusive)

    def set_clip(self, x0, y0, x1, y1):
        self.clip = (max(0, x0), max(0, y0), min(self.w, x1), min(self.h, y1))

    def reset_clip(self):
        self.clip = (0, 0, self.w, self.h)

    def put(self, x, y, c):
        cx0, cy0, cx1, cy1 = self.clip
        if cx0 <= x < cx1 and cy0 <= y < cy1:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x0, y0, x1, y1, c):
        cx0, cy0, cx1, cy1 = self.clip
        x0, y0 = max(x0, cx0), max(y0, cy0)
        x1, y1 = min(x1, cx1), min(y1, cy1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill(x0, y0, x1, y0 + t, c)
        self.fill(x0, y1 - t, x1, y1, c)
        self.fill(x0, y0, x0 + t, y1, c)
        self.fill(x1 - t, y0, x1, y1, c)

    def hline(self, x0, x1, y, c, t=1):
        self.fill(x0, y, x1, y + t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.fill(x, y0, x + t, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill(x, y, x + t, y + t, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.put(x, y, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.put(x, y, c)

    def poly(self, pts, c, fill=True):
        if fill:
            ys = [p[1] for p in pts]
            for y in range(min(ys), max(ys) + 1):
                xs_at = []
                n = len(pts)
                for i in range(n):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % n]
                    if (y0 <= y < y1) or (y1 <= y < y0):
                        if y1 != y0:
                            xi = x0 + (y - y0) * (x1 - x0) // (y1 - y0)
                            xs_at.append(xi)
                xs_at.sort()
                for i in range(0, len(xs_at) - 1, 2):
                    self.fill(xs_at[i], y, xs_at[i + 1] + 1, y + 1, c)
        else:
            n = len(pts)
            for i in range(n):
                self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0],
                          pts[(i + 1) % n][1], c, 1)

    def char(self, x, y, ch, scale, c):
        g = FONT.get(ch)
        if g is None:
            g = FONT.get('?')
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.fill(x + col * scale, y + row * scale,
                              x + (col + 1) * scale, y + (row + 1) * scale, c)

    def text(self, x, y, s, scale, c, bold=False):
        s = clean(s)
        for ch in s:
            self.char(x, y, ch, scale, c)
            if bold:
                self.char(x + 1, y, ch, scale, c)
            x += 6 * scale
        return x

    def text_c(self, cx, y, s, scale, c, bold=False):
        x = cx - text_w(s, scale) // 2
        return self.text(x, y, s, scale, c, bold)

    def text_r(self, x1, y, s, scale, c, bold=False):
        x = x1 - text_w(s, scale)
        return self.text(x, y, s, scale, c, bold)

    def para(self, x, y, s, scale, c, max_chars, lh=None, bold=False):
        if lh is None:
            lh = 8 * scale + 2
        for ln in wrap(s, max_chars):
            self.text(x, y, ln, scale, c, bold)
            y += lh
        return y


def chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    return out


def write_png(cv, path):
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    data = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- scenes
# Each scene draws one small procedural picture, clipped to its own panel.
# No flags, faces, logos or invented details: simple shapes only.

def scene_strait(cv, x0, y0, x1, y1):
    """HERO: tankers in the Strait of Hormuz at night, smoke and flares."""
    cv.set_clip(x0, y0, x1, y1)
    cv.fill(x0, y0, x1, y0 + (y1 - y0) * 2 // 5, (18, 24, 48))      # night sky
    cv.fill(x0, y0 + (y1 - y0) * 2 // 5, x1, y1, SEA)                # sea
    cv.circle(x0 + (x1 - x0) * 4 // 5, y0 + 26, 16, (240, 220, 160))
    cv.circle(x0 + (x1 - x0) * 4 // 5, y0 + 26, 11, (250, 235, 190))
    # missile arcs (red dashes on a clean parabola)
    for k in range(3):
        bx = x0 + 30 + k * 95
        by = y0 + 34 + k * 10
        for t in range(0, 41, 3):
            px = bx + t * 3
            py = by - int(28 * 4 * (t / 40.0) * (1 - t / 40.0))
            cv.circle(px, py, 2, RED)
    # tanker 1 (far)
    ty = y0 + (y1 - y0) * 3 // 5
    cv.fill(x0 + 40, ty, x0 + 210, ty + 22, INK)
    cv.fill(x0 + 55, ty - 16, x0 + 95, ty, INK)
    cv.fill(x0 + 150, ty - 10, x0 + 185, ty, (120, 20, 20))
    cv.fill(x0 + 40, ty + 22, x0 + 210, ty + 26, (90, 90, 90))
    # thin smoke column from tanker 1
    for i in range(6):
        cv.circle(x0 + 72 + i * 4, ty - 20 - i * 8, 4 + i, (110, 110, 110))
    # tanker 2 (near, burning)
    ty2 = y0 + (y1 - y0) * 4 // 5
    cv.fill(x0 + 190, ty2, x0 + 370, ty2 + 26, (30, 30, 30))
    cv.fill(x0 + 205, ty2 - 18, x0 + 250, ty2, (30, 30, 30))
    cv.fill(x0 + 300, ty2 - 12, x0 + 340, ty2, (120, 20, 20))
    for i in range(3):
        cv.circle(x0 + 222 + i * 4, ty2 - 20 - i * 8, 6 + i * 2, ORANGE)
    cv.circle(x0 + 226, ty2 - 24, 5, YELLOW)
    # speedboat wake
    cv.line(x0 + 20, y1 - 12, x0 + 120, y1 - 12, PAPER, 2)
    cv.fill(x0 + 120, y1 - 20, x0 + 150, y1 - 12, INK)
    cv.reset_clip()


def scene_cop(cv, x0, y0, x1, y1):
    """LEAD: COP31 plenary hall in Antalya - stage, screen, delegate desks."""
    cv.set_clip(x0, y0, x1, y1)
    cv.fill(x0, y0, x1, y1, (238, 232, 214))                        # hall wall
    # big screen
    sx0, sy0 = x0 + (x1 - x0) // 5, y0 + 6
    sx1, sy1 = x1 - (x1 - x0) // 5, y0 + 36
    cv.fill(sx0, sy0, sx1, sy1, BLUE)
    cv.rect(sx0, sy0, sx1, sy1, INK, 2)
    cv.text_c((sx0 + sx1) // 2, sy0 + 7, "COP31", 2, PAPER, True)
    cv.text_c((sx0 + sx1) // 2, sy0 + 21, "ANTALYA", 1, PAPER)
    # stage + podium
    cv.fill(x0 + 10, y0 + 42, x1 - 10, y0 + 50, (120, 100, 70))
    cv.fill((x0 + x1) // 2 - 14, y0 + 34, (x0 + x1) // 2 + 14, y0 + 50, INK)
    # delegate desks, three rows
    for r in range(3):
        dy = y0 + 56 + r * 14
        cv.fill(x0 + 12, dy, x1 - 12, dy + 8, (160, 140, 100))
        for k in range(9):
            dx = x0 + 22 + k * ((x1 - x0 - 44) // 8)
            cv.circle(dx, dy - 5, 4, (40, 40, 90) if k % 3 else (140, 30, 30))
    cv.reset_clip()


def scene_bahrain(cv, x0, y0, x1, y1):
    """LEAD: Bahrain industrial site in daylight - factory, chimneys,
    smoke column and fire glow after the strike."""
    cv.set_clip(x0, y0, x1, y1)
    cv.fill(x0, y0, x1, y1, (198, 214, 226))                        # pale sky
    cv.fill(x0, y1 - 18, x1, y1, (150, 140, 120))                  # ground
    # factory block, left
    cv.fill(x0 + 14, y0 + 30, x0 + 130, y1 - 18, (120, 120, 118))
    cv.fill(x0 + 14, y0 + 30, x0 + 130, y0 + 36, (90, 90, 88))
    for k in range(5):
        cv.fill(x0 + 26 + k * 22, y0 + 44, x0 + 40 + k * 22,
                y0 + 56, (60, 60, 58))
    # chimney with a thin smoke column
    cv.fill(x0 + 140, y0 + 12, x0 + 152, y1 - 18, (90, 90, 88))
    for i in range(5):
        cv.circle(x0 + 146 + i * 3, y0 + 10 - i * 3, 4 + i, (110, 110, 110))
    # damaged hall, right: jagged broken roof, fire glow at its base
    cv.poly([(x0 + 170, y1 - 18), (x0 + 170, y0 + 38),
             (x0 + 196, y0 + 28), (x0 + 214, y0 + 40),
             (x0 + 238, y0 + 30), (x0 + 262, y0 + 40),
             (x0 + 286, y1 - 18)], (150, 60, 50))
    cv.circle(x0 + 226, y1 - 24, 8, ORANGE)
    cv.circle(x0 + 226, y1 - 26, 4, YELLOW)
    cv.circle(x0 + 250, y1 - 22, 5, ORANGE)
    cv.reset_clip()


def scene_cricket(cv, x0, y0, x1, y1):
    """LEAD: Test cricket in Wellington - pitch, stumps, bat, ball, board."""
    cv.set_clip(x0, y0, x1, y1)
    cv.fill(x0, y0, x1, y1, GREEN)                                  # outfield
    # pitch strip
    px0 = x0 + (x1 - x0) // 2 - 26
    px1 = x0 + (x1 - x0) // 2 + 26
    cv.fill(px0, y0, px1, y1, SAND)
    cv.hline(px0, px1, y0 + 18, PAPER, 2)
    cv.hline(px0, px1, y1 - 18, PAPER, 2)
    # stumps, both ends
    for sy in (y0 + 12, y1 - 26):
        for k in range(3):
            cv.fill(px0 + 18 + k * 7, sy, px0 + 22 + k * 7, sy + 14, YELLOW)
    # batsman: head, body, bat
    bx = x0 + (x1 - x0) // 2 - 34
    by = y0 + (y1 - y0) // 2
    cv.circle(bx, by - 16, 7, (200, 160, 120))
    cv.line(bx, by - 9, bx - 4, by + 12, INK, 4)
    cv.line(bx - 4, by + 12, bx - 12, by + 26, INK, 3)
    cv.line(bx - 4, by + 12, bx + 6, by + 26, INK, 3)
    cv.line(bx + 2, by - 4, bx + 16, by + 8, INK, 3)
    cv.line(bx + 16, by + 8, bx + 26, by + 22, (210, 180, 130), 4)
    # red ball in flight
    cv.circle(x0 + (x1 - x0) * 3 // 4, y0 + 22, 5, RED)
    # scoreboard
    bx0, by0 = x1 - 118, y0 + 6
    cv.fill(bx0, by0, bx0 + 112, by0 + 30, INK)
    cv.text(bx0 + 6, by0 + 4, "IND 521/4", 2, PAPER, True)
    cv.text(bx0 + 6, by0 + 20, "RECORD IN NZ", 1, YELLOW)
    cv.reset_clip()


# ---------------------------------------------------------------- map
# Stylised continents as polygons, in map-box coordinates (origin 16, 606).
MAP_OX, MAP_OY = 16, 612
CONTINENTS = [
    [(28, 30), (55, 8), (120, 6), (175, 16), (195, 28), (170, 42),
     (150, 48), (145, 72), (115, 80), (95, 62), (60, 58), (35, 48)],
    [(215, 6), (235, 4), (240, 14), (222, 16)],
    [(150, 86), (182, 82), (208, 96), (200, 118), (180, 132), (162, 108),
     (150, 96)],
    [(470, 14), (515, 6), (552, 14), (542, 38), (505, 44), (482, 36),
     (468, 24)],
    [(478, 56), (535, 50), (568, 64), (562, 96), (528, 124), (500, 100),
     (478, 72)],
    [(538, 6), (700, 4), (850, 12), (905, 36), (860, 58), (815, 52),
     (790, 78), (745, 72), (705, 58), (655, 52), (600, 44), (560, 28)],
    [(800, 70), (815, 68), (818, 80), (802, 82)],
    [(760, 80), (775, 78), (778, 88), (762, 90)],
    [(822, 96), (878, 90), (895, 108), (862, 126), (828, 116)],
    [(940, 120), (950, 116), (954, 128), (944, 130)],
]
# (number, x, y) absolute coords - each pin sits on land, checked visually.
PINS = [
    (1, 648, 658), (2, 566, 650), (3, 962, 734), (4, 672, 672),
    (5, 505, 648), (6, 524, 620), (7, 556, 622), (8, 496, 620),
    (9, 812, 674), (10, 482, 634), (11, 726, 668), (12, 188, 718),
]


def draw_map(cv, y0, y1):
    cv.fill(16, y0, 1008, y1, LBLUE)
    for poly in CONTINENTS:
        pts = [(MAP_OX + x, MAP_OY + y) for (x, y) in poly]
        cv.poly(pts, LGREEN)
        cv.poly(pts, (90, 130, 90), fill=False)
    for num, px, py in PINS:
        cv.circle(px, py, 10, RED)
        cv.circle(px, py, 10, PAPER, fill=False)
        s = str(num)
        cv.text(px - 3 * len(s), py - 4, s, 1, PAPER, True)


# ---------------------------------------------------------------- content
# 36 stories. Hero + 3 leads first reported 22 Nov 2026 UTC; mids and
# briefs are the weekend round-up, honestly labelled by reporting date.
# Hero + 3 leads carry drawn panels; mids and briefs are text.
HERO_KICKER = "1 - GULF"
HERO_HEAD = ["IRAN HITS US BASES IN",
             "BAHRAIN AS TANKERS BURN",
             "OFF OMAN"]
HERO_BODY = ("Two waves of drones and missiles hit four US "
             "bases in Bahrain on Saturday night; three "
             "tankers were struck near the Strait of Hormuz. "
             "Bahrain said its defences intercepted several.")

LEADS = [
    ("2 - CLIMATE - ANTALYA",
     ["COP31 DEAL TEXT TABLED AS",
      "TALKS RUN PAST DEADLINE"],
     "Presidents say the new text is one 'all parties "
     "can agree upon'. Approval session due Sunday morning."),
    ("3 - SPORT - WELLINGTON",
     ["INDIA SMASH RECORD TOTAL",
      "IN NEW ZEALAND"],
     "Pant's century lifts India to 521 for 4 on day "
     "four, the highest Test innings by India on New "
     "Zealand soil."),
    ("4 - GULF - BAHRAIN",
     ["BAHRAIN DEMANDS UN",
      "ACTION OVER IRAN STRIKES"],
     "Bahrain asks the UN to act and seeks damages "
     "after Iran hit a civilian industrial site and "
     "US bases on Saturday night."),
]

MIDS = [
    ("5 - FRANCE",
     ["FRENCH PROTEST",
      "LIVING COSTS FOR",
      "SIXTH WEEKEND"]),
    ("6 - POLAND",
     ["RUSSIAN MISSILES",
      "CRASH IN POLAND;",
      "TUSK: PROVOCATION"]),
    ("7 - BALTIC",
     ["DRONES HIT RUSSIAN",
      "CARGO SHIP; FINLAND",
      "TIGHTENS SECURITY"]),
    ("8 - DENMARK",
     ["DENMARK SAYS RUSSIA",
      "PLOTTED TO KILL",
      "A RAPPER"]),
    ("9 - HONG KONG",
     ["HONG KONG VOTES FOR",
      "ELECTION COMMITTEE;",
      "5,700 VOTERS"]),
    ("10 - TRADE - SATURDAY",
     ["EU AND INDONESIA",
      "SIGN TRADE DEAL;",
      "98.5% TARIFFS CUT"]),
    ("11 - INDIA",
     ["MODI OPENS NITISH",
      "SETU BRIDGE ACROSS",
      "THE GANGES, BIHAR"]),
    ("12 - BRAZIL",
     ["BOLSONARO IN",
      "INTENSIVE CARE WITH",
      "BOWEL OBSTRUCTION"]),
]

# 24 numbered briefs; each line is at most 40 chars incl. its number.
BRIEFS = [
    "13 FBI PROBES BREACH OF CRIME DATABASE",
    "14 US AIRLINES WARNED OF COPYCAT THREAT",
    "15 US OPEN TO LATIN AMERICAN UN CHIEF",
    "16 CENTCOM DENIES IRAN DOWNED AN F-16",
    "17 14 IRANIAN TANKERS STAGE OFF KHARG",
    "18 QATAR-MEDIATED US-IRAN TALKS GO ON",
    "19 ISRAEL STRIKES TOWNS IN SOUTH LEBANON",
    "20 3 KILLED IN GAZA AID-VEHICLE STRIKE",
    "21 'EL CHAPO ISIDRO' HELD IN SINALOA",
    "22 ANTHROPIC IPO RAISES RECORD $81.3BN",
    "23 24 DEAD AS BOAT CAPSIZES IN NIGERIA",
    "24 SWEDEN SUMMONS RUSSIAN AMBASSADOR",
    "25 FRANCE SEEKS UN MEETING ON KYIV HITS",
    "26 ESTONIA TO SHUT RUSSIA BORDER ON 1 DEC",
    "27 KHARKIV DRONE HITS HOMES, 11 HURT",
    "28 WILLIAM INSURES 10,000 FOREST WORKERS",
    "29 JAPAN TO TRAIN WITH LIVE FIRE IN INDIA",
    "30 PAKISTAN MINISTER TO ATTEND SCO MEET",
    "31 CYCLONE AKVAN HALTS 14 RANCHI FLIGHTS",
    "32 AUSTRALIA WIN T20 OPENER IN MELBOURNE",
    "33 ZELENSKYY: NATO IS THE BEST GUARANTEE",
    "34 BRENT CRUDE AT $92.57 FRI",
    "35 BLAIR: REJOIN EU ONLY IF IT INNOVATES",
    "36 EISENKOT INVITES LIKUD TO COALITION",
]

NUMBERS = [
    ("4", "US BASES HIT", "IN BAHRAIN"),
    ("3", "TANKERS STRUCK", "OFF OMAN"),
    ("14", "TANKERS STAGED", "OFF KHARG"),
    ("98.5%", "TARIFF LINES CUT", "EU-INDONESIA DEAL"),
    ("521/4", "INDIA'S RECORD", "TEST TOTAL IN NZ"),
    ("24", "DEAD IN NIGERIA", "BOAT DISASTER"),
]


# ---------------------------------------------------------------- grain
def add_grain(cv, seed=20261122):
    """Deterministic paper grain: sparse per-pixel brightness jitter from a
    fixed-seed xorshift32, so two runs stay byte-identical. About one pixel
    in eight is shifted by -8..+8 in all channels (hue preserved): subtle
    on text, visible as newsprint texture on flat paper. (A plain LCG was
    tried first and rejected: its low bits cycle with period 1024, so it
    could only ever speckle 1,024 distinct pixels.)"""
    state = seed & 0xffffffff
    px = cv.px
    for i in range(0, len(px), 3):
        state ^= (state << 13) & 0xffffffff
        state ^= state >> 17
        state ^= (state << 5) & 0xffffffff
        state &= 0xffffffff
        if state & 7:
            continue
        d = ((state >> 3) % 17) - 8
        if d == 0:
            continue
        for j in (i, i + 1, i + 2):
            v = px[j] + d
            px[j] = 0 if v < 0 else (255 if v > 255 else v)


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H)

    # ---- masthead
    cv.text(16, 20, "VOL. 1 - NO. 326", 1, GREY)
    cv.text_r(1008, 20, "SUNDAY EDITION", 1, GREY)
    cv.text_c(512, 4, "THE WORLD TODAY", 6, INK, True)
    cv.hline(16, 1008, 50, INK, 2)

    # ---- red date bar
    cv.fill(16, 54, 1008, 78, RED)
    cv.text(24, 61, "SUNDAY 22 NOVEMBER 2026 - 36 STORIES", 2, PAPER, True)
    cv.text_r(1000, 61, "DIARY: COP31 VOTE 06:00 GMT", 2, PAPER)

    # ---- hero
    cv.rect(16, 80, 1008, 258, INK, 2)
    cv.text(28, 90, HERO_KICKER, 2, RED, True)
    y = 112
    for ln in HERO_HEAD:
        cv.text(28, y, ln, 3, INK, True)
        y += 24
    cv.para(28, 192, HERO_BODY, 2, INK, 47, lh=16)
    cv.rect(612, 86, 1000, 250, INK, 2)
    scene_strait(cv, 613, 87, 999, 249)

    # ---- three leads with drawn panels
    scenes = (scene_cop, scene_cricket, scene_bahrain)
    for i, (kicker, head, body) in enumerate(LEADS):
        x0 = 16 + i * 334
        x1 = x0 + 324
        cv.rect(x0, 258, x1, 436, INK, 2)
        cv.rect(x0 + 6, 264, x1 - 6, 342, INK, 1)
        scenes[i](cv, x0 + 7, 265, x1 - 7, 341)
        cv.text(x0 + 10, 348, kicker, 1, RED, True)
        y = 362
        for ln in head:
            cv.text(x0 + 10, y, ln, 2, INK, True)
            y += 16
        cv.para(x0 + 10, 398, body, 1, INK, 51, lh=10)

    # ---- eight mid cards
    for i, (kicker, head) in enumerate(MIDS):
        col, row = i % 4, i // 4
        x0 = 16 + col * 248
        y0 = 436 + row * 82
        cv.rect(x0, y0, x0 + 238, y0 + 78, INK, 1)
        cv.text(x0 + 8, y0 + 8, kicker, 1, RED, True)
        y = y0 + 22
        for ln in head:
            cv.text(x0 + 8, y, ln, 2, INK, True)
            y += 16

    # ---- map
    cv.text(16, 598, "WHERE IT HAPPENED - 12 PINNED STORIES", 2, INK, True)
    cv.text_r(1008, 600, "NUMBERS MATCH THE STORIES ABOVE", 1, GREY)
    cv.rect(16, 612, 1008, 742, INK, 2)
    draw_map(cv, 612, 742)

    # ---- briefs
    cv.text(16, 746, "MORE FROM THE WEEKEND - 24 BRIEFS", 2, RED, True)
    cv.text_r(1008, 749, "BY THE NUMBERS BELOW", 1, GREY)
    for i, b in enumerate(BRIEFS):
        col = i // 12
        row = i % 12
        cv.text(16 + col * 508, 764 + row * 15, b, 2, INK)

    # ---- by the numbers
    for i, (num, l1, l2) in enumerate(NUMBERS):
        x0 = 16 + i * 167
        cv.rect(x0, 946, x0 + 157, 984, INK, 1)
        cv.text_c(x0 + 78, 950, num, 2, RED, True)
        cv.text_c(x0 + 78, 966, l1, 1, INK)
        cv.text_c(x0 + 78, 975, l2, 1, GREY)

    # ---- footer
    cv.hline(16, 1008, 988, INK, 1)
    cv.text(16, 994, "Sources: Reuters, AP, BBC, AFP, The Guardian, "
                     "ESPNcricinfo, UKMTO, as reported this weekend.",
            1, GREY)
    cv.text(16, 1006, "Drawn by an AI agent for make.fun - one page, "
                      "36 stories, no photo, no hype.", 1, GREY)
    cv.text_r(1008, 1006, "PAGE 1 OF 1", 1, GREY)

    # ---- deterministic paper grain, last so it textures everything
    add_grain(cv)
    return cv


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'entry.png')
    n = write_png(build(), path)
    print('wrote %s (%d bytes)' % (path, n))


if __name__ == '__main__':
    main()
