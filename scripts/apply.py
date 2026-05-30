#!/usr/bin/env python3
"""Legacy fallback: patch `gentle-kozz` into an installed gentle-pi package.

Normal activation is now the supported Pi extension in `extensions/gentle-kozz.ts`.
Use this script only for old sessions that explicitly depend on a patched built-in
persona selector. It intentionally patches only persona/language fields and does
not rewrite SDD, subagent, memory, safety, or OpenSpec orchestration sections.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# Resolve the active Pi runtime location from the home directory so the legacy
# fallback works on Windows or Linux. `pi list` is the source of truth; override
# with GENTLE_PI_DIR if the runtime lives elsewhere.
DEFAULT_GENTLE_PI_DIR = Path(
    os.environ.get(
        "GENTLE_PI_DIR",
        Path.home() / ".pi" / "agent" / "npm" / "node_modules" / "gentle-pi",
    )
)
# Default the workspace to the current directory; override with
# GENTLE_KOZZ_WORKSPACE to target a specific project root.
DEFAULT_WORKSPACE = Path(os.environ.get("GENTLE_KOZZ_WORKSPACE", Path.cwd()))

PERSONA_BLOCK = """type PersonaMode = "gentleman" | "neutral" | "gentle-kozz";

const PERSONA_OPTIONS = ["gentleman", "neutral", "gentle-kozz"] as const;

interface PersonaConfig {
	prompt: string;
	spanishStyleRule: string;
	languageBoundaryRule: string;
}

const GENTLEMAN_PERSONA_PROMPT = `Persona:
- Be direct, technical, and concise.
- When the user writes Spanish, answer in natural Rioplatense Spanish with voseo.
- Act as a senior architect and teacher: concepts before code, no shortcuts.
- Treat AI as a tool directed by the human; never present yourself as a default chatbot.
- Push back when the user asks for code without enough context or understanding.
- Correct errors directly, explain why, and show the better path.`;

const NEUTRAL_PERSONA_PROMPT = `Persona:
- Be direct, technical, concise, warm, and professional.
- Always respond in the same language the user writes in.
- Do not use slang or regional expressions.
- Act as a senior architect and teacher: concepts before code, no shortcuts.
- Treat AI as a tool directed by the human; never present yourself as a default chatbot.
- Push back when the user asks for code without enough context or understanding.
- Correct errors directly, explain why, and show the better path.`;

const GENTLE_KOZZ_PERSONA_PROMPT = `Persona:
- Be direct, rigorous, concise, and highly technical.
- Match the user's current language; in Spanish, use warm neutral Lima Spanish without regional voseo or slang-heavy phrasing.
- Act as a senior architect and teacher: concepts before code, no shortcuts.
- Treat AI as a tool directed by the human; the user leads product and architecture direction.
- Push back when context is missing, the approach is inefficient, or the implementation would be non-idiomatic for the active stack.
- Verify technical claims before agreeing; if wrong, explain why with evidence and show the optimized path.
- Keep persona out of artifacts: code, comments, UI copy, docs, commit messages, branch names, PR bodies, and filenames default to professional English unless the project or user requests otherwise.
- When surfacing risk, include what triggers it at runtime, what breaks if ignored, the mitigation, and the underlying concept name.`;

function personaConfig(persona: PersonaMode): PersonaConfig {
	if (persona === "neutral") {
		return {
			prompt: NEUTRAL_PERSONA_PROMPT,
			spanishStyleRule:
				"- Keep the response in the user's language; in Spanish, use neutral/professional Spanish without regional expression.",
			languageBoundaryRule:
				"User-facing conversation should stay in the user's language. In `neutral` mode, Spanish stays neutral/professional without regional expression.",
		};
	}
	if (persona === "gentle-kozz") {
		return {
			prompt: GENTLE_KOZZ_PERSONA_PROMPT,
			spanishStyleRule:
				"- Keep the response in the user's language; in Spanish, use warm neutral Lima Spanish without regional voseo or slang-heavy phrasing.",
			languageBoundaryRule:
				"User-facing conversation should stay in the user's language. In `gentle-kozz` mode, Spanish uses warm neutral Lima Spanish without regional voseo or slang-heavy phrasing.",
		};
	}
	return {
		prompt: GENTLEMAN_PERSONA_PROMPT,
		spanishStyleRule:
			"- Keep the response in the user's language; in Spanish, use natural Rioplatense voseo.",
		languageBoundaryRule:
			"User-facing conversation should stay in the user's language. In `gentleman` mode, Spanish uses natural Rioplatense voseo.",
	};
}

function renderOrchestratorPrompt(persona: PersonaMode): string {
	const config = personaConfig(persona);
	return getOrchestratorPrompt().replace(
		"{{PERSONA_SPANISH_STYLE_RULE}}",
		config.spanishStyleRule,
	).replace("{{PERSONA_LANGUAGE_BOUNDARY_RULE}}", config.languageBoundaryRule);
}

"""

READ_PERSONA_FUNCTION = """function readPersonaMode(cwd: string): PersonaMode {
	const path = personaConfigPath(cwd);
	if (!existsSync(path)) return "gentleman";
	try {
		const parsed: unknown = JSON.parse(readFileSync(path, "utf8"));
		if (!isRecord(parsed)) return "gentleman";
		if (parsed.mode === "neutral" || parsed.mode === "gentle-kozz") {
			return parsed.mode;
		}
		return "gentleman";
	} catch {
		return "gentleman";
	}
}

