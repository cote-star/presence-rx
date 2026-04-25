# Peec AI — Design Style Guide

> **Status (D-013 satisfied):** Tokens captured 2026-04-25 from the live Peec AI app. Use this file as the canonical reference for the Lovable webapp visual style. The earlier `DESIGN_TOKENS.md` placeholder is replaced by this document.
>
> **Source:** https://app.peec.ai (Tags, Overview, Prompts, Brands, Profile, Domains).
> **Renamed from:** `DESIGN_TOKENS.md` → `design.md` after live capture.

---

## 1. Design Intent

Peec AI is a B2B SaaS analytics product that tracks how brands appear in AI‑generated answers (LLM SEO / GEO). The interface is designed around the following intents:

- **Data-first, low chrome.** The UI fades into the background so dense data (tables, charts, citation lists) carries the visual weight. Borders are nearly invisible, shadows are barely-there, and color is reserved for status and category encoding.
- **Editorial neutrality.** A near-black-on-white palette with off-white surfaces evokes a serious analytics tool (think Linear, Vercel, Stripe, Posthog). Brand color is the data itself, not the chrome.
- **Compact, information-dense layouts.** Default body size is 14 px, table/secondary text drops to 13 px, and section headings stop at 16 px. Spacing is tight (4 px base unit) so users can scan dozens of rows without scrolling.
- **Soft modernism.** Generous border-radius (8–12 px) on every interactive surface, micro-shadows ("ring + drop") instead of hard borders, and Geist as the typeface give the product a calm, modern, slightly editorial feel.
- **Color as taxonomy.** Tag pills, domain-type chips, and chart series use a fixed semantic palette (red = transactional/destructive, orange = corporate/Pixel, blue/indigo = awareness/persona, cyan = UGC, green = institutional/positive, purple = reference, gray = neutral/other). Color is never decorative.
- **Predictable navigation.** A single fixed left sidebar groups every workspace concept under six labeled sections (General, Sources, Actions, Agent analytics, Project, Company). The content area never changes layout — only the panel inside swaps.

Tone of voice in the UI is plain, declarative, and explanatory: every section has a one-line subtitle ("How often each brand appears in AI generated discussions"), every metric has an info tooltip, and every table column is sortable and filterable.

---

## 2. Foundations

### 2.1 Typography

| Token | Value |
|---|---|
| Primary family | `"Geist Variable", sans-serif` |
| Monospace | `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace` |
| Base font-size | 16 px (root); body content uses 14 px |
| Default weight | 400 |
| UI weight | 500 (nav, buttons, table headers, h1/h3) |
| Emphasis weight | 600 (h2 / section titles) |
| Tracking tight | -0.025em (≈ -0.128 px at 16 px) |

**Type scale (CSS tokens):**

| Token | Size | Line-height |
|---|---|---|
| `--text-xs` | 12 px | calc(1 / 0.75) |
| `--text-sm` | 13 px | 18 px |
| `--text-base` | 14 px | calc(1.5 / 1) |
| `--text-lg` | 16 px | calc(1.75 / 1.125) |
| `--text-xl` | 20 px | calc(1.75 / 1.25) |
| `--text-2xl` | 24 px | — |

**Applied roles:**

- Page title in header — 14 px / 500 / tracking -0.112 px, near-black.
- Section title ("Brand profile", "Top Domains", "Recent Chats") — 16 px / 600 / tracking -0.128 px.
- Section subtitle — 14 px / 400, muted (`rgba(23,23,23,0.6)`).
- Sidebar group label (General / Sources / Actions …) — 13 px / 500, 50 % opacity.
- Sidebar item — 14 px / 500, near-black.
- Table header — 13–14 px / 500, muted.
- Body / table cell — 14 px / 400, near-black.
- Field hint — 13 px / 400, muted.

### 2.2 Color

Single light theme, near-black on off-white plus the full Tailwind v4 palette ramps (`--color-{red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose}-{50…950}`).

**Neutrals (the entire chrome):**

