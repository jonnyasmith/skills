# Issue tracker: Azure DevOps Boards

Issues and PRDs for this repo live as Azure DevOps Boards work items in the `<PROJECT>` project of the `<ORGANISATION>` organisation. Use the [`az`](https://learn.microsoft.com/en-us/cli/azure/) CLI with the `azure-devops` extension for all operations.

> **Authoring note (delete this block when the doc is written).** Unlike GitHub and GitLab, Azure DevOps has no single "issue" primitive: the work-item types, their hierarchy, their states, and the required classification fields all vary by the project's **process** (Basic / Agile / Scrum / CMMI, or an inherited variant). Every angle-bracket placeholder below must be resolved to a concrete value during `/setup-repo-skills` — discovered from the live board, then confirmed by the user. A doc shipped with placeholders intact is worse than no doc: an agent cannot tell "unconfigured" from "configured as `<EPIC_ID>`". Delete any section the board does not use.

## Configuration

Run commands inside this repository, and configure the defaults once:

```sh
az devops configure --defaults organization=https://dev.azure.com/<ORGANISATION> project="<PROJECT>"
```

Every work item this repo creates must carry these classification fields:

- **Area:** `<AREA_PATH>`
- **Iteration:** `<ITERATION_PATH>`

Pass them on every create:

```sh
--area "<AREA_PATH>" --iteration "<ITERATION_PATH>"
```

## Work-item types

This project runs the **`<PROCESS>`** process. The skills' vocabulary maps onto its types as:

| Skill concept | Work-item type | Notes |
| --- | --- | --- |
| Spec / PRD (`/to-spec`) | `<SPEC_TYPE>` | usually `Feature` |
| Ticket (`/to-tickets`) | `<TICKET_TYPE>` | the requirement tier: `User Story` (Agile), `Product Backlog Item` (Scrum), `Requirement` (CMMI), `Issue` (Basic) |
| Defect | `Bug` | |

A ticket is a vertical slice delivering end-to-end behaviour, so it belongs on the **requirement tier**, not on `Task`. `Task` stays free for whoever implements the ticket to decompose it — do not create Tasks from `/to-tickets`.

## Epic hierarchy

_(Only present when the board requires it. Delete this section otherwise.)_

Every `<SPEC_TYPE>` must be linked as a child of exactly one of these Epics:

| Epic | Work-item ID | Use for |
| --- | ---: | --- |
| `<EPIC_TITLE>` | `<EPIC_ID>` | `<one clause: the kind of outcome this Epic covers>` |

Choose the Epic from the work's **primary outcome**, not from the component being changed. If the correct Epic is genuinely ambiguous, ask rather than guess. After creating the item, add the parent link and verify it:

```sh
az boards work-item relation add --id <item-id> --relation-type parent --target-id <epic-id>
az boards work-item show --id <item-id> --expand relations
```

## Conventions

- **Create a work item**: `az boards work-item create --type "<TYPE>" --title "..." --description=@/tmp/wi-body.md --area "<AREA_PATH>" --iteration "<ITERATION_PATH>"`.

  **Pass long or punctuation-heavy content from a file, not inline.** Azure CLI core expands a `@`-prefixed argument into that file's contents by rewriting raw `argv` before argparse runs, so it works on every parameter of every command, extensions included. This is the only way to keep backticks, `$`, and quotes intact across both Bash and PowerShell — a spec body full of markdown will otherwise be mangled by the shell. Four hazards, none of them documented on Microsoft Learn:

  - **A missing file is a silent no-op** — the literal string `@/tmp/wi-body.md` is posted as the field value and the command exits `0`. Always guard with `test -s <path> || exit 1`.
  - Use the `--description=@<path>` form, not `--description @<path>`: expansion happens pre-argparse, so a body whose first character is `-` is otherwise parsed as a flag.
  - Trailing newlines are stripped; interior newlines survive verbatim.
  - A non-UTF-8 file is silently base64-encoded. Write UTF-8.
  - In PowerShell the `@` must be quoted (`'@body.md'`) — it is the splatting operator.

  **Descriptions are HTML, and the body format is fixed at creation.** `System.Description`, `Microsoft.VSTS.TCM.ReproSteps`, and `Microsoft.VSTS.Common.AcceptanceCriteria` are `html`-typed fields and default to HTML content; `az boards work-item` always writes HTML. Markdown is opt-in **per work item and per field**, is irreversible once saved, and has no process-, project-, or org-level setting. It requires the sibling patch op `{"op":"add","path":"/multilineFieldsFormat/System.Description","value":"Markdown"}`, which `az boards work-item` cannot emit — every op it builds is hardcoded to `/fields/{field}`.

  Only `az devops invoke` can send that op, and **only on the create call** — see [Markdown bodies](#markdown-bodies). There is no CLI route that patches an existing work item, so an item created with `az boards work-item create` is HTML for the rest of its life. **Decide the body format before the first write.** Retrofitting means deleting the item and recreating it.

  Azure DevOps does not convert Markdown placed in an HTML-format field: it stores the source and renders it as HTML, so `## Heading` and `- bullet` surface as literal text in one run-on paragraph. If the item is HTML-format, emit real HTML — convert the body yourself before posting.

- **Read a work item**: `az boards work-item show --id <id> --expand all` (includes fields, relations, and links).
- **List / search**: `az boards query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM workitems WHERE [System.TeamProject] = '<PROJECT>' AND [System.WorkItemType] = '<TYPE>' AND [System.State] <> 'Closed'"`. `az boards query` handles **flat** WIQL only — it reads the `workItems` key of the response. A `FROM workitemLinks` query returns `workItemRelations` instead and will not come back through this command; read links with `--expand relations` on the individual item instead.
- **Comment**: `az boards work-item update --id <id> --discussion "..."`.
- **Update fields**: `az boards work-item update --id <id> --fields "System.FieldName=value"`. `--fields` takes **space-separated** `field=value` pairs, so quote each pair as one token — a value containing spaces needs the whole pair inside the quotes. The split is on the **first** `=`, so a value may itself contain `=`. Use reference names (`System.Tags`), not friendly names. `field=@/tmp/value.txt` also works.
- **Triage labels** live in `System.Tags`, separated by `; `. **Writing tags is destructive** — `System.Tags` is a scalar string, so a patch to it replaces the entire tag set rather than appending. Always read-modify-write: `az boards work-item show --id <id> --fields System.Tags`, splice the triage tag into (or out of) the existing list, then write the complete list back. Never send a delta.
- **Close**: set the state explicitly with `az boards work-item update --id <id> --state "<state>"`. The completed state depends on type and process — for this project:
  - `<SPEC_TYPE>` → `<SPEC_COMPLETED_STATE>`
  - `<TICKET_TYPE>` → `<TICKET_COMPLETED_STATE>`
  - `Bug` → `<BUG_COMPLETED_STATE>`

  Never use `Removed`: it is terminal but means "abandoned, never delivered", which is a different claim from "done".
- **Raw REST via the CLI**: `az devops invoke --area <area> --resource <resource> --route-parameters project="<PROJECT>" <route-params> --http-method POST --media-type application/json-patch+json --in-file <path> --api-version 7.1 -o json`. `--in-file` is the only way to send a request body. **`--api-version` defaults to `5.0`** — always pass it explicitly. Pass `7.1` or `7.1-preview`; a dotted preview such as `7.1-preview.3` crashes the version parser.

  **Every route parameter in the resource's template is mandatory**, and a missing one surfaces as a raw `KeyError: '<name>'` traceback rather than a usage error. For `--area wit --resource workitems` the template is `{project}/_apis/wit/workItems/${type}`, so `type` is required — see [Markdown bodies](#markdown-bodies) for the consequences.

  **Never run `az devops invoke` without `--area` and `--resource`.** Bare, it enumerates every resource location in the organisation and does not return in any useful time (observed: still running at 5 minutes). To discover a template, target the specific area/resource instead.

- **Discovering types and states** (when this doc goes stale, or for a type not listed above): `az devops invoke --area wit --resource workitemtypes --route-parameters project="<PROJECT>" --api-version 7.1 -o json`. There is no `az boards work-item type list`. Valid relation names come from `az boards work-item relation list-type`.

Infer the organisation and project from `git remote -v` — the CLI's `--detect true` default does this inside a clone; the explicit `az devops configure` defaults above make it deterministic.

## Markdown bodies

A spec or ticket body is long Markdown. To have it render as Markdown rather than as one literal run-on paragraph, the work item must be **created** with `az devops invoke` — `az boards work-item create` cannot set the format, and nothing can change it afterwards. Build the whole item in that one call: fields, tags, body, format, and the parent link.

**Verified against a live board (Azure CLI 2.88.0, `azure-devops` extension 1.0.2, API 7.1).** Serialise the patch document with a real JSON serialiser — the body contains newlines, quotes and backticks that a shell heredoc will corrupt:

```py
import json
body = open("/tmp/wi-body.md").read()
patch = [
    {"op": "add", "path": "/fields/System.Title", "value": "<title>"},
    {"op": "add", "path": "/fields/System.AreaPath", "value": "<AREA_PATH>"},
    {"op": "add", "path": "/fields/System.IterationPath", "value": "<ITERATION_PATH>"},
    {"op": "add", "path": "/fields/System.Tags", "value": "<triage-label>"},
    {"op": "add", "path": "/fields/System.Description", "value": body},
    {"op": "add", "path": "/multilineFieldsFormat/System.Description", "value": "Markdown"},
    # Parent link, in the same call — Hierarchy-Reverse points at the parent.
    # Omit this op where the board has no Epic hierarchy.
    {"op": "add", "path": "/relations/-", "value": {
        "rel": "System.LinkTypes.Hierarchy-Reverse",
        "url": "https://dev.azure.com/<ORGANISATION>/_apis/wit/workItems/<EPIC_ID>",
    }},
]
open("/tmp/wi-patch.json", "w").write(json.dumps(patch))
```

```sh
test -s /tmp/wi-patch.json || exit 1
az devops invoke --area wit --resource workitems \
  --route-parameters project="<PROJECT>" type=<SPEC_TYPE> \
  --http-method POST --media-type application/json-patch+json \
  --in-file /tmp/wi-patch.json --api-version 7.1 -o json \
  --query '{id:id, fmt:multilineFieldsFormat, tags:fields."System.Tags", rel:relations[0].rel}'
```

The `--query` above is the acceptance check: `fmt` must come back `{"System.Description": "markdown"}`. Swap `type=` for `<TICKET_TYPE>` or `Bug` as appropriate; a `<TICKET_TYPE>` parents to its spec `<SPEC_TYPE>`, not to an Epic.

**There is no update route through `az devops invoke`.** The `wit`/`workitems` location resolves to the create template only, so an existing item cannot be patched this way — both spellings fail, and neither error says so plainly:

| Attempt | Result |
| --- | --- |
| `--route-parameters id=<n>` with `PATCH` | `KeyError: 'type'` traceback — the template has no `id` |
| `--route-parameters type=<n>` with `PATCH` | `VS402323: Work item type <n> does not exist in project …` — `<n>` is read as a type name |

Ordinary field updates on an existing item go through `az boards work-item update` (which writes HTML). Only the create path can choose Markdown.

**If an item already exists in HTML format**, either leave it (HTML renders correctly — it is only the source that is ugly) or delete and recreate it. Do not burn time hunting for a format-flip route; there isn't one.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats pull requests as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same states as issues, using `az repos pr`:

- **Read a PR**: `az repos pr show --id <id>`.
- **List PRs for triage**: `az repos pr list --status active -o json`, then keep only PRs whose `createdBy` is outside the team.
- **Close**: `az repos pr update --id <id> --status abandoned`.
- **Label on create only**: `az repos pr create --labels ...` exists; `az repos pr update` has no label flag. Labels are split on spaces, so a label containing a space becomes several labels.
- **Comment**: no `az repos pr comment` exists. Post a thread through the REST API, building the JSON with a real serialiser so the comment text is escaped correctly:

  ```sh
  jq -n --arg c "$COMMENT" '{comments:[{parentCommentId:0,content:$c,commentType:1}],status:1}' > /tmp/thread.json
  az devops invoke --area git --resource threads \
    --route-parameters project="<PROJECT>" repositoryId=<repo> pullRequestId=<id> \
    --http-method POST --in-file /tmp/thread.json --api-version 7.1 -o json
  ```

  Because the triage vocabulary cannot be applied to PRs as cheaply as to work items, prefer converting an accepted PR-borne request into a work item and triaging that.

Azure DevOps numbers work items and pull requests in separate spaces, so `AB#42` (a work item) and `PR 42` are unambiguous once the surface is named.

## When a skill says "publish to the issue tracker"

Create a work item of the type the mapping above gives for the artefact — `<SPEC_TYPE>` for a spec, `<TICKET_TYPE>` for a ticket, `Bug` for a defect — with the required Area and Iteration, and its Epic parent link where the Epic hierarchy section applies.

Spec and ticket bodies are long Markdown, so **use the single `az devops invoke` create call in [Markdown bodies](#markdown-bodies)** — it sets fields, tags, body, Markdown format and the parent link at once, and the format cannot be added later. Do not reach for `az boards work-item create --description=@<path>` for these: it works, but it writes the Markdown source into an HTML field, where it renders as one literal run-on paragraph.

## When a skill says "fetch the relevant ticket"

Run `az boards work-item show --id <id> --expand all`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is one work item with **child** work items as tickets.

- **Map**: a `<SPEC_TYPE>` tagged `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body in its description, parented to its Epic where that applies.
- **Child ticket**: a `<TICKET_TYPE>` linked as a **child** of the map (`az boards work-item relation add --id <child> --relation-type parent --target-id <map>`), tagged `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: Azure DevOps' native **dependency link** (`System.LinkTypes.Dependency`) — the canonical, UI-visible representation, present in every stock process. Add the edge from the blocked ticket: `az boards work-item relation add --id <child> --relation-type predecessor --target-id <blocker>`, which records "`<child>` is blocked by `<blocker>`" (it writes `Dependency-Reverse` on the child; the relation name states the **target's** role). `--relation-type` accepts **friendly names only** — `parent`, `child`, `predecessor`, `successor`, `related`; a reference name such as `System.LinkTypes.Dependency-Reverse` is rejected outright. A ticket is unblocked when every predecessor has reached its completed state. Do not record blocking as body prose.
- **Frontier query**: list the map's children — `az boards work-item show --id <map> --expand relations` and keep the `System.LinkTypes.Hierarchy-Forward` targets — then for each child read `--expand relations` and collect its `System.LinkTypes.Dependency-Reverse` (predecessor) targets. Fetch those predecessors' states in one flat WIQL query, drop any child with an unfinished predecessor or an `System.AssignedTo` value, and take the first remaining in map order.
- **Claim**: `az boards work-item update --id <n> --assigned-to "<user>"` — the session's first write.
- **Resolve**: `az boards work-item update --id <n> --discussion "<answer>"`, then `az boards work-item update --id <n> --state "<TICKET_COMPLETED_STATE>"`, then append a context pointer (gist + link) to the map's Decisions-so-far.
