"""Shared palette helpers for the Neon Mary generators.

Extracted so every variant generator applies identical contrast logic. The
helper was previously copy-pasted into generate.py, generate_crow.py and
generate_amelie.py, and simply omitted from the newer generators -- which is
how the Tron, Dark City and Fifth Element skins shipped with comment text at
1.38-1.96:1 against their own background.
"""


def _lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hx: str) -> float:
    """WCAG relative luminance of an #rrggbb string."""
    hx = hx.lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(a: str, b: str) -> float:
    """WCAG contrast ratio between two #rrggbb colours."""
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def muted(dim: str, bg: str, fg: str, target: float = 3.0) -> str:
    """Return a readable muted/comment colour.

    ANSI colour 8 is typically too close to the background to read as comment
    text. Blend it toward the foreground until it clears `target` contrast,
    preserving the palette's own hue rather than substituting a generic grey.
    """
    if ratio(dim, bg) >= target:
        return dim
    d = [int(dim.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    f = [int(fg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    best = dim
    for step in range(1, 101):
        t = step / 100.0
        best = "#%02x%02x%02x" % tuple(
            int(round(d[i] + (f[i] - d[i]) * t)) for i in range(3))
        if ratio(best, bg) >= target:
            break
    return best


def pick(bg: str, fg: str, *candidates: str, target: float = 3.0) -> str:
    """First candidate that clears `target` against bg, else a lifted fallback.

    Most palettes can map a UI role straight onto an ANSI slot, but the slot
    that works for one film can be far too dark in another -- Evangelion's
    ANSI 5 is a deep Unit-01 aubergine at 1.82:1 on its own background, where
    every other variant's ANSI 5 clears 3:1 comfortably. Passing the normal
    slot first and its bright counterpart second keeps the intended hue and
    only falls back to blending when neither is legible.
    """
    for c in candidates:
        if c and ratio(c, bg) >= target:
            return c
    return muted(candidates[0], bg, fg, target)


# --- wallpaper grading -----------------------------------------------------
#
# The Mary source is very dark (mean relative luminance ~0.074). `-modulate`
# applies a gain, so even 175% brightness only reached ~0.32 -- nowhere near
# the 0.78-0.92 luminance of the light-mode panels, which left every light
# wallpaper reading as mid-grey with the UI floating on top of it.
#
# A light treatment needs a tonal remap rather than a gain: lift the black
# point with -level, then veil toward white. Measured at level 0%,40%,2.0 with
# a 76% white veil the result lands at ~0.68 mean luminance while keeping
# enough tonal spread (~23) for the portrait to stay legible as artwork.
LIGHT_LEVEL = "0%,40%,2.0"
LIGHT_VEIL = 76
LIGHT_SAT = 55


def light_grade_args(tint: str = "#ffffff") -> list:
    """ImageMagick args producing a genuine high-key wash of a dark source."""
    return [
        "-level", LIGHT_LEVEL,
        "-modulate", f"100,{LIGHT_SAT},100",
        "(", "+clone", "-fill", tint, "-colorize", "100", ")",
        "-compose", "blend", "-define", f"compose:args={LIGHT_VEIL}",
        "-composite",
    ]