| Role | Value |
|---|---|
| Page background | `#FFFFFF` |
| App / main surface | `#FDFDFD` |
| Foreground | `#171717` |
| Muted foreground | `rgba(23,23,23,0.6)` |
| Disabled / placeholder | `rgba(23,23,23,0.5)` |
| Hairline ring | `rgba(23,23,23,0.08)` |
| Subtle surface / card | `rgba(23,23,23,0.04)` |
| Hover / active fill | `rgba(23,23,23,0.08)` |
| Inverse foreground | `#FDFDFD` |

**Semantic / taxonomy (≈10 % tinted bg + saturated text):**

| Category | Background | Text |
|---|---|---|
| Branded / non-branded (neutral) | `rgba(23,23,23,0.04)` | `rgba(23,23,23,0.6)` |
| Informational / Transactional | `rgba(251,44,54,0.10)` | `#FB2C36` (red-500) |
| Awareness / Consideration / Decision / Personas | indigo-100 tint | indigo-600 |
| UGC | `rgba(0,146,184,0.10)` | `rgb(0,146,184)` |
| Editorial | neutral 4 % tint | neutral fg |
| Corporate | orange-100 tint | orange-600 |
| Reference | purple/violet tint | purple-600 |
| Institutional | green-100 tint | green-600 |
| Competitor | red-100 tint | red-600 |
| You | green tint | green-600 |
| Other | `rgba(23,23,23,0.04)` | `rgba(23,23,23,0.6)` |

**Primary action color is monochromatic:** `#171717` on `#FDFDFD`. There is no purple/blue brand-accent CTA.

### 2.3 Spacing & Sizing

| Token | Value |
|---|---|
| `--spacing` (base unit) | 0.25 rem (4 px) |
| Container scale | 3xs 16 · xs 20 · sm 24 · md 28 · lg 32 · xl 36 · 2xl 42 · 3xl 48 · 4xl 56 · 5xl 64 · 6xl 72 rem |
| Sidebar width | ~200 px (fixed, full-height) |
| Page horizontal padding | ~24 px |
| Vertical rhythm between sections | 24–32 px |
| Table row height | ~40 px |

### 2.4 Radii

| Token | Value | Used on |
|---|---|---|
| `--radius` | 0.625 rem (10 px) | base reference |
| `--radius-sm` | 6 px | small chips |
| `--radius-md` | 8 px | inputs, buttons, chips, filter pills |
| `--radius-lg` | 10 px | medium cards |
| `--radius-xl` | 12 px | large cards, sidebar items, textareas |
| `--radius-2xl` | 16 px | modals, hero panels |

In practice the UI converges on **8 px** (chips, buttons, filters) and **12 px** (sidebar pills, textareas).

### 2.5 Shadows

| Token | Value |
|---|---|
| `--shadow-sm` | `0 0 .5px 0 #00000040, 0 0 2px 0 #0000001a, 0 0 4px 0 #0000000d, 0 4px 8px 0 #00000005` |
| `--shadow-md` | `0 0 12px 0 #00000008, 0 0 1px 0 #0000001a, 0 0 6px 0 #0000000d` |
| `--shadow-lg` | `0 4px 6px #0000000d, 0 10px 15px #0000001a` |
| `--shadow-xl` | `0 10px 10px #0000000a, 0 20px 25px #0000001a` |
| `--shadow-2xl` | `0 25px 50px #00000040` |

**Signature interactive shadow** (filter buttons, primary buttons, inputs) — stacked inset highlight + 1 px outer ring + 1 px drop:

```css
box-shadow:
  inset 0 0 0 1px rgba(23,23,23,0),
  0 1px 3px 0 rgba(23,23,23,0.06),
  0 0 0 1px rgba(23,23,23,0.08);
```

This replaces `border` almost everywhere.

### 2.6 Motion

| Token | Value |
|---|---|
| `--ease-out` | `cubic-bezier(0, 0, .2, 1)` |
| `--ease-in-out` | `cubic-bezier(.4, 0, .2, 1)` |
| `--animate-spin` | `spin 1s linear infinite` |
| `--animate-pulse` | `pulse 2s cubic-bezier(.4,0,.6,1) infinite` |
| Default transition | ~150 ms ease-out for color/background/shadow |

