---
name: azure-devops
description: Open, read and update pull requests and create or read work items (PBIs) in Azure DevOps (datumplatforminteractive / Platform Interactive) through its REST API, without the Azure CLI. Use when asked to open or raise a PR in Azure Repos, check a PR's status, change a PR's title, description or draft state, or create or look up a PBI or other Azure Boards work item.
---

# Azure DevOps

`scripts/ado.py` in this skill's directory calls the Azure DevOps REST API. It uses only the Python standard library and prints JSON. Run it with `python3 ~/.claude/skills/azure-devops/scripts/ado.py <command> ...`.

The org, project and repository come from the `origin` remote of the clone you run it in (or `--cwd <clone>`), falling back to `datumplatforminteractive` / `Platform Interactive`. Git pushes stay on SSH; the script is only for the REST calls.

## Token

The script reads a personal access token at run time from `AZURE_DEVOPS_PAT`, then the keyring (`secret-tool`, `service=azure-devops org=<org>`), then `~/.config/azure-devops/pat`. Never ask the user to paste the token into the chat, never print it, and never write it into a repository or this skill. If the script reports that no token was found, tell the user to run:

```
! secret-tool store --label='Azure DevOps PAT (datumplatforminteractive)' service azure-devops org datumplatforminteractive
```

The token needs **Code: Read & write** (pull requests), **Work Items: Read & write** (work items, and linking them to pull requests) and **Build: Read** (CI results and logs for `pr-checks`; without it, `pr-checks` still shows which policies passed). A 401, or a "non-JSON" error, means the token is wrong or expired; a 403 means a missing scope.

`check` confirms the token works and shows whose it is. Run it first in a session. The token is in the keyring; `~/.config/azure-devops/pat` is only a fallback, so an empty or missing file there is normal.

## Opening a pull request

1. **Push the branch** over SSH (`git push -u origin <branch>`). `create-pr` refuses a branch that is not on `origin` or whose `origin` copy differs from the local branch.
2. **Draft the title and description with `/write-pull-requests`.** Give it the repository, base branch (the remote default, `master` in these repos) and head branch. Tell it:
   - These repos have no PR template and squash-merge, so the title is a Conventional Commits title and becomes the merge commit.
   - House style, from recent merged PRs: `## Summary`, `## Change log`, `## Testing`, plus `## Breaking changes` only when there are any. The Testing section lists only checks that actually ran, with results; anything not run is marked `Not run` with the reason.
   - The description renders as Markdown and **must be 4,000 characters or fewer**; Azure Repos rejects longer ones. Keep it to the reviewer's essentials.
   - Which work items the PR addresses, if the user supplied any. Link them with `--work-item` (the platform link that skill asks for) and end the description with `Refs #123`, as the team's PRs do. Never invent an id.
   - When the PR depends on a PR in another repository, say so and give the merge order. Mention it as `!<PR id>`, which Azure DevOps links.
   Write the description it returns to a file in the scratchpad, without a code fence.
3. **Dry run** to check what will be sent:
   ```
   ado.py create-pr --cwd <clone> --title "<title>" --description-file <file> [--work-item N] [--draft] --dry-run
   ```
   The output shows the repository, source, target, draft state, linked work items, lengths and any `problems`, and the command exits 1 when there are problems. Read the whole output; don't filter it with `grep`. Fix every problem before continuing. A branch that isn't pushed yet is expected at this point if you plan to push after the user's go-ahead. Show the user the repository, branches, title and draft state and get their go-ahead: opening a PR is visible to the team.
4. **Create** by running the same command without `--dry-run`. It refuses if an active PR already exists for the same source and target.
5. **Read it back** with `ado.py get-pr <id>` to confirm the rendered title, description, draft state and linked work items (the final check `/write-pull-requests` requires), and give the user the `url`.

To change an existing PR, use `update-pr <id> --title ... --description-file ... [--publish | --draft]`, with `--dry-run` first.

## A batch: PBIs and PRs together

When the user asks for several PBIs and PRs at once (for example, one PBI per repository, each linked to its PR):

1. Read the parent feature with `get-work-item <id>`, and look at a few of its recent children to match their titles.
2. Draft everything, dry-run everything, and show the user one table of all the PBIs and PRs. Get a single go-ahead for the whole batch, not one per item.
3. Create the PBIs first, append `Refs #<new id>` to each PR description, push the branches, then open the PRs with `--work-item <new id>`. Open them in merge order when they depend on each other.
4. Read every PBI and PR back and give the user one table of links.

## Work items

```
ado.py create-work-item --title "<title>" --description-file <file> --acceptance-criteria-file <file> \
  --parent <feature id> --dry-run
```

- The default type is `Product Backlog Item`; pass `--type` for others (`Bug`, `Task`, `Feature`).
- Defaults: area `Platform Interactive\Infrastructure Intelligence`, iteration `Platform Interactive\2026 Roadmap`, assigned to the token's owner (the user). These are `DEFAULT_AREA` and `DEFAULT_ITERATION` in `ado.py`. The iteration changes yearly; when a new roadmap iteration starts, update the constant. Override per item with `--area`, `--iteration` or `--assign-to`.
- Always write a description and acceptance criteria. The description says what is wrong or missing, why it matters, and the scope (the repository and what changes). The acceptance criteria are observable outcomes, one per bullet. Write both for someone who hasn't seen the code or the conversation.
- Title style for PBIs under a feature: `<Repository>: <outcome>`, for example `II-User-Interface: save groups with recipients and show the previous label in history`.
- Description and acceptance criteria are sent as Markdown, which this organisation accepts; `get-work-item` shows the fields stored as `markdown`. Keep `--html` for another organisation that rejects Markdown.
- Dry-run first and confirm with the user before creating, as for pull requests.

## Other commands

- `list-prs [--repo R] [--status active|completed|abandoned|all] [--source <branch>]`
- `get-pr <id>`: summary, description and linked work items
- `pr-checks <id>`: branch policies (build, reviewers, work item linking) and, for a failed build, the failing tasks with their errors and log tails
- `get-work-item <id>`
