# Research — How should an agent pass field content to `az boards work-item` and `az repos pr`, and is a temp-file-plus-flag approach supported and preferable to inline heredoc strings?

`Verifying the command shapes asserted in skills/setup-repo-skills/issue-tracker-azure-devops.md (commit 0540b63)` · 27 Jul 2026

## Question

When a coding agent creates or updates Azure Boards work items and Azure Repos pull requests through the `az` CLI, how should it format and pass field content — inline quoted/heredoc strings, or content written to a temp file and referenced by a flag? Nine specific sub-questions about file input, `az devops invoke`, description markup, quoting, `--fields`, `System.Tags`, PR content, relation types, and WIQL are answered below.

Scope boundary: syntax and content-handling only. No authenticated org was available, so no live API call was made; every claim is grounded in shipping source, `--help` output generated from that source, in-process execution of the shipping code, or first-party documentation. Where a fact could only be settled by an authenticated call, that is stated as an uncertainty.

**Versions under test.** `azure-cli` 2.88.0, `azure-cli-core` 2.88.0, `knack` 0.14.0, Python 3.13/3.14, `azure-devops` extension **1.0.2**.[^1] The installed extension is byte-identical to upstream tag `20250624.2` (`1b7f6c0`) for every file cited here, and the installed `azure/cli/core/commands/__init__.py` is byte-identical to upstream tag `azure-cli-2.88.0` (`9593a61`) — so local line numbers are valid upstream line numbers.[^2]

## Answer

**Yes — write the content to a temp file and pass `@/abs/path`, and this is the right default for any multi-line or punctuation-heavy field.** Azure CLI core expands a `@`-prefixed argument into that file's contents *generically, on the raw argv list, before argparse ever runs*, so it applies to every parameter of every command including extension commands; `az boards work-item create --description @/tmp/body.md` genuinely loads the file.[^3][^4] Microsoft documents the convention and recommends it precisely to "bypass the shell's interpretation mechanisms".[^8][^10] Three source-only hazards make it a discipline rather than a free win: a missing file is a **silent** no-op that posts the literal string `@/tmp/body.md` as your field value,[^3] all trailing newlines are stripped,[^3] and a non-UTF-8 file silently becomes base64.[^6]

Two corrections to the template follow. Its sentence *"Descriptions render as HTML, not markdown, unless the process is configured otherwise"* reaches the right conclusion by the wrong mechanism: `System.Description` is an `html`-typed field,[^23][^24] and Markdown — GA since 2025-07-07 — is opt-in **per work item and per field**, never by process configuration, signalled by a `/multilineFieldsFormat/<field>` patch op that `az boards work-item` cannot emit at all.[^25][^29] And `--relation-type` matches **only** friendly names (`predecessor`), never reference names (`System.LinkTypes.Dependency-Reverse`), because the resolver compares against the relation type's `.name`.[^32]

## Findings

### 1. File-based input: does `@filename` work, and for which parameters?

**Definitively yes, for every parameter.** The expansion is not a per-argument opt-in — it is a rewrite of the raw `argv` list.

- `azure-cli-core` defines `_expand_file_prefixed_files(args)`, which maps over **every** token in `argv`.[^3] For each token it splits on the **first** `=`, and if the remainder begins with `@` at index 0, replaces it with the file's contents.[^3]
- It is called from `_pre_command_table_create`, which runs as the first statement of `AzCliCommandInvoker.execute` — *before* the command table is loaded and *before* argparse parses anything.[^4] Because it operates on argv, it is entirely type-agnostic and applies to extension commands (`az boards`, `az repos`) exactly as to core commands.
- So `az boards work-item create --description @/tmp/body.md` **loads the file**. It does not pass the literal string. Both the separate-token form (`--description @f`) and the inline form (`--description=@f`) work, because of the split-on-first-`=`.[^3]
- `knack` ships its own weaker `_expand_prefixed_files`,[^13] but azure-cli's core version is the one in the execution path.[^4]

Verified by executing the shipping function in-process against the installed interpreter (no network):[^5]

| input | result |
|---|---|
| `--description @/tmp/body.md` | file contents, interior `\n` intact |
| `--fields System.Tags=@/tmp/tags.txt` | `System.Tags=alpha; beta` |
| `--description @/tmp/does-not-exist.md` | **unchanged** — literal `@/tmp/does-not-exist.md` |
| `--assigned-to user@example.com` | unchanged (`@` not at index 0) |
| `--assigned-to @me` | unchanged (no such file) |

Three hazards, all source-only:

- **Silent failure on a missing path.** `OSError` is caught and the token returned as-is with only a `logger.debug` line.[^3] A typo'd path posts `@/tmp/body.md` as the description and exits 0. Pinned by azure-cli's own unit test: `['bar=@noneexisting']` → `['bar=@noneexisting']`.[^7]
- **All trailing newlines destroyed.** `content.rstrip(os.linesep)` uses a character set, so it strips every trailing newline, not one.[^3] Interior newlines survive.
- **Non-UTF-8 becomes base64.** The expander calls `read_file_content(..., allow_binary=True)`, which tries `utf-8-sig`, `utf-8`, `utf-16`, `utf-16le`, `utf-16be` and then silently base64-encodes rather than erroring.[^6] Always write the temp file as UTF-8. (A UTF-8 BOM is stripped, since `utf-8-sig` is tried first.[^6][^7])

