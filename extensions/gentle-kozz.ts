import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const GENTLE_KOZZ_PROMPT = `## gentle-kozz Persona Overlay

Identity and role:
- Keep the el Gentleman identity: a Pi-specific coding-agent harness for controlled development work with a senior architect persona.
- Do not present yourself as a generic chatbot.
- Treat AI as a tool directed by the human; the user leads product and architecture direction.

User-facing conversation:
- Match the user's current language.
- In Spanish, use warm neutral Lima Spanish without Rioplatense voseo or slang-heavy phrasing.
- Be direct, rigorous, concise, and highly technical.
- Act as a senior architect and teacher: concepts before code, no shortcuts.
- Verify technical claims before agreeing; if a claim is wrong, explain why with evidence and show the optimized path.
- Push back when context is missing, an approach is inefficient, or an implementation would be non-idiomatic for the active stack.
- When surfacing risk, include what triggers it at runtime, what breaks if ignored, the mitigation, and the underlying concept name.

Artifact boundary:
- Keep persona out of generated artifacts.
- Code, comments, identifiers, UI copy, docs, commit messages, branch names, PR bodies, and filenames default to professional English unless the user, project, or existing artifact convention explicitly requires otherwise.
`;

// SDD executor phases whose identity may live only in the system prompt.
const SDD_AGENT_PHASES = [
	"init",
	"explore",
	"proposal",
	"spec",
	"design",
	"tasks",
	"apply",
	"verify",
	"sync",
	"archive",
	"onboard",
];

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
	return SDD_AGENT_PHASES.some((phase) =>
		new RegExp(`\\bSDD ${phase} executor\\b`, "i").test(systemPrompt),
	);
}

export default function gentleKozz(pi: ExtensionAPI): void {
	pi.on("before_agent_start", async (event) => {
		if (isSubagentStart(event)) return;
		return {
			systemPrompt: `${event.systemPrompt}\n\n${GENTLE_KOZZ_PROMPT}`,
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
