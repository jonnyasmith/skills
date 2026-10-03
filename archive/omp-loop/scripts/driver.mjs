// Deterministic driver for the implementation-loop, for omp's `eval` runtime.
//
// The loop's decisions already live in plan.mjs/gate.mjs. This turns the
// remaining prose — "dispatch next", "never advance on a failed gate" — into
// control flow, so there is no execution path that skips a gate or reorders a
// frontier. Intermediate sub-agent reports stay in local variables instead of
// accumulating in the host transcript.
//
// Host-side capabilities arrive as injected dependencies rather than globals:
// the eval prelude installs `agent`/`tool` in the cell scope, and an imported
// module cannot rely on seeing them. Injection also makes the loop testable
// with fakes, outside any harness.
//
// Usage from an eval cell (see the omp-loop SKILL.md):
//   const { runLoop } = await import(
//     `${process.env.HOME}/.claude/skills/omp-loop/scripts/driver.mjs`);
//   return await runLoop({ agent, hub: (a) => tool.hub(a), log }, { ...config });

import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

// plan.mjs and gate.mjs belong to the implementation-loop skill; this driver
// only executes them. Default to the sibling skill so a caller supplies paths
// only when the scripts live somewhere else.
const SIBLING_SCRIPTS = resolve(
	dirname(fileURLToPath(import.meta.url)),
	"../../implementation-loop/scripts",
);

const DEFAULTS = {
	scriptsDir: SIBLING_SCRIPTS,
	ticketsDir: null, // one of ticketsDir / ticketsJson
	ticketsJson: null,
	journal: null, // required
	repo: process.cwd(),
	verify: [], // shell commands the gate must see exit 0
	requireCriteria: false, // pass --criteria for local ticket files
	order: null, // explicit user order, ids comma-joined
	specRef: null, // appended to the prompt when tickets don't link the spec
	agentType: undefined, // omp agent type; undefined = default `task`
	maxFollowUps: 1, // gate retries per ticket before aborting
	maxTickets: 100, // hard stop; a runaway loop burns real money
};

function required(config, key) {
	if (!config[key]) throw new Error(`config.${key} is required`);
	return config[key];
}

// Run a script and hand back parsed stdout plus the exit code. Both scripts
// print JSON on stdout in success and failure, so a non-zero exit is data, not
// an exception.
function runScript(argv, cwd) {
	try {
		const stdout = execFileSync("node", argv, { cwd, encoding: "utf8", stdio: "pipe" });
		return { code: 0, json: JSON.parse(stdout) };
	} catch (err) {
		const stdout = String(err.stdout ?? "");
		let json = null;
		try {
			json = JSON.parse(stdout);
		} catch {
			/* non-JSON failure, e.g. node itself blew up */
		}
		if (json === null) {
			throw new Error(
				`${argv[0]} failed with no JSON output (exit ${err.status}): ${String(err.stderr ?? "").trim() || stdout.trim()}`,
			);
		}
		return { code: err.status ?? 1, json };
	}
}

function git(repo, ...args) {
	return execFileSync("git", args, { cwd: repo, encoding: "utf8" }).trim();
}

function failedChecks(gate) {
	return (gate.checks ?? []).filter((c) => !c.ok);
}

// The follow-up names only the failed checks. Anything more re-litigates work
// the sub-agent already did and invites it to churn.
function followUpMessage(gate) {
	const lines = failedChecks(gate).map((c) => `- ${c.name}: ${c.detail}`);
	return [
		"Your ticket did not pass the completion gate. Unmet checks only:",
		...lines,
		"",
		"Fix exactly these, commit to the current branch, and leave the working tree clean. Do not start other work.",
	].join("\n");
}

