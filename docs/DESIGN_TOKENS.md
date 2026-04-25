# Design Tokens — Lovable Webapp

> **Constraint (D-013, locked 2026-04-25):** the Lovable webapp surface (Tier 4 #20) must visually align with Peec AI's design philosophy. Visual disconnection from Peec reads as "wrapper that doesn't respect the host" — judges will include the Peec PM. Visual alignment is a credibility signal that costs no demo time.

## Status

Public-facing design tokens (exact hex codes, font families, surface specs) are **not exposed in peec.ai's HTML or public docs.** The agent building the Lovable webapp must capture these tokens directly from the live rendered Peec interface (peec.ai homepage + product screenshots in marketing pages + docs.peec.ai). This file is the constraint reference, not the token table.

This file should be filled in once the Lovable lane begins, before any visual work lands.

## What to Capture from the Live Peec Interface

When the Lovable lane kicks off, capture and document below:

### 1. Color palette
- [ ] Primary brand color (likely a single saturated hue used for CTAs and key data)
- [ ] Secondary / accent color
- [ ] Neutral background (light mode and dark mode if both exist)
- [ ] Surface / card background
- [ ] Border / divider color
- [ ] Text colors (primary, muted, inverted)
- [ ] Status colors (success / warning / error / info, especially for evidence-tier badges)

Capture as: `--peec-primary: #XXXXXX;` style CSS custom properties, plus the Peec component or page where each was observed.

### 2. Typography
- [ ] Font family (sans-serif primary; possibly a display variant or monospace for data)
- [ ] Heading scale (h1 / h2 / h3 sizes and weights)
- [ ] Body sizes and weights
- [ ] Letter spacing on uppercase labels (Peec marketing site uses tracked-uppercase tag pills based on the homepage observation)

### 3. Surface / spacing patterns
- [ ] Card border radius
- [ ] Card padding
- [ ] Surface elevation (flat vs subtle shadow vs strong shadow)
- [ ] Gap between dashboard tiles
- [ ] Page padding / max-width

### 4. Iconography
- [ ] Icon library or style (line / filled / duotone)
- [ ] Brand glyph or logo treatment

### 5. Motion / interaction
- [ ] Hover state changes (color shift / shadow / scale)
- [ ] Loading states (skeleton vs spinner)
- [ ] Transition speed (fast / medium / slow)

## Observed Design Philosophy (from public peec.ai content)

What we *can* infer from public materials, even without exact tokens:

- **Clean, data-driven aesthetic** suited for marketing analytics — not a consumer-app look.
- **Tabbed organization** in dashboards ("Attio, Last 7 days, All tags") — the webapp should follow this pattern for the Solution Dashboard.
- **Side-by-side metric comparison** is core — the webapp's blind-spot map and competitor landscape should support this layout.
- **Action-oriented voice** — "Use Data to Pick Winners," "Act on Insights." The webapp's microcopy should match this register, not "AI insights" generic marketing-speak.
- **Hierarchical feature organization** — "Set up Prompts → Use Data → Add Brands → Choose AI Models." Suggests numbered or sequenced patterns are common.
- **Export-focused functionality** — `.csv`, Looker Studio, API. The webapp's data pages should expose download links where it makes sense.

## How to Use This File

1. When the Lovable lane starts, the assigned agent (Claude design or Codex) opens peec.ai + a Peec product screenshot in DevTools.
2. Captures the actual color hexes, font families, and spacing values from rendered styles.
3. Fills in the checklist above with values + observation source.
4. Translates them into a Lovable theme config or Tailwind tokens.
5. Builds the webapp UI from the Tier 1 / 1.5 / 2 features and the `/future-directions` static page using these tokens.

## Hard Constraints

- **No copy-pasting Peec assets directly.** Logos, photography, illustrations stay on Peec. We match the *style*, not appropriate the brand.
- **Color contrast must remain accessible.** WCAG AA at minimum for body text and data labels.
- **Don't out-Peec Peec on their own homepage.** The webapp visually nods to Peec; it doesn't pretend to *be* Peec. Distinct enough that nobody confuses our artifact for theirs.

## When This File Is Done

When the checklist above is filled in and the Lovable theme is wired to the captured tokens, mark this file with a "Tokens captured" header and date. The follow-up gate is the Saturday 17:00 Lovable feasibility checkpoint — if the webapp isn't pushing real data by then, the eligibility-critical lane swaps to Entire (D-005, D-009) and design-token capture is no longer in critical path.
