---
name: write-pull-requests
description: Draft and verify clear pull request titles and descriptions for GitHub and Azure Repos. Use when creating, updating, or reviewing PR metadata, preparing a squash-merge title, summarising branch changes, reporting verification, or linking GitHub issues and Azure Boards work items.
---

# Write Pull Requests

There is no universal Conventional Pull Requests specification. Apply the repository's PR convention first; otherwise use the reviewer-oriented convention below and make the title compatible with Conventional Commits when it may become a squash-merge commit.

## Discover the local convention

Inspect:

- Repository and agent instructions.
- GitHub or Azure Repos pull request templates.
- PR-title linting and release automation.
- The repository's merge strategy.
- Recent merged PR titles and descriptions when available.

Treat explicit repository rules and templates as authoritative. Preserve required headings and complete every applicable prompt instead of replacing the template with a generic format.

## Establish the PR's exact scope

Identify the base and head branches. Read the complete diff from their merge base and the full subject and body of each non-merge commit unique to the head branch. Exclude uncommitted and unrelated changes.

Determine the PR's single purpose, motivation, externally meaningful behaviour, implementation shape, risks, compatibility impact, and verification evidence. Recommend splitting the PR when independent changes obscure that purpose.

## Write the title

Follow an enforced repository format when one exists. Otherwise:

- Use `<type>[optional scope][optional !]: <description>` when the repository squash-merges PRs, generates releases from PR titles, or checks semantic titles.
- Choose `feat`, `fix`, and breaking-change notation by the PR's net effect, following the Conventional Commits rules.
- Use a short, specific, imperative title and aim for fewer than 50 characters.
- Describe the outcome rather than the activity, branch name, ticket number, or number of files changed.

## Write the description

Start from the repository's template. When no template exists, use only the applicable sections from this structure:

```markdown
## Summary

Explain what changed and why in two or three sentences.

## Change log

- Describe each significant, distinct change.

## Testing

- Name each check performed and its result.

## Breaking changes

Explain the compatibility impact and migration path.
```

Keep the description useful to a reviewer:

- Explain the problem and resulting behaviour before implementation detail.
- Synthesise commits into distinct changes; do not reproduce the commit log.
- Report only verification that actually ran. Write `Not run` and the reason when no verification ran and the template requires a testing section.
- Include screenshots or recordings for material visual changes when available.
- Call out risky areas, deliberate omissions, rollout constraints, and reviewer guidance when they materially aid review.
- Remove empty headings, unchecked boilerplate, instructional comments, and placeholders unless the repository requires them.

## Link tickets deliberately

Include every supplied or repository-required ticket that the PR genuinely addresses. Never invent a ticket ID.

- For a related GitHub issue that remains open, end with `Refs #123`.
- For a GitHub issue completed by the PR, end with `Closes #123`.
- For multiple completed GitHub issues, repeat the keyword: `Closes #123, Closes #456`.
- For an Azure Boards work item in Azure Repos, use the platform's work-item link and include `Refs #123` when a textual reference is useful.
- For Azure Boards connected to GitHub, use `Refs AB#123`.
- Use a state-changing Azure Boards keyword only when the user or repository workflow explicitly requires that transition.

Place ticket references at the end of the description. Distinguish association from completion: use `Refs` by default and a closing keyword only when the PR completes the ticket or local instructions require it.

## Verify and deliver

Confirm:

- The title follows local checks and accurately represents the entire PR.
- The description explains both what changed and why.
- Every material diff area is represented once in the change log.
- Testing claims match observed evidence.
- Breaking changes, risks, and migration steps are explicit.
- Ticket syntax matches the host and intended state transition.
- The final description contains no stale template content.

When asked only for a draft, return the title followed by the raw Markdown description without a code fence. When asked to create or update a PR, verify the target repository, base branch, head branch, draft state, and final rendered metadata before performing the requested action.
