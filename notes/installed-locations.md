# Installed locations

## Active Pi runtime

Use `pi list` to identify the package Pi actually loads. Paths are home-relative
and OS-independent:

```text
# Linux / macOS
$HOME/.pi/agent/npm/node_modules/gentle-pi

# Windows
%USERPROFILE%\.pi\agent\npm\node_modules\gentle-pi
```

## Active personal overlay package

This extension is registered in Pi's settings `packages` array. Confirm with
`pi list` — it should appear pointing at this repo's checkout, e.g.:

```text
/data/Projects/gentle-pi-gentle-kozz-mod   # local checkout (this machine)
```

Settings file that holds the registration:

```text
# Linux / macOS
$HOME/.pi/agent/settings.json

# Windows
%USERPROFILE%\.pi\agent\settings.json
```

For a machine-independent install (no local path), use the GitHub source:

```bash
pi install git:github.com/kozz36/gentle-kozz-pi-extension
```

## Legacy patch fallback

The patch script is historical fallback material only. The normal activation
path is the Pi extension in `extensions/gentle-kozz.ts`.

Validate the legacy patch only when explicitly needed (resolves paths from
`$HOME` and the current directory):

```bash
python scripts/apply.py --dry-run
```
