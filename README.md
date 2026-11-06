# Flatcap for Obsidian

![Version](https://img.shields.io/badge/version-2.0.1-blueviolet) ![Obsidian](https://img.shields.io/badge/Obsidian-1.13.4%2B-7c3aed) ![License](https://img.shields.io/badge/license-MIT-blue)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/screenshot-slate.png">
    <source media="(prefers-color-scheme: light)" srcset="images/screenshot-daylight.png">
    <img src="images/screenshot-slate.png" alt="Obsidian with Flatcap in Slate: file explorer and bookmarks on the left, a research note with properties, a callout, a code block, a table and a checklist, a local graph, and outline and backlinks on the right" width="100%">
  </picture>
</p>

<p align="center"><sub>Slate or Daylight is shown to match your GitHub appearance.</sub></p>

**Flatcap for Obsidian** brings the Flatcap visual system to your notes: matte graphite surfaces, one mineral-blue accent, IBM Plex for the interface and for reading, Cascadia for code.

> The interface organizes. Content takes the foreground. Color informs.

It is a single `theme.css` with two independently tuned modes. **Slate** is used when Obsidian is dark and **Daylight** when it is light, so the theme follows whatever you choose under **Settings → Appearance → Base color scheme** (Dark, Light, or Adapt to system).

## Quiet precision

[Flatcap](https://github.com/cheycron/flat-cap-theme) is a semantic visual system for focused work. Colors are named for **what they do**, not for how they look, and the two modes share roles rather than identical values: Daylight is not an inverted Slate.

- **Hierarchy before decoration.** Sidebars and tabs sit on a quiet canvas; the note you read sits on a lighter surface; menus and dialogs float above both.
- **Useful color.** Mineral blue marks links, selection and primary actions. Callouts use feedback colors only for real states, always with an icon and a title.
- **Explicit interaction.** Focus, the current file, and the keyboard-selected row are distinct signals that do not rely on color alone.
- **Content first.** IBM Plex at a comfortable measure for reading; Cascadia with restrained syntax colors for code.

## Install

### From the community directory (once listed)

Flatcap is being submitted to the Obsidian community directory. When it appears there:

1. Open **Settings → Appearance**.
2. Under **Themes**, click **Manage**.
3. Search for `Flatcap` and click **Install and use**.

Until then, use the manual install below.

### Manually

1. In your vault, create the folder `.obsidian/themes/Flatcap/`.
2. Copy `theme.css` and `manifest.json` from the [latest release](https://github.com/cheycron/flatcap-obsidian/releases) (or from this repository) into it.
3. Reload Obsidian, open **Settings → Appearance → Themes** and pick **Flatcap**.

## Fonts

Obsidian themes cannot load fonts from the network, so Flatcap names them as local families and falls back gracefully. For the intended look, install these on every device you use:

- **[IBM Plex Sans](https://github.com/IBM/plex)** for the interface and reading.
- **[Cascadia Code](https://github.com/microsoft/cascadia-code)** (or Cascadia Mono) for code.

Without them the interface uses Segoe UI or your system font, and code uses `ui-monospace` or Consolas. Layout and colors are unaffected. Fonts you choose yourself under **Settings → Appearance** always win over the theme.

## Motion

Motion is short and functional. Hover and selection changes take **120 ms** (`--fc-motion-fast`), menus and tooltips fade in over 140 ms, and dialogs rise 6 px while fading in over 200 ms with a decelerating curve and no overshoot. There is no looping or decorative animation, and theme switches are never animated.

Obsidian's own animations (sidebars, canvas, loaders) are left alone. With **prefers-reduced-motion: reduce** the theme's entrance animations are removed and its transitions resolve instantly.

## Accessibility

- **Contrast.** Text, links and syntax colors are measured against the surface they sit on: primary text at least 7:1, secondary and accent text at least 5:1, field and toggle boundaries and the focus ring at least 3:1. Results from Obsidian 1.15.0 are in [Verification](#verification).
- **Focus.** Obsidian's focus ring uses the Flatcap focus color, and the theme adds `:focus-visible` rules for tree rows, tabs and links. Only the link ring (2 px solid, 2 px offset) was confirmed in the running app; the tree-row and tab rules are in the stylesheet but a full keyboard walk-through is still pending.
- **Not color alone.** The current file and the keyboard-selected row carry a 2 px bar; links are always underlined (unresolved ones dashed, never faded); callouts have an icon, a title and a colored edge; tags have a border.
- **Increased contrast.** With `prefers-contrast: more` text and control borders switch to the core's high-contrast tokens, and dividers, table and code borders become control-strength.
- **Forced colors.** In `forced-colors: active` the theme keeps system colors and draws outlines for focus and the current row.

## Compatibility

- **Obsidian 1.13.4 or newer** (`minAppVersion`). Callout colors changed from RGB components to full CSS colors between 1.12.7 and 1.13.4, and the theme depends on the new form. Developed and checked on **1.15.0** (Linux). Versions in between 1.12.7 and 1.13.4 have not been tested.
- **Accent color.** Flatcap sets its own accent, so the *Accent color* picker under Appearance has no effect while the theme is active.
- **Style Settings.** Not required and not used.
- Plugin-drawn UI that hard-codes its own colors is outside the theme's reach.
- On Linux, Obsidian 1.15.0 opens **Settings** in its own window. It was not captured separately.

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

## Rebuilding

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

## License

Distributed under the [MIT License](LICENSE).

<p align="center">
  <a href="https://www.buymeacoffee.com/cheycron">
    <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee">
  </a>
</p>