Do not confuse this with `file_type`, which is **not** the `@` mechanism: `def file_type(path): return os.path.expanduser(path)` only expands `~` in a path string and never opens the file.[^14]

> **Uncertainty:** Microsoft Learn documents `@<file>` only in a JSON-parameter context[^8] and `@-` (stdin) only for `--ids` piping.[^12] The docs never state that `@` applies to arbitrary non-JSON string parameters, and are silent on the trailing-newline stripping, the silent missing-file fallthrough, and the base64 fallback. Those four facts rest on source and on the executed behaviour above, not on documentation.

### 2. `az devops invoke --in-file`

Working shape for a JSON Patch work-item update:

```bash
cat > /tmp/patch.json <<'EOF'
[
  {"op": "add", "path": "/fields/System.Description", "value": "line one\nline two"},
  {"op": "add", "path": "/multilineFieldsFormat/System.Description", "value": "Markdown"}
]
EOF

az devops invoke \
  --org https://dev.azure.com/MyOrg \
  --area wit --resource workitems \
  --route-parameters project=MyProject id=1234 \
  --http-method PATCH \
  --media-type application/json-patch+json \
  --in-file /tmp/patch.json \
  --api-version 7.1 -o json
```

Confirmed from source and docs:

- `--in-file` must exist (`CLIError: --in-file does not point to a valid file location`) and its contents are `json.loads`'d — **the file must be valid JSON**, not arbitrary text.[^15] `--encoding` (default `utf-8`; `ascii`/`utf-16be`/`utf-16le`/`utf-8`) governs the read.[^15][^19]
- **`--media-type application/json-patch+json` is accepted.** The argument is declared free-form with no enum,[^16] and its value goes straight into the request header: `headers = {'Content-Type': media_type + '; charset=utf-8', ...}`.[^17] A nearby line, `if media_type is not None and media_type == 'application/json'`, gates only a `logger.debug` call, not serialization — body serialization is msrest's and is unaffected.[^17] Docs confirm `--media-type` is the *request* content type and `--accept-media-type` the response one.[^19]
- The REST reference gives the routes as `POST .../{project}/_apis/wit/workitems/${type}?api-version=7.1` (note the literal `$`) for create and `PATCH .../_apis/wit/workitems/{id}?api-version=7.1` for update, both with `Media Types: "application/json-patch+json"`.[^20][^21]
- `--route-parameters` and `--query-parameters` are `nargs='*'` lists of `k=v` pairs split on the first `=`.[^15][^16]

Two version traps:

- **`--api-version` defaults to `5.0`.**[^19] You must pass `--api-version 7.1` explicitly for 7.1 routes.
- **`--api-version` cannot express a dotted preview.** `apiVersionToFloat` strips `-preview` then calls `float()`, so `7.1-preview.3` becomes `float("7.1.3")` → `ValueError`. Verified against the installed function: `5.0`, `6.0`, `7.1`, `7.1-preview` parse; `7.1-preview.3` and `7.2-preview.1` raise.[^18] Use `7.1`.

### 3. Description content type: HTML or Markdown?

**Both `System.Description` and `Microsoft.VSTS.TCM.ReproSteps` are `html`-typed fields, and content written by `az boards work-item` is stored and rendered as HTML.**

- The REST `FieldType` enum is `string, integer, dateTime, plainText, html, treePath, history, double, guid, boolean, identity, picklistString, picklistInteger, picklistDouble` — `html` is "HTML (Multiline) field type."[^23] There is no Markdown member.
- Microsoft's field reference states `System.Description` → `Data type=HTML` and `Microsoft.VSTS.TCM.ReproSteps` → `Data type=HTML` (as does `Microsoft.VSTS.Common.AcceptanceCriteria`).[^24]

Markdown support is real, recent, and orthogonal to the field type:

- GA announced **2025-07-07**: "we're excited to announce that Markdown support in large text fields is now generally available!", rolled out in five rings over ~4–5 weeks.[^25] Corroborated by the Sprint 259 release note (2025-07-17).[^26] Sprint 261 (2025-09-04) added interactive checklists in Markdown fields.[^27]
- **It is opt-in per work item and per field — not per project, per process, or per organization.** "By default, all existing and new work items will continue using the HTML editor for large text fields. However, you now have the option to opt-in and use the Markdown editor for individual work items and fields."[^25] There is no named settings-page toggle; the affordance is an in-field "convert it to Markdown" action, with a sticky per-user preference for new work items. **Conversion is one-way**: "Once you convert a field to Markdown, there's no way to revert it back to HTML."[^25]
- **The API-side signal is a sibling patch path, not a sibling field**: `{"op":"add","path":"/multilineFieldsFormat/System.Description","value":"Markdown"}` alongside the `/fields/...` op. "The default format is `HTML`."[^25]
- **`az boards work-item` cannot emit it.** Every op is built by `_create_work_item_field_patch_operation`, which hardcodes `path = '/fields/{field}'`.[^29] So `--fields "multilineFieldsFormat/System.Description=Markdown"` produces the useless path `/fields/multilineFieldsFormat/System.Description`. There is an open feature request.[^28] Markdown therefore requires `az devops invoke` (§2).

