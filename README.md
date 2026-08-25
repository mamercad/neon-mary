# Neon Mary Theme Family

**Neon Mary** is a family of themes built around the `mary.png` artwork. This repository contains ten variants: **Blade Runner**, **The Crow (1994)**, **Amélie (2001)**, **Tron (1982)**, **Dark City (1998)**, **The Fifth Element (1997)**, **The Grand Budapest Hotel (2014)**, **Neon Genesis Evangelion (1995)**, **The Matrix (1999)**, and **Solaris (1972)**. Each variant has dark and light palette modes for terminals, editors, Omarchy, and Hermes Agent.

The canonical artwork is derived from the Mary source. The original square source is preserved as `wallpapers/original-mary-1254.png`; each variant keeps the Mary composition while applying its own visual treatment. Light variants use the same composition with a restrained readable grade rather than invented overlays.

> **Note**
> The desktop compositions below are designed presentation images rather than
> live system captures.

## Screenshots gallery

Each variant is shown as a full desktop in both modes: the wallpaper, the
transparent top bar, a terminal workspace, and the theme inspector.

### Blade Runner

| Dark | Light |
| --- | --- |
| ![Neon Mary Blade Runner dark desktop](screenshots/desktop-blade-runner-dark-example.png) | ![Neon Mary Blade Runner light desktop](screenshots/desktop-blade-runner-light-example.png) |

### The Crow (1994)

| Dark | Light |
| --- | --- |
| ![Neon Mary The Crow dark desktop](screenshots/desktop-crow-dark-example.png) | ![Neon Mary The Crow light desktop](screenshots/desktop-crow-light-example.png) |

### Amélie (2001)

| Dark | Light |
| --- | --- |
| ![Neon Mary Amélie dark desktop](screenshots/desktop-amelie-dark-example.png) | ![Neon Mary Amélie light desktop](screenshots/desktop-amelie-light-example.png) |

### Tron (1982)

| Dark | Light |
| --- | --- |
| ![Neon Mary Tron dark desktop](screenshots/desktop-tron-dark-example.png) | ![Neon Mary Tron light desktop](screenshots/desktop-tron-light-example.png) |

### Dark City (1998)

| Dark | Light |
| --- | --- |
| ![Neon Mary Dark City dark desktop](screenshots/desktop-dark-city-dark-example.png) | ![Neon Mary Dark City light desktop](screenshots/desktop-dark-city-light-example.png) |

### The Fifth Element (1997)

| Dark | Light |
| --- | --- |
| ![Neon Mary The Fifth Element dark desktop](screenshots/desktop-fifth-element-dark-example.png) | ![Neon Mary The Fifth Element light desktop](screenshots/desktop-fifth-element-light-example.png) |

### The Grand Budapest Hotel (2014)

The only light-first variant: the palette was measured from the film itself
rather than inverted from a dark one, so the **light mode is the primary
treatment**.

| Dark | Light |
| --- | --- |
| ![Neon Mary Grand Budapest dark desktop](screenshots/desktop-grand-budapest-dark-example.png) | ![Neon Mary Grand Budapest light desktop](screenshots/desktop-grand-budapest-light-example.png) |

### Neon Genesis Evangelion (1995)

| Dark | Light |
| --- | --- |
| ![Neon Mary Evangelion dark desktop](screenshots/desktop-evangelion-dark-example.png) | ![Neon Mary Evangelion light desktop](screenshots/desktop-evangelion-light-example.png) |

### The Matrix (1999)

| Dark | Light |
| --- | --- |
| ![Neon Mary Matrix dark desktop](screenshots/desktop-matrix-dark-example.png) | ![Neon Mary Matrix light desktop](screenshots/desktop-matrix-light-example.png) |

### Solaris (1972)

| Dark | Light |
| --- | --- |
| ![Neon Mary Solaris dark desktop](screenshots/desktop-solaris-dark-example.png) | ![Neon Mary Solaris light desktop](screenshots/desktop-solaris-light-example.png) |

Wallpapers are generated at 3840×2160, 2560×1440, 1920×1080, 2560×1600,
2160×1440, 2048×1536, 2048×2048, and 1440×2560 in both modes; the apply
scripts install the 4K version. See [`omarchy/apply.sh`](omarchy/apply.sh)
and the per-variant apply scripts.

## Variants

### Blade Runner

- `dark`: wet-asphalt black, cyan, magenta, violet, mint, and Blade Runner amber.
- `light`: pale cyan-gray surface with the same neon accents darkened for readable contrast.

### The Crow (1994)

- `dark`: gothic charcoal, ash, mauve, weathered blue, olive, and blood red.
- `light`: pale ash-gray with ink, mauve, olive, and blood-red accents.

### Amélie (2001)

- `dark`: deep café brown with ochre, butter yellow, olive, teal, and poppy red.
- `light`: warm cream surface with the same ochre/poppy/teal accents darkened for readable contrast.

### Tron (1982)

- `dark`: grid black with phosphor cyan, electric blue, violet, amber, and green.
- `light`: pale cyan-gray with the same cybernetic accents darkened for readable contrast.

### Dark City (1998)

- `dark`: perpetual-night black with steel blue, clockwork violet, sodium amber, and muted crimson.
- `light`: pale steel-gray with blue, violet, amber, and crimson accents.

### The Fifth Element (1997)

- `dark`: deep violet-black with electric cyan, ultraviolet, solar amber, green, and coral red.
- `light`: warm cream with the same colorful accents darkened for readable contrast.

### The Grand Budapest Hotel (2014)

