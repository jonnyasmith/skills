# Global Instructions

## Subagents

Load the /subagent-orchestration skill before spawning any subagent or writing a workflow. It sets the model and effort for each role (UI work always uses `opus`), reviews, the test gate and commits.

## Replies

Write the full answer (findings, plan, options, recommendation) as message text before calling `wrap_up`. The next-step box ends the turn and nothing after it is shown, so its recap and question must never point to anything ("below", "above", "the plan") that isn't already in the message.

## Mock-ups

Build mock-ups as a Design artifact (canvas of artboards), never inside the project's codebase. Don't add mock-up routes, pages or components to the app unless I ask for that.

## Git

In a repository, when tests and lint pass (or the project has no checks), automatically stage and commit the changes using conventional commits. Do not push or create PRs unless asked.