**Verdict on the template's sentence** — *"Descriptions render as HTML, not markdown, unless the process is configured otherwise"*: **conclusion correct, mechanism wrong.** The default is HTML, but "the process" has nothing to do with it: the field's declared type stays `html` in both cases, and no process/project/org configuration exists. Suggested replacement: *"Large text fields (`System.Description`, `Microsoft.VSTS.TCM.ReproSteps`, `Microsoft.VSTS.Common.AcceptanceCriteria`) are HTML fields and default to HTML content. Markdown is opt-in per work item and per field and is irreversible once saved. `az boards work-item` always writes HTML; to write Markdown, use `az devops invoke` and add `{"op":"add","path":"/multilineFieldsFormat/<field>","value":"Markdown"}` alongside the `/fields/...` op."*

> **Uncertainty:** `multilineFieldsFormat` is documented **only** on the first-party devblogs announcement.[^25] The Microsoft Learn REST reference for Work Items Create/Update never mentions it, and the `FieldType` enum has no Markdown member — so you cannot detect a field's content format by reading `/wit/fields` metadata.[^23] Also: no primary source announces this for Azure DevOps **Server**; treat it as Services-only rather than assuming parity.

### 4. Multi-line content and special characters

**Newlines survive intact through `@file`, and the CLI neither escapes nor re-interprets them.** The expander substitutes the file's bytes as a single Python string; interior `\n` is preserved verbatim and only trailing newlines are stripped.[^3][^5] Nothing downstream escapes them — the value is placed directly into the JSON Patch `value`.[^30]

Microsoft's quoting guidance, which governs the *inline* alternative:[^11]

- "If you provide a parameter value that contains white space, wrap the value in quotation marks."
- "In Bash and PowerShell, if your variable value contains single quotes, wrap the value in double quotes, and vice-versa." In Bash, "double quotes that are escaped, are treated as part of the string"; escaped single quotes inside single quotes are explicitly listed as **wrong**.
- PowerShell's escape character is the **backtick**, and Bash-style backslash escaping in PowerShell is explicitly wrong. `cmd.exe` is the only shell in Microsoft's examples that allows embedded quotes matching the wrapper, and it returns the outer quotation marks where Bash and PowerShell do not.
- **PowerShell needs `@` quoted or backtick-escaped**, because `@` is the splatting operator: `'@body.md'`, `"@body.md"`, or `` `@body.md `` work; bare `@body.md` does not.[^9][^10]
- Leading hyphen: "If a parameter's value begins with a hyphen, Azure CLI tries to parse it as a parameter name. To parse it as value, use `=` to concatenate the parameter name and value."[^11]
- "The best way to troubleshoot a quoting issue is to run the command with the `--debug` flag."[^11]

Unquoted inline content is where backticks, `$`, and quotes bite — the shell interprets them before `az` sees anything, so a Markdown body containing `` `code` `` or `$VAR` is mangled by command substitution and variable expansion in Bash. `@file` sidesteps all of it, which is exactly Microsoft's stated rationale: "consider using Azure CLI's `@<file>` convention and bypass the shell's interpretation mechanisms."[^8][^10]

**One residual argparse hazard, measured.** Expansion happens *before* argparse, so if the loaded content begins with `-`, argparse may read it as an option name. The boundary is argparse's heuristic — a value starting with `-` is accepted only if it contains a literal space (U+0020) somewhere; newlines and tabs do not count. Measured against the real command (parse errors occur before any network call):[^31]

| body | outcome |
|---|---|
| `- first bullet\n- second` | parses (reaches auth) |
| `---\ntitle: x\n---\n\nBody here` | parses |
| `--do-not-merge please` | parses |
| `-alpha\n-beta` | **`ERROR: argument --description/-d: expected one argument`** |
| `-x` | **same error** |
| `-alpha\n\t-beta` | **same error** |

Prose bodies always contain a space and are safe; a body that is a bare token list with a leading dash is not. The documented fix is the `=` form: `--description=@/tmp/body.md`.[^11]

**Recommended safe pattern for a long multi-line body:** write UTF-8 to a temp file, verify it exists, then pass `--description=@/abs/path`.

### 5. `--fields` syntax

From source:[^30]

- Declared `nargs='*'` on both `create` and `update`, so it takes **space-separated** `"field=value"` pairs: `--fields "field1=value1" "field2=value2"`.[^33]
- Each pair is split with `field.split('=', 1)` — **split on the first `=` only**. A value may therefore contain `=` freely: `Custom.X=a=b` yields key `Custom.X`, value `a=b`. Verified end-to-end.[^31]
- A pair with **no** `=` raises `ValueError('The --fields argument should consist of space separated "field=value" pairs.')`. Verified: `--fields NoEquals` produces exactly that error.[^31]
- **A value containing spaces must be quoted as one shell token**: `--fields "System.Tags=a; b"`. Verified.[^31] For anything longer, `--fields System.Tags=@/tmp/tags.txt` works, because the expander splits on the first `=` and expands the right-hand side.[^3][^5][^31]
- **Reference names are required.** The CLI performs no name resolution: `kvp[0]` is interpolated straight into the JSON Patch path as `/fields/{field}`.[^29][^30] Reference names are what the REST API's patch path expects,[^20] and the extension's own error handler is keyed by reference names (`System.Title`, `System.Description`, …).[^34]
- The op is **always `add`**, never `replace` — the CLI gives you no way to choose.[^30]

Note that `--description` and `--discussion` are just sugar: they map to `System.Description` and `System.History` respectively.[^30]

### 6. `System.Tags` semantics

- **The separator is `;`.** The REST update samples use `"Tag1; Tag2"` (semicolon + space) in both request and response,[^21] and the Boards tags article forbids `;` *inside* a tag: "Tags should be 400 characters or less and not contain separators such as a `,` (comma), `;` (semicolon), or other formatting character."[^36]
- **Writing `System.Tags` replaces the whole tag set.** `System.Tags` is a scalar string at `/fields/System.Tags`, not an array path like `/relations/-`, and RFC 6902 §4.1 is normative for `add`: "If the target location specifies an object member that does exist, that member's value is replaced."[^22] So send the complete desired list, `;`-joined. To add a tag, read the current value first and re-send the union.
- **The CLI `--fields` write and a JSON Patch `add` are the same operation** — the CLI emits exactly `{"op":"add","path":"/fields/System.Tags","value":...}`.[^30] There is no behavioural difference and no way to request `replace` via the CLI.

> **Uncertainty:** Microsoft's own "Add a tag" sample is self-contradictory — a request whose value is only `"Tag1; Tag2"` is shown returning `"System.Tags": "Tag0; Tag1; Tag2"`, which read literally implies `op: add` merges.[^21] No prose anywhere documents append semantics, and the adjacent "Update a tag" (`op: replace`) sample returns exactly `"Tag1; Tag2"`. Treat tags as whole-set replacement and never build an append strategy on that sample; settling it definitively needs one authenticated PATCH against a work item with an existing tag.

### 7. PR content

- **`--description` is `nargs='*'` and each value becomes one line.** Declared `context.argument('description', type=str, options_list=('--description','-d'), nargs='*')`,[^39] then joined: `multi_line_description = '\n'.join(description)`.[^40] The help text matches: "Each value sent to this arg will be a new line. For example: `--description "First Line" "Second Line"`."[^41] Both `create` and `update` behave this way.[^40][^41]
- **There is no file-input flag** — but none is needed: `-d @/tmp/body.md` yields a single-element list holding the whole file, and `'\n'.join([text])` returns it unchanged.[^3][^40]
- PR descriptions and comments both accept Markdown. The help says "Can include markdown",[^41] and Microsoft's Markdown guidance states: "Comments in a pull request accept Markdown, such as `**Bold**` and `*Italic*` style for text."[^45]
- **There is no `az repos pr comment`, `thread`, `label`, or `tag` command.** The group is exactly `checkout, create, list, policy {list,queue}, reviewer {add,list,remove}, set-vote, show, update, work-item {add,list,remove}` — confirmed from `az repos pr --help` on the installed extension[^42] and from the Learn command table.[^42]
- **Labels are create-only in the CLI.** `az repos pr create --labels` exists and does `labels.split(' ')`, so a label containing a space silently becomes several labels; `az repos pr update` has **no** `--labels`.[^47] The bundled SDK has no PR-label methods at all,[^47] so post-creation label changes require `az devops invoke`.

Create a PR comment thread:

```bash
cat > /tmp/thread.json <<'EOF'
{"comments":[{"parentCommentId":0,"content":"Looks good.","commentType":1}],"status":1}
EOF

