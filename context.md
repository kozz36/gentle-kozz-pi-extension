# Code Context

## Current source of truth

The `gentle-kozz` behavior is provided by this Pi extension package. Pi loads it
because its settings include this package under `packages` — either a local
checkout path or the GitHub source:

```bash
# machine-independent install
pi install git:github.com/kozz36/gentle-kozz-pi-extension
# or, from a local checkout
pi install ./
```

The settings file holding the registration is home-relative:

```text
# Linux / macOS
$HOME/.pi/agent/settings.json
# Windows
%USERPROFILE%\.pi\agent\settings.json
```

Confirm with:

```bash
pi list
```

## Active runtime path

The active `gentle-pi` package resolved by Pi is home-relative and OS-independent:

```text
# Linux / macOS
$HOME/.pi/agent/npm/node_modules/gentle-pi
# Windows
%USERPROFILE%\.pi\agent\npm\node_modules\gentle-pi
```

Always trust `pi list` over any hardcoded path; a stale global npm install may
hold previously patched copies that are no longer active.

## Relevant files

1. `package.json` — Pi package manifest with `pi.extensions` and local development dependencies.
2. `extensions/gentle-kozz.ts` — overlay implementation. It appends `GENTLE_KOZZ_PROMPT` in `before_agent_start` and registers `/gentle-kozz`.
3. `.pi/gentle-ai/persona.json` — built-in `gentle-pi` persona selector. Keep it on `gentleman`; the `gentle-kozz` overlay comes from this extension.
4. `.pi/settings.json` — project subagent model overrides; it does not install this package globally.
5. `README.md` — install/activation and legacy fallback documentation.
6. `notes/installed-locations.md` — active vs stale package path notes.

## Runtime behavior

Current `gentle-pi` 0.3.10 supports only built-in persona modes:

```text
gentleman | neutral
```

It does not recognize `gentle-kozz` as a built-in mode. The correct setup is therefore:

1. let built-in `gentle-pi` load its base `gentleman` persona;
2. let `extensions/gentle-kozz.ts` append the `gentle-kozz` overlay through Pi's supported extension hook.

## Validation commands

```bash
pi list
./node_modules/.bin/tsc --noEmit --pretty false
node --check extensions/gentle-kozz.ts
```

Expected result: the package appears in `pi list`, TypeScript passes, and Node accepts the extension syntax.
