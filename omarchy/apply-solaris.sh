#!/usr/bin/env bash
set -euo pipefail
mode="${1:-dark}"
case "$mode" in dark|light) ;; *) echo "Usage: $0 [dark|light]" >&2; exit 2 ;; esac
theme="neon-mary-solaris-${mode}"
omarchy-theme-set "$theme"
omarchy bar transparent true