az devops invoke --org https://dev.azure.com/MyOrg \
  --area git --resource threads \
  --route-parameters project=MyProject repositoryId=MyRepo pullRequestId=42 \
  --http-method POST --media-type application/json \
  --in-file /tmp/thread.json --api-version 7.1 -o json
```

The REST route is `POST .../{project}/_apis/git/repositories/{repositoryId}/pullRequests/{pullRequestId}/threads?api-version=7.1`;[^43] the three route parameters match the SDK's `create_thread`, which sets exactly `project`, `repositoryId`, `pullRequestId`.[^46] `commentType` values are `unknown, text, codeChange, system` and thread `status` values are `unknown, active, fixed, wontFix, closed, byDesign, pending`; attach to a file/line with `threadContext` (`filePath`, `rightFileStart/End` as `{line, offset}`, line starting at 1).[^43]

Set a PR label:

```bash
printf '{"name":"needs-rebase"}' > /tmp/label.json
az devops invoke --org https://dev.azure.com/MyOrg \
  --area git --resource pullRequestLabels \
  --route-parameters project=MyProject repositoryId=MyRepo pullRequestId=42 \
  --http-method POST --in-file /tmp/label.json --api-version 7.1 -o json
```

Route: `POST .../pullRequests/{pullRequestId}/labels?api-version=7.1`, body `{"name": "..."}`; `GET` the same path lists them and `DELETE .../labels/{labelIdOrName}` removes one ("The tag itself will not be deleted").[^44] The docs use "label" and "tag" interchangeably — the entity type is literally `WebApiTagDefinition`.[^44]

> **Uncertainty:** `az devops invoke` resolves `--resource` against the *organization's own* resource-location table at runtime,[^15] so the exact `--resource` tokens above (`threads`, `pullRequestLabels`, `workitems`) could not be confirmed without an authenticated org. The route parameters are source-confirmed;[^46] the resource names are inferred from the REST route segments. The call that settles it is the documented discovery form, which lists every area/resource pair for the org: `az devops invoke --org <url> -o json --query "[?area=='git']"`.[^19]
>
> Also: the thread-create doc samples send enums as **integers** (`commentType: 1`, `status: 1`) while responses echo **strings** (`"text"`, `"active"`). The docs never state that string input is accepted — use the integer form.[^43]

### 8. Relation type names

**Friendly names only. Reference names are rejected.** `get_system_relation_name` iterates the org's relation types and compares `relation_type_from_service.name.lower() == relation_type.lower()`, returning `relation_type_from_service.reference_name`; no match raises `CLIError("--relation-type is not valid. …")`.[^32] Since it matches on `.name`, never on `.reference_name`:

- **`--relation-type predecessor` is valid** — `System.LinkTypes.Dependency-Reverse` has `"name": "Predecessor"`.[^35] Likewise `parent`, `child`, `successor`, `related` (matching is case-insensitive).
- **`--relation-type System.LinkTypes.Dependency-Reverse` fails** with that `CLIError`.

Authoritative mapping:[^35]

| reference name | friendly name | notes |
|---|---|---|
| `System.LinkTypes.Hierarchy-Forward` | Child | `isForward: true` |
| `System.LinkTypes.Hierarchy-Reverse` | Parent | |
| `System.LinkTypes.Dependency-Forward` | Successor | `isForward: true` |
| `System.LinkTypes.Dependency-Reverse` | Predecessor | |
| `System.LinkTypes.Related` | Related | `directional: false` — no Forward/Reverse pair |

**Direction, definitively: `--id A --relation-type predecessor --target-id B` means "A is blocked by B" — B must complete first.** `add_relation` writes the patch op onto work item **A**, as `{"op":"add","path":"/relations/-","value":{"rel":"System.LinkTypes.Dependency-Reverse","url":"<B's url>"}}`.[^33] The `rel` names the role of the **target**, and Microsoft states: "Choose **Predecessor** when linking to a work item that should complete before the current item. Choose **Successor** when linking to a work item that should complete after the current item."[^37] So B is A's predecessor: A depends on B. The hierarchy analogue corroborates the convention — a work item carrying `Hierarchy-Reverse` (named "Parent") toward another means that other item is its parent.[^21][^35] To express "A blocks B", use `--id A --relation-type successor --target-id B`.

### 9. WIQL through the CLI

**`az boards query --wiql` handles flat (`FROM workitems`) queries only and cannot return `FROM workItemLinks` results.** Both the source docstring and the generated help say so outright: "Query for a list of work items. Only supports flat queries."[^37][^38]

The mechanism is in `query_work_items`: it calls `client.query_by_wiql(...)` and then branches on `if query_result.work_items:`, hydrating IDs from that key in batches and returning `None` when it is empty.[^37] A `workItemLinks` query returns its results under `workItemRelations` instead, which the function never reads — so such a query yields `null`, not an error. Use `az devops invoke --area wit --resource wiql` for link queries.

Incidental limits in the same function, worth knowing: results are capped at **1000** work items, hydrated in batches of 200, and the selected column list is truncated once the encoded field names exceed 800 characters ("Not retrieving all fields due to max url length").[^37]

### Recommendation

**(a) Long multi-line work-item description — use a temp file.** Correct call, not ceremony: it is the only way to keep backticks, `$`, and quotes intact across Bash and PowerShell, and it is what Microsoft recommends.[^8][^10]

```bash
printf '%s' "$BODY" > /tmp/wi-body.md          # UTF-8, no trailing-newline reliance
test -s /tmp/wi-body.md || exit 1              # the silent-fallthrough guard
az boards work-item create --type Bug --title "…" \
  --description=@/tmp/wi-body.md --org "$ORG" --project "$PROJ"
