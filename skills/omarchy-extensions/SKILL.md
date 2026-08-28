---
name: omarchy-extensions
description: >
  Add new functionality to an Omarchy desktop and pick the surface it belongs
  on: a menu row, keybinding, bar module, shell plugin, hook, or a TUI in a
  floating terminal. Use also when making an app that knows nothing about
  Omarchy follow `omarchy theme set`. Changing config that already exists is
  the `omarchy` skill.
---

# Extending Omarchy

Omarchy ships defaults in package-owned `/usr/share/omarchy/` and loads
`~/.config/` **after** them, so an extension is additive: supply only what you
add. Read the packaged tree freely — it is where the defaults you are extending
live — and never write to it, because `omarchy update` overwrites it.

This skill is for *adding* a feature. Changing a setting that already exists is
the `omarchy` skill and its topic guides (`hyprland.md`, `plugins.md`,
`theming.md`, `hooks.md`).

## The unit of extension is a shell command

Every surface below ends by handing a string to bash. So the first move is
always the same, whatever the request: build the thing as a script that runs on
its own, printing or doing exactly one job.

Do this before choosing a surface. One working script reaches a menu row, a
chord, the bar and a hook with no glue code between them, and it is the only
part you can test without the desktop in the way.

**Done when:** the script runs from a plain shell, with no desktop surface
involved, and its output or effect is right.

## The ladder

Rungs, cheapest first. Each one costs more to write and much more to maintain
across an `omarchy update` than the one above it.

| # | Rung | Reach for it when |
|---|---|---|
| 1 | Desktop launcher (`omarchy tui install`, `omarchy webapp install`) | the thing is an app you want to start |
| 2 | Menu row (`~/.config/omarchy/extensions/omarchy-menu.jsonc`) | it is a command you want to *find* by name |
| 3 | Keybinding (`~/.config/hypr/bindings.lua`) | it is a command you want on a chord |
| 4 | Bar command module (`type: "command"`) | it is a command whose *output* belongs on screen |
| 5 | Hook (`~/.config/omarchy/hooks/<event>.d/`) | it should run when the system changes, not when you ask |
| 6 | Themed template (`~/.config/omarchy/themed/*.tpl`) | an app must follow `omarchy theme set` |
| 7 | Bar QML module (`bar/modules/<id>.qml`) | the output needs interaction the bar cannot express |
| 8 | Full shell plugin (`plugins/<id>/manifest.json`) | it needs a popup, a panel, a service, or a whole bar |

**Descend a rung only when the one above cannot express the thing.** Say which
rung you picked and what the rung above could not do, before building anything.
Picking a rung too low is the expensive mistake: a popup with clickable rows is
rung 8 and hundreds of lines of QML, while the same information as a count is
rung 4 and about twenty lines of shell.

Interaction and glanceability are different jobs, and one feature often wants
two rungs: a bar module for *what is true right now*, and a rung 2/3 command for
*let me act on it*. Adding the second is cheap; do not replace one with the
other without asking.

## Branches

- Writing a menu row — fields, dotted ids, one container for your rows,
  overriding a stock row: [`MENU.md`](MENU.md)
- Delivering a command as a floating terminal app, and giving it modal
  vim-style keys: [`TUI.md`](TUI.md)
- Anything on the bar — command module, QML module, plugin, indicator:
  [`BAR.md`](BAR.md)
- Making a foreign app follow the theme: [`THEMING.md`](THEMING.md)

## Verify on the real surface

A staged diff is not evidence. Exercise the surface you built.

| Rung | Check |
|---|---|
| 2 | the row appears in `omarchy menu` and its action runs; the file hot-reloads on save |
| 3 | `hyprctl reload && hyprctl configerrors` is silent, and `omarchy menu keybindings --print` lists the binding *with its description* |
| 4, 7, 8 | the widget draws, and its click or popup does what it claims — QML edits need `omarchy restart shell` |
| 5 | fire the event for real (`omarchy theme set <current>`), do not assume the hook ran |
| 6 | `omarchy theme set` a *different* theme, confirm the rendered artefact changed, then set it back |

Take a screenshot when the change is visual. `grim` is installed; crop to the
window with
`grim -g "$(hyprctl clients -j | jq -r '.[] | select(.class=="<class>") | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')"`.

## Wire the reach

A working command nobody can invoke is unfinished. Give it a menu row, a chord,
or both — they are one line each, and the two suit different moments: the row is
searchable when the chord is not yet muscle memory.

Two rules that make the difference between reachable and invisible:

- **Check the chord is free** with `omarchy menu keybindings --print`. Single
  letters are mostly taken by preinstalled apps and webapps. Rebinding one
  Omarchy already uses needs `hl.unbind` first.
- **Always pass the description** to `o.bind`. That argument is what
  `omarchy menu keybindings` renders, so an undescribed bind cannot be found.

A menu row can also hide or tick itself (`when`, `checked`) — a chord cannot.
That is often the reason to prefer rung 2.

## Standing traps

- **Shell IPC reaches plugins, not scripts.** `omarchy-shell shell toggle|summon`
  reaches a bar widget's popup, which is how rungs 2 and 3 drive rung 8. But
  `omarchy-shell shell call <id> <method>` resolves against panel/overlay/menu
  loaders only, so it cannot call a method on a `bar-widget`.
- **Notifications are a surface.** `omarchy notification send` with `--exec`
  makes the notification a button, and `omarchy osd` renders in the desktop's
  own visual language. Reach for these before inventing a window.
- **Two surfaces are pure text and easy to forget.** `~/.config/omarchy/branding/`
  holds `about.txt` and `screensaver.txt` (`omarchy branding about|screensaver`),
  and a theme *overlay* is one edited file dropped into
  `~/.config/omarchy/themes/<stock-name>/` — no fork, the user directory is read
  after the packaged one.

## If the machine's config is managed

On a chezmoi-managed machine, edit the live file under `~/.config/`, verify it
on the real surface, and only then `chezmoi add` it. A staged file that was
never run is not verified, and the repo's own `AGENTS.md` owns the rest.
