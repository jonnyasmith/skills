---
name: conventional-commits
description: Write and evaluate Git commit messages against Conventional Commits 1.0.0. Use when drafting a commit message, committing changes, reviewing commit history for compliance, rewriting a non-conforming message, deciding a commit's type, scope, breaking-change marker, body, and footers, or referencing GitHub issues and Azure Boards work items without closing them.
---

# Conventional Commits

## Establish the local convention

Inspect the repository's instructions, contribution guide, commit-lint configuration, release tooling, and recent commit history. Treat explicit repository rules as extensions to Conventional Commits. Prefer the repository's established types, scopes, casing, line limits, and issue-footer conventions where they do not contradict the specification.

If no local convention exists, use lowercase types, an optional concise scope, and a short imperative description.

## Understand the change

Read the exact diff represented by the proposed commit, including staged changes when preparing a real commit. Identify its single primary intent and user-visible or developer-visible effect.

Recommend separate commits when independent changes require different types or descriptions. Do not claim that unstaged or unrelated work is part of the message.

## Compose the message

Use this structure:

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

Choose each element deliberately:

- Use `feat` when the commit adds a feature.
- Use `fix` when the commit fixes a bug.
- Use another type only when it better describes the change. Conventional Commits permits additional types but assigns them no intrinsic SemVer meaning.
- Add a scope in parentheses only when it gives useful codebase context. Use a noun consistent with the repository, such as `parser` or `api`.
- Add `!` immediately before `:` when the change breaks compatibility. Ensure the description states the breaking change.
- Write the description as a concrete summary of the change. Begin it immediately after `: `.
- Add a body one blank line after the description when the reason, approach, constraints, or migration context is not evident from the header. Keep the body free-form.
- Add footers one blank line after the body, or one blank line after the description when there is no body.
- Format each footer as `<token>: <value>` or `<token> #<value>`. Replace whitespace in tokens with `-`, except for `BREAKING CHANGE`.
- Use `BREAKING CHANGE: <description>` or `BREAKING-CHANGE: <description>` for a breaking-change footer. Keep `BREAKING CHANGE` uppercase.
- Include co-authors and other trailers only when supported by the task or repository context.

Signal every breaking change with `!`, a breaking-change footer, or both. When migration detail would help, include the footer even if `!` is present.

## Reference tickets without closing them

Collect every ticket ID supplied by the user, branch name, task context, or repository instructions that the commit actually addresses. Add each ticket as its own `Refs:` footer:

- Use `Refs: #123` for a GitHub issue in the same repository.
- Use `Refs: owner/repository#123` for an issue in another GitHub repository.
- Use `Refs: #123` for an Azure Boards work item when committing to Azure Repos.
- Use `Refs: AB#123` for an Azure Boards work item when committing to a GitHub repository connected to Azure Boards.
- Use `Refs: <full-ticket-URL>` when the hosting context is unknown.

Use one footer per ticket. Preserve the platform's exact ID and include only tickets genuinely addressed by the commit. If a required ticket ID is unavailable, request it instead of inventing one.

Use `Refs:` exclusively for ticket linkage. Never pair a ticket reference with `Close`, `Closes`, `Closed`, `Fix`, `Fixes`, `Fixed`, `Resolve`, `Resolves`, or `Resolved`; GitHub and Azure DevOps can interpret those keywords as instructions to change ticket state.

## Verify

Before returning or using the message, confirm all of the following:

- The header matches the required structure and contains a non-empty description.
- `feat` and `fix` reflect feature and bug-fix intent rather than merely the kinds of files changed.
- The message describes the complete commit and nothing outside it.
- Any scope and additional type follow the repository's vocabulary.
- Breaking behaviour is clearly signalled and explained.
- Bodies and footer blocks have the required blank-line separation.
- Every footer uses a valid token and separator.
- Every in-scope ticket appears in a separate `Refs:` footer using the correct platform syntax.
- No ticket reference is paired with a closing or resolution keyword.
- The result satisfies stricter local linting and formatting rules.

When asked only for a commit message, return only the message without a code fence or explanation. When asked to perform a commit, do so only with the user's authorisation and preserve the verified message exactly.

## Examples

```text
feat(parser): support nested array expressions
```

```text
fix(cache): prevent stale reads after invalidation

Track the invalidation generation on each entry so readers cannot reuse data
created before the latest invalidation.

Refs: #482
```

```text
feat(api)!: replace offset pagination with cursors

BREAKING CHANGE: clients must send `after` instead of `page`
```
