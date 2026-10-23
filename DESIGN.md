# DESIGN.md — Linguistics PhD Explorer

Visual world: **light, modern and a little playful**. A near-white ground, one deep teal-green accent, and IPA symbols as the
signature: tilted pastel "stickers" in the hero, a pastel glyph tile for each person (keyed to their main subfield),
a /transcription/ tag, `[S your query]` / `[NP you]` bracket labels, and results that hang off one tree line.
Everything else stays calm and legible. Light by default, dark honoured.

## Principles (from Figma's design basics)
- **60-30-10 colour:** ~60% light neutral ground and white cards, ~30% dark ink, ~10% colour.
- **One action colour** for primary actions (Find matches, links, fit scores). Selected states (current page,
  checked filters, view switch) use neutral grey + ink so the main button stays the strongest element.
- **Warm/cool pairing:** cool teal action + warm coral highlight, used sparingly ("your research", Saved).
- **Hierarchy:** H1 max 48px, body 16px, lines ~60–70 characters; secondary text in muted ink.
- **Contrast:** body text ≥ 4.5:1, large text ≥ 3:1.
- **Progressive disclosure:** extra filters folded under "More filters"; methods live on the About page.
- **Consistency:** pills for every button and chip; one radius scale; one shadow pair.

## Tokens (src/styles/global.css)
- Neutrals `--bg #FAF9F7`, cards `#FFF`; ink espresso `#2B1D1C`.
- Action teal `--action #357070`; highlight coral `--accent-2 #D4562F`.
- Solid decoration colours (`--s-*`): coral, teal, deep teal, cream, espresso — stickers and person tiles only.
- Soft tints (`--p-*`/`--i-*`) for labels; lenses: subfield = cream, method = teal, data = espresso, population = coral, language = deep teal.
- Type: Geist (UI and headings), Geist Mono (bracket labels), Noto Sans (IPA glyphs).

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
