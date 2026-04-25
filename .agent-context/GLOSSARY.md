# Glossary

Terminology used across the repo. If two docs disagree on a term, this file wins; patch the other doc.

## Product Terms

**Presence Rx**
The product. The discipline layer on top of Peec AI that diagnoses AI-answer blind spots, classifies them by gap type, prescribes the right intervention, and refuses to promote weak claims. Tagline: *Diagnose. Prescribe. Refuse.* (with the longer descriptive line *Find your brand's blind spots in AI answers* as a sub-tagline.) Renamed from "Proof of Presence" Saturday 2026-04-25 (D-014) to better capture the diagnose-prescribe pattern that is the actual product punchline.

**Presence Verdict**
The deliverable. A structured Markdown diagnosis of the brand's six-axis blind spots, classified by gap type, written from generated JSON. Filename: `PRESENCE_VERDICT.md`.

**Presence Verdict Pack**
The four-artifact bundle: `PRESENCE_VERDICT.md` + `ACTION_BRIEF.md` + `EVIDENCE_LEDGER.json` + `manifest.json`.

**Action Brief**
The shorter, executive-facing companion to the Presence Verdict. Filename: `ACTION_BRIEF.md`. Always includes a **Claims To Avoid** section sourced from the blocked-claims register.

**Evidence Ledger**
The machine-readable JSON of every claim with its source refs, evidence tier, guardrail decision, and counter-evidence considered. Filename: `EVIDENCE_LEDGER.json`.

**Manifest**
JSON metadata for a generated run: snapshot ID, taxonomy versions, freshness, comparability, artifact list. Filename: `manifest.json`.

**Invisible Champion**
The data pattern that anchors the demo: Nothing Phone has the best position in field (2.4) but only 20% visibility. When the AI mentions it, it ranks #1; but 80% of AI answers ignore it.

**Ironic Gap**
The 6% visibility in Minimalist Hardware vs Apple's 39%, on a brand built on minimalism. The blocked-claim moment of the demo.

## Gap Types (Tier 1.5 — the new sharp moment)

**Gap-type classifier**
Tier 1.5 feature (D-011). Every blind-spot finding gets a `gap_type` field. Tier 1 diagnoses *where* the brand is invisible (by axis); Tier 1.5 classifies *what kind of fix* each blind spot needs. Each gap type triggers a different intervention class in `ACTION_BRIEF.md`.

**Perception gap (`gap_type = perception`)**
Brand wants to be known for X; AI doesn't perceive it that way. Content and citations may exist, but the *association* is missing. Detection: brand profile vs Gemini perception themes diverge; competitor owns the trait language. Nothing Phone example: Minimalist Hardware (6% vs Apple 39%) — brand built on minimalism, AI associates "minimalist" with Apple. Intervention class: positioning + messaging correction.

**Indexing gap (`gap_type = indexing`)**
Content exists on owned domains but isn't surfacing in AI answers. Retrieval ≠ citation. Detection: owned domain retrieval rate high, citation rate low; structured-data signals missing. Nothing Phone example: nothing.tech retrieved but underused for relevant prompts. Intervention class: schema markup, structured data, AI-citation optimization.

**Volume / frequency gap (`gap_type = volume_frequency`)**
Content is sparse or absent on the topic. Brand may have the product or proof point, but no public surface area. Detection: low Peec signal across all owned/earned channels; competitor dominates with sustained editorial + UGC volume. Nothing Phone example: Wireless Audio at 1% — Nothing Ear product exists, presence is near-zero, Apple at 53%. Intervention class: content creation + distribution + amplification.

**Intervention class**
The fix type triggered by a gap type. `perception` → positioning + reframing. `indexing` → schema + AI-citation optimization. `volume_frequency` → content creation + amplification. Each `ACTION_BRIEF.md` recommendation carries an intervention class so a marketer can route the work to the right team.

## Diagnosis Axes

**Topic axis**
Where the brand is invisible by Peec topic. Source: `get_brand_report(dims=topic_id)`.

**Channel axis**
Which content types miss the brand: UGC vs editorial vs reference vs corporate. Source: `get_domain_report` + gap filter.

**Engine axis**
Which AI engines (ChatGPT, Gemini, etc.) ignore the brand. Source: `get_brand_report(dims=model_id)`.

**Geography axis**
Which markets cannot see the brand. Source: `get_brand_report(dims=country_code)`. For Nothing Phone today, US-only data; other markets via `create_prompt`.

**Authority axis**
Whether content is retrieved (found) but not cited (trusted). Source: `get_url_report` retrieval_rate vs citation_rate.

**Evidence axis**
What the AI actually says when asked. Sampled receipts from `list_chats` + `get_chat`.

## Method / Guardrail Terms

**Method ladder**
The four-tier classification of evidence quality: `peec_confirmed`, `method_consensus`, `fallback_directional`, `insufficient_evidence`. Each tier has allowed claim language attached.

**Three-field guardrail**
The triple-check on every finding: `input_gate_status` (can it enter analysis?), `evidence_tier` (how strong?), `publication_status` (can it appear in executive output?). A finding can pass the input gate and have moderate evidence yet still be held back from publication.

**Decision bucket**
The operational disposition of a finding: `act_now`, `test_next`, `monitor`, `deprioritize`, `block`.

**Blocked claim**
An attractive claim that the system explicitly refuses, with a reason and a safe rewrite. Lives in the **Claims To Avoid** section of `ACTION_BRIEF.md` and the `blocked_claims_register` in `EVIDENCE_LEDGER.json`.

**Safe rewrite**
The defensible version of a blocked claim. Always paired with the blocked claim and the next evidence to collect.

**Receipts**
The full evidence chain attached to a recommendation: claim_id -> Peec ref -> public proof -> Gemini analysis -> source-of-record -> guardrail decision -> allowed language. Demo proof step.

**Counter-evidence**
Evidence that was considered and rejected for a claim, recorded alongside supporting evidence in the `rejected_evidence` array. Adversarial receipts.

**Pipeline funnel**
The stage-by-stage record of how many findings entered, how many dropped, why, and what evidence would have unblocked them. Artifact: `pipeline_funnel.json`.

## Source-of-Record Terms

**Peec is the source of truth for visibility.**
Mentions, rank, position, share of voice. Never overridden by Gemini or Tavily.

**Gemini owns analysis language.**
Themes, perception, missing associations, scenario wording. Not visibility truth.

**Tavily owns public-web evidence.**
Public proof, gap detection, competitor messaging. Not AI-answer truth.

**Guardrail engine owns go / no-go decisions.**
Derived rules over the three above. Source-of-record map: `source_of_record.json`.

## Campaign Taxonomy Terms

**Visibility topic**
Peec's pre-built prompt grouping. Five for Nothing Phone (Smartphone Design, Mobile Ecosystem, Consumer Tech Innovation, Minimalist Hardware, Wireless Audio).

**Parent topic**
Our marketing-language abstraction over Peec topics: e.g. `transparent_hardware`, `minimalist_category_language`, `mobile_design_authority`. See [../docs/PARENT_TOPIC_AND_UNSUPERVISED_PATTERNS.md](../docs/PARENT_TOPIC_AND_UNSUPERVISED_PATTERNS.md).

**Campaign type**
A higher abstraction: `product_innovation`, `brand_marketing`, `customer_experience`, etc. Maps Peec topics into marketer-facing plays.

**Campaign category**
The top-level rollup: `Brand & Commercial`, `Corporate & Financial`, `Risk & Regulatory`, `Stakeholder & Culture`, `Fallback`. Used when type-level evidence is too thin.

**Campaign granularity fallback**
The rule: prefer campaign type; roll up to category when type-level evidence is insufficient. Visible in artifacts as `campaign_granularity_reason`.

## Loop Terms

**Feedback loop**
The system's headline differentiator: emit `prompts_to_add.json`, then call `create_prompt` to register monitoring prompts back into the Peec project. The system improves the data it depends on.

**Prescription**
Tier 3 features (geo expansion, monitoring prompts, custom tags, sub-topics). The setup moment in the demo - data populates after Peec's next daily run.

**Loop closure**
The demo beat where we run the prescription writes live and narrate "we just told Peec what to monitor." The proof point is the API success, not new metrics.

## Eligibility Terms

**Eligibility-critical lane**
Items #13 (Gemini), #14 (Tavily), #20 (Lovable, with Entire fallback) in `SCOPE_FINAL.md`. Must ship in real code paths or risk disqualification.

**Real code path**
A partner technology counts toward eligibility only if it is invoked from running code or visible in a workflow. README mentions and "planned" usage do not count.

**Hard fallback**
The pre-decided swap: if Lovable is not integrated by Saturday 17:00, use Entire as the third eligible partner tech.

## Future-Directions Terms (D-012)

**Future Directions split**
The hard line between what the public submission contains (steps 1-6 of the solution flow plus the gap-type classifier) and what the private prototype demonstrates (steps 7-8: channel activation, lift study, spend allocation). Permission to *use* one-time external benchmark data ≠ permission to *publish* it. The split lets us show vision without exposing fingerprintable methodology or data.

**`/future-directions` page**
Static route in the Lovable webapp. Source content from [../docs/FUTURE_DIRECTIONS.md](../docs/FUTURE_DIRECTIONS.md). Concept-only: architecture diagram, illustrative allocation table, methodology described in own words. Banner at top declares the page illustrative. Generic vendor references (Morning Consult, Pathmatics, brand-lift methodology) are fine as industry citations. **No agency attribution, no specific client engagement, no engagement-bound data, no tables shaped like a specific permissioned export.**

**Sneak peek**
2-min storyboard segment 1:50-2:00: 5-15 second teaser of the channel-activation roadmap. Title card framing: *"Future direction. Calibrated against external industry benchmarks held under license, not redistributable."*

**Private finalist demo**
Build step #21 in the priority order. Sunday afternoon, post-submission. Channel-activation prototype using one-time-permissioned external benchmark data. Lives outside the public repo. Only used in the live finalist pitch if advancing.

## Design Terms (D-013)

**Peec design philosophy**
The Lovable webapp must align visually with Peec AI's interface — clean, data-driven, executive-readable, near-black on off-white, single light theme, Geist Variable typeface, 14 px body, 8 px / 12 px radii, signature inset+ring shadow replacing borders. Tokens captured 2026-04-25 from the live peec.ai interface (their public HTML/docs do not expose CSS). See [../docs/design.md](../docs/design.md).

**Design tokens**
Color palette, typography, spacing, surface, motion, iconography references for the Lovable webapp. Captured by inspecting the live rendered Peec interface in DevTools. Filled in by the Lovable lane before any visual work lands.

## Process Terms

**Public-safety scan**
The pre-push grep for private paths, internal names, work credentials, agency-attribution / client-engagement / engagement-bound-data fingerprints, etc. Every generated artifact must pass this before the repo goes public. **Generic industry vendor names (Morning Consult, Pathmatics, brand-lift methodology) are not flagged** — these are public companies and standard methodologies referenced industry-wide. The fingerprint risk is *agency name + specific client engagement + engagement-shaped data*, not the vendor names themselves. See [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md).

**Submission gate**
Items #14-19 in the build priority order: public GitHub repo via `gh-play`, README listing every API/tool used, public-safety scan on artifacts, submission form verification on Discord, video recording, submit.

**Loop closure demo segment**
2-minute storyboard segment 1:25-1:40: run prescription writes live, narrate the loop.

**Gap-type demo segment**
2-minute storyboard segment 0:30-0:50: classify each blind spot by gap type, narrate why each needs a different fix. The new sharp moment.

## When to Update

Add a term when a new doc introduces it and it is not already here. Remove a term when no doc uses it anymore.
