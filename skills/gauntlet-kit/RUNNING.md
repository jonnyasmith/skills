# Arming the run

What the user does after pasting `PROMPT.md`, and what to watch. These are host settings and operator timing; no line of the prompt reaches them.

## Before the paste

```bash
omp config set compaction.methodOrder '[snapcompact, shake, remote, soft]'
omp config set compaction.thresholdPercent 75
```

`snapcompact` archives history locally with no summarizer call and survives an overflow; `shake` turns large tool results into recoverable `artifact://` references. Both are local, so neither costs a round-trip mid-round.

Leave `compaction.idleEnabled` off. A lead running this loop waits in bursts of tens of seconds, far under the idle timer, so it would never fire.

## During the run

The lead is a switchboard. In a measured two-hour run of this shape, 91 of its 219 tool calls were `hub`: strict alternation of one `send` to one named subagent, then one `wait` that returned one message. That is the loop working, not the loop stuck.

Compact **between waves**: after a wave's critics have reported and before the next dispatch. That is the only moment the lead holds no half-finished promise. `/handoff` or `/compact` there is safe because the progress page holds the state; mid-round it is survivable only because of that page, which is why its re-read discipline is in the prompt.

Worth watching, in order of how much it costs when it goes wrong:

| Watch | Healthy | Wrong |
| --- | --- | --- |
| The lead's own edits | none | it granted itself the shared file and is now both author and arbiter |
| Ownership messages | a few in the first minutes | still arriving in round three: the up-front ownership list was never written |
| Critic scores | discriminating, some below pass | every piece 8 or above on round one, which means the bar is too easy or the critic read a report |
| A repeated biggest gap | named once | named twice: the piece is stalled and further rounds buy nothing |
| Subagent context | builders compacting themselves | a builder past 200,000 tokens with no compaction yet, about to lose its own item list |

`--advisor` adds a second critic over the lead itself, which is the only check on the lead's decisions.

## After the run

The decisions the lead recorded on the progress page are the run's durable output, alongside the work. Fold the machine facts it discovered — how to launch the probe, which flag the build needs, what fails silently — into wherever this project keeps them, so the next run does not re-derive them. Leave taste and verdicts out: a critic that reads last round's score is an anchored critic.