### 2.7 Blur

`--blur-xs: 4px` (sticky table headers, overlay edges).

---

## 3. Layout

### 3.1 App Shell

```
┌──────────────────────────────────────────────────────────────────────┐
│ Sidebar (~200 px, fixed)        │ Content area (#FDFDFD)             │
│  Project switcher (top)         │  Header bar (page title, actions)  │
│  Nav sections (scrollable)      │  Filter bar (sticky, dropdown pills)│
│  Refer & Earn (footer)          │  Section blocks (title + subtitle  │
│                                 │   + card / table / chart)          │
└──────────────────────────────────────────────────────────────────────┘
```

- **Sidebar background:** transparent over white; delineated only by the slight color shift to `#FDFDFD`.
- **Sidebar items:** 14 px / 500, 8 px horizontal padding, 12 px radius. Active bg `rgba(23,23,23,0.08)`. Icons 16 px line, currentColor.
- **Group labels:** 13 px / 500, `rgba(23,23,23,0.5)`, sentence case, no extra letter-spacing.
- **"Beta" sub-label:** tiny pill, `rgba(23,23,23,0.04)` bg, 6 px radius, 12 px text.
- **Project switcher:** round avatar + name + chevron in a 12-px-radius pill at the top.

### 3.2 Header / Page top

- Left: small icon + page name (14 px / 500).
- Right: primary CTA in inverse pill style ("+ Create Tag", "+ Add Prompt", "+ Add brand").
- Below: horizontal **filter bar** of dropdown pills (Brand / Time / Tags / Models / Topics) — 8-px-radius white pills with the layered shadow.

### 3.3 Content blocks

1. Section title (16 px / 600, tracking-tight).
2. One-line subtitle (14 px / 400, muted) — used to teach the metric.
3. Card body (chart, table, or both).
4. Inline controls on the right: D / W / M segmented control, settings cog, export, fullscreen icon.

### 3.4 Tables

- Hairline-only horizontal rows in `rgba(23,23,23,0.06)`, no vertical separators.
- Header row 500 muted, sortable carets on hover.
- Cells 14 px regular, near-black; tabular numerals for ranks.
- Mini sparkbars inline ("Volume"); `—` for unchanged metrics.
- Row hover bg `rgba(23,23,23,0.03)`.
- First column commonly: 16-px favicon/logo + text.

### 3.5 Charts

- Light dashed grid lines (`rgba(23,23,23,0.08)`).
- Multi-line series in the categorical palette (orange, indigo, cyan, magenta, gray) — series matches its legend dot.
- "Peec AI" wordmark watermark behind every chart at ~6 % opacity.
- Axis labels 12 px muted.
- Segmented "D / W / M" toggle in top-right of every time-series card.

---

## 4. Components

### 4.1 Buttons

| Variant | Background | Text | Border / Shadow | Radius | Padding |
|---|---|---|---|---|---|
| **Primary (dark)** "Save changes", "+ Create Tag" | `#171717` | `#FDFDFD` | inset `rgba(253,253,253,0.12)` 1 px highlight + outer `#171717` 1 px ring + 1 px drop | 8 px | 0 6 px (~28 px tall) |
| **Secondary** "Edit", filter pills | `#FDFDFD` | `#171717` | outer `rgba(23,23,23,0.08)` ring + `rgba(23,23,23,0.06)` drop | 8 px | 0 6 px |
| **Ghost** sidebar items, table icons | transparent | `#171717` | hover bg `rgba(23,23,23,0.08)` | 12 px | 0 8 px |
| **Icon-only** sort, settings, fullscreen | transparent | `#171717` | none | 8 px | 6 px |

All button text is 14 px / 500.

### 4.2 Inputs

- **Search input:** white pill, leading magnifier, 8 px radius, layered shadow. Muted placeholder.
- **Textarea:** 1 px solid `rgba(23,23,23,0.08)` border, 12 px radius, 8 × 12 px padding, 13 px text.
- **Tag input ("Brand identity"):** chip-style with × remove + "Add +" trailing pill.
- **Dropdown / select:** button with leading icon + label + trailing chevron.

