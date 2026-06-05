import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const GENTLE_KOZZ_PROMPT = `## gentle-kozz Persona Overlay

Identity and role:
- Keep the el Gentleman identity: a Pi-specific coding-agent harness for controlled development work with a senior architect persona.
- Do not present yourself as a generic chatbot.
- Treat AI as a tool directed by the human; the user leads product and architecture direction.

User-facing conversation:
- Match the user's current language.
- In Spanish, use neutral Spanish without Rioplatense voseo or slang-heavy phrasing.
- Be direct, rigorous, concise, and highly technical.
- Act as a senior architect and teacher: concepts before code, no shortcuts.
- Verify technical claims before agreeing; if a claim is wrong, explain why with evidence and show the optimized path.
- Push back when context is missing, an approach is inefficient, or an implementation would be non-idiomatic for the active stack.
- When surfacing risk, include what triggers it at runtime, what breaks if ignored, the mitigation, and the underlying concept name.

Artifact boundary:
- Keep persona out of generated artifacts.
- Code, comments, identifiers, UI copy, docs, commit messages, branch names, PR bodies, and filenames default to professional English unless the user, project, or existing artifact convention explicitly requires otherwise.
`;

// Rules that are NOT already present in the gentle-pi base prompt.
// We append these only when merging, avoiding duplication.
const GENTLE_KOZZ_ADDITIONS = `## gentle-kozz additions
- Verify technical claims before agreeing; if a claim is wrong, explain why with evidence and show the optimized path.
- When surfacing risk, include what triggers it at runtime, what breaks if ignored, the mitigation, and the underlying concept name.
- Keep persona out of generated artifacts. Code, comments, identifiers, UI copy, docs, commit messages, branch names, PR bodies, and filenames default to professional English unless the user, project, or existing artifact convention explicitly requires otherwise.`;

const SDD_AGENT_PHASE_PATTERN =
	/\bSDD (init|explore|proposal|spec|design|tasks|apply|verify|sync|archive|onboard) executor\b/i;

function readStringPath(source: unknown, path: string[]): string | undefined {
	let current: unknown = source;
	for (const key of path) {
		if (current === null || typeof current !== "object") return undefined;
		current = (current as Record<string, unknown>)[key];
	}
	return typeof current === "string" ? current : undefined;
}

function readAgentNames(event: unknown): string[] {
	return [
		readStringPath(event, ["agentName"]),
		readStringPath(event, ["agent"]),
		readStringPath(event, ["name"]),
		readStringPath(event, ["agent", "name"]),
		readStringPath(event, ["subagent", "name"]),
	]
		.filter((value): value is string => value !== undefined)
		.map((value) => value.trim())
		.filter((value) => value.length > 0);
}

// The persona overlay is conversational: it must apply only to the main
// interactive agent. Any named subagent (SDD phase executor, delegate, etc.)
// must keep its task-specific prompt unpolluted.
function isSubagentStart(event: unknown): boolean {
	if (readAgentNames(event).length > 0) return true;
	const systemPrompt = readStringPath(event, ["systemPrompt"]) ?? "";
	return SDD_AGENT_PHASE_PATTERN.test(systemPrompt);
}

/**
 * Merge the gentle-kozz overlay into the base system prompt.
 *
 * When gentle-pi has already injected its base `gentleman` prompt, we
 * surgically replace the conflicting Rioplatense-voseo rules with the
 * gentle-kozz Lima-Spanish rules and append only the genuinely new rules.
 * This avoids the contradiction the LLM sees when two Spanish-style
 * directives are stacked, and it cuts prompt bloat by ~60 %.
 *
 * If the base prompt is not the gentle-pi `gentleman` prompt (e.g. another
 * package is active), we fall back to concatenating the full overlay.
 */
function applyGentleKozzOverlay(basePrompt: string): string {
	// Already merged in a previous pass (should not happen, but guard anyway).
	if (basePrompt.includes("## gentle-kozz")) return basePrompt;

	// Detect the gentle-pi base prompt by its header.
	if (basePrompt.includes("## el Gentleman Identity and Harness")) {
		const merged = basePrompt
			.replace(
				/When the user writes Spanish, answer in natural Rioplatense Spanish with voseo\./g,
				"Match the user's current language. In Spanish, use neutral Spanish without regional voseo or slang-heavy phrasing.",
			)
			.replace(
				/- Keep the response in the user's language; in Spanish, use natural Rioplatense voseo\./g,
				"- Keep the response in the user's language; in Spanish, use neutral Spanish without regional voseo or slang-heavy phrasing.",
			)
			.replace(
				/User-facing conversation should stay in the user's language\. In `gentleman` mode, Spanish uses natural Rioplatense voseo\./g,
				"User-facing conversation should stay in the user's language. In `gentle-kozz` mode, Spanish uses neutral Spanish without regional voseo or slang-heavy phrasing.",
			);

		// Sanity check: if the upstream prompt changed its wording (e.g. swapped
		// "Rioplatense" for "Argentine" or "Porteño") and our .replace() calls
		// failed to match, we fall back to concatenating the full overlay. This
		// is a last-line-of-defence check; it cannot catch every future upstream
		// rephrase, but it prevents silently leaving a voseo directive active.
		if (merged.includes("Rioplatense")) {
			return `${basePrompt}\n\n${GENTLE_KOZZ_PROMPT}`;
		}

		return `${merged}\n\n${GENTLE_KOZZ_ADDITIONS}`;
	}

	// Fallback for non-gentle-pi base prompts.
	return `${basePrompt}\n\n${GENTLE_KOZZ_PROMPT}`;
}

export default function gentleKozz(pi: ExtensionAPI): void {
	pi.on("before_agent_start", (event) => {
		if (isSubagentStart(event)) return;
		return {
			systemPrompt: applyGentleKozzOverlay(event.systemPrompt),
		};
	});

	pi.registerCommand("gentle-kozz", {
		description:
			"Confirm that the gentle-kozz persona overlay extension is active.",
		handler: async (_args, ctx) => {
			ctx.ui.notify("gentle-kozz persona overlay is active.", "info");
		},
	});
}
