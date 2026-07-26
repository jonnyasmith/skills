#!/usr/bin/env node
// Deterministic execution planner for the implementation-loop skill.
//
// Reads a ticket set, resolves blocking edges, rejects cycles and dangling
// references, and emits a total execution order. Same input always yields the
// same order: no model judgement participates.
//
// Usage:
//   plan.mjs --dir .scratch/<slug>/issues [--journal <path>] [--order 3,1,2]
//   plan.mjs --json tickets.json          [--journal <path>] [--order 3,1,2]
//
// --json expects `gh issue list --json number,title,body,state` output, or any
// array of { id|number, title, body, state?, url? }.
//
// Exit 0 with a plan on stdout; exit 1 with { errors: [...] } when the graph is
// unsound. Never mutates anything.

import { readFileSync, readdirSync } from "node:fs";
import { basename, join } from "node:path";

const NONE = /^\s*(none\b|n\/a\b|-\s*$|—)/i;

function parseArgs(argv) {
	const args = { dir: null, json: null, journal: null, order: null };
	for (let i = 0; i < argv.length; i++) {
		const flag = argv[i];
		if (flag === "--dir") args.dir = argv[++i];
		else if (flag === "--json") args.json = argv[++i];
		else if (flag === "--journal") args.journal = argv[++i];
		else if (flag === "--order") args.order = argv[++i];
		else throw new Error(`unknown flag: ${flag}`);
	}
	if (!args.dir === !args.json) throw new Error("pass exactly one of --dir or --json");
	return args;
}

