#!/usr/bin/env node
// Mechanical completion gate for the implementation-loop skill.
//
// Decides whether a delegated ticket is actually done using repository facts,
// not the sub-agent's prose report. Passing appends a journal entry, which is
// what makes a restarted loop resume instead of re-deciding.
//
// Usage:
//   gate.mjs --ticket 03 --baseline <sha> --journal <path> \
//            [--repo <dir>] [--verify "<cmd>"]... [--criteria <ticket.md>]
//
// Exit 0 => ticket closed and journalled. Exit 1 => JSON naming the failed
// checks; feed exactly those back to the same sub-agent.

import { appendFileSync, readFileSync } from "node:fs";
import { execFileSync, execSync } from "node:child_process";
import { relative, resolve } from "node:path";

function parseArgs(argv) {
	const args = {
		ticket: null,
		baseline: null,
		journal: null,
		repo: process.cwd(),
		verify: [],
		criteria: null,
	};
	for (let i = 0; i < argv.length; i++) {
		const flag = argv[i];
		if (flag === "--ticket") args.ticket = argv[++i];
		else if (flag === "--baseline") args.baseline = argv[++i];
		else if (flag === "--journal") args.journal = argv[++i];
		else if (flag === "--repo") args.repo = argv[++i];
		else if (flag === "--verify") args.verify.push(argv[++i]);
		else if (flag === "--criteria") args.criteria = argv[++i];
		else throw new Error(`unknown flag: ${flag}`);
	}
	for (const required of ["ticket", "baseline", "journal"]) {
		if (!args[required]) throw new Error(`--${required} is required`);
	}
	return args;
}

function git(repo, ...gitArgs) {
	return execFileSync("git", gitArgs, { cwd: repo, encoding: "utf8" }).trim();
}

function main() {
	const args = parseArgs(process.argv.slice(2));
	const checks = [];
	const fail = (name, detail) => checks.push({ name, ok: false, detail });
	const pass = (name, detail) => checks.push({ name, ok: true, detail });

	const head = git(args.repo, "rev-parse", "HEAD");
	const branch = git(args.repo, "rev-parse", "--abbrev-ref", "HEAD");

	// 1. New commits exist on the current branch since dispatch. rev-list is
	//    directional, so a reset or a detached rewind fails here rather than
	//    passing on a bare "HEAD changed" comparison.
	const newCommits = git(args.repo, "rev-list", "--count", `${args.baseline}..HEAD`);
	if (Number(newCommits) > 0) {
		pass("committed", `${newCommits} new commit(s) on ${branch}`);
	} else {
		fail("committed", `no new commits on ${branch} since ${args.baseline.slice(0, 12)}`);
	}

	// 2. Nothing left uncommitted — a dirty tree means the next ticket's agent
	//    would inherit half-finished work it did not author. The journal itself
	//    is exempt: it is loop bookkeeping, and failing on it would make an
	//    in-repo journal permanently un-passable.
	const journalRel = relative(resolve(args.repo), resolve(args.journal));
	const dirty = git(args.repo, "status", "--porcelain")
		.split("\n")
		.filter((l) => l.trim() && l.slice(3).replace(/^"|"$/g, "") !== journalRel);
	if (dirty.length) fail("clean-tree", dirty.slice(0, 20).join("\n"));
	else pass("clean-tree", "working tree clean");

	// 3. Acceptance criteria ticked in the ticket source, when the ticket format
	//    carries checkboxes and the caller opted in.
	if (args.criteria) {
		const body = readFileSync(args.criteria, "utf8");
		const boxes = body.split("\n").filter((l) => /^\s*[-*]\s*\[[ xX]\]/.test(l));
		const unticked = boxes.filter((l) => /\[\s\]/.test(l));
		if (boxes.length === 0) fail("criteria", `no acceptance criteria found in ${args.criteria}`);
		else if (unticked.length)
			fail("criteria", `${unticked.length}/${boxes.length} unticked:\n${unticked.join("\n")}`);
		else pass("criteria", `${boxes.length}/${boxes.length} ticked`);
	}

	// 4. Project verification. Run last: it is the slowest and the previous
	//    checks already prove there is something worth verifying.
	for (const cmd of args.verify) {
		try {
			execSync(cmd, { cwd: args.repo, encoding: "utf8", stdio: "pipe" });
			pass("verify", cmd);
		} catch (err) {
			const out = `${err.stdout ?? ""}${err.stderr ?? ""}`.trim().split("\n").slice(-40).join("\n");
			fail("verify", `${cmd} exited ${err.status}\n${out}`);
		}
	}

	const failed = checks.filter((c) => !c.ok);
	const result = {
		ticket: args.ticket,
		ok: failed.length === 0,
		branch,
		commit: head,
		commits: git(args.repo, "rev-list", `${args.baseline}..HEAD`).split("\n").filter(Boolean),
		checks,
	};

	if (result.ok) {
		appendFileSync(
			args.journal,
			JSON.stringify({ ...result, verifiedAt: new Date().toISOString() }) + "\n",
		);
	}

	process.stdout.write(JSON.stringify(result, null, 2) + "\n");
	process.exit(result.ok ? 0 : 1);
}

try {
	main();
} catch (err) {
	process.stdout.write(JSON.stringify({ ok: false, error: String(err.message ?? err) }, null, 2) + "\n");
	process.exit(1);
}
