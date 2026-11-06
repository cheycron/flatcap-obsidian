# Flatcap for Obsidian: reference

Reference for [Flatcap for Obsidian](../README.md). Unlike the other Flatcap integrations, `scripts/build.py` here only generates `theme.css`; it does not write documentation, so this file is maintained by hand. It is not part of the release (the release publishes only `manifest.json` and `theme.css`).

## Motion

Motion is short and functional. Hover and selection changes take **120 ms** (`--fc-motion-fast`), menus and tooltips fade in over 140 ms, and dialogs rise 6 px while fading in over 200 ms with a decelerating curve and no overshoot. There is no looping or decorative animation, and theme switches are never animated.

Obsidian's own animations (sidebars, canvas, loaders) are left alone. With **prefers-reduced-motion: reduce** the theme's entrance animations are removed and its transitions resolve instantly.

## Accessibility details

- **Contrast.** Text, links and syntax colors are measured against the surface they sit on: primary text at least 7:1, secondary and accent text at least 5:1, field and toggle boundaries and the focus ring at least 3:1. Results from Obsidian 1.15.0 are in [Verification](#verification).
- **Focus.** Obsidian's focus ring uses the Flatcap focus color, and the theme adds `:focus-visible` rules for tree rows, tabs and links. Only the link ring (2 px solid, 2 px offset) was confirmed in the running app; the tree-row and tab rules are in the stylesheet but a full keyboard walk-through is still pending.
- **Not color alone.** The current file and the keyboard-selected row carry a 2 px bar; links are always underlined (unresolved ones dashed, never faded); callouts have an icon, a title and a colored edge; tags have a border.
- **Increased contrast.** With `prefers-contrast: more` text and control borders switch to the core's high-contrast tokens, and dividers, table and code borders become control-strength.
- **Forced colors.** In `forced-colors: active` the theme keeps system colors and draws outlines for focus and the current row.

## Verification

Checked in Obsidian 1.15.0 for Linux, driven headless, in both modes, with rendered colors read from the DOM. Every sampled text pair meets WCAG AA (4.5:1) or better; every sampled non-text boundary meets 3:1.

| Area | Slate | Daylight |
| :-- | :-- | :-- |
| Body, headings, properties, tables, navigation, status bar | 7.68:1 or higher | 7.09:1 or higher (completed tasks 6.03:1) |
| Links | 8.02:1 | 6.77:1 |
| Tags and accent text on a selected surface | 5.75:1 | 5.68:1 |
| Callout titles on their surfaces | 5.49:1 to 6.89:1 | 5.09:1 to 6.46:1 |
| Syntax colors on the code surface | 7.96:1 to 9.63:1 | 5.66:1 to 6.42:1 |
| Primary and danger buttons | 9.30:1 and 8.36:1 | 6.77:1 and 5.98:1 |
| Field border, toggle track, slider track (non-text) | 4.32:1 | 4.39:1 |

Not covered: the graph's rendering of unresolved nodes (Obsidian dims them itself), screen readers, mobile layouts, Windows and macOS, and a visual inspection of `forced-colors` (only its computed styles were checked).

## Compatibility details

- Callout colors changed from RGB components to full CSS colors between Obsidian 1.12.7 and 1.13.4, and the theme depends on the new form. Versions in between have not been tested.
- **Style Settings.** Not required and not used.
- Plugin-drawn UI that hard-codes its own colors is outside the theme's reach.
- On Linux, Obsidian 1.15.0 opens **Settings** in its own window. It was not captured separately.

## How it is built

`theme.css` is generated. Do not edit it by hand.

| File | Role |
| :-- | :-- |
| `src/theme.json` | Vendored copy of the Flatcap 2.0 core: the only source of values. |
| `src/rules.css` | Obsidian rules written against `--fc-*` roles. It contains no literal colors. |
| `scripts/build.py` | Python 3.10+, standard library only, deterministic. |

```sh
python3 scripts/build.py             # write theme.css
python3 scripts/build.py --check     # fail if theme.css is stale or a hex has no source
python3 scripts/build.py --contrast  # token-level contrast of the key pairs
python3 scripts/build.py --sync      # refresh src/theme.json from ../00-Flatcap
```

`--check` also verifies that every hex color in `theme.css` is a value in `src/theme.json`.
