"""
Programmatic icon generator for the AUTO Blogger GUI.

Uses PIL/Pillow to draw crisp vector-style icons and converts them to
tkinter-compatible PhotoImage objects.  No external icon files needed.

Copyright 2025 AryanVBW
"""

import tkinter as tk
from typing import Dict, Optional, Tuple
import math

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class IconFactory:
    """Generates 16x16 / 20x20 pixel icons as tk.PhotoImage using PIL drawing."""

    def __init__(self, root: tk.Tk, size: int = 16):
        self.root = root
        self.size = size
        self._cache: Dict[str, ImageTk.PhotoImage] = {}
        # Keep references so tkinter GC doesn't destroy them
        self._refs: list = []

    def get(self, name: str, size: int = 0, color: str = '') -> Optional[ImageTk.PhotoImage]:
        """Get (or create & cache) an icon by name.

        Args:
            name:  Icon name (e.g. 'check', 'search', 'trash').
            size:  Override size. 0 = use factory default.
            color: Override foreground color. '' = use icon default.
        """
        if not PIL_AVAILABLE:
            return None

        sz = size or self.size
        key = f"{name}_{sz}_{color}"
        if key in self._cache:
            return self._cache[key]

        draw_fn = getattr(self, f'_draw_{name}', None)
        if draw_fn is None:
            return None

        img = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_fn(draw, sz, color)

        photo = ImageTk.PhotoImage(img)
        self._cache[key] = photo
        self._refs.append(photo)  # prevent GC
        return photo

    # ── helper ────────────────────────────────────────────────────────
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _c(hex_color: str, alpha: int = 255) -> Tuple[int, ...]:
        """Convert hex to RGBA tuple."""
        r, g, b = IconFactory._hex_to_rgb(hex_color)
        return (r, g, b, alpha)

    # ── icon drawings ─────────────────────────────────────────────────
    # Each method draws into a PIL ImageDraw at the given size.

    def _draw_lock(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#6366f1')
        m = max(1, s // 8)
        # Shackle arc
        d.arc([s*0.28, s*0.08, s*0.72, s*0.52], 0, 180, fill=fg, width=max(2, s//8))
        # Body rectangle
        d.rounded_rectangle([s*0.2, s*0.42, s*0.8, s*0.88], radius=s//10, fill=fg)
        # Keyhole
        d.ellipse([s*0.42, s*0.52, s*0.58, s*0.64], fill=(255,255,255,220))

    def _draw_image(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#8b5cf6')
        # Frame
        d.rounded_rectangle([s*0.1, s*0.15, s*0.9, s*0.85], radius=s//10, outline=fg, width=max(1, s//8))
        # Mountain
        d.polygon([(s*0.2, s*0.72), (s*0.4, s*0.42), (s*0.6, s*0.62), (s*0.8, s*0.38), (s*0.85, s*0.72)], fill=fg)
        # Sun
        d.ellipse([s*0.22, s*0.24, s*0.36, s*0.38], fill=fg)

    def _draw_robot(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#6366f1')
        # Antenna
        d.line([(s*0.5, s*0.08), (s*0.5, s*0.22)], fill=fg, width=max(1, s//8))
        d.ellipse([s*0.44, s*0.04, s*0.56, s*0.14], fill=fg)
        # Head
        d.rounded_rectangle([s*0.22, s*0.22, s*0.78, s*0.58], radius=s//10, fill=fg)
        # Eyes
        d.ellipse([s*0.32, s*0.32, s*0.44, s*0.44], fill=(255,255,255,220))
        d.ellipse([s*0.56, s*0.32, s*0.68, s*0.44], fill=(255,255,255,220))
        # Body
        d.rounded_rectangle([s*0.28, s*0.62, s*0.72, s*0.92], radius=s//12, fill=fg)

    def _draw_clipboard(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#64748b')
        # Board
        d.rounded_rectangle([s*0.18, s*0.15, s*0.82, s*0.92], radius=s//10, outline=fg, width=max(1, s//8))
        # Clip
        d.rounded_rectangle([s*0.35, s*0.06, s*0.65, s*0.24], radius=s//14, fill=fg)
        # Lines
        lw = max(1, s//10)
        for i, y in enumerate([0.38, 0.52, 0.66, 0.78]):
            w = 0.5 if i == 3 else 0.48
            d.line([(s*0.3, s*y), (s*(0.3+w), s*y)], fill=fg, width=lw)

    def _draw_gear(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#64748b')
        cx, cy = s/2, s/2
        # Outer teeth
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = cx + math.cos(angle) * s * 0.25
            y1 = cy + math.sin(angle) * s * 0.25
            x2 = cx + math.cos(angle) * s * 0.42
            y2 = cy + math.sin(angle) * s * 0.42
            d.line([(x1, y1), (x2, y2)], fill=fg, width=max(2, s//5))
        # Center circle
        r = s * 0.22
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fg)
        # Hole
        r2 = s * 0.09
        d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=(0,0,0,0))

    def _draw_wrench(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#64748b')
        # Handle
        d.line([(s*0.25, s*0.75), (s*0.65, s*0.35)], fill=fg, width=max(2, s//6))
        # Head
        d.arc([s*0.45, s*0.08, s*0.92, s*0.52], 200, 70, fill=fg, width=max(2, s//6))

    def _draw_trash(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#ef4444')
        w = max(1, s//8)
        # Lid
        d.line([(s*0.2, s*0.22), (s*0.8, s*0.22)], fill=fg, width=w)
        d.line([(s*0.38, s*0.22), (s*0.38, s*0.12)], fill=fg, width=w)
        d.line([(s*0.38, s*0.12), (s*0.62, s*0.12)], fill=fg, width=w)
        d.line([(s*0.62, s*0.12), (s*0.62, s*0.22)], fill=fg, width=w)
        # Body
        d.line([(s*0.25, s*0.22), (s*0.3, s*0.88)], fill=fg, width=w)
        d.line([(s*0.3, s*0.88), (s*0.7, s*0.88)], fill=fg, width=w)
        d.line([(s*0.7, s*0.88), (s*0.75, s*0.22)], fill=fg, width=w)
        # Inner lines
        for x in [0.4, 0.5, 0.6]:
            d.line([(s*x, s*0.32), (s*x, s*0.78)], fill=fg, width=max(1, w-1))

    def _draw_play(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#10b981')
        d.polygon([(s*0.3, s*0.15), (s*0.3, s*0.85), (s*0.82, s*0.5)], fill=fg)

    def _draw_stop(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#ef4444')
        d.rounded_rectangle([s*0.2, s*0.2, s*0.8, s*0.8], radius=s//12, fill=fg)

    def _draw_search(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        w = max(2, s//7)
        # Circle
        d.ellipse([s*0.12, s*0.08, s*0.62, s*0.58], outline=fg, width=w)
        # Handle
        d.line([(s*0.58, s*0.54), (s*0.88, s*0.86)], fill=fg, width=w)

    def _draw_folder(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#f59e0b')
        # Tab
        d.polygon([(s*0.1, s*0.25), (s*0.1, s*0.18), (s*0.4, s*0.18), (s*0.48, s*0.25)], fill=fg)
        # Body
        d.rounded_rectangle([s*0.1, s*0.25, s*0.9, s*0.82], radius=s//14, fill=fg)

    def _draw_chart(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        w = max(1, s//8)
        # Bars
        bars = [(0.2, 0.55), (0.38, 0.35), (0.56, 0.5), (0.74, 0.22)]
        bw = s * 0.12
        for x, top in bars:
            d.rectangle([s*x, s*top, s*x+bw, s*0.85], fill=fg)
        # Baseline
        d.line([(s*0.12, s*0.88), (s*0.9, s*0.88)], fill=fg, width=max(1, s//10))

    def _draw_pencil(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#64748b')
        w = max(2, s//7)
        # Body
        d.line([(s*0.2, s*0.8), (s*0.75, s*0.25)], fill=fg, width=w)
        # Tip
        d.polygon([(s*0.12, s*0.88), (s*0.2, s*0.75), (s*0.25, s*0.8)], fill=fg)
        # Eraser
        d.line([(s*0.72, s*0.28), (s*0.82, s*0.18)], fill=self._c('#f59e0b'), width=w)

    def _draw_plus(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#10b981')
        w = max(2, s//5)
        d.line([(s*0.5, s*0.18), (s*0.5, s*0.82)], fill=fg, width=w)
        d.line([(s*0.18, s*0.5), (s*0.82, s*0.5)], fill=fg, width=w)

    def _draw_check(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#10b981')
        w = max(2, s//6)
        d.line([(s*0.18, s*0.5), (s*0.4, s*0.75), (s*0.82, s*0.22)], fill=fg, width=w, joint='curve')

    def _draw_toggle(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#10b981')
        # Track
        d.rounded_rectangle([s*0.1, s*0.3, s*0.9, s*0.7], radius=s//4, fill=fg)
        # Knob (right = ON)
        r = s * 0.17
        d.ellipse([s*0.9-r*2-s*0.06, s*0.5-r, s*0.9-s*0.06, s*0.5+r], fill=(255,255,255,240))

    def _draw_circle(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#9ca3af')
        w = max(2, s//6)
        d.ellipse([s*0.18, s*0.18, s*0.82, s*0.82], outline=fg, width=w)

    def _draw_flask(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#8b5cf6')
        w = max(1, s//8)
        # Neck
        d.line([(s*0.38, s*0.1), (s*0.38, s*0.38)], fill=fg, width=w)
        d.line([(s*0.62, s*0.1), (s*0.62, s*0.38)], fill=fg, width=w)
        d.line([(s*0.32, s*0.1), (s*0.68, s*0.1)], fill=fg, width=w)
        # Body
        d.polygon([(s*0.38, s*0.38), (s*0.18, s*0.85), (s*0.82, s*0.85), (s*0.62, s*0.38)], outline=fg, width=w)
        # Liquid
        d.polygon([(s*0.3, s*0.62), (s*0.22, s*0.82), (s*0.78, s*0.82), (s*0.7, s*0.62)], fill=self._c('#c4b5fd'))

    def _draw_save(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        # Outer body
        d.rounded_rectangle([s*0.12, s*0.12, s*0.88, s*0.88], radius=s//10, fill=fg)
        # Disk slot
        d.rectangle([s*0.3, s*0.12, s*0.7, s*0.42], fill=(255,255,255,220))
        # Label area
        d.rectangle([s*0.25, s*0.55, s*0.75, s*0.82], fill=(255,255,255,180))

    def _draw_xmark(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#ef4444')
        w = max(2, s//6)
        d.line([(s*0.22, s*0.22), (s*0.78, s*0.78)], fill=fg, width=w)
        d.line([(s*0.78, s*0.22), (s*0.22, s*0.78)], fill=fg, width=w)

    def _draw_globe(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        w = max(1, s//8)
        r = s * 0.38
        cx, cy = s/2, s/2
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=fg, width=w)
        # Meridian
        d.ellipse([cx-r*0.45, cy-r, cx+r*0.45, cy+r], outline=fg, width=max(1, w-1))
        # Equator
        d.line([(cx-r, cy), (cx+r, cy)], fill=fg, width=max(1, w-1))

    def _draw_user(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#64748b')
        cx = s / 2
        # Head
        hr = s * 0.16
        d.ellipse([cx-hr, s*0.12, cx+hr, s*0.12+hr*2], fill=fg)
        # Body
        d.arc([s*0.2, s*0.42, s*0.8, s*1.0], 180, 0, fill=fg, width=max(2, s//5))

    def _draw_hourglass(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#f59e0b')
        w = max(1, s//8)
        # Top and bottom bars
        d.line([(s*0.22, s*0.12), (s*0.78, s*0.12)], fill=fg, width=w)
        d.line([(s*0.22, s*0.88), (s*0.78, s*0.88)], fill=fg, width=w)
        # Glass shape
        d.line([(s*0.28, s*0.12), (s*0.5, s*0.5)], fill=fg, width=w)
        d.line([(s*0.72, s*0.12), (s*0.5, s*0.5)], fill=fg, width=w)
        d.line([(s*0.28, s*0.88), (s*0.5, s*0.5)], fill=fg, width=w)
        d.line([(s*0.72, s*0.88), (s*0.5, s*0.5)], fill=fg, width=w)

    def _draw_warning(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#f59e0b')
        # Triangle
        d.polygon([(s*0.5, s*0.1), (s*0.1, s*0.88), (s*0.9, s*0.88)], outline=fg,
                  width=max(2, s//7))
        # Exclamation
        w = max(1, s//8)
        d.line([(s*0.5, s*0.35), (s*0.5, s*0.62)], fill=fg, width=w)
        r = s * 0.04
        d.ellipse([s*0.5-r, s*0.72-r, s*0.5+r, s*0.72+r], fill=fg)

    def _draw_book(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#6366f1')
        w = max(1, s//8)
        # Left page
        d.rounded_rectangle([s*0.1, s*0.15, s*0.48, s*0.85], radius=s//16, outline=fg, width=w)
        # Right page
        d.rounded_rectangle([s*0.52, s*0.15, s*0.9, s*0.85], radius=s//16, outline=fg, width=w)
        # Spine
        d.line([(s*0.5, s*0.12), (s*0.5, s*0.88)], fill=fg, width=w)

    def _draw_newspaper(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#64748b')
        w = max(1, s//8)
        # Paper
        d.rounded_rectangle([s*0.12, s*0.1, s*0.88, s*0.9], radius=s//14, outline=fg, width=w)
        # Headline
        d.rectangle([s*0.22, s*0.2, s*0.78, s*0.36], fill=fg)
        # Text lines
        lw = max(1, s//12)
        for y in [0.46, 0.56, 0.66, 0.76]:
            d.line([(s*0.22, s*y), (s*0.78, s*y)], fill=fg, width=lw)

    def _draw_new_badge(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#10b981')
        # Badge background
        d.rounded_rectangle([s*0.05, s*0.2, s*0.95, s*0.8], radius=s//6, fill=fg)
        # "N" letter (simple)
        w = max(1, s//7)
        d.line([(s*0.22, s*0.65), (s*0.22, s*0.35)], fill=(255,255,255,230), width=w)
        d.line([(s*0.22, s*0.35), (s*0.42, s*0.65)], fill=(255,255,255,230), width=w)
        d.line([(s*0.42, s*0.65), (s*0.42, s*0.35)], fill=(255,255,255,230), width=w)

    def _draw_refresh(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        w = max(2, s//7)
        cx, cy = s/2, s/2
        r = s * 0.32
        # Arc
        d.arc([cx-r, cy-r, cx+r, cy+r], 30, 330, fill=fg, width=w)
        # Arrow head
        ax = cx + math.cos(math.radians(30)) * r
        ay = cy - math.sin(math.radians(30)) * r
        d.polygon([(ax, ay), (ax-s*0.12, ay-s*0.04), (ax-s*0.04, ay+s*0.1)], fill=fg)

    def _draw_info(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        cx = s / 2
        # Circle
        r = s * 0.38
        d.ellipse([cx-r, cx-r, cx+r, cx+r], outline=fg, width=max(2, s//7))
        # Dot
        dr = s * 0.05
        d.ellipse([cx-dr, s*0.28-dr, cx+dr, s*0.28+dr], fill=fg)
        # Line
        d.line([(cx, s*0.4), (cx, s*0.72)], fill=fg, width=max(2, s//7))

    def _draw_skip(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#9ca3af')
        # Two triangles + bar
        d.polygon([(s*0.12, s*0.2), (s*0.12, s*0.8), (s*0.42, s*0.5)], fill=fg)
        d.polygon([(s*0.42, s*0.2), (s*0.42, s*0.8), (s*0.72, s*0.5)], fill=fg)
        # End bar
        d.rectangle([s*0.74, s*0.2, s*0.82, s*0.8], fill=fg)

    def _draw_download(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#3b82f6')
        w = max(2, s//7)
        # Arrow down
        d.line([(s*0.5, s*0.12), (s*0.5, s*0.6)], fill=fg, width=w)
        d.line([(s*0.3, s*0.45), (s*0.5, s*0.65), (s*0.7, s*0.45)], fill=fg, width=w, joint='curve')
        # Tray
        d.line([(s*0.18, s*0.78), (s*0.18, s*0.88), (s*0.82, s*0.88), (s*0.82, s*0.78)],
               fill=fg, width=w, joint='curve')

    def _draw_config(self, d: ImageDraw.Draw, s: int, c: str):
        """Alias for gear"""
        self._draw_gear(d, s, c)

    def _draw_connection(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#10b981')
        w = max(1, s//7)
        # Two chain links
        d.arc([s*0.08, s*0.25, s*0.52, s*0.75], 90, 270, fill=fg, width=w)
        d.arc([s*0.48, s*0.25, s*0.92, s*0.75], 270, 90, fill=fg, width=w)

    def _draw_key(self, d: ImageDraw.Draw, s: int, c: str):
        fg = self._c(c or '#f59e0b')
        w = max(1, s//7)
        # Head
        r = s * 0.18
        d.ellipse([s*0.15, s*0.5-r, s*0.15+r*2, s*0.5+r], outline=fg, width=w)
        # Shaft
        d.line([(s*0.15+r*2, s*0.5), (s*0.85, s*0.5)], fill=fg, width=w)
        # Teeth
        d.line([(s*0.72, s*0.5), (s*0.72, s*0.65)], fill=fg, width=w)
        d.line([(s*0.82, s*0.5), (s*0.82, s*0.65)], fill=fg, width=w)