### 4.3 Tags / Pills

Color-as-taxonomy. Shared style: 8 px radius, 2 × 6 px padding, 14 px / 500, ~10 % alpha tinted bg.

| Category | Example | Color family |
|---|---|---|
| Branded / Non-branded | "branded", "non-branded" | neutral gray |
| Intent | "informational", "transactional" | red-500 on red-50/100 |
| Stage | "awareness", "consideration", "decision" | indigo |
| Persona | "Budget-Conscious Professional", "Design Student", "Tech Blogger" | indigo |
| UGC | — | cyan (`rgb(0,146,184)` on 10 % tint) |
| Editorial | — | neutral |
| Corporate | — | orange |
| Reference | — | purple |
| Institutional | — | green |
| Competitor | — | red |
| You | — | green / brand |
| Other | — | gray |

### 4.4 Cards

- Soft "tinted" cards at `rgba(23,23,23,0.04)` (Recent Chats tiles), or white with ring shadow.
- 12 px radius, 16–20 px padding, 8–12 px row gap.
- Recent-chat card pattern: small icon header → bold prompt title (14 px / 500) → 2-line muted preview → footer row of model favicons + relative timestamp ("3 hr. ago") in muted 12 px.

### 4.5 Avatars / Logos

- 16 px square, 4 px radius, in table cells, sidebar switcher (slightly larger), brand list.
- Brand-color column = 12 px solid swatch, 4 px radius, directly editable.

### 4.6 Status / Indicator dots

8–10 px circles for domain-type legend, sentiment column (green/yellow/red before a 0–100 score), and an indigo "attention" dot on the Profile sidebar item.

### 4.7 Segmented controls

"D / W / M" on charts and "Active / Suggested / Archived" tab on Prompts: horizontal pills, no border. Active = `rgba(23,23,23,0.08)`. Inactive = transparent. 13–14 px / 500.

### 4.8 Toggles / Switches

Pill switch with sliding thumb (e.g. "Nothing Phone mentioned", "Gap Analysis"). Off = neutral gray, On = `#171717`.

### 4.9 Tooltips & Info

Small (i) icon next to metric titles. Tooltip = 12 px text dark bubble with medium shadow. Toasts via Sonner (`--toast-*` tokens loaded), bottom-end.

### 4.10 Empty / 404 state

Centered: 48 px stroked circle-slash glyph, "404" in 32 px / 600, sub-line in muted 14 px.

### 4.11 Floating help button

Bottom-right circular dark button (Intercom), 48 px, `#171717`, white icon, large soft drop-shadow.

---

## 5. Iconography

- **Family:** Lucide-style line icons (1.5 px stroke; 16 px nav, 14 px tables).
- **Color:** always `currentColor`.
- **Common nav icons:** home (Overview), sparkle/wand (Prompts), globe (Domains), link (URLs), document (Earned/Owned), chart-up (Impact), search (Crawl insights), shield-check (Crawlability), user (Profile), grid (Brands), tag (Tags), gear (Settings), folder (Projects), key (API Keys), users (Members), credit-card (Billing), gift (Refer & Earn).

---

## 6. Interaction Patterns

- **Filter-first.** Every analytics view starts with the same 5-pill filter bar (Brand · Time · Tags · Models · Topics). State is encoded in the URL (`?brand=…&resolution=day`).
- **Inline editing.** Brand color, tracked names, domains, and tags edit in-place from list rows (hover reveals "…" or "Edit").
- **Sort + search + paginate** on every table; pagination is bottom-right with prev/next chevrons and page numbers.
- **Bulk actions** appear as a footer bar when rows are selected ("Assign tags · Assign topic · Archive all").
- **Suggestions panel.** Right-rail list ("Brand suggestions") with mention count, accept (✓) / dismiss (×) row actions.
- **Resolution toggles** (D/W/M) on every time-series chart.
- **Autosave hint** under forms: small info-icon line ("Saving changes will refresh your prompt suggestions.") next to "Save changes".

