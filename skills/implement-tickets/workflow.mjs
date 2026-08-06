export const meta = {
	name: "implement-tickets",
	description: "Implement a resolved ticket set one at a time, each in a fresh /implement worker",
	whenToUse:
		"When a spec's tickets have been ordered by plan.mjs and the whole set should be built end to end, sequentially.",
	phases: [{ title: "Implement", detail: "one worker per ticket, strictly sequential" }],
};

// Ordering is not decided here. `plan.mjs` resolved the blocking graph before
// this script started and its tickets arrive as `args` — workflow scripts have
// no filesystem access, and the graph only needs resolving once anyway.
//
// There is deliberately no gate. `/implement` owns tests, review and commit for
// its own ticket; re-checking that from out here is the second gate that makes
// these loops brittle. The worker's own report is the signal.

const REPORT = {
	type: "object",
	properties: {
		completed: {
			type: "boolean",
			description: "True only if the work is implemented, verified, reviewed and committed.",
		},
		summary: { type: "string", description: "What changed, in one or two sentences." },
		verification: {
			type: "string",
			description: "The type-check and test commands run, and their results.",
		},
		review: { type: "string", description: "The /code-review outcome." },
		commit: {
			type: "string",
			description: "Commit SHA on the current branch, or empty if nothing was committed.",
		},
		blocker: {
			type: "string",
			description: "When completed is false, the one condition needed to proceed. Empty otherwise.",
		},
	},
	required: ["completed", "summary", "verification", "review", "commit", "blocker"],
	additionalProperties: false,
};

const plan = args ?? {};
const specRef = plan.specRef ?? null;
const all = plan.tickets ?? [];

if (!all.length) {
	throw new Error("args must carry plan.mjs tickets: [{ id, title, source, done }]");
}

// Tickets the planner already considers done are skipped, so a re-run after an
// interruption resumes rather than rebuilds.
const pending = all.filter((t) => !t.done);
const skipped = all.length - pending.length;
if (skipped) log(`${skipped} already done; ${pending.length} to implement`);

phase("Implement");

const implemented = [];
let halted = null;

// Sequential by construction. Each worker inherits its predecessors' work
// through commits on the shared branch, so there is nothing to parallelise.
for (const ticket of pending) {
	const prompt = [
		`Use /implement to implement ${ticket.source}.`,
		specRef ? `The governing spec is ${specRef}.` : null,
		"Report what you changed, the verification you ran and its result, the review outcome, and the commit SHA.",
	]
		.filter(Boolean)
		.join(" ");

	const report = await agent(prompt, {
		label: `ticket-${ticket.id}`,
		phase: "Implement",
		schema: REPORT,
	});

	// A null report means the worker died or was skipped. Treat it as incomplete:
	// the next ticket may depend on this commit.
	if (!report || !report.completed) {
		halted = {
			ticket: ticket.id,
			title: ticket.title,
			blocker: report?.blocker || "worker produced no result",
		};
		log(`halted at ticket ${ticket.id}: ${halted.blocker}`);
		break;
	}

	implemented.push({
		ticket: ticket.id,
		title: ticket.title,
		commit: report.commit,
		summary: report.summary,
		verification: report.verification,
		review: report.review,
	});
	log(`ticket ${ticket.id} complete (${report.commit || "no SHA reported"})`);
}

const notReached = pending.slice(implemented.length + (halted ? 1 : 0)).map((t) => t.id);
if (notReached.length) log(`not reached: ${notReached.join(", ")}`);

return {
	order: pending.map((t) => t.id),
	implemented,
	halted,
	notReached,
	// Said plainly so a clean report is not mistaken for verified work: every
	// claim above is the worker's own, not an independent check.
	verifiedBy: "worker self-report; no external gate",
};
