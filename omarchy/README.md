# Omarchy themes

Each `neon-mary-{dark,light}` directory is a native theme package with `colors.toml`, `icons.theme`, and all generated background variants. `apply.sh` installs the selected package, applies it, and enables Omarchy's transparent top bar through the supported `omarchy bar transparent true` command.

```sh
./omarchy/apply.sh dark
# or: ./omarchy/apply.sh light
```

`omarchy/generated/` contains portable downstream resource snapshots for the supported terminal/editor targets.
