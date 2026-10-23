# DESIGN.md — Linguistics PhD Explorer

Visual world: **light, modern and a little playful**. A near-white ground, one sage accent, and IPA symbols as the
signature: tilted pastel "stickers" in the hero, a pastel glyph tile for each person (keyed to their main subfield),
a /transcription/ tag, `[S your query]` / `[NP you]` bracket labels, and results that hang off one tree line.
Everything else stays calm and legible. Light by default, dark honoured.

## Tokens (src/styles/global.css)
- Ground `--bg #FAFAF7`, cards `--bg-2 #FFF`, insets `--bg-3`; ink `#1E2421` with two quieter steps; hairlines `--line #ECEAE3`.
- Accent (sage): `--action #3F7A5A`, soft `--action-soft #E3F0E7`, text `--action-text #2F6A4B`.
- Pastel pairs (ground / ink): lavender, peach, mint, butter, sky (`--p-*` / `--i-*`).
  Lenses: subfield = butter, method = mint, data = sky, population = peach, language = lavender.
- Radii 12 / 18 / 22px; pills (999px) for buttons, chips, nav. Shadows: soft, low.
- Type: Geist (UI and headings, 700, tight tracking), Geist Mono (bracket labels, "We read this as" chips),
  Noto Sans for IPA glyphs. Self-hosted through @fontsource packages. Chinese falls back to the system CJK stack.

## Rules
- No eyebrows or all-caps labels, no emoji, no gradients.
- Fit = slim bar + number in the accent colour. Saved = peach.
- Playful bits are decoration (`aria-hidden`), never carry meaning on their own.

## Components
- `.brand` six-bar wordmark · `.sig` five-bar signal glyph next to every fit number · `.loadbar` six bars that light during model download.
- `.chip[data-dim]` lens-tinted label chips (square swatch, tinted ground); `.primary` adds weight and ★.
- `.row` person row (avatar · identity · side actions) shared by Match, Directory, Shortlist. `.drawer` right-side detail panel.
- `.seg` segmented control for view switches; `.facet` checklists with counts; `.pin` map markers.

## Rules
- No eyebrows/kickers, no all-caps labels, no emoji icons, no decorative gradients, no same-size card grids.
- Numbers align (tabular); scores always show the glyph + number together.
- Copy names the action ("Find matches", "Save", "Export CSV"); errors name the fix.
- Unit field: `.fld-tag` pill on program units (Linguistics departments outlined in the action colour); `.fld` italic note on person rows in adjacent units.