"""

ORCH_SPANISH_RULE = "{{PERSONA_SPANISH_STYLE_RULE}}"
ORCH_LANGUAGE_RULE = "{{PERSONA_LANGUAGE_BOUNDARY_RULE}}"


def replace_between(
    text: str, start_marker: str, end_marker: str, replacement: str
) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[:start] + replacement + text[end:]


def replace_function(text: str, function_name: str, replacement: str) -> str:
    marker = f"function {function_name}("
    start = text.index(marker)
    depth = 0
    body_started = False
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
            body_started = True
        elif ch == "}":
            depth -= 1
            if body_started and depth == 0:
                end = i + 1
                while end < len(text) and text[end] in "\r\n":
                    end += 1
                return text[:start] + replacement + text[end:]
    raise ValueError(f"Could not locate end of {function_name}")


def patch_orchestrator(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = text.replace(
        "- Keep the response in the user's language; in Spanish, use natural Rioplatense voseo.",
        ORCH_SPANISH_RULE,
    )
    text = text.replace(
        "- Keep the response in the user's language and follow the currently selected persona mode.",
        ORCH_SPANISH_RULE,
    )
    text = text.replace(
        "User-facing conversation should stay in the user's language and follow the currently selected persona mode. In `gentleman` mode, Spanish uses natural Rioplatense voseo. In `neutral` mode, Spanish stays neutral/professional without regional expression.",
        ORCH_LANGUAGE_RULE,
    )
    if ORCH_SPANISH_RULE not in text or ORCH_LANGUAGE_RULE not in text:
        raise RuntimeError("orchestrator placeholders were not installed")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def patch_extension(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = replace_between(
        text,
        "type PersonaMode =",
        "function buildGentlePrompt(persona: PersonaMode): string {",
        PERSONA_BLOCK,
    )

    text = text.replace(
        'function buildGentlePrompt(persona: PersonaMode): string {\n\tconst personaPrompt =\n\t\tpersona === "neutral" ? NEUTRAL_PERSONA_PROMPT : GENTLEMAN_PERSONA_PROMPT;',
        "function buildGentlePrompt(persona: PersonaMode): string {\n\tconst config = personaConfig(persona);",
    )
    text = text.replace("${personaPrompt}", "${config.prompt}")
    text = text.replace(
        "${ORCHESTRATOR_PROMPT}`;", "${renderOrchestratorPrompt(persona)}`;"
    )
    text = text.replace(
        "${getOrchestratorPrompt()}`;", "${renderOrchestratorPrompt(persona)}`;"
    )

    text = replace_function(text, "readPersonaMode", READ_PERSONA_FUNCTION)
    text = text.replace(
        'if (selected !== "gentleman" && selected !== "neutral") return;',
        "if (!PERSONA_OPTIONS.includes(selected as PersonaMode)) return;",
    )
    text = text.replace(
        'description: "Switch el Gentleman persona between gentleman and neutral.",',
        'description: "Switch el Gentleman persona between gentleman, neutral, and gentle-kozz.",',
    )

    required = [
        '"gentle-kozz"',
        "GENTLE_KOZZ_PERSONA_PROMPT",
        "renderOrchestratorPrompt(persona)",
        "PERSONA_OPTIONS.includes",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"extension patch missing required markers: {missing}")

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def activate_workspace_persona(workspace: Path) -> bool:
    path = workspace / ".pi" / "gentle-ai" / "persona.json"
    content = '{\n  "mode": "gentle-kozz"\n}\n'
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def validate(gentle_pi_dir: Path, workspace: Path) -> None:
    ext = (gentle_pi_dir / "extensions" / "gentle-ai.ts").read_text(encoding="utf-8")
    orch = (gentle_pi_dir / "assets" / "orchestrator.md").read_text(encoding="utf-8")
    assert '"gentle-kozz"' in ext
    assert "warm neutral Lima Spanish" in ext
    assert "GENTLE_KOZZ_PERSONA_PROMPT" in ext
    assert ORCH_SPANISH_RULE in orch
    assert ORCH_LANGUAGE_RULE in orch
    assert "Rioplatense" not in orch
    assert "voseo" not in orch
    persona_path = workspace / ".pi" / "gentle-ai" / "persona.json"
    assert persona_path.exists()
    assert "gentle-kozz" in persona_path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gentle-pi-dir", type=Path, default=DEFAULT_GENTLE_PI_DIR)
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ext = args.gentle_pi_dir / "extensions" / "gentle-ai.ts"
    orch = args.gentle_pi_dir / "assets" / "orchestrator.md"
    if not ext.exists() or not orch.exists():
        raise SystemExit(
            f"gentle-pi package files not found under {args.gentle_pi_dir}"
        )

    if args.dry_run:
        # Patch copies in memory-equivalent temp strings by writing nowhere: validate current state only.
        validate(args.gentle_pi_dir, args.workspace)
        print("dry-run ok: current install already contains gentle-kozz mod")
        return

    changed = []
    if patch_orchestrator(orch):
        changed.append(str(orch))
    if patch_extension(ext):
        changed.append(str(ext))
    if activate_workspace_persona(args.workspace):
        changed.append(str(args.workspace / ".pi" / "gentle-ai" / "persona.json"))
    validate(args.gentle_pi_dir, args.workspace)
    print("gentle-kozz mod applied")
    if changed:
        print("changed:")
        for item in changed:
            print(f"- {item}")
    else:
        print("changed: none (already applied)")


if __name__ == "__main__":
    main()