// A ticket body carries its edges either inline (`**Blocked by:** 01, 02`) or as
// a section (`## Blocked by` followed by list items). Accept both; the two
// ticket templates in /to-tickets differ only in that shape.
function extractBlockedBy(body) {
	const inline = body.match(/^\s*\*{0,2}Blocked by:?\*{0,2}:?\s*(.+)$/im);
	if (inline) return splitRefs(inline[1]);

	const section = body.match(/^#{1,6}\s*Blocked by\s*$([\s\S]*?)(?=^#{1,6}\s|\Z)/im);
	if (section) {
		const items = section[1]
			.split("\n")
			.map((l) => l.replace(/^\s*[-*]\s*(\[[ xX]\]\s*)?/, "").trim())
			.filter(Boolean);
		return items.flatMap(splitRefs);
	}
	return [];
}

function splitRefs(text) {
	if (NONE.test(text)) return [];
	return text
		.split(/[,;]|\band\b/i)
		.map((s) => s.trim().replace(/^[-*]\s*/, "").replace(/\.$/, ""))
		.filter((s) => s && !NONE.test(s));
}

function extractCriteria(body) {
	return body
		.split("\n")
		.filter((l) => /^\s*[-*]\s*\[[ xX]\]/.test(l))
		.map((l) => ({
			text: l.replace(/^\s*[-*]\s*\[[ xX]\]\s*/, "").trim(),
			checked: /\[[xX]\]/.test(l),
		}));
}

function extractStatus(body) {
	const m = body.match(/^\s*\*{0,2}Status:?\*{0,2}:?\s*(.+)$/im);
	return m ? m[1].trim() : null;
}

function extractTitle(body, fallback) {
	const h1 = body.match(/^#\s+(.+)$/m);
	if (!h1) return fallback;
	// "# 03 — Build the thing" -> "Build the thing"
	return h1[1].replace(/^\s*\d+\s*[—–-]\s*/, "").trim();
}

function loadFromDir(dir) {
	return readdirSync(dir)
		.filter((f) => f.endsWith(".md"))
		.sort()
		.map((file) => {
			const body = readFileSync(join(dir, file), "utf8");
			const num = basename(file).match(/^(\d+)/);
			return {
				id: num ? String(Number(num[1])) : basename(file, ".md"),
				source: join(dir, file),
				title: extractTitle(body, basename(file, ".md")),
				body,
				state: null,
			};
		});
}

function loadFromJson(path) {
	const raw = JSON.parse(readFileSync(path, "utf8"));
	const list = Array.isArray(raw) ? raw : raw.tickets;
	if (!Array.isArray(list)) throw new Error("--json must hold an array of tickets");
	return list.map((t) => {
		const body = t.body ?? "";
		return {
			id: String(t.id ?? t.number),
			source: t.url ?? `#${t.id ?? t.number}`,
			title: t.title ?? extractTitle(body, String(t.id ?? t.number)),
			body,
			state: t.state ? String(t.state).toLowerCase() : null,
		};
	});
}

// Refs in the wild are "01", "1", "#12", a URL, or a bare title. Resolve to a
// canonical id or fail loudly — a silently dropped edge is the exact class of
// bug this script exists to prevent.
function buildResolver(tickets, errors) {
	const byId = new Map();
	const byTitle = new Map();
	for (const t of tickets) {
		if (byId.has(t.id)) errors.push(`duplicate ticket id "${t.id}" (${t.source})`);
		byId.set(t.id, t);
		const key = t.title.toLowerCase();
		if (byTitle.has(key)) byTitle.set(key, null); // ambiguous
		else byTitle.set(key, t);
	}
	return (ref, from) => {
		const num = ref.match(/(?:^|#|\/)(\d+)\s*$/);
		if (num) {
			const canonical = String(Number(num[1]));
			if (byId.has(canonical)) return canonical;
		}
		const exact = byTitle.get(ref.toLowerCase());
		if (exact) return exact.id;
		if (exact === null) {
			errors.push(`ticket ${from}: blocker "${ref}" matches more than one ticket title`);
			return null;
		}
		errors.push(`ticket ${from}: blocker "${ref}" matches no supplied ticket`);
		return null;
	};
}

function findCycle(ids, blockers) {
	const WHITE = 0;
	const GREY = 1;
	const BLACK = 2;
	const colour = new Map(ids.map((id) => [id, WHITE]));
	const stack = [];
	let cycle = null;

	const visit = (id) => {
		if (cycle) return;
		colour.set(id, GREY);
		stack.push(id);
		for (const dep of blockers.get(id)) {
			if (cycle) break;
			const c = colour.get(dep);
			if (c === GREY) cycle = [...stack.slice(stack.indexOf(dep)), dep];
			else if (c === WHITE) visit(dep);
		}
		stack.pop();
		colour.set(id, BLACK);
	};

	for (const id of ids) if (colour.get(id) === WHITE) visit(id);
	return cycle;
}

// How many tickets does finishing this one eventually unlock? Replaces the
// skill's subjective "prefer what unlocks the most work" with a number.
function unlockCounts(ids, dependents) {
	const memo = new Map();
	const reach = (id, seen = new Set()) => {
		if (memo.has(id)) return memo.get(id);
		const out = new Set();
		for (const child of dependents.get(id)) {
			if (seen.has(child)) continue;
			seen.add(child);
			out.add(child);
			for (const g of reach(child, seen)) out.add(g);
		}
		memo.set(id, out);
		return out;
	};
	return new Map(ids.map((id) => [id, reach(id).size]));
}

function compareIds(a, b) {
	const na = Number(a);
	const nb = Number(b);
	if (Number.isFinite(na) && Number.isFinite(nb) && na !== nb) return na - nb;
	return a < b ? -1 : a > b ? 1 : 0;
}

function loadJournal(path) {
	if (!path) return new Map();
	let raw;
	try {
		raw = readFileSync(path, "utf8");
	} catch {
		return new Map(); // absent journal = nothing done yet
	}
	const done = new Map();
	for (const line of raw.split("\n")) {
		if (!line.trim()) continue;
		const entry = JSON.parse(line);
		done.set(String(entry.ticket), entry);
	}
	return done;
}

function main() {
	const args = parseArgs(process.argv.slice(2));
	const errors = [];
	const tickets = args.dir ? loadFromDir(args.dir) : loadFromJson(args.json);
	if (tickets.length === 0) {
		process.stdout.write(JSON.stringify({ errors: ["no tickets found"] }, null, 2) + "\n");
		process.exit(1);
	}

	const resolve = buildResolver(tickets, errors);
	const ids = tickets.map((t) => t.id);
	const blockers = new Map(ids.map((id) => [id, new Set()]));
	const dependents = new Map(ids.map((id) => [id, new Set()]));

	for (const t of tickets) {
		for (const ref of extractBlockedBy(t.body)) {
			const dep = resolve(ref, t.id);
			if (dep === null) continue;
			if (dep === t.id) {
				errors.push(`ticket ${t.id}: blocks itself`);
				continue;
			}
			blockers.get(t.id).add(dep);
			dependents.get(dep).add(t.id);
		}
	}

	const cycle = findCycle(ids, blockers);
	if (cycle) errors.push(`blocking cycle: ${cycle.join(" -> ")}`);

	if (errors.length) {
		process.stdout.write(JSON.stringify({ errors }, null, 2) + "\n");
		process.exit(1);
	}

	const journal = loadJournal(args.journal);
	const explicit = args.order ? args.order.split(",").map((s) => s.trim()) : [];
	const unlocks = unlockCounts(ids, dependents);
	const rank = (id) => {
		const i = explicit.indexOf(id);
		return i === -1 ? Number.MAX_SAFE_INTEGER : i;
	};

	// Kahn with a total-order tie-break: explicit order, then transitive unlock
	// count desc, then id asc. No two ready tickets can ever compare equal.
	const remaining = new Set(ids);
	const satisfied = new Set();
	const order = [];
	while (remaining.size) {
		const ready = [...remaining].filter((id) =>
			[...blockers.get(id)].every((d) => satisfied.has(d)),
		);
		if (ready.length === 0) {
			errors.push("unsatisfiable graph: no ready ticket among remaining");
			break;
		}
		ready.sort(
			(a, b) => rank(a) - rank(b) || unlocks.get(b) - unlocks.get(a) || compareIds(a, b),
		);
		const next = ready[0];
		remaining.delete(next);
		satisfied.add(next);
		order.push(next);
	}

	if (errors.length) {
		process.stdout.write(JSON.stringify({ errors }, null, 2) + "\n");
		process.exit(1);
	}

	const byId = new Map(tickets.map((t) => [t.id, t]));
	const isDone = (id) => {
		if (journal.has(id)) return "journal";
		const t = byId.get(id);
		if (t.state === "closed") return "tracker-closed";
		const status = extractStatus(t.body);
		if (status && /^(done|complete[d]?|closed|merged)\b/i.test(status)) return "tracker-status";
		return null;
	};

	const plan = order.map((id) => {
		const t = byId.get(id);
		const criteria = extractCriteria(t.body);
		return {
			id,
			title: t.title,
			source: t.source,
			blockedBy: [...blockers.get(id)].sort(compareIds),
			unlocks: unlocks.get(id),
			criteria: criteria.length,
			criteriaChecked: criteria.filter((c) => c.checked).length,
			done: isDone(id),
			commit: journal.get(id)?.commit ?? null,
		};
	});

	const next = plan.find((p) => !p.done) ?? null;
	process.stdout.write(
		JSON.stringify(
			{
				errors: [],
				total: plan.length,
				remaining: plan.filter((p) => !p.done).length,
				order: plan.map((p) => p.id),
				next: next && { id: next.id, title: next.title, source: next.source },
				tickets: plan,
			},
			null,
			2,
		) + "\n",
	);
}

try {
	main();
} catch (err) {
	process.stdout.write(JSON.stringify({ errors: [String(err.message ?? err)] }, null, 2) + "\n");
	process.exit(1);
}