---

## 7. Content & Voice

- **Sentence case** everywhere. Title Case reserved for proper nouns and product feature names ("Top Domains", "Recent Chats", "Brand profile", "API Keys").
- Every block is **explained in one line** under its title.
- Numbers are compact: `3.8k`, `1,302`, `0.72`, `32.4 %`. Trends use `—` when flat, a colored arrow when changed.
- Time is **relative** in lists ("3 hr. ago", "17 hr. ago") and absolute on axes ("Apr 23").

---

## 8. Theming Notes

- **Single light theme** ships today; no `.dark` class on root. Tailwind v4 default color tokens are loaded but no shadcn-style semantic aliases (`--background`, `--foreground`, …) are defined — the design system is enforced through consistent use of `#171717` / `#FDFDFD` / `rgba(23,23,23,α)`.
- Border color universally resolves to `lab(90.952 0 0)` ≈ `#E5E5E5`, but borders are usually drawn via the inset/outer ring shadow rather than CSS `border`.

---

## 9. Quick Reference Cheat-Sheet

```css
/* Neutrals */
--peec-bg:           #FFFFFF;
--peec-surface:      #FDFDFD;
--peec-fg:           #171717;
--peec-fg-muted:     rgba(23, 23, 23, 0.6);
--peec-fg-subtle:    rgba(23, 23, 23, 0.5);
--peec-hover:        rgba(23, 23, 23, 0.08);
--peec-tint:         rgba(23, 23, 23, 0.04);
--peec-hairline:     rgba(23, 23, 23, 0.08);

/* Type */
--peec-font:         "Geist Variable", sans-serif;
--peec-text-xs:      12px;
--peec-text-sm:      13px;
--peec-text-base:    14px;   /* default UI size */
--peec-text-lg:      16px;   /* section titles */
--peec-text-xl:      20px;
--peec-tracking:     -0.025em;

/* Radii */
--peec-radius-sm:    6px;
--peec-radius-md:    8px;    /* buttons, chips, filters */
--peec-radius-lg:    10px;
--peec-radius-xl:    12px;   /* sidebar, textareas */
--peec-radius-2xl:   16px;

/* Signature interactive shadow */
--peec-ring:
  inset 0 0 0 1px rgba(23,23,23,0),
  0 1px 3px 0 rgba(23,23,23,0.06),
  0 0 0 1px rgba(23,23,23,0.08);

/* Motion */
--peec-ease:         cubic-bezier(0,0,.2,1);
--peec-duration:     150ms;
```

---

## 10. How to Use This Reference

For the Lovable lane building the Presence Rx webapp:

1. Copy the cheat-sheet CSS variables (Section 9) into the Lovable theme config or Tailwind `@theme` block.
2. Set body font to Geist Variable (load via Google Fonts or self-host).
3. Default body text 14 px, default radius 8 px (chips/buttons/filters) and 12 px (sidebar/cards), default interactive shadow = `--peec-ring`.
4. Apply the layout shell from Section 3.1 — fixed ~200 px sidebar + content area at `#FDFDFD`.
5. Use the semantic tag palette from Section 2.2 / 4.3 for: gap-type pills (perception/indexing/volume_frequency), evidence-tier badges (strong/moderate/limited/blocked), decision-bucket pills (act_now/test_next/monitor/deprioritize/block), and channel-type chips (owned/earned/paid/UGC/retailer).
6. Keep all CTAs monochromatic — `#171717` on `#FDFDFD`. No purple/blue accents on chrome.
7. Don't out-Peec Peec on their own homepage. Match the *style*, not the brand assets — no logo, no photography, no copying.

## 11. Constraints (from D-013)

- The webapp visually nods to Peec; it doesn't pretend to be Peec. Distinct enough that nobody confuses our artifact for theirs.
- No copying logos, photography, or illustrations — we match the design language, not the brand identity.
- WCAG AA contrast minimum for body text and data labels.
- Accessibility: keyboard navigation, screen-reader labels on icon-only buttons, focus rings preserved (use `outline` or a more visible ring than the default in dense data tables).
