#!/usr/bin/env python3
"""Generate the social-share (Open Graph) image public/og-default.png — a
1200x630 card built from the cover emblem (public/cover-mark.png) + the title,
in the site palette. Rendered from an SVG via headless Chrome.

Usage: uv run python scripts/generate_og_image.py
(Needs google-chrome-stable / chromium on PATH.)
"""
import base64
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

PAPER = "#fbf4e6"
INK = "#2b2118"
INK_SOFT = "#6a5f4b"
ACCENT = "#7a1f0e"
GOLD = "#b8923f"

emblem_b64 = base64.b64encode((PUBLIC / "cover-mark.png").read_bytes()).decode()

SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="{PAPER}"/>
  <rect x="24" y="24" width="1152" height="582" rx="18" fill="none"
        stroke="{GOLD}" stroke-width="3" stroke-opacity="0.5"/>
  <image x="96" y="135" width="360" height="360" preserveAspectRatio="xMidYMid meet"
         href="data:image/png;base64,{emblem_b64}"/>
  <g font-family="Georgia, 'Times New Roman', serif">
    <text x="510" y="250" font-size="74" font-weight="700" fill="{INK}">SchaakStudie</text>
    <text x="510" y="332" font-size="74" font-weight="700" fill="{INK}">SpinselS <tspan fill="{ACCENT}">2</tspan></text>
    <text x="514" y="392" font-size="30" font-style="italic" fill="{INK_SOFT}">Originele schaakeindspelstudies</text>
    <text x="514" y="436" font-size="30" font-style="italic" fill="{INK_SOFT}">van Ignace Vandecasteele</text>
    <text x="514" y="520" font-size="26" letter-spacing="2" fill="{GOLD}">schaakstudiespinsels2.be</text>
  </g>
</svg>"""


def main():
    chrome = next((c for c in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser")
                   if shutil.which(c)), None)
    if not chrome:
        sys.exit("no Chrome/Chromium on PATH")
    out = PUBLIC / "og-default.png"
    with tempfile.TemporaryDirectory() as td:
        svg = Path(td) / "og.svg"
        svg.write_text(SVG, encoding="utf-8")
        subprocess.run([
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--default-background-color=00000000",
            "--force-device-scale-factor=1", "--window-size=1200,630",
            f"--screenshot={out}", f"file://{svg}",
        ], check=True, capture_output=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
