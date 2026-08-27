# Menu rows — `~/.config/omarchy/extensions/omarchy-menu.jsonc`

Rung 2, and the cheapest surface that makes a command *findable*. One file
behind `SUPER + SPACE`. `SUPER + ALT + SPACE` is not a second place: both run
`omarchy-menu toggle`, the second with the `apps` route.

Rows are object keys, and the parent comes from the dotted id — `personal.notes`
lands under a `personal` submenu, and `personal` lands on the root. Reusing an
existing id **overrides or extends that row, keeping every field you do not
mention**, which is how you replace a stock action without forking the file.

| Field | Effect |
|---|---|
| `icon` | Nerd Font glyph in the icon column |
| `label` | row title |
| `action` | shell command; omit it and the row becomes a submenu |
| `target` | id of an existing submenu to open — links and aliases |
| `provider` | runtime row generator; **closed set**, see below |
| `aliases` | extra `omarchy menu summon <name>` routes, also searchable |
| `description` | subtitle and extra search text |
| `when` | shell condition; the row is hidden when it fails |
| `checked` | shell condition; appends a tick when it succeeds |

The file hot-reloads on save.

`when` and `checked` are the reason a row often beats a chord: the row can hide
or tick itself, a chord cannot. They are shell conditions evaluated as the menu
renders, so keep them cheap — a `test`, not a scan.

## `provider` is a closed set

The shipped comment says a provider works when "a `provider_name` function or
command named `name` returns JSON rows", which reads like a plugin point. It is
not. `Menu.qml` holds a hard-coded map — `fonts` and `power-profiles`, each a
bash one-liner emitting `label\tvalue\tcurrent`, plus a QML-native `apps` — and
an unknown name is a **silent no-op**, not an error.

Generate rows with `when` on static rows, or with a `service`/`panel` plugin.

## Reaching a plugin from a row

`action` can drive rung 8 without the plugin knowing:

```jsonc
"ports": {"icon":"󰒍","label":"Dev ports","action":"omarchy-shell shell toggle jonny.ports"}
```

`omarchy-shell` only forwards to a running shell; it never starts one.

## Verifying

`omarchy menu summon <id>` runs a row's action directly, which is the fastest
proof that both the JSONC parsed and the command works. If the row is missing
entirely, the parse failed — the whole file is ignored silently, so check a
trailing comma or a stray brace before suspecting the row.