Designed light-first — the palette is measured from the film, which is
genuinely bright (mean luminance 0.518, 43.7% of pixels above 0.60, 71.4%
warm), rather than inverted from a dark one. The two modes lean on different
eras rather than being a plain inversion.

- `light` *(primary)*: 1932 confectionery pink with aubergine, lacquer red, Mendl's gold, and alpine blue.
- `dark`: the 1968 lobby — burnt orange and oxblood with façade pink as the accent.

### Neon Genesis Evangelion (1995)

- `dark`: NERV black with Unit-01 purple, toxic green, signal orange, and warning red.
- `light`: bone-white with deep aubergine, olive, and the same warning red darkened for readable contrast.

### The Matrix (1999)

- `dark`: phosphor green, rain-black, constructed-world blue, and warning red.
- `light`: pale green-white with readable terminal green, ink, and red accents.

### Solaris (1972)

- `dark`: amber instrument light over spacecraft brown, with distant ocean blue and muted rose.
- `light`: warm archival paper with brass, blue, and rose accents.

## Included targets

- Native Omarchy packages with `colors.toml`, `icons.theme`, and wallpaper variants.
- Neon Mary: The Crow (1994) and Amélie (2001) Omarchy packages and Hermes skins in dark/light modes.
- Neon Mary: Tron (1982) Omarchy packages and Hermes skins in dark/light modes.
- Neon Mary: Dark City (1998) and The Fifth Element (1997) Omarchy packages and Hermes skins in dark/light modes.
- Neon Mary: The Grand Budapest Hotel (2014) light-first Omarchy packages and Hermes skins in light/dark modes.
- Neon Mary: Neon Genesis Evangelion (1995) Omarchy packages and Hermes skins in dark/light modes.
- Neon Mary: The Matrix (1999) and Solaris (1972) Omarchy packages and Hermes skins in dark/light modes.
- Ghostty, iTerm2, Terminal.app, Kitty, Alacritty, WezTerm, Windows Terminal, fzf, tmux, Vim/Neovim, and VS Code resources.
- Windows 11 `.theme` files, accent-colour `.reg` files, and PowerShell installers in `windows/` — wallpaper, light/dark mode, accent colour, and the Windows Terminal scheme, all per-user and reversible.
- Hermes Agent skins for CLI/TUI/desktop surfaces.
- Wallpapers: 3840×2160, 2560×1440, 1920×1080, 2560×1600, 2160×1440, 2048×1536, 2048×2048, and 1440×2560 in both modes.
- `generate.py` to reproduce wallpaper variants and generated resources from the palette/source inputs.

## Install

```sh
# Omarchy (copy one package, then apply it)
cp -r omarchy/themes/neon-mary-dark ~/.config/omarchy/themes/
omarchy-theme-set neon-mary-dark
# Optional shell preference: keep the top menubar transparent
omarchy bar transparent true

# The Crow (1994) variant — applies the dark version and transparent bar
./omarchy/apply-crow.sh dark

# Amélie (2001) variant — applies the dark version and transparent bar
./omarchy/apply-amelie.sh dark

# Tron (1982) variant — applies the dark version and transparent bar
./omarchy/apply-tron.sh dark

# Dark City / The Fifth Element — applies a dark variant and transparent bar
./omarchy/apply-cinematic.sh dark-city dark
./omarchy/apply-cinematic.sh fifth-element dark

# The Grand Budapest Hotel — light-first, so `light` is this script's default
./omarchy/apply-grand-budapest.sh light

# Neon Genesis Evangelion
./omarchy/apply-evangelion.sh dark

# The Matrix (1999)
./omarchy/apply-matrix.sh dark

# Solaris (1972)
./omarchy/apply-solaris.sh dark

# Windows 11 (PowerShell, per-user, no OS patching)
#   wallpaper + light/dark mode + accent colour + Windows Terminal scheme
.\windows\apply-theme.ps1 -Variant grand-budapest -Mode light
.\windows\apply-theme.ps1 -Variant tron -SkipTerminal   # leave WT alone
.\windows\apply-terminal.ps1 -Variant tron -Mode dark   # terminal only
.\windows\apply-theme.ps1 -Revert

# Hermes Agent (active profile home; do not copy secrets)
mkdir -p "${HERMES_HOME:-$HOME/.hermes}/skins"
cp hermes/skins/neon-mary-dark.yaml "${HERMES_HOME:-$HOME/.hermes}/skins/"
hermes config set display.skin neon-mary-dark
```

Terminal files are portable exports; install them using each application's normal theme/import mechanism. iTerm2 and Terminal.app resources are intentionally kept as inspectable exports rather than modifying macOS preferences automatically.

## Rebuild and validate

```sh
python3 generate.py
python3 validate.py

# Contrast + YAML audit across every Hermes skin in the repo
python3 validate_contrast.py

# Rebuild the dark/light showcase desktops from each variant's palette,
# then rasterise them (embeds each wallpaper as a data URI)
python3 generate_showcases.py
python3 render_screenshots.py

# Windows 11 .theme + accent .reg files, and verify they decode correctly
python3 generate_windows.py
python3 validate_windows.py

# Structural check across every variant: palettes, all 8 wallpaper sizes in
# both locations, Omarchy packages, Hermes skins, terminal/editor exports,
# and that each variant is registered in the shared tooling
python3 validate.py
```

The Blade Runner generator uses the canonical current artwork from `~/Wallpapers/blade-runner-neon-mary-4k.png`; the variant generators derive their respective treatments from `~/Pictures/mary.png`. No source secrets or machine-local configuration are included.

## License

Theme code and configuration: MIT. Artwork provenance and redistribution rights remain with the original artwork owner; this repository preserves the supplied local source and should only be published where you have the right to share it.
