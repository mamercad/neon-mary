#!/usr/bin/env bash
set -euo pipefail

mode="${1:-dark}"
case "$mode" in dark|light) ;; *) echo "Usage: $0 [dark|light]" >&2; exit 2 ;; esac
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
theme="neon-mary-amelie-${mode}"
theme_dir="$HOME/.config/omarchy/themes/$theme"
mkdir -p "$HOME/.config/omarchy/themes"
rm -rf "$theme_dir"
cp -a "$repo_root/omarchy/themes/$theme" "$theme_dir"
omarchy-theme-set "$theme"
omarchy-theme-bg-set "$theme_dir/backgrounds/4k.png"
omarchy-shell background refresh || true
omarchy bar transparent true
printf 'Applied %s with transparent top bar.\n' "$theme"
