#!/usr/bin/env python3
"""Render the showcase SVGs to PNG with their wallpaper actually embedded.

The showcase SVGs reference their wallpaper with a relative external href:

    <image href="../wallpapers/amelie/dark/4k.png" .../>

Neither ImageMagick's internal MSVG/rsvg delegate nor rsvg-convert reliably
resolves that relative path here, so every committed example rendered with a
flat dark void where the artwork should be -- the panels float on nothing and
the "transparent bar" treatment has nothing to be transparent over.

Fix: inline the referenced PNG as a base64 data URI before rasterising, so the
image travels inside the SVG and no path resolution is required. The .svg
sources on disk stay human-editable with their relative hrefs; only the
in-memory copy handed to the renderer is rewritten.
"""
import base64
import mimetypes
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "screenshots"

def discover() -> list[str]:
    """Every showcase SVG in screenshots/, so new variants are picked up
    automatically. A hardcoded list silently skips whatever was added last --
    that is how the Tron, Dark City, and Fifth Element examples shipped with
    their wallpapers missing."""
    return sorted(
        p.stem for p in SHOTS.glob("desktop-*-example.svg")
    )


HREF = re.compile(r'(<image[^>]*?\shref=")([^"]+)(")', re.I)


def inline_images(svg_text: str, base: Path) -> tuple[str, int]:
    """Replace relative <image href> targets with base64 data URIs."""
    count = 0

    def repl(m):
        nonlocal count
        head, href, tail = m.groups()
        if href.startswith(("data:", "http://", "https://")):
            return m.group(0)
        target = (base / href).resolve()
        if not target.exists():
            raise SystemExit(f"  !! referenced image missing: {target}")
        mime = mimetypes.guess_type(target.name)[0] or "image/png"
        data = base64.b64encode(target.read_bytes()).decode("ascii")
        count += 1
        return f"{head}data:{mime};base64,{data}{tail}"

    return HREF.sub(repl, svg_text), count


def render(stem: str) -> None:
    svg = SHOTS / f"{stem}.svg"
    png = SHOTS / f"{stem}.png"
    if not svg.exists():
        print(f"skip {stem}: no SVG")
        return
    text = svg.read_text(encoding="utf-8")
    inlined, n = inline_images(text, SHOTS)
    if n == 0:
        print(f"  {stem}: no external images to inline")
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write(inlined)
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            ["rsvg-convert", "-w", "1920", "-h", "1080",
             str(tmp_path), "-o", str(png)],
            check=True, capture_output=True)
    finally:
        tmp_path.unlink(missing_ok=True)
    print(f"  {stem}: embedded {n} image(s) -> {png.name} "
          f"({png.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    names = sys.argv[1:] or discover()
    print("rendering showcase screenshots")
    for stem in names:
        render(stem)
