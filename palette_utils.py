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
