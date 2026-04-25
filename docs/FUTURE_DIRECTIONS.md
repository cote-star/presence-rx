# Future Directions — Channel Activation Layer

> **Status:** Concept-only. Static preview. Not part of the hackathon submission deliverable.
> **Why this lives in the repo:** to source the static page in the Lovable webapp at `/future-directions`. The page is illustrative; the channel-activation layer would be calibrated against external industry benchmark data (e.g., Morning Consult brand-lift, Pathmatics competitor spend) held under license, which is not redistributable.

## Banner Text (rendered prominently on the webapp page)

> **Future Direction — Static Preview**
>
> The diagnostic pipeline (Steps 1–6) is the live, reproducible deliverable. This Channel Activation layer is illustrative: it would calibrate against external industry benchmark data — Morning Consult brand-lift benchmarks, Pathmatics competitor-spend context, and similar industry-standard tools — held under license and used with permission for one-time analysis, not redistributable. The architecture and method below are reproducible end-to-end with public data; production benchmarks are not.

## Where This Sits in the Pipeline

```text
[Steps 1-6: diagnostic pipeline — public, reproducible]
        |
        v  generates
        |  - PRESENCE_VERDICT.md (gap-type classified)
        |  - ACTION_BRIEF.md (intervention class per recommendation)
        |  - EVIDENCE_LEDGER.json
        |
        v
[Steps 7-8: channel activation — future direction, illustrative below]
        |
        v
   Gap-weighted activation planner
        |
        v
   Channel allocation recommendation
```

## How It Would Work

The diagnostic layer answers *what kind of fix is needed*. The activation layer answers *which channels deliver that fix at what spend*. It scores channels using four inputs:

| Input | Source (in concept) | What it provides |
|---|---|---|
| Gap size | Peec MCP (already in pipeline) | Visibility delta vs competitors per blind spot |
| Channel authority | Peec domain + URL reports (already in pipeline) | Which channel types AI engines actually cite |
| Competitor channel benchmark | External industry data (held privately) | Where competitors invest to own each channel |
| Lift benchmark prior | External industry data (held privately) | Expected lift per dollar by channel |

The output is a **channel allocation recommendation**, not a causal model:

```text
For each blind-spot finding, by gap type:
  channel_score = gap_size × channel_authority × lift_benchmark_prior
  budget_share = channel_score / sum(channel_scores across all gaps)

Output:
  - Recommended activation priority (channel ranking by gap)
  - Illustrative budget split (informational, not a causal forecast)
  - Risk note: "Budget split is a planning hypothesis grounded in external priors, not a causal proof."
```

## Five-Channel Taxonomy

Activation is split across five channel categories — clearer than a binary "editorial vs UGC" framing:

| Channel | What it means | Diagnostic-pipeline signal |
|---|---|---|
| Owned content | Comparison pages, product proof pages, schema, docs | URL gap on the brand's own domains; nothing.tech for Nothing Phone |
| Earned / editorial | PR, reviewer outreach, listicle inclusion | Editorial gap domains: rtings, whathifi, dezeen, yankodesign, zdnet |
| Paid amplification | Social / search / display pushing proof assets | No direct Peec signal; this is the activation layer |
| Creator / UGC | Reviews, community proof | YouTube, Reddit, Medium, nothing.community (already strong for Nothing Phone) |
| Retailer / review surfaces | Where AI pulls product facts | Product / spec sites, retailer pages |

## Illustrative Output (synthetic, for the static preview only)

The webapp page would render an example like the table below. **The numbers shown are illustrative for the preview — the production version calibrates against external benchmarks held privately.**

| Gap (target brand) | Gap type | Recommended primary channel | Illustrative allocation share |
|---|---|---|---|
| Minimalist Hardware | Perception | Earned / editorial + Owned content | 50% |
| Mobile Ecosystem | Indexing | Owned content (schema, structured data) | 25% |
| Wireless Audio | Volume / frequency | Creator / UGC + Paid amplification | 20% |
| Consumer Tech Innovation | Perception | Earned / editorial | 5% |

These percentages are **illustrative**. The production version would derive them from the gap-weighted activation planner using external benchmark priors.

## What's Out of Scope for the Public Repo

The line is **agency / client / specific-engagement attribution** — not the names of public industry tools or general methodology terms. So:

**Fine to include (public):**

- Naming public industry data providers as references: Morning Consult (brand-lift surveys), Pathmatics (competitor digital ad spend), and similar widely-used market-research tools.
- "Brand lift" as a generic methodology term — it's industry-standard (Nielsen, Google Ads, Meta, and many others all run brand-lift studies).
- Methodology described in own words: "calibrated against industry brand-lift benchmarks" or "competitor channel-spend context from a major ad-intelligence provider."
- Aggregated illustrative outputs like the table above.

**Not fine to include (private):**

- Agency names (any agency) — direct attribution links the work to a specific firm.
- Specific client engagements, named studies, or any reference distinctive enough to identify a particular agency-client engagement.
- Verbatim text or data tables copied from any client deliverable.
- Specific lift percentages tied to brand + category + time window in detail sufficient to back-derive a known engagement.
- Per-competitor spend numbers shaped like a specific export from a permissioned engagement (column structure, time windows, schema match).
- Code paths or function names that reference specific client engagements (e.g., `load_<agency>_<client>_lift.py`).

The static page on the Lovable webapp uses the illustrative content above and the banner text. The vendor names appear; the agency, client, and engagement attributions do not.

## Hackathon Posture

| Asset | Public? | Content type |
|---|---|---|
| `FUTURE_DIRECTIONS.md` (this file) | Yes (in repo) | Concept-only, illustrative numbers, generic vendor names allowed, no agency/client attribution |
| `/future-directions` page in Lovable webapp | Yes (in webapp) | Reads from this file; rendered with the banner |
| 5–15 second sneak peek at end of submission video | Yes (in video) | Title card + concept animation + illustrative allocation table; vendor names OK in the title card framing |
| Channel-activation prototype with real benchmark data | **No — outside the public repo** | Built locally for the live finalist pitch only, if advancing |

The line is **agency / client / engagement attribution**: vendor names like Morning Consult and Pathmatics are public companies referenced industry-wide, so they're fine on the public surface as generic data-provider citations. What lives outside the public repo is anything calibrated against a specific client engagement and any agency-attributable case study.

## Why Split This Way

Three reasons judges will respect the split:

1. **Discipline over flash.** Showing what we *won't* publish (because it's calibrated against permissioned data) is a credibility signal — the same logic as the blocked-claim pattern in the diagnostic layer.
2. **Honest reproducibility.** The public submission is end-to-end reproducible. The future-directions layer is honestly marked as not-reproducible-from-public-sources.
3. **Roadmap, not overpromise.** Judges have seen plenty of teams gesture at vision they didn't build. We're showing exactly what's built and exactly where it goes — with a clean line between the two.
