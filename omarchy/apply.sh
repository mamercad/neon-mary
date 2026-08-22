#!/usr/bin/env bash
set -euo pipefail

mode="${1:-dark}"
case "$mode" in
  dark|light) ;;
  *) printf 'Usage: %s [dark|light]\n' "$0" >&2; exit 2 ;;
esac

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
theme="neon-mary-${mode}"
theme_dir="${HOME}/.config/omarchy/themes/${theme}"
mkdir -p "${HOME}/.config/omarchy/themes"
rm -rf "$theme_dir"
cp -a "${repo_root}/omarchy/themes/${theme}" "$theme_dir"
omarchy-theme-set "$theme"
omarchy-theme-bg-set "${theme_dir}/backgrounds/4k.png"
omarchy-shell background refresh
omarchy bar transparent true
printf 'Applied %s with a transparent top bar.\n' "$theme"
