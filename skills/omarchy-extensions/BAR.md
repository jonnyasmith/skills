# Putting something on the bar

Three rungs share the bar, and the cheapest that works is almost always right.
`bar.layout.<section>` in `~/.config/omarchy/shell.json` accepts arbitrary ids
alongside the built-in `omarchy.*` ones, and `BarModel.js` infers the kind from
the keys present — `exec` means a command module, `source` means QML — so `type`
is documentation, not a switch.

## Rung 4: a command module

```jsonc
{ "id": "vpn", "type": "command", "exec": "~/.config/omarchy/bar/scripts/vpn",
  "interval": 5, "tooltip": "VPN", "onClick": "nm-connection-editor" }
```

The command may print plain text or Waybar-style JSON
(`{"text":…,"tooltip":…,"class":…}`), which makes every Waybar module on the
internet a candidate. It runs as `bash -lc`, so a login shell's PATH applies.

`onClick` can launch a TUI, which is how a twenty-line module replaces a popup:
glanceable state on the bar, interaction in a floating terminal. See
[`TUI.md`](TUI.md).

## Rung 7: a loose QML module

`{ "id": "gpu", "type": "qml" }` loads
`~/.config/omarchy/bar/modules/gpu.qml`, or `source` points elsewhere. The
module is an `Item` with `implicitWidth`/`implicitHeight`, and receives `bar`,
`moduleName` and `settings` after load. `bar` exposes the live theme colours,
`bar.fontFamily`, `bar.position`, `bar.run(command)`, the shared tooltip, and
the one-popup-at-a-time coordinator.

A loose module is a worse deal than it looks: no manifest means no settings
schema, no entry in `omarchy plugin list`, and no `omarchy bar move`. Once the
widget is worth keeping, promote it to rung 8.

## Rung 8: a full shell plugin

A directory under `~/.config/omarchy/plugins/<id>/` with a `manifest.json` and
the QML its `entryPoints` name. `kinds` decides what the shell does with it:
`bar-widget`, `panel`, `overlay`, `menu`, `service`, `bar`.

`service` is the quiet one: a plugin with no UI at all, loaded once per session
inside a process that is already running, beats a user systemd unit for anything
that needs to talk to the shell.

Plugins run **unsandboxed** inside `omarchy-shell`. They install disabled so the
code can be read first:

```bash
omarchy plugin add <git-url> --enable --yes
omarchy plugin validate <folder>
omarchy plugin list --json
omarchy-shell shell rescanPlugins && omarchy plugin enable <id>   # by hand
```

## Traps

- **QML edits need `omarchy restart shell`.** Upstream says saving under
  `~/.config/omarchy/plugins/` hot-reloads, and the log line appears, but an
  already-mounted bar widget is not re-instantiated. The edit looks like it did
  nothing.
- **`bar.shellQuote()` does not exist**, despite sitting beside `bar.run()` in
  the bar README. Quoting is `Util.shellQuote` on the `qs.Commons` singleton.
  Calling the documented one throws out of the click handler with nothing in the
  journal, so the row just looks dead.
- **A widget's settings are the bare keys of its layout entry**, not a nested
  `settings` object — `entrySettings` in `shell/plugins/bar/BarModel.js` strips
  only `id`. Any other surface that needs the same values should read them from
  there with `jq`, so one place configures both.
- **Declare a full-width mouse area *before* the buttons inside it.** QML
  delivers a click to the last overlapping sibling, so the reverse order
  silently eats every button press. Row highlight then has to follow either
  area, since hovering a button leaves the row's own.
- **Adding an indicator means owning the cluster.** `omarchy plugin clone
  omarchy.indicators` works, and `omarchy.clonePaths` even copies the sibling
  `../indicators/` directory and rewrites the relative path in the copied QML.
  But the set of indicators is an array literal in `Indicators.qml` and the
  settings picker is a closed `options` list in the manifest, so a new indicator
  means editing both, then merging upstream by hand forever. A one-glyph rung 4
  module next to the cluster costs nothing and survives updates.

## Cost check before rung 8

Rung 8 is right when the thing genuinely needs a popup, a panel, a service or a
whole bar. It is wrong when the popup exists only to hold rows you could reach
faster from a chord. Count the QML: a few hundred lines of widget to render a
list that a rung 4 count plus a floating picker would deliver in fifty is the
trade to make deliberately, not by default.
