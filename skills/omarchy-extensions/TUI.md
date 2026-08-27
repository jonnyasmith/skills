# Delivering a command as a floating terminal app

A TUI in a floating terminal is not a rung of its own. It is a shell command
delivered from rung 1, 2 or 3, plus one naming convention. Omarchy's own
dictation config works exactly this way: `voxtype configure` is a TUI shipped
inside the package, and `omarchy-voxtype-config` is a four-line wrapper that
launches it in a floating terminal.

```bash
omarchy launch tui --app-id=TUI.float <cmd>     # new floating terminal
omarchy launch or focus tui <cmd>               # or raise the existing one
omarchy tui install "Name" <cmd> float <icon>   # a .desktop file, for the launcher
```

The window closes when the command exits, which is what makes a picker — open,
choose, gone — feel right for a keyboard user.

## A dying process cannot spawn

**The trap that costs the most time.** A TUI that exits as soon as it acts
cannot be the thing that launches a GUI app. It looks like the action did
nothing at all.

The mechanism: opening a URL in an already-running browser is a *handoff* — a
short-lived child sends the URL to the running instance, which opens the window.
When the terminal exits at the same moment, that child dies with the terminal's
scope, before the window exists.

`exec`, `setsid --fork`, `systemd-run --user` and `systemd-run --user --scope`
all fail identically. **The fix is not detachment.** Something that is not
exiting has to do the spawning, and Hyprland is the long-lived process a script
can reach:

```bash
hyprctl dispatch "hl.dsp.exec_cmd(\"omarchy-launch-or-focus-webapp localhost:$port $url\")"
```

This is the script-level equivalent of a bar widget's `bar.run()`, which never
had the bug because its spawner is the long-lived `omarchy-shell`.

Two details:

- `hyprctl dispatch exec <cmd>` is **no longer parsed** — it returns a Lua
  syntax error and rc=7. The dispatchers are `hl.dsp.*`; find the name you want
  with `grep -rhoP 'hl\.dsp\.\w+' /usr/share/omarchy/ | sort -u`.
- A command that is *already* started by the systemd user manager as a unit's
  own main process — `omarchy-launch-browser` — survives without this. That
  asymmetry is the symptom: one action works, its sibling silently does not.

## The window will tile unless you say `TUI.float`

`omarchy-launch-tui` derives the app-id from the command name when you do not
pass one, and the float rule in `/usr/share/omarchy/default/hypr/apps/system.lua`
matches a **closed list** of app-ids: `TUI.float`, `org.omarchy.btop`,
`org.omarchy.terminal`, and a handful more. A new name is not in it, so the
terminal opens tiled in the current workspace.

Pass `--app-id=TUI.float` from every surface that launches it.

## `launch tui` or `launch or focus tui`

`or focus` matches on the app-id. Once you have borrowed the shared `TUI.float`
id to get floating, that pattern matches *every* floating TUI, so it will raise
`btop` instead of your command.

- Exits on the first real keystroke (a picker, a chooser) → plain
  `omarchy launch tui --app-id=TUI.float`. There is nothing worth focusing.
- Stays open (a monitor, an editor) → `or focus`, and give it a dedicated
  app-id plus your own float window rule.

Do not use `omarchy launch floating terminal with presentation` for an
interactive TUI: it prints the Omarchy logo and a "done" banner, because it is
built for one-shot installer scripts.

## One line of output is not a message

A terminal that opens and closes faster than it can be read delivers nothing.
When the command has only a line to say — "nothing is listening" — send it to
the desktop instead, and keep stdout for the case where a human ran it by hand:

```bash
if [[ -n ${HYPRLAND_INSTANCE_SIGNATURE:-} ]] && command -v omarchy-notification-send >/dev/null 2>&1; then
  omarchy-notification-send -g <glyph> "Title" "$message"
else
  echo "$message"
fi
```

## Colours

`fzf`, `gum` and any other TUI you write are unthemed by default: Omarchy themes
every TUI it *ships*, and yours is not one of them. See
[`THEMING.md`](THEMING.md) — a rung 6 template the script reads at launch, with
no hook needed.

Two rules for a terminal UI specifically:

- Use `-1` (inherit) for background, gutter and preview background rather than
  the theme's background colour, or an opaque pane throws away the terminal's
  own transparency (`alpha` in `foot.ini`).
- `fzf` colours whole lines; only the fuzzy-match highlight is finer. Per-field
  colour has to be an ANSI escape in the data you feed it, built from the same
  rendered palette.

## Verifying without a keyboard

The window is not scriptable through the tool that launched it, so drive it:

- `wtype -k Return`, `wtype "text"` — synthesises real keystrokes into the
  focused window. Confirms the keys your TUI binds actually arrive.
- A pty harness (`script`, a supervised process with a pty) tests the key
  handling but **not** the teardown race above, because nothing is exiting.
  Reproduce a launch bug with the real floating terminal, never a pty.
