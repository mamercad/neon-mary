#!/usr/bin/env bash
set -euo pipefail
variant="${1:-dark-city}"
mode="${2:-dark}"
case "$variant" in dark-city|fifth-element) ;; *) echo "Usage: $0 [dark-city|fifth-element] [dark|light]" >&2; exit 2 ;; esac
case "$mode" in dark|light) ;; *) echo "Usage: $0 [dark-city|fifth-element] [dark|light]" >&2; exit 2 ;; esac
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
theme="neon-mary-${variant}-${mode}"
theme_dir="$HOME/.config/omarchy/themes/$theme"
mkdir -p "$HOME/.config/omarchy/themes"
rm -rf "$theme_dir"
cp -a "$repo_root/omarchy/themes/$theme" "$theme_dir"
omarchy-theme-set "$theme"
omarchy-theme-bg-set "$theme_dir/backgrounds/4k.png"
omarchy-shell background refresh || true
omarchy bar transparent true
printf 'Applied %s with transparent top bar.\n' "$theme"