export async function runLoop(deps, userConfig = {}) {
	const { agent, hub, log = () => {} } = deps;
	if (typeof agent !== "function") throw new Error("deps.agent is required");

	const config = { ...DEFAULTS, ...userConfig };
	required(config, "scriptsDir");
	required(config, "journal");
	if (!config.ticketsDir === !config.ticketsJson) {
		throw new Error("pass exactly one of config.ticketsDir or config.ticketsJson");
	}

	const planArgv = [
		`${config.scriptsDir}/plan.mjs`,
		...(config.ticketsDir ? ["--dir", config.ticketsDir] : ["--json", config.ticketsJson]),
		"--journal",
		config.journal,
		...(config.order ? ["--order", config.order] : []),
	];

	const completed = [];
	let abort = null;
	let lastTicketId = null;
	let plan = null;

	for (let iteration = 0; iteration < config.maxTickets; iteration++) {
		const planned = runScript(planArgv, config.repo);
		plan = planned.json;

		if (planned.code !== 0) {
			// An unsound graph is a defect in the tickets. Repairing it by
			// inference would silently change what gets built.
			abort = { reason: "plan-error", errors: plan.errors };
			break;
		}
		if (!plan.next) break; // frontier empty: every ticket done

		const ticket = plan.next;

		// A ticket reappearing after its own passing gate means the journal is
		// not where the planner is reading from. Without this the loop would
		// re-dispatch the same work forever.
		if (ticket.id === lastTicketId) {
			abort = {
				reason: "stalled",
				ticket,
				detail: `ticket ${ticket.id} was gated green but is still on the frontier; check that --journal matches between plan and gate`,
			};
			break;
		}

		const baseline = git(config.repo, "rev-parse", "HEAD");
		const label = `Ticket-${ticket.id}`;
		log(`[${iteration + 1}/${plan.total}] dispatching ticket ${ticket.id}: ${ticket.title}`);

		const prompt = [
			`Use /implement to implement ${ticket.source}.`,
			config.specRef ? `The governing spec is ${config.specRef}.` : null,
		]
			.filter(Boolean)
			.join(" ");

		let report;
		// The bridge validates option presence, not just value: an explicit
		// `agent: undefined` is rejected outright, so the key must be absent.
		const spawnOpts = { label, handle: true };
		if (config.agentType) spawnOpts.agent = config.agentType;
		try {
			report = await agent(prompt, spawnOpts);
		} catch (err) {
			abort = { reason: "agent-failed", ticket, detail: String(err.message ?? err) };
			break;
		}

		const gateArgv = [
			`${config.scriptsDir}/gate.mjs`,
			"--ticket",
			ticket.id,
			"--baseline",
			baseline,
			"--journal",
			config.journal,
			"--repo",
			config.repo,
			...(config.requireCriteria && config.ticketsDir ? ["--criteria", ticket.source] : []),
			...config.verify.flatMap((cmd) => ["--verify", cmd]),
		];

		let gate = runScript(gateArgv, config.repo).json;
		let followUps = 0;

		while (!gate.ok && followUps < config.maxFollowUps) {
			followUps++;
			log(`  gate failed (${failedChecks(gate).map((c) => c.name).join(", ")}); follow-up ${followUps}`);
			if (typeof hub !== "function") break; // no messaging: fail fast rather than re-dispatch
			try {
				await hub({
					op: "send",
					to: report.id ?? label,
					message: followUpMessage(gate),
					await: true,
					i: `Following up on ticket ${ticket.id}`,
				});
			} catch (err) {
				abort = { reason: "follow-up-failed", ticket, detail: String(err.message ?? err) };
				break;
			}
			gate = runScript(gateArgv, config.repo).json;
		}
		if (abort) break;

		if (!gate.ok) {
			// Advancing here is the one failure the whole design exists to
			// prevent, so it is an abort, never a warning.
			abort = { reason: "gate-failed", ticket, followUps, failed: failedChecks(gate) };
			break;
		}

		log(`  ticket ${ticket.id} green at ${gate.commit.slice(0, 8)}`);
		completed.push({
			id: ticket.id,
			title: ticket.title,
			source: ticket.source,
			commit: gate.commit,
			commits: gate.commits,
			followUps,
			checks: gate.checks.map((c) => c.name),
			transcript: report.handle ?? null,
		});
		lastTicketId = ticket.id;
	}

	const finalPlan = runScript(planArgv, config.repo).json;

	return {
		ok: abort === null && (finalPlan.remaining ?? 0) === 0,
		completed,
		abort,
		order: finalPlan.order ?? plan?.order ?? [],
		remaining: finalPlan.remaining ?? null,
		verifiedBy: config.verify,
		unverifiedNote:
			config.verify.length === 0
				? "no --verify commands were supplied: tickets were gated on commit and clean tree only"
				: null,
	};
}
