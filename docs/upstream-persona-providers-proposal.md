# Upstream proposal: first-class persona providers

## Problem

Personalizing el Gentleman currently requires patching the installed `gentle-pi` package when the desired persona is not one of the built-in modes. That creates patch drift: package updates, reinstalls, or package-manager repairs can overwrite local changes.

## Goal

Allow users and packages to provide persona overlays without modifying `node_modules` or forking `gentle-pi`.

## Proposed shape

Add a first-class persona provider mechanism:

```ts
interface PersonaProvider {
  id: string;
  label: string;
  prompt: string;
  spanishStyleRule?: string;
  languageBoundaryRule?: string;
}
```

Extensions or packages could register providers:

```ts
pi.registerPersonaProvider({
  id: "gentle-kozz",
  label: "gentle-kozz",
  prompt: "...",
  spanishStyleRule: "...",
  languageBoundaryRule: "...",
});
```

The existing `/gentle:persona` command would list built-in and registered personas, then persist the selected provider id in the normal persona config.

## Acceptance criteria

- Built-in `gentleman` and `neutral` behavior remains unchanged.
- External packages can register persona providers without mutating package internals.
- The selected persona survives Pi restarts through the existing persona config path.
- Missing providers fail safely with a visible warning and fallback to `gentleman`.
- Generated artifacts remain governed by the existing language/artifact boundary rules.

## Migration path

The current `gentle-kozz` extension remains a supported overlay package. Once provider registration exists, it can switch from `before_agent_start` prompt appending to `registerPersonaProvider`.
