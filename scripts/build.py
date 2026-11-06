#!/usr/bin/env python3
"""Generate theme.css (Flatcap 2.0 for Obsidian).

    python3 scripts/build.py              # write theme.css in the repo root
    python3 scripts/build.py --check      # fail if theme.css is stale or a hex has no source
    python3 scripts/build.py --contrast   # token-level contrast of key pairs
    python3 scripts/build.py --sync       # refresh src/theme.json from ../00-Flatcap

Inputs : src/theme.json (vendored copy of the Flatcap 2.0 core, the only source
         of values) and src/rules.css (Obsidian rules written against --fc-* roles,
         no literal colors).
Output : theme.css. Python 3.10+, standard library only, deterministic.
"""
from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "src" / "theme.json"
RULES = ROOT / "src" / "rules.css"
OUT = ROOT / "theme.css"
UPSTREAM = (ROOT / ".." / "00-Flatcap" / "src" / "theme.json").resolve()

# Obsidian mode class -> Flatcap mode. Obsidian puts one of them on <body>.
MODES = {".theme-dark": "slate", ".theme-light": "daylight"}

CONTRAST_MAP = {
    "text.primary": "contrast.text.primary",
    "text.secondary": "contrast.text.secondary",
    "text.muted": "contrast.text.muted",
    "border.control": "contrast.border.control",
}

# Roles that Obsidian exposes as "r, g, b" triplets (plugins and snippets read
# --color-*-rgb). Derived arithmetically from the hex in theme.json.
RGB_ROLES = {"danger.fg": "danger", "success.fg": "success", "warning.fg": "warning",
             "accent.fg": "accent", "info.fg": "info"}


def cssname(key: str) -> str:
    return "--fc-" + key.replace(".", "-")


def rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def lum(h: str) -> float:
    def ch(v: int) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hsl_triplet(h: str) -> tuple[str, str, str]:
    r, g, b = (v / 255 for v in rgb(h))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return f"{hh * 360:.1f}", f"{ss * 100:.1f}%", f"{ll * 100:.1f}%"


def load() -> dict:
    return json.loads(THEME.read_text(encoding="utf-8"))


def rem_to_em(v: str) -> str:
    return v.replace("rem", "em")


def mode_vars(theme: dict, mode: str, contrast: bool = False) -> dict[str, str]:
    t = dict(theme["themes"][mode])
    if contrast:
        for base, over in CONTRAST_MAP.items():
            t[base] = t[over]
    out = {cssname(k): v for k, v in t.items() if not k.startswith("contrast.")}
    if contrast:
        return {k: out[k] for k in map(cssname, CONTRAST_MAP)}
    shadow = theme["elevation"][mode]["shadow.overlay"]
    out["--fc-shadow-overlay"] = shadow
    out["--fc-scrim"] = f"color-mix(in srgb, {t['bg.canvas']} 72%, transparent)"
    for role, name in RGB_ROLES.items():
        out[f"--fc-{name}-rgb"] = ", ".join(str(x) for x in rgb(t[role]))
    h, s, l = hsl_triplet(t["accent.fill"])
    out["--fc-accent-h"], out["--fc-accent-s"], out["--fc-accent-l"] = h, s, l
    return out


def foundation_vars(theme: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for section in ("typography", "metrics"):
        for k, v in theme[section].items():
            out[cssname(k)] = v
    for k, v in theme["density"]["compact"].items():
        out[cssname(k) + "-compact"] = v
    for k, v in theme["density"]["comfortable"].items():
        out[cssname(k) + "-comfortable"] = v
    # Headings in em so they follow Obsidian's own "font size" setting.
    for name in ("title", "heading", "control", "code"):
        out[f"--fc-font-size-{name}-em"] = rem_to_em(theme["typography"][f"font.size.{name}"])
    return out


def block(selector: str, decls: dict[str, str], indent: str = "") -> str:
    body = "".join(f"{indent}\t{k}: {v};\n" for k, v in decls.items())
    return f"{indent}{selector} {{\n{body}{indent}}}\n"


def header(theme: dict) -> str:
    digest = hashlib.sha256(THEME.read_bytes()).hexdigest()[:12]
    return (
        "/*******************************************************************\n"
        f" * Flatcap {theme['version']} for Obsidian: Slate (dark) + Daylight (light)\n"
        " * Quiet precision. The interface organizes. Content takes the\n"
        " * foreground. Color informs.\n"
        " *\n"
        " * Core:   https://github.com/cheycron/flat-cap-theme\n"
        f" * Values: src/theme.json (Flatcap {theme['version']}, sha256 {digest}).\n"
        " *         Every color, font, size and metric below comes from that\n"
        " *         file through scripts/build.py. Do not edit by hand.\n"
        " * Modes:  Slate on .theme-dark, Daylight on .theme-light (Obsidian\n"
        " *         Appearance > Base color scheme: Dark, Light or Adapt to system).\n"
        " * Fonts:  IBM Plex Sans (UI + reading), Cascadia Code (code). Install\n"
        " *         them locally: themes cannot load remote fonts. Fallbacks apply.\n"
        " *******************************************************************/\n"
    )


def build(theme: dict) -> str:
    rules = RULES.read_text(encoding="utf-8")
    parts = ['@charset "UTF-8";\n\n', header(theme), "\n"]
    parts.append(block("body", foundation_vars(theme)))
    parts.append("\n@media (prefers-reduced-motion: reduce) {\n")
    parts.append(block("body", {"--fc-motion-fast": "0ms"}, "\t"))
    parts.append("}\n")
    for sel, mode in MODES.items():
        parts.append("\n" + block(sel, mode_vars(theme, mode)))
    parts.append("\n@media (prefers-contrast: more) {\n")
    for sel, mode in MODES.items():
        parts.append(block(sel, mode_vars(theme, mode, contrast=True), "\t"))
    parts.append("}\n")
    parts.append("\n" + rules.rstrip() + "\n")
    return "".join(parts)


HEX = re.compile(r"#[0-9A-Fa-f]{8}\b|#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")


def provenance(theme: dict, text: str) -> list[str]:
    """Every hex in theme.css must be a value of theme.json; rules.css has none."""
    known = set()

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, str):
            known.update(m.upper() for m in HEX.findall(x))
    walk(theme)
    problems = [f"rules.css contains literal hex {h}" for h in sorted(set(HEX.findall(RULES.read_text(encoding='utf-8'))))]
    for h in sorted(set(HEX.findall(text))):
        if h.upper() not in known:
            problems.append(f"theme.css hex {h} is not in src/theme.json")
    return problems


