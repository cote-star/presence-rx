# End-To-End Build Guide And Storyboard

This is the synthesis doc for building the Presence Verdict Pack on the locked Nothing Phone project. It merges the current repo knowledge into one execution path: what to build, which artifacts prove it works, what the dashboard should show, and how the 2-minute demo should flow.

## Product In One Sentence

Peec shows where the brand appears in AI answers; this project turns that visibility into an auditable marketer action brief with evidence refs, guardrails, blocked claims, and prompts to monitor.

Tagline: **Find your brand's blind spots in AI answers.**

## Six-Axis Blind-Spot Model + Gap-Type Classifier

The Presence Verdict diagnoses blind spots across six axes (where) and classifies each one by gap type (what kind of fix). The locked scope ([SCOPE_FINAL.md](SCOPE_FINAL.md)) maps each axis to specific Tier 1 features and the gap-type classifier to Tier 1.5.

### Six axes (where)

| Axis | Question | Peec source | Verified data (Nothing Phone) |
| --- | --- | --- | --- |
| Topic | Where is the brand invisible? | `get_brand_report(dims=topic_id)` | 5 topics: 72% / 12% / 10% / 6% / 1% |
| Channel | Which content types miss the brand? | `get_domain_report` + gap filter | UGC strong; editorial gaps at rtings, whathifi, zdnet, dezeen, yankodesign |
| Engine | Which AI engines ignore the brand? | `get_brand_report(dims=model_id)` | Gemini 26%, ChatGPT 18%, Google AI Overview 17% |
| Geography | Which markets cannot see the brand? | `get_brand_report(dims=country_code)` | US-only data; geo expansion via `create_prompt` (setup, not result) |
| Authority | Is the brand's content trusted, or just found? | `get_url_report` retrieval vs citation | nothing.community citation rate 1.21 (highest); editorial sites cite competitors instead |
| Evidence | What does the AI actually say? | `list_chats` + `get_chat` | 3-5 sampled responses become receipts in `EVIDENCE_LEDGER.json` |

### Gap-type classifier (what kind of fix)

Every blind spot row in `study_ssot.json` carries a `gap_type` field. Detection signals come from the same data already in the pipeline.

| Gap type | Detection signal | Intervention class | Nothing Phone example |
| --- | --- | --- | --- |
| `perception` | Brand profile vs Gemini perception themes diverge; competitor owns the trait language; Tavily public proof confirms | Positioning + messaging correction | Minimalist Hardware: 6% vs Apple 39% |
| `indexing` | Owned-domain retrieval high, citation low; structured-data signals missing | Schema + AI-citation optimization | nothing.tech retrieved but underused for relevant prompts |
| `volume_frequency` | Low Peec signal across all owned/earned channels; competitor dominates with sustained editorial + UGC volume | Content creation + amplification | Wireless Audio: 1% vs Apple 53%, Nothing Ear product exists |

## End-To-End Flow

```text
Peec MCP snapshot (Nothing Phone)
  |
  |-- read tools (per-axis ingestion) ---
  |     get_brand_report (topic / model / country)
  |     get_domain_report (gap filter)
  |     get_url_report (gap URLs)
  |     list_chats + get_chat (evidence sample)
  |     get_actions (Peec's own opportunity scores)
  |
  v
prompt_universe.json + study_ssot.json
  -> Tavily public-evidence search for editorial gap domains
  -> Gemini perception themes per axis
  -> Value-added metrics (relevance, source trust, unsupervised topics, parent topics, trend signals)
  -> Competitor landscape (combined-metric ownership map)
  -> Gap-type classifier: perception / indexing / volume_frequency on every blind spot  [Tier 1.5 — demo centerpiece]
  -> guardrail engine (3-field check + decision buckets + blocked-claims register; consumes gap_type)
  -> EVIDENCE_LEDGER.json (claims + receipts + counter-evidence + gap_type)
  -> PRESENCE_VERDICT.md (per-axis diagnosis grouped by gap type)
  -> ACTION_BRIEF.md (CLAIMS TO AVOID + actions per axis + intervention class per gap type + monitoring plan)
  -> manifest.json (snapshot id, taxonomy version, freshness, comparability)
  -> Lovable webapp (eligibility-critical; visual style follows Peec design tokens; Entire fallback by 17:00)
       |- main route: solution dashboard (the proof chain + blocked claim + gap types + action brief)
       |- /future-directions: static preview of channel-activation layer (concept-only, banner, no real benchmark data)
  |
  |-- write tools (prescription / loop closure) ---
  |     create_prompt (geo expansion + monitoring for blind-spot topics)
  |     create_tag (campaign taxonomy in Peec)
  |     create_topic (sub-themes)
  |
  v
Demo proof: every recommendation traceable; one blocked claim with safe rewrite; gap-type classifier shown across blind spots; loop closure shown; sneak peek at /future-directions in the close.
```

