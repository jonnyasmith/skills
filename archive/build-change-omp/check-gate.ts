// omp commit gate: runs check-gate.py (the Claude Code PreToolUse hook) on omp tool calls.
// Installed by the build-change skill as <repo>/.omp/hooks/pre/check-gate.ts, next to
// <repo>/.omp/hooks/check-gate.py. The skill replaces "__CHECK__" with the repo's check command.
// check-gate.py exit 2 blocks the tool call with its stderr as the reason.
import * as path from "node:path";
import type { HookAPI } from "@oh-my-pi/pi-coding-agent/extensibility/hooks";

const CHECK = "__CHECK__";
const GATE = path.join(import.meta.dir, "..", "check-gate.py");

// check-gate.py only protects .claude files. Also protect the omp gate and omp settings.
const OMP_GUARDED = /(^|\/)\.omp\/(hooks\/(pre\/check-gate\.ts|check-gate\.py)|settings\.json|config\.ya?ml)$/;

// Paths touched by a hashline `edit` patch: `[PATH#TAG]` headers and `MV DEST` ops.
function editPaths(patch: string): string[] {
	const paths: string[] = [];
	for (const m of patch.matchAll(/^\[(.+?)#[0-9A-Fa-f]{4}\]\s*$/gm)) paths.push(m[1]);
	for (const m of patch.matchAll(/^MV\s+"?(.+?)"?\s*$/gm)) paths.push(m[1]);
	return paths;
}

async function runGate(event: object, cwd: string): Promise<string | undefined> {
	const proc = Bun.spawn(["python3", GATE, CHECK], {
		cwd,
		stdin: new Blob([JSON.stringify(event)]),
		stdout: "pipe",
		stderr: "pipe",
	});
	const [code, stderr] = await Promise.all([proc.exited, new Response(proc.stderr).text()]);
	if (code === 2) return stderr.trim() || "check-gate: blocked";
	return undefined;
}

export default function checkGate(pi: HookAPI): void {
	pi.on("tool_call", async (event, ctx) => {
		const input = event.input as Record<string, unknown>;

		if (event.toolName === "bash") {
			const cwd = path.resolve(ctx.cwd, String(input.cwd ?? ""));
			const reason = await runGate(
				{ tool_name: "Bash", tool_input: { command: String(input.command ?? "") }, cwd },
				cwd,
			);
			return reason ? { block: true, reason } : undefined;
		}

		let files: string[];
		if (event.toolName === "write") files = [String(input.path ?? "")];
		else if (event.toolName === "edit") files = editPaths(String(input.input ?? ""));
		else return;

		for (const file of files) {
			const abs = path.resolve(ctx.cwd, file);
			if (OMP_GUARDED.test(abs)) {
				return {
					block: true,
					reason: "check-gate: the check gate and omp settings cannot be changed from inside a session. Ask the user.",
				};
			}
			const reason = await runGate(
				{ tool_name: event.toolName === "write" ? "Write" : "Edit", tool_input: { file_path: abs }, cwd: ctx.cwd },
				ctx.cwd,
			);
			if (reason) return { block: true, reason };
		}
	});
}