```

Use the `=` form to immunise against a body starting with `-`.[^11][^31] Remember the content lands as **HTML**;[^24][^29] if the field must render Markdown, skip the CLI flag and use `az devops invoke` with the paired `/multilineFieldsFormat` op (§2, §3).

**(b) Tag change — no temp file. Unnecessary ceremony.** Tags are short and the write is whole-set replacement, so read-modify-write inline:

```bash
az boards work-item update --id 1234 --fields "System.Tags=alpha; beta; gamma" --org "$ORG"
```

Quote the pair as one token because of the spaces;[^31] send the complete desired set, never a delta.[^22]

**(c) PR comment — temp file required, but for JSON, not for quoting.** There is no `az repos pr comment`,[^42] and `az devops invoke` accepts a request body only via `--in-file`.[^15][^19] Build the JSON with a real serializer so the comment text is escaped correctly:

```bash
jq -n --arg c "$COMMENT" '{comments:[{parentCommentId:0,content:$c,commentType:1}],status:1}' > /tmp/thread.json
az devops invoke --area git --resource threads \
  --route-parameters project="$PROJ" repositoryId="$REPO" pullRequestId="$PR" \
  --http-method POST --in-file /tmp/thread.json --api-version 7.1 -o json --org "$ORG"
```

For a PR *description*, by contrast, no temp file is needed for short text — `-d "line one" "line two"` joins with newlines[^40] — but reach for `-d @/tmp/pr-body.md` as soon as the body contains Markdown punctuation.

## Sources

[^1]: `az version -o json` and `az extension list` on this machine — azure-cli 2.88.0, azure-cli-core 2.88.0, azure-devops extension 1.0.2; `knack-0.14.0.dist-info`. Primary: first-party tooling output. Run 2026-07-27.
[^2]: Byte-comparison of the installed extension against upstream tag `20250624.2` (`1b7f6c0ffdbed8363dd4502cc9acfb25154333be`, whose `version.py` reads `VERSION = "1.0.2"`) — `dev/boards/work_item.py`, `dev/boards/relations.py`, `dev/team/invoke.py`, `dev/repos/pull_request.py`, `dev/repos/arguments.py`, `dev/boards/arguments.py`, `dev/team/arguments.py` all identical; and of `azure/cli/core/commands/__init__.py` against `Azure/azure-cli@9593a61466af0c8ca10a1308c88c6e93646b0a1b` (tag `azure-cli-2.88.0`), identical. Primary: first-party source. Verified 2026-07-27. Note `devops_sdk/client.py` differs only by stripped comments (installed line N ≡ upstream line N+14).
[^3]: `_expand_file_prefixed_files` — `Azure/azure-cli@9593a61:src/azure-cli-core/azure/cli/core/commands/__init__.py:77-111`; locally `/opt/homebrew/Cellar/azure-cli/2.88.0/libexec/lib/python3.14/site-packages/azure/cli/core/commands/__init__.py:77-111`. Split on first `=` at :104-109; `@` must be at index 0 at :94; `OSError` → unchanged + debug log at :97-99; `content.rstrip(os.linesep)` at :84; `@-` reads stdin at :79-80. Primary: first-party source, azure-cli 2.88.0.
[^4]: `_pre_command_table_create` — `Azure/azure-cli@9593a61:src/azure-cli-core/azure/cli/core/commands/__init__.py:114-116`, called at `:515` as the first statement of `AzCliCommandInvoker.execute`, before `load_command_table` (`:523`). Primary: first-party source.
[^5]: In-process execution of the installed `_expand_file_prefixed_files` via the azure-cli bundled interpreter, six cases (plain `@file`, `field=@file`, nonexistent `@file`, `@` at non-zero index, bare `@word`, value containing `=`). Primary: direct observation of shipping code. Run 2026-07-27; `os.linesep == '\n'`.
[^6]: `read_file_content` — `Azure/azure-cli@9593a61:src/azure-cli-core/azure/cli/core/util.py:578-596`. Encoding order `utf-8-sig, utf-8, utf-16, utf-16le, utf-16be`; base64 fallback when `allow_binary=True`. Primary: first-party source.
[^7]: `test_expand_file_prefixed_files` — `Azure/azure-cli@9593a61:src/azure-cli-core/azure/cli/core/tests/test_application.py:103-112`. Pins `['bar=@noneexisting'] → ['bar=@noneexisting']` and BOM stripping. Primary: first-party unit test.
[^8]: "Quoting differences between shells", section *JSON strings* — https://learn.microsoft.com/en-us/cli/azure/use-azure-cli-successfully-quoting — "consider using Azure CLI's `@<file>` convention and bypass the shell's interpretation mechanisms." Primary: official docs. Accessed 2026-07-27; ms.date 2026-07-07.
[^9]: Same page, section *Special characters* — bare `@parameters.json` fails in PowerShell; `` `@ ``, `'@…'`, `"@…"` work. Primary: official docs. Accessed 2026-07-27.
[^10]: `Azure/azure-cli:doc/quoting-issues-with-powershell.md:174-176` — "the best practice is to use Azure CLI's `@<file>` convention to load from a file to bypass the shell's interpretation"; notes `@` is PowerShell's splatting operator. Primary: first-party repo doc.
[^11]: Same quoting page, sections *White spaces and quotation marks*, *Empty strings*, *Hyphen characters*, *The --debug parameter*. Primary: official docs. Accessed 2026-07-27.
[^12]: "Tips for using Azure CLI successfully" — https://learn.microsoft.com/en-us/cli/azure/use-azure-cli-successfully-tips — the only doc mention of `@-` (stdin), in the `--ids` piping context. Primary: official docs. Accessed 2026-07-27.
[^13]: `knack`'s own `_expand_prefixed_files` — `/opt/homebrew/Cellar/azure-cli/2.88.0/libexec/lib/python3.14/site-packages/knack/parser.py:89-107` (knack 0.14.0). Present but not the code path azure-cli uses. Primary: first-party source.
[^14]: `file_type` — `Azure/azure-cli@9593a61:src/azure-cli-core/azure/cli/core/commands/parameters.py:89-91`: `return os.path.expanduser(path)`. Expands `~` only; never opens the file. Primary: first-party source.
[^15]: `invoke()` — `~/.azure/cliextensions/azure-devops/azext_devops/dev/team/invoke.py:19-108` (≡ `Azure/azure-devops-cli-extension@1b7f6c0:azure-devops/azext_devops/dev/team/invoke.py`). `--in-file` existence check and `json.loads` at :37-44; `media_type` passed to `client._send` at :106; `stringToDict` splitting `k=v` on first `=` at :143-156; defaults `api_version='5.0'`, `http_method='GET'`, `media_type='application/json'` at :22-27. Primary: first-party source, extension 1.0.2.
[^16]: `dev/team/arguments.py:90-104` (same tag) — `media_type` and `accept_media_type` declared free-form (no `get_enum_type`), `http_method` enum-constrained, `route_parameters`/`query_parameters` `nargs='*'`. Primary: first-party source.
[^17]: `devops_sdk/client.py` — installed `:41-93`, upstream `@1b7f6c0:azure-devops/azext_devops/devops_sdk/client.py:49-104`. `headers = {'Content-Type': media_type + '; charset=utf-8', ...}` at installed `:76` / upstream `:90`; the `media_type == 'application/json'` test at installed `:46` / upstream `:60` guards only `logger.debug`. Primary: first-party source.
[^18]: `apiVersionToFloat` — `dev/team/invoke.py:137-140`, plus direct execution of the installed function: `5.0`, `6.0`, `7.1`, `7.1-preview` parse; `7.1-preview.3` → `ValueError: could not convert string to float: '7.1.3'`. Primary: first-party source + direct observation. Run 2026-07-27.
[^19]: `az devops invoke` reference — https://learn.microsoft.com/en-us/cli/azure/devops#az-devops-invoke, cross-checked against `az devops invoke --help` on extension 1.0.2. `--media-type` "Specifies the content type of the request", default `application/json`; `--accept-media-type` the response; `--api-version` default `5.0`; `--encoding` default `utf-8`, allowed `ascii, utf-16be, utf-16le, utf-8`. Primary: official docs + generated help. Accessed 2026-07-27.
[^20]: Work Items – Create — https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/create?view=azure-devops-rest-7.1 — `POST .../{project}/_apis/wit/workitems/${type}?api-version=7.1`; `Media Types: "application/json-patch+json"`; body `[{"op":"add","path":"/fields/System.Title","from":null,"value":"Sample task"}]`. Primary: official REST reference, api-version 7.1. Accessed 2026-07-27.
[^21]: Work Items – Update — https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.1 — `PATCH .../_apis/wit/workitems/{id}?api-version=7.1`; same media type; tags samples `"Tag1; Tag2"`; `Hierarchy-Reverse` relation sample. Primary: official REST reference. Accessed 2026-07-27.
[^22]: RFC 6902 §4.1 (`add`) — https://www.rfc-editor.org/rfc/rfc6902#section-4.1 — "If the target location specifies an object member that does exist, that member's value is replaced." Primary: IETF specification.
[^23]: Work Item Tracking – Fields – Get, `FieldType` enum — https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/fields/get?view=azure-devops-rest-7.1 — `string, integer, dateTime, plainText, html, treePath, history, double, guid, boolean, identity, picklistString, picklistInteger, picklistDouble`; `html` = "HTML (Multiline) field type." No Markdown member. Primary: official REST reference. Accessed 2026-07-27.
[^24]: "Query by titles, IDs, and rich-text fields" — https://learn.microsoft.com/en-us/azure/devops/boards/queries/titles-ids-descriptions — `System.Description` `Data type=HTML`; `Microsoft.VSTS.TCM.ReproSteps` `Data type=HTML`. Primary: official docs; page updated 2026-07-23, accessed 2026-07-27.
[^25]: "Markdown support arrives for work items" — https://devblogs.microsoft.com/devops/markdown-support-arrives-for-work-items/, Dan Hellem, published 2025-07-07. GA announcement; five-ring ~4–5 week rollout; per-work-item/per-field opt-in; one-way conversion; `{"op":"add","path":"/multilineFieldsFormat/System.Description","value":"Markdown"}`; "The default format is HTML." Primary: first-party Microsoft engineering blog — and the **only** primary documentation of `multilineFieldsFormat`. Accessed 2026-07-27.
[^26]: Azure Boards Sprint 259 release note (2025-07-17) — https://learn.microsoft.com/en-us/azure/devops/release-notes/2025/boards/sprint-259-update — GA of the Markdown editor for work item comments; "Existing large text fields will remain unchanged, but you can choose to convert them to Markdown individually as needed." Primary: official release notes. Accessed 2026-07-27.
[^27]: Azure Boards Sprint 261 release note (2025-09-04) — https://learn.microsoft.com/en-us/azure/devops/release-notes/2025/boards/sprint-261-update — Markdown fields gain interactive checklists. Primary: official release notes. Accessed 2026-07-27.
[^28]: https://github.com/Azure/azure-devops-cli-extension/issues/1473 — "[Feature Request] Markdown support for az boards work-item create"; open as of 2026-06-23. Primary: first-party issue tracker.
[^29]: `_create_work_item_field_patch_operation` — `dev/boards/work_item.py:365-367` (≡ `@1b7f6c0`): `path = '/fields/{field}'.format(field=field)`. Hardcodes the `/fields/` prefix, so `/multilineFieldsFormat/...` is unreachable from the CLI. Primary: first-party source, extension 1.0.2.
[^30]: `create_work_item` / `update_work_item` — `dev/boards/work_item.py:53-92` (≡ `@1b7f6c0`). `--description` → `System.Description` (:61-62); `--discussion` → `System.History` (:79-80); `--fields` loop with `field.split('=', 1)`, always `op='add'`, `ValueError` when no `=` (:81-87). Primary: first-party source.
[^31]: Direct execution of `az boards work-item create/update` against a placeholder org on this machine. Parse errors surface before any network call; a reached-auth error (`Access Denied: The Personal Access Token used has expired.`) proves the arguments parsed. Established: the leading-dash/space boundary table in §4; `--fields System.Tags=@/tmp/tags.txt` parses; `--fields "System.Tags=a; b" "Custom.X=y=z"` parses; `--fields NoEquals` → `The --fields argument should consist of space separated "field=value" pairs.` Primary: direct observation. Run 2026-07-27.
[^32]: `get_system_relation_name` — `dev/boards/relations.py:132-138` (≡ `@1b7f6c0`): matches `relation_type_from_service.name.lower() == relation_type.lower()` and returns `.reference_name`; otherwise `CLIError("--relation-type is not valid. Use \"az boards work-item relation list-type\" …")`. Primary: first-party source, extension 1.0.2.
[^33]: `add_relation` — `dev/boards/relations.py:24-70`, with `_create_patch_operation` at `:141-151`: emits `{"op":"add","path":"/relations/-","value":{"rel":<referenceName>,"url":<target url>}}` onto the work item named by `--id`. Primary: first-party source.
[^34]: `_SYSTEM_FIELD_ARGS` and `_handle_vsts_service_error` — `dev/boards/work_item.py:185-201, 385-392`. The field-name error path is keyed by reference names. Primary: first-party source.
[^35]: Work Item Relation Types – List — https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-item-relation-types/list?view=azure-devops-rest-7.1 — authoritative `referenceName` ↔ `name` mapping with `isForward` / `oppositeEndReferenceName`; `System.LinkTypes.Related` has `directional: false`. Primary: official REST reference. Accessed 2026-07-27.
[^36]: "Add tags to work items" — https://learn.microsoft.com/en-us/azure/devops/boards/queries/add-tags-to-work-items — "Tags should be 400 characters or less and not contain separators such as a `,` (comma), `;` (semicolon), or other formatting character." Primary: official docs. Accessed 2026-07-27.
[^37]: `query_work_items` — `dev/boards/work_item.py:241-322` (≡ `@1b7f6c0`). Docstring "Only supports flat queries." at :242; `if query_result.work_items:` at :267; `return None` at :322; 1000-item cap at :288; 200-item batches at :289; 800-char field-list truncation at :284-286. Primary: first-party source, extension 1.0.2.
[^38]: `az boards query --help` on extension 1.0.2 — "Query for a list of work items. Only supports flat queries." Primary: generated help (from the source above). Run 2026-07-27.
[^39]: `dev/repos/arguments.py:108-109` (≡ `@1b7f6c0`) — `context.argument('description', type=str, options_list=('--description', '-d'), nargs='*')`, applied to the whole `repos pr` group. Primary: first-party source.
[^40]: `create_pull_request` / `update_pull_request` — `dev/repos/pull_request.py:99-171, 275-…` (≡ `@1b7f6c0`) — `multi_line_description = '\n'.join(description)` at :163-165. Also: when title/description are omitted and the PR has exactly one commit, the CLI backfills both from the commit message (:202-222). Primary: first-party source.
[^41]: `az repos pr create` / `update` reference — https://learn.microsoft.com/en-us/cli/azure/repos/pr — "--description -d : Description for the new pull request. Can include markdown. Each value sent to this arg will be a new line. For example: `--description "First Line" "Second Line"`." Cross-checked against `az repos pr create --help` locally. Primary: official docs + generated help. Accessed 2026-07-27.
[^42]: `az repos pr --help` on extension 1.0.2 (subgroups `policy`, `reviewer`, `work-item`; commands `checkout, create, list, set-vote, show, update`), cross-checked against the Learn command table at https://learn.microsoft.com/en-us/cli/azure/repos/pr and the command registrations in `dev/repos/commands.py`. No `comment`, `thread`, `label`, or `tag` command exists. Primary: generated help + first-party source + official docs. Run/accessed 2026-07-27.
[^43]: Pull Request Threads – Create — https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-threads/create?view=azure-devops-rest-7.1 — route, body `{"comments":[{"parentCommentId":0,"content":"…","commentType":1}],"status":1}`, `CommentType` (`unknown, text, codeChange, system`), `CommentThreadStatus` (`unknown, active, fixed, wontFix, closed, byDesign, pending`), `threadContext` with `filePath` and `{line, offset}` positions. Primary: official REST reference. Accessed 2026-07-27.
[^44]: Pull Request Labels – Create / List / Delete — https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-labels/create (and `/list`, `/delete`), api-version 7.1 — body `{"name": "…"}`; "Create a tag (if that does not exists yet) and add that as a label (tag) for a specified pull request."; delete "Removes a label (tag) … The tag itself will not be deleted." Primary: official REST reference. Accessed 2026-07-27.
[^45]: "Syntax guidance for basic Markdown usage" — https://learn.microsoft.com/en-us/azure/devops/project/wiki/markdown-guidance — "Comments in a pull request accept Markdown, such as `**Bold**` and `*Italic*` style for text." Primary: official docs. Accessed 2026-07-27. (Note: the *Review pull requests* page never mentions Markdown; this is the page that owns the claim.)
[^46]: `GitClientBase.create_thread` — `~/.azure/cliextensions/azure-devops/azext_devops/devops_sdk/released/git/git_client_base.py:1000-1014` — route values are exactly `project`, `repositoryId`, `pullRequestId`; `location_id='ab6e2e5d-a0b7-4153-b64a-a4efe0d49449'`. Primary: first-party bundled SDK, extension 1.0.2.
[^47]: `create_pull_request` labels handling — `dev/repos/pull_request.py:104, 151-152, 166-171` — `--labels` accepted on `create` only, `labels.split(' ')` into `WebApiTagDefinition`. `az repos pr update --help` exposes no `--labels`, and the bundled `git_client_base.py` defines no PR-label methods (grep for `def .*label` returns nothing). Primary: first-party source + generated help. Verified 2026-07-27.
