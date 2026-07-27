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

- **Create a work item**: `az boards work-item create --type "<TYPE>" --title "..." --description "..." --area "<AREA_PATH>" --iteration "<ITERATION_PATH>"`. Use a heredoc in a shell variable for multi-line descriptions. Descriptions render as HTML, not markdown, unless the process is configured otherwise.
- **Read a work item**: `az boards work-item show --id <id> --expand all` (includes fields, relations, and links).
- **List / search**: `az boards query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM workitems WHERE [System.TeamProject] = '<PROJECT>' AND [System.WorkItemType] = '<TYPE>' AND [System.State] <> 'Closed'"`. `az boards query` handles **flat** WIQL only — it reads the `workItems` key of the response. A `FROM workitemLinks` query returns `workItemRelations` instead and will not come back through this command; read links with `--expand relations` on the individual item instead.
- **Comment**: `az boards work-item update --id <id> --discussion "..."`.
- **Update fields**: `az boards work-item update --id <id> --fields "System.FieldName=value"`. `--fields` takes **space-separated** `field=value` pairs, so quote each pair individually for multiples.
- **Triage labels** live in `System.Tags`, semicolon-separated. **Writing tags is destructive** — `--fields "System.Tags=..."` replaces the entire tag set. Always read-modify-write: `az boards work-item show --id <id> --fields System.Tags`, splice the triage tag into (or out of) the existing list, then write the whole list back.
- **Close**: set the state explicitly with `az boards work-item update --id <id> --state "<state>"`. The completed state depends on type and process — for this project:
  - `<SPEC_TYPE>` → `<SPEC_COMPLETED_STATE>`
  - `<TICKET_TYPE>` → `<TICKET_COMPLETED_STATE>`
  - `Bug` → `<BUG_COMPLETED_STATE>`

  Never use `Removed`: it is terminal but means "abandoned, never delivered", which is a different claim from "done".
- **Discovering types and states** (when this doc goes stale, or for a type not listed above): `az devops invoke --area wit --resource workitemtypes --route-parameters project="<PROJECT>" --api-version 7.1 -o json`. There is no `az boards work-item type list`. Relation names come from `az devops invoke --area wit --resource workitemrelationtypes --api-version 7.1 -o json`.

Infer the organisation and project from `git remote -v` — the CLI's `--detect true` default does this inside a clone; the explicit `az devops configure` defaults above make it deterministic.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats pull requests as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same states as issues, using `az repos pr`:

- **Read a PR**: `az repos pr show --id <id>`.
- **List PRs for triage**: `az repos pr list --status active -o json`, then keep only PRs whose `createdBy` is outside the team.
- **Close**: `az repos pr update --id <id> --status abandoned`.
- **Comment and label**: not exposed by the CLI. Post a comment thread with `az devops invoke --area git --resource threads --http-method POST --route-parameters project="<PROJECT>" repositoryId=<repo> pullRequestId=<id> --in-file <json>`, and set PR labels via the `git`/`pullRequestLabels` resource. Because the triage vocabulary cannot be applied to PRs as cheaply as to work items, prefer converting an accepted PR-borne request into a work item and triaging that.

Azure DevOps numbers work items and pull requests in separate spaces, so `AB#42` (a work item) and `PR 42` are unambiguous once the surface is named.

## When a skill says "publish to the issue tracker"

Create a work item of the type the mapping above gives for the artefact — `<SPEC_TYPE>` for a spec, `<TICKET_TYPE>` for a ticket, `Bug` for a defect — with the required Area and Iteration, and its Epic parent link where the Epic hierarchy section applies.

## When a skill says "fetch the relevant ticket"

Run `az boards work-item show --id <id> --expand all`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is one work item with **child** work items as tickets.

- **Map**: a `<SPEC_TYPE>` tagged `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body in its description, parented to its Epic where that applies.
- **Child ticket**: a `<TICKET_TYPE>` linked as a **child** of the map (`az boards work-item relation add --id <child> --relation-type parent --target-id <map>`), tagged `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: Azure DevOps' native **dependency link** (`System.LinkTypes.Dependency`) — the canonical, UI-visible representation, present in every stock process. Add the edge from the blocked ticket: `az boards work-item relation add --id <child> --relation-type predecessor --target-id <blocker>`. A ticket is unblocked when every predecessor has reached its completed state. Do not record blocking as body prose.
- **Frontier query**: list the map's children — `az boards work-item show --id <map> --expand relations` and keep the `System.LinkTypes.Hierarchy-Forward` targets — then for each child read `--expand relations` and collect its `System.LinkTypes.Dependency-Reverse` (predecessor) targets. Fetch those predecessors' states in one flat WIQL query, drop any child with an unfinished predecessor or an `System.AssignedTo` value, and take the first remaining in map order.
- **Claim**: `az boards work-item update --id <n> --assigned-to "<user>"` — the session's first write.
- **Resolve**: `az boards work-item update --id <n> --discussion "<answer>"`, then `az boards work-item update --id <n> --state "<TICKET_COMPLETED_STATE>"`, then append a context pointer (gist + link) to the map's Decisions-so-far.