## Build Priorities

### P0: Submission-Critical

Build these first:

- Peec ingestion into normalized prompt observations.
- Prompt clustering by funnel stage and prompt type.
- Tavily enrichment for public proof and proof gaps.
- Gemini classification/analysis for topics, perception, and scenarios.
- Guardrail function that labels claims as `actionable`, `directional`, `insufficient_evidence`, or `blocked`.
- Core artifacts: `PRESENCE_VERDICT.md`, `ACTION_BRIEF.md`, `EVIDENCE_LEDGER.json`, `manifest.json`.
- One proof chain in the output: recommendation -> claim -> evidence refs -> source of record -> guardrail decision.
- One blocked or downgraded claim.

### P1: Differentiation

Add these once P0 works:

- `study_ssot.json` as the shared source for Markdown and dashboard.
- `pipeline_funnel.json` to explain how raw prompts became fewer recommendations.
- `source_of_record.json` so judges see which tool owns each metric.
- `hero_cards.json` for the dashboard opener.
- `cluster_diagnostics.json` for QA flags and merge decisions.

### P2: Polish

Add only if the demo is already repeatable:

- Lovable dashboard or local executive view.
- Scenario comparison card.
- Strategic quadrant or decision-bucket chart.
- Exportable one-page action summary.

## Minimal File Tree

```text
.
|-- README.md
|-- src/
|   |-- ingest_peec.ts
|   |-- enrich_tavily.ts
|   |-- analyze_gemini.ts
|   |-- guardrails.ts
|   |-- generate_artifacts.ts
|   `-- types.ts
|-- data/
|   |-- raw/
|   `-- generated/
|       |-- prompt_universe.json
|       |-- parent_topics.json
|       |-- study_ssot.json
|       |-- EVIDENCE_LEDGER.json
|       |-- pipeline_funnel.json
|       |-- source_of_record.json
|       |-- hero_cards.json
|       |-- manifest.json
|       |-- PRESENCE_VERDICT.md
|       `-- ACTION_BRIEF.md
`-- docs/
```

The exact language/framework can change, but keep this shape: one pipeline, one generated output directory, one source-of-record table, one demo path.

## Data Contracts To Protect

Every claim should carry:

- `claim_id`
- `cluster_id`
- `campaign_type`
- `campaign_category`
- `parent_topic`
- `evidence_refs`
- `source_of_record`
- `evidence_tier`
- `publication_status`
- `decision_bucket`
- `allowed_language`
- `unavailable_reason` when any field is missing or disabled

Every run should carry:

- `peec_snapshot_id`
- `artifact_version`
- `prompt_universe_version`
- `topic_taxonomy_version`
- `campaign_type_mapping_version`
- `generated_at`
- `freshness`
- `comparability`

## Implementation Steps

### 1. Normalize Peec Observations

Output:

- prompt text
- model/provider if available
- target brand mentions
- competitor mentions
- rank/position fields if available
- answer text or summarized answer text
- prompt type
- funnel stage
- Peec evidence ref

Guardrail: no recommendation can enter `ACTION_BRIEF.md` without at least one Peec evidence ref.

### 2. Build Prompt Universe

Group prompts into:

- `category`
- `competitor`
- `buying_intent`
- `problem_aware`
- `analyst_review`

Attach stage:

- `awareness`
- `consideration`
- `decision`
- `retention`

Output: `prompt_universe.json`.

### 3. Cluster And Diagnose

Cluster prompts by intent and theme. Keep this explainable:

- rule grouping first
- Gemini theme labels second
- manual seed only when declared

Output:

- `study_ssot.json`
- `cluster_diagnostics.json`
- `pipeline_funnel.json`

