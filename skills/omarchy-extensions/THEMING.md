# Making a foreign app follow `omarchy theme set`

Rung 6. Every `*.tpl` in `~/.config/omarchy/themed/` is rendered from the active
theme's `colors.toml` into `~/.local/state/omarchy/current/theme/`, and then the
`theme-set.d` hooks run.

A template is plain text with `{{ key }}` placeholders, so it works for any
format — TOML, JSON, CSS, shell. Keys are the ones in `colors.toml`
(`accent`, `foreground`, `background`, `muted`, `red`…`bright_magenta`), plus
derived ones: `selection_background`, `selection_foreground`, and
`{{ mix background foreground 30% }}` for a blend.

Read the current theme before writing a template:

```bash
cat ~/.local/state/omarchy/current/theme/colors.toml
ls /usr/share/omarchy/default/themed/          # 17 worked examples
```

## The load-bearing detail

**A template is only rendered inside a theme operation.** Editing a `.tpl` does
nothing until `omarchy theme set` or `omarchy-theme-refresh` runs. So a fresh
machine and an edited template both need one refresh to converge, and on a
chezmoi-managed machine that belongs in a `run_onchange_` script keyed on the
template's hash.

## Three shapes

Pick by what the app can do, not by preference.

1. **Base config loads the artefact.** The app has an include directive, so keep
   a repo-managed config that reads the rendered file (nvim, omp). Best: your
   config stays yours, the theme is one line of it.
2. **The whole config is the artefact.** The app has no include and ignores a
   multi-path config variable, so the rendered file must be the entire config
   (starship). Forced, not chosen — the whole config now lives in the template.
3. **The consumer reads the state dir at run time.** A script can just read
   `~/.local/state/omarchy/current/theme/<name>` when it starts. Cheapest and
   least obvious: no hook, no reload, no live-reload story, because it is already
   reading the current theme.

## When you need a hook, and when you do not

A `theme-set.d` hook exists for exactly one job: copying or signalling a rendered
artefact to somewhere else. Shape 3 needs no hook. Shapes 1 and 2 need one when
the app reads a path you cannot render into directly, or needs a reload signal.

```bash
omarchy hook install theme-set <script>    # copies it in, marks it executable
```

One trap: a theme installed from a git repo may ship its own config file for an
app you also template. That copy is staged first and makes the stock renderer
skip your template entirely — so the hook has to render it a second time.

## Terminal UIs

A TUI inherits the terminal's palette for ANSI colours 0–15 with no work at all,
so reach for a template only when you need the theme's *semantic* colours —
`accent` for a pointer, `selection_background` for the highlighted row. Keep
background and gutter as "inherit" so the terminal's transparency survives.

Shape 3 fits a TUI perfectly: one shell-syntax file holding the flags, sourced
as the script starts.

```sh
# rendered to ~/.local/state/omarchy/current/theme/fzf.env
FZF_THEME_OPTS="--color=fg:{{ foreground }},bg:-1,hl:{{ accent }},bg+:{{ selection_background }},…"
FZF_THEME_ACCENT="{{ accent }}"
```

Verify by switching to a different theme, confirming the rendered file's colours
changed to match the new `colors.toml`, and switching back.
