# gentle-kozz Pi persona package

Supported Pi extension package for the `gentle-kozz` persona overlay.

This package is now the source of truth for the personal `gentle-kozz` behavior. It uses Pi's package/extension system and does not patch `node_modules`.

## Recommended installation

Install the supported extension package from GitHub (works on Windows, Linux,
or macOS without cloning):

```bash
pi install git:github.com/kozz36/gentle-kozz-pi-extension
```

Or install from a local clone/checkout, run from the repo directory:

```bash
pi install ./
```

For a one-off test without installing, point Pi at the repo directory:

```bash
pi -e .
```

Then reload or start a new Pi session:

```text
/reload
```

Confirm the extension command exists:

```text
/gentle-kozz
```

## Active runtime model

The active Pi package installation is resolved by `pi list`. The runtime path is
home-relative and OS-independent:

```text
# Linux / macOS
$HOME/.pi/agent/npm/node_modules/gentle-pi

# Windows
%USERPROFILE%\.pi\agent\npm\node_modules\gentle-pi
```

Always trust `pi list` over any hardcoded path; a stale global npm install may
contain previously patched copies that are no longer active.

## What the extension does

`extensions/gentle-kozz.ts` appends a persona overlay through Pi's supported `before_agent_start` extension hook. It does not modify `node_modules`.

The overlay keeps the el Gentleman identity but changes Spanish/persona behavior to:

- warm neutral Lima Spanish;
- no Rioplatense/regional voseo;
- direct senior-architect rigor;
- concepts before code;
- technical artifacts in professional English by default;
- verification before agreeing with technical claims;
- risk explanations with runtime trigger, breakage, mitigation, and concept name.

## Project persona file

The file `.pi/gentle-ai/persona.json` is only for the built-in `gentle-pi` persona selector.

Current `gentle-pi` 0.3.10 supports only:

```text
gentleman | neutral
```

It does not recognize `gentle-kozz` as a built-in persona mode. Keep this workspace on the base `gentleman` persona and let this extension append the `gentle-kozz` overlay.

## Legacy patch workflow

The old workflow patched the globally installed `gentle-pi` package in place:

- `<gentle-pi>/extensions/gentle-ai.ts`
- `<gentle-pi>/assets/orchestrator.md`

where `<gentle-pi>` is the runtime path reported by `pi list`. That is fragile
because package updates, reinstalls, or package-manager repairs can overwrite
patched files. Treat the patch script and snapshots as historical fallback
material only, not as the normal activation path.

`scripts/apply.py` resolves the gentle-pi runtime from `$HOME/.pi/agent/npm/node_modules/gentle-pi`
by default and the workspace from the current directory, so it runs on Windows
or Linux. Override with `GENTLE_PI_DIR` / `GENTLE_KOZZ_WORKSPACE` or the
`--gentle-pi-dir` / `--workspace` flags.

If a legacy session explicitly depends on the patched built-in selector,
validate it manually before use:

```bash
python scripts/apply.py --dry-run
```

## Upstream proposal

The long-term fix is first-class persona provider registration in `gentle-pi`, so packages can register selectable personas instead of appending overlays. Draft proposal:

```text
docs/upstream-persona-providers-proposal.md
```