Diagnostics to show:

- prompt count per cluster
- small/weak/incoherent cluster flags
- merge decisions
- dropped records and reasons

### 4. Add Parent Topics And Campaign Taxonomy

Use the parent-topic flow:

```text
identified topic
  -> classified topic
  -> final parent topic
  -> campaign type
  -> campaign category
```

If type-level evidence is sparse, roll up to category. If neither is defensible, use `campaign_type: "other"` and keep it out of the executive action list.

Output:

- `parent_topics.json`
- `topic_coverage_audit.json`

### 5. Enrich With Tavily

Use Tavily for:

- competitor public proof
- public sources that support or contradict a claim
- proof gaps where the target brand lacks public support

Tavily should not override Peec visibility. It supports public proof and evidence refs.

### 6. Analyze With Gemini

Use Gemini for:

- perception themes
- missing associations
- parent-topic classification
- safe scenario wording
- draft narrative cards

Gemini should not be treated as the source of visibility metrics.

### 7. Apply Guardrails

Use three separate fields:

| field | role |
| --- | --- |
| `input_gate_status` | Whether the finding can enter analysis. |
| `evidence_tier` | How strong the evidence is. |
| `publication_status` | Whether it can appear in executive output. |

Decision buckets:

- `act_now`
- `test_next`
- `monitor`
- `deprioritize`
- `block`

Blocked claims must stay visible in `CLAIMS_TO_AVOID`, not silently disappear.

### 8. Generate Artifacts

Generate in this order:

1. `EVIDENCE_LEDGER.json`
2. `study_ssot.json`
3. `PRESENCE_VERDICT.md`
4. `ACTION_BRIEF.md`
5. `manifest.json`
6. dashboard inputs: `hero_cards.json`, `pipeline_funnel.json`, `source_of_record.json`

The Markdown should be regenerated from structured files, not hand-maintained separately.

## Dashboard Visual Storyboard

### Screen 1: Executive Snapshot

Purpose: show the product is not just a table of Peec metrics.

```text
+-------------------------------------------------------------+
| Presence Verdict: Nothing Phone                             |
| Find your brand's blind spots in AI answers                               |
+--------------+--------------+--------------+---------------+
| Guardrail    | Actionable   | Blocked      | Source        |
| pass rate    | actions      | claims       | freshness     |
+--------------+--------------+--------------+---------------+
| Top decision buckets: act_now | test_next | monitor | block |
+-------------------------------------------------------------+
```

Data: `hero_cards.json`, `manifest.json`.

### Screen 2: Prompt Cluster Map

Purpose: show where the brand wins, loses, or is absent.

```text
+----------------------------+----------+------------+--------+
| Prompt cluster             | Owner    | Tier       | Bucket |
+----------------------------+----------+------------+--------+
| Smartphone Design          | Nothing  | strong     | hold   |
| Minimalist Hardware        | Apple    | strong     | act    |
| Wireless Audio             | Apple    | strong     | test   |
| Mobile Ecosystem           | Apple    | moderate   | test   |
| Consumer Tech Innovation   | unclear  | limited    | watch  |
+----------------------------+----------+------------+--------+
```

Data: `study_ssot.json`. Numbers verified against the Nothing Phone Peec project (see [SCOPE_FINAL.md](SCOPE_FINAL.md) "Topic Breakdown").

### Screen 3: Proof Chain

Purpose: prove one recommendation is auditable.

```text
Recommendation
  -> claim_id
  -> Peec evidence ref
  -> Tavily public proof ref
  -> Gemini analysis ref
  -> source_of_record
  -> guardrail decision
```

Data: `ACTION_BRIEF.md`, `EVIDENCE_LEDGER.json`, `source_of_record.json`.

### Screen 4: Blocked Claim

Purpose: show discipline and win trust.

```text
Tempting claim: "Nothing Phone is the go-to minimalist tech brand."
Status: blocked
Reason: EVIDENCE_CONTRADICTION (6% Peec visibility vs Apple at 39%)
Safe rewrite: "Nothing Phone dominates Smartphone Design but is invisible in adjacent topics like Minimalist Hardware."
Next evidence: publish minimalist hardware content and rerun the prompt cluster after the next snapshot.
```

