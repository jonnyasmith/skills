// Fake-driven tests for driver.mjs. plan.mjs, gate.mjs and git are real; only
// the host capabilities (agent, hub) are faked, so these cover the control flow
// the driver is responsible for.

import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runLoop } from "./driver.mjs";

const SCRIPTS = process.env.LOOP_SCRIPTS ?? `${process.env.HOME}/.claude/skills/implementation-loop/scripts`;

const sh = (cwd, cmd, args) => execFileSync(cmd, args, { cwd, encoding: "utf8" }).trim();

function scaffold(tickets) {
	const root = mkdtempSync(join(tmpdir(), "loop-test-"));
	const issues = join(root, "issues");
	mkdirSync(issues);
	for (const [n, title, blocked] of tickets) {
		writeFileSync(
			join(issues, `${n}-${title.toLowerCase().replace(/\W+/g, "-")}.md`),
			`# ${n} — ${title}\n\n**Blocked by:** ${blocked}\n\n**Status:** ready-for-agent\n\n- [ ] does the thing\n`,
		);
	}
	sh(root, "git", ["init", "-q", "-b", "main"]);
	sh(root, "git", ["config", "user.email", "t@t"]);
	sh(root, "git", ["config", "user.name", "t"]);
	writeFileSync(join(root, "seed.txt"), "seed\n");
	sh(root, "git", ["add", "-A"]);
	sh(root, "git", ["commit", "-qm", "seed"]);
	return { root, issues, journal: join(root, "journal.jsonl") };
}

const results = [];
function check(name, cond, detail = "") {
	results.push({ name, ok: !!cond, detail });
	console.log(`${cond ? "PASS" : "FAIL"}  ${name}${cond ? "" : `\n      ${detail}`}`);
}

// ---------------------------------------------------------------- happy path
{
	const { root, issues, journal } = scaffold([
		["01", "Expand", "None"],
		["02", "Migrate", "01"],
		["03", "Contract", "02"],
	]);
	const dispatched = [];
	const out = await runLoop(
		{
			agent: async (prompt) => {
				dispatched.push(prompt);
				writeFileSync(join(root, `f${dispatched.length}.txt`), "x");
				sh(root, "git", ["add", "-A"]);
				sh(root, "git", ["commit", "-qm", `work ${dispatched.length}`]);
				return { id: `Ticket-${dispatched.length}`, handle: "agent://x", text: "done" };
			},
			hub: async () => ({}),
		},
		{ scriptsDir: SCRIPTS, ticketsDir: issues, journal, repo: root, verify: ["test -f seed.txt"] },
	);
	check("happy: ok", out.ok, JSON.stringify(out.abort));
	check("happy: all three completed", out.completed.length === 3, String(out.completed.length));
	check("happy: dependency order", out.completed.map((c) => c.id).join(",") === "1,2,3", out.completed.map((c) => c.id).join(","));
	check("happy: prompt shape", dispatched[0].startsWith("Use /implement to implement ") && dispatched[0].includes("01-expand.md"), dispatched[0]);
	check("happy: distinct commits", new Set(out.completed.map((c) => c.commit)).size === 3);
	check("happy: no follow-ups", out.completed.every((c) => c.followUps === 0));
	rmSync(root, { recursive: true, force: true });
}

// ------------------------------------------- gate fails, follow-up repairs it
{
	const { root, issues, journal } = scaffold([["01", "Only", "None"]]);
	let hubCalls = 0;
	const out = await runLoop(
		{
			// leaves the tree dirty: commits nothing
			agent: async () => {
				writeFileSync(join(root, "stray.txt"), "uncommitted");
				return { id: "Ticket-1", handle: "agent://x", text: "done (badly)" };
			},
			hub: async ({ message }) => {
				hubCalls++;
				check("followup: names only failed checks", message.includes("committed") && message.includes("clean-tree") && !message.includes("verify:"), message);
				sh(root, "git", ["add", "-A"]);
				sh(root, "git", ["commit", "-qm", "fix"]);
				return {};
			},
		},
		{ scriptsDir: SCRIPTS, ticketsDir: issues, journal, repo: root },
	);
	check("followup: ok after repair", out.ok, JSON.stringify(out.abort));
	check("followup: hub called once", hubCalls === 1, String(hubCalls));
	check("followup: recorded on ticket", out.completed[0]?.followUps === 1);
	rmSync(root, { recursive: true, force: true });
}

// ------------------------------------------------- gate never passes: abort
{
	const { root, issues, journal } = scaffold([
		["01", "Never", "None"],
		["02", "Later", "01"],
	]);
	let dispatches = 0;
	const out = await runLoop(
		{
			agent: async () => {
				dispatches++;
				return { id: "Ticket-1", handle: null, text: "did nothing" };
			},
			hub: async () => ({}),
		},
		{ scriptsDir: SCRIPTS, ticketsDir: issues, journal, repo: root, maxFollowUps: 1 },
	);
	check("abort: not ok", out.ok === false);
	check("abort: reason gate-failed", out.abort?.reason === "gate-failed", JSON.stringify(out.abort));
	check("abort: names the check", out.abort?.failed?.some((f) => f.name === "committed"));
	check("abort: never advanced to ticket 2", dispatches === 1 && out.completed.length === 0, `dispatches=${dispatches}`);
	check("abort: frontier untouched", out.remaining === 2, String(out.remaining));
	rmSync(root, { recursive: true, force: true });
}

// -------------------------------------------------- unsound graph: no spawns
{
	const { root, issues, journal } = scaffold([
		["01", "A", "03"],
		["02", "B", "01"],
		["03", "C", "02"],
	]);
	let dispatches = 0;
	const out = await runLoop(
		{ agent: async () => { dispatches++; return {}; }, hub: async () => ({}) },
		{ scriptsDir: SCRIPTS, ticketsDir: issues, journal, repo: root },
	);
	check("cycle: reason plan-error", out.abort?.reason === "plan-error", JSON.stringify(out.abort));
	check("cycle: nothing dispatched", dispatches === 0, String(dispatches));
	check("cycle: reports the cycle", String(out.abort?.errors).includes("cycle"), String(out.abort?.errors));
	rmSync(root, { recursive: true, force: true });
}

// --------------------------------- journal that never records: stall guard
{
	const { root, issues } = scaffold([["01", "Loop", "None"]]);
	let dispatches = 0;
	const out = await runLoop(
		{
			agent: async () => {
				dispatches++;
				writeFileSync(join(root, `f${dispatches}.txt`), "x");
				sh(root, "git", ["add", "-A"]);
				sh(root, "git", ["commit", "-qm", `w${dispatches}`]);
				return { id: "Ticket-1", handle: null, text: "ok" };
			},
			hub: async () => ({}),
		},
		{ scriptsDir: SCRIPTS, ticketsDir: issues, journal: "/dev/null", repo: root },
	);
	check("stall: detected", out.abort?.reason === "stalled", JSON.stringify(out.abort));
	check("stall: caught before any redispatch", dispatches === 1, String(dispatches));
	rmSync(root, { recursive: true, force: true });
}

const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} passed`);
process.exit(failed.length ? 1 : 0);