PAIRS = [
    ("text.primary", "bg.canvas", 7), ("text.primary", "bg.surface", 7), ("text.primary", "bg.raised", 7),
    ("text.primary", "bg.hover", 7), ("text.primary", "bg.selected", 7),
    ("text.secondary", "bg.surface", 5), ("text.secondary", "bg.canvas", 5), ("text.secondary", "bg.hover", 5),
    ("text.muted", "bg.canvas", 5), ("text.muted", "bg.surface", 5), ("text.muted", "bg.selected", 5),
    ("text.muted", "bg.hover", 5),
    ("accent.fg", "bg.canvas", 5), ("accent.fg", "bg.surface", 5), ("accent.fg", "bg.raised", 5),
    ("accent.fg", "bg.selected", 5), ("accent.fg", "bg.hover", 5),
    ("accent.on", "accent.fill", 4.5), ("accent.on", "accent.hover", 4.5), ("accent.on", "accent.pressed", 4.5),
    ("accent.fill", "bg.canvas", 3), ("accent.fill", "bg.surface", 3),
    ("border.control", "bg.canvas", 3), ("border.control", "bg.surface", 3), ("border.control", "bg.raised", 3),
    ("focus.ring", "bg.canvas", 3), ("focus.ring", "bg.surface", 3), ("focus.ring", "bg.selected", 3),
    ("success.fg", "success.bg", 4.5), ("warning.fg", "warning.bg", 4.5),
    ("danger.fg", "danger.bg", 4.5), ("info.fg", "info.bg", 4.5),
    ("text.primary", "success.bg", 7), ("text.primary", "warning.bg", 7), ("text.primary", "danger.bg", 7),
    ("text.primary", "info.bg", 7),
    ("selection.fg", "selection.bg", 4.5),
    ("syntax.keyword", "bg.canvas", 5), ("syntax.function", "bg.canvas", 5), ("syntax.string", "bg.canvas", 5),
    ("syntax.number", "bg.canvas", 5), ("syntax.type", "bg.canvas", 5), ("syntax.comment", "bg.canvas", 5),
    ("text.secondary", "bg.canvas", 5),
]


def contrast_report(theme: dict) -> str:
    lines = []
    for mode in ("slate", "daylight"):
        t = theme["themes"][mode]
        lines.append(f"[{mode}]")
        for fg, bg, target in PAIRS:
            r = ratio(t[fg], t[bg])
            lines.append(f"  {fg:<16} on {bg:<14} {r:6.2f}:1  target {target}:1  {'ok' if r >= target else 'FAIL'}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if theme.css is stale or a hex lacks provenance")
    ap.add_argument("--contrast", action="store_true", help="print token-level contrast ratios and exit")
    ap.add_argument("--sync", nargs="?", const=str(UPSTREAM), metavar="PATH",
                    help="copy theme.json from the core checkout (default ../00-Flatcap/src/theme.json)")
    args = ap.parse_args()

    if args.sync:
        src = Path(args.sync)
        if not src.is_file():
            print(f"error: {src} not found", file=sys.stderr)
            return 2
        shutil.copyfile(src, THEME)
        print(f"synced {src} -> {THEME.relative_to(ROOT)}")

    theme = load()
    if not str(theme.get("version", "")).startswith("2."):
        print(f"error: expected Flatcap 2.x theme.json, got {theme.get('version')}", file=sys.stderr)
        return 2
    if args.contrast:
        print(contrast_report(theme))
        return 0

    text = build(theme)
    if args.check:
        bad = provenance(theme, text)
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            bad.insert(0, "theme.css is stale (run python3 scripts/build.py)")
        if bad:
            print("\n".join("error: " + b for b in bad), file=sys.stderr)
            return 1
        print("ok: theme.css is up to date; every hex comes from src/theme.json")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote theme.css ({len(text.encode())} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