Data: blocked claims register in `EVIDENCE_LEDGER.json` or `ACTION_BRIEF.md`.

### Screen 5: Action Brief

Purpose: end with what a marketer should do.

```text
This week:
1. Create public proof for the missing association.
2. Update comparison content for competitor-owned clusters.
3. Monitor these prompts after publishing.

Claims to avoid:
- blocked claim with reason
```

Data: `ACTION_BRIEF.md`.

## 2-Minute Demo Storyboard — Invisible Champion

Anchored to the Nothing Phone narrative. Source of truth: [SCOPE_FINAL.md](SCOPE_FINAL.md) "The Demo Story (2 minutes)".

| time | visual | words |
| --- | --- | --- |
| 0:00-0:15 | Executive snapshot — 20% / 2.4 / 50 prompts / 5 topics / 10 brands | "Nothing Phone ranks #1 when AI mentions it — but 80% of AI answers don't mention it at all." |
| 0:15-0:30 | Multi-axis blind-spot map (topic / channel / engine / content type) | "Four blind spots: 6% in Minimalist Hardware (ironic gap), editorial review sites cite Apple, Gemini sees the brand more than ChatGPT, LISTICLE/COMPARISON pages skip it." |
| **0:30-0:50** | **Gap-type classifier (the new sharp moment)** | "But not all blind spots are the same. **Minimalist Hardware is a perception problem.** **Mobile Ecosystem is an indexing problem.** **Wireless Audio is a volume problem.** Each needs a different fix. Every recommendation in our action brief carries a gap type." |
| 0:50-1:10 | Proof chain on the Minimalist Hardware finding | "Every finding has receipts. Peec: 6% visibility, Apple at 39%. Tavily: Apple dominates public minimalist content. Gemini: 'minimalist' is associated with Apple, not Nothing. Methods agree, evidence tier strong, gap type = perception." |
| 1:10-1:25 | Blocked claim + safe rewrite | "'Nothing Phone is the go-to minimalist tech brand' — BLOCKED. The system refuses the claim, offers a safe rewrite, names the next evidence to collect." |
| 1:25-1:40 | Prescription writes via Peec MCP (`create_prompt`, `create_tag`) | "We tell Peec what to monitor next: new prompts for DE/GB and the gap topics, campaign tags created. This is loop closure — setup, not new metrics." |
| 1:40-1:50 | Presence Verdict Pack (artifacts + Lovable dashboard) | "The deliverable: PRESENCE_VERDICT.md, ACTION_BRIEF.md, EVIDENCE_LEDGER.json, manifest.json. Every recommendation traceable. Every blocked claim justified." |
| **1:50-2:00** | **Sneak peek: /future-directions in the Lovable webapp** | "Where this goes next — channel activation, gap-weighted spend allocation. *Future direction. Calibrated against external industry benchmarks held under license, not redistributable.* Static preview, separate from the diagnostic pipeline above." |

## Build Order For The Team

1. Confirm Peec MCP access and pick one sample brand.
2. Generate `prompt_universe.json` from real Peec data.
3. Generate `study_ssot.json` with clusters, visibility, parent topics, campaign mapping, and evidence fields.
4. Add Tavily enrichment refs and Gemini analysis refs.
5. Implement guardrails and blocked-claims register.
6. Generate Markdown artifacts.
7. Build dashboard from the same structured files.
8. Run public-safety scan.
9. Record the demo using the proof chain and blocked claim.

## Validation Checklist

Before recording:

- [ ] The repo contains no private names, paths, work systems, or copied private text.
- [ ] Peec data appears in a real artifact, not only README prose.
- [ ] Gemini output is used in a real classification/analysis step.
- [ ] Tavily output is used as public evidence or proof-gap analysis.
- [ ] Lovable or another eligible partner tech is used in a real visible workflow.
- [ ] Every executive recommendation has an evidence ref.
- [ ] Every blocked claim has a reason and a safe rewrite.
- [ ] Missing metrics use `null` plus an unavailable reason.
- [ ] The 2-minute video can follow one proof path without handwaving.

## Main Build Risk

The biggest risk is producing a polished marketing brief that looks generic. The fix is to make the evidence chain visible everywhere: prompt cluster, Peec ref, public proof, method agreement, guardrail decision, and allowed language.
