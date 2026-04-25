# Decisions

Locked decisions on the Peec build, with rationale and links to source docs. Open questions at the bottom.

## Locked Decisions

### D-001: Track is Peec
- **Decision:** Build for the Peec AI track (not Buena, not Qontext).
- **When locked:** Saturday 2026-04-25, ~12:30 CEST.
- **Why:** Peec MCP gave us deeper data than expected; Nothing Phone "Invisible Champion" pattern is a stronger demo than Buena's freshness loop or Qontext's broad VFS scope.
- **Source:** [../../../TRACK_DECISION.md](../../../TRACK_DECISION.md)

### D-002: Brand is Nothing Phone
- **Decision:** Demo on the existing Nothing Phone Peec project, not Attio (the obvious default).
- **When locked:** Saturday afternoon, after MCP exploration.
- **Why:** (1) other teams will default to Attio; (2) Nothing Phone is the Invisible Champion (best position 2.4, only 20% visibility); (3) Minimalist Hardware ironic gap (6% vs Apple 39%) is the blocked-claim moment.
- **Source:** [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md) "Strategic Decision: Nothing Phone, Not Attio"

### D-003: Product naming
- **Decision:** Product = **Presence Rx** (renamed from "Proof of Presence" — see D-014). Deliverable = **Presence Verdict** (filename `PRESENCE_VERDICT.md`). Primary tagline = **Diagnose. Prescribe. Refuse.** Sub-tagline = *Find your brand's blind spots in AI answers.*
- **When locked:** Saturday afternoon, during polish pass. Renamed from "Proof of Presence" Saturday late afternoon (D-014).
- **Why:** The earlier "AI Distribution Study" framing was too generic. The "Proof of Presence" name covered the receipts/diagnosis half but missed the prescribe + refuse half once Tier 1.5 (gap-type classifier) landed. **Presence Rx** captures the diagnose-classify-prescribe-refuse pattern that is the actual product punchline. All in-repo and parent-challenge docs are reconciled to this naming.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md), [../README.md](../README.md), D-014 (rename rationale).

### D-004: Six-axis blind-spot model
- **Decision:** Diagnose blind spots across Topic / Channel / Engine / Geography / Authority / Evidence axes.
- **When locked:** Saturday afternoon, after holistic MCP analysis.
- **Why:** Peec exposes far more than topic visibility. Each axis maps to a different Peec read tool and unlocks differentiated insight no other team will surface.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md), [../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md](../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md)

### D-005: Eligibility-critical lane
- **Decision:** Gemini + Tavily + Lovable are the three eligible partner technologies. All three must ship in real code paths. Entire is the hard fallback for Lovable if not integrated by Saturday 17:00.
- **When locked:** Saturday afternoon, during scope review.
- **Why:** Hackathon rules require 3 eligible partner technologies. Peec MCP is the required track tool; eligibility unconfirmed. If Lovable stalls, Entire fills the third slot via a review/sign-off workflow over blocked claims.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) "Eligibility-critical lane" callout

### D-006: 22 features in 4 tiers
- **Decision:** Tier 1 (must-ship) = 9 features, Tier 2 (should-ship + eligibility critical) = 5, Tier 3 (prescription / setup) = 5, Tier 4 (surface) = 3. 16-step build priority order with submission gates.
- **When locked:** Saturday afternoon, after holistic MCP analysis and validation pass.
- **Why:** Compresses everything we can build into a clear ordering with feasibility and impact ratings. Tier 3 framing makes "setup, not result" honest about Peec's daily-run delay.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md)

### D-007: No `create_project` available
- **Decision:** We work entirely inside the existing Nothing Phone Peec project. New brands, prompts, topics, and tags are created via `create_*` write tools. No custom-project strategy.
- **When locked:** Saturday afternoon, after MCP write-tool inventory.
- **Why:** Peec MCP exposes write tools for brands / prompts / topics / tags but **no `create_project`**. New prompts populate only after Peec's daily run, so Tier 3 prescription writes are demo-as-setup, not demo-as-result.
- **Source:** [../docs/PEEC_MCP_TOOL_MAP.md](../docs/PEEC_MCP_TOOL_MAP.md) "Write Tools (Constrained)"

### D-008: Repo is play-side only
- **Decision:** No work credentials, no work connectors, no work SaaS endpoints. The repo will be public.
- **When locked:** Saturday morning, at scaffold creation.
- **Why:** Hackathon rules require a public GitHub repo. Work-side data and tooling are off-limits per the user's global agent policy.
- **Source:** [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md), [../AGENTS.md](../AGENTS.md)

### D-009: Lovable is Tier 1 (eligibility-critical)
- **Decision:** Lovable promoted from Tier 4 to eligibility-critical. Entire is the hard fallback. `pm-dashboard.html` is the local visual shell, not a substitute for partner-tech eligibility.
- **When locked:** Saturday 14:00 CEST validation pass.
- **Why:** Lovable was originally rated Feasibility 4/10 with "could reuse pm-dashboard.html instead." That phrasing risked dropping a partner tech to zero real-code-path integration, which would fall below the 3-partner minimum.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) item #20

### D-010: Tier 3 prescription writes are setup, not results
- **Decision:** Tier 3 features (`create_prompt` for monitoring, geo expansion, custom tags, new topics) demo the **API-call moment**. Data populates after Peec's next daily run, post-demo. The proof point is loop closure ("we just told Peec what to monitor"), not new metrics.
- **When locked:** Saturday 14:00 CEST validation pass.
- **Why:** Peec runs daily snapshots. New prompts created mid-demo will not have data within the 2-minute window. Honest framing avoids judges expecting populated data.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) Tier 3 callout

### D-011: Gap-Type Classifier (Tier 1.5) is the new sharp moment
- **Decision:** Add a `gap_type` field — `perception` / `indexing` / `volume_frequency` — to every blind-spot finding. Each gap type triggers a different intervention class in `ACTION_BRIEF.md`. Diagnoses *what kind of fix is needed*, not just *where the gap is*.
- **When locked:** Saturday 2026-04-25, late afternoon, after step 5 validation.
- **Why:** Tier 1 already diagnoses where the brand is invisible (topic/channel/engine/content type). Without gap-type, every blind spot looks generic in the action brief. With gap-type, every recommendation carries an intervention class that judges grok in 5 seconds. Buildable today using only Peec + Tavily + Gemini outputs already in the pipeline — no new external data.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) Tier 1.5 section.

### D-012: Future Directions split — public repo vs private follow-up
- **Decision:** Steps 7-8 (channel activation, lift study, spend allocation) split into two assets: (a) a public-repo `FUTURE_DIRECTIONS.md` with concept-only content + a static page in the Lovable webapp, both clearly marked as illustrative and calibrated against industry benchmarks generically (Morning Consult brand-lift, Pathmatics competitor spend) without engagement-bound data; (b) a private-only prototype using one-time-permissioned external benchmark data from a specific client engagement, built outside the public repo, demoed only in a live finalist pitch if advancing. Submission video may include a 5-15s sneak peek at the end using conceptual visuals + illustrative numbers; vendor names in the framing are fine, agency attribution and client-engagement specifics are not.
- **When locked:** Saturday 2026-04-25, late afternoon. Refined later that day to clarify that public-industry-vendor names (Morning Consult, Pathmatics) and generic methodology terms (brand lift) are *not* the fingerprint risk — the risk is agency attribution + specific client engagement + engagement-bound data.
- **Why:** Permission to *use* the external benchmark data from a specific engagement does not equal permission to *publish* it. The fingerprint risk is **agency name + specific client engagement + engagement-shaped data** — not the names of public industry tools or generic methodology terms used industry-wide. Morning Consult and Pathmatics are public companies referenced by hundreds of agencies and brands; brand-lift study is industry-standard terminology (Nielsen, Google Ads, Meta all run brand-lift). Citing them generically does not create attribution. What does create attribution: naming the agency, naming a specific client engagement, copying verbatim deliverables, importing data from an engagement into the Nothing Phone analysis. The split keeps engagement-bound work outside the public repo while letting the public surface honestly describe the methodology category.
- **Source:** [../docs/FUTURE_DIRECTIONS.md](../docs/FUTURE_DIRECTIONS.md), [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) Tier 4 #21.

### D-013: Lovable webapp must follow Peec AI's design philosophy
- **Decision:** The Lovable dashboard surface (Tier 4 #20, eligibility-critical) must align visually with Peec AI's design philosophy — clean, data-driven, executive-readable, with color and typography pulled from the live peec.ai interface. Tokens captured in [../docs/design.md](../docs/design.md) (renamed from `DESIGN_TOKENS.md`).
- **Status:** ✓ **Satisfied 2026-04-25 (late afternoon).** Tokens captured from a live walkthrough of the Peec AI app (Tags, Overview, Prompts, Brands, Profile, Domains). The Lovable build can apply the cheat-sheet CSS variables (Section 9) directly.
- **When locked:** Saturday 2026-04-25, late afternoon.
- **Why:** Track judges include the Peec PM. A surface visually disconnected from Peec reads as "wrapper that doesn't respect the host." Visual alignment is a credibility signal that a 2-minute demo can leverage without spending a sentence on it.
- **Source:** [../docs/design.md](../docs/design.md), [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) Tier 4 #20.

### D-014: Renamed from "Proof of Presence" → "Presence Rx"
- **Decision:** Rename the product from "Proof of Presence" to **Presence Rx**. Adopt **Diagnose. Prescribe. Refuse.** as the primary tagline; keep *Find your brand's blind spots in AI answers* as a sub-tagline. GitHub repo name `cote-star/presence-rx`. Local folder also renamed `challenges/peec/repo` → `challenges/peec/presence-rx` (D-014 follow-up, Saturday late afternoon — kept the folder name aligned with the GitHub repo for less ambiguity).
- **When locked:** Saturday 2026-04-25, late afternoon, after Tier 1.5 (gap-type classifier) added.
- **Why:** "Proof of Presence" carried the receipts/diagnosis half but undersold the prescribe + refuse half once the gap-type classifier landed. "Presence Rx" captures all four moves (diagnose, classify, prescribe, refuse) in two syllables. Rx is universally read as "prescription" — matching what the product actually does. Preserves brand equity from the existing repo while signaling the broader scope.
- **Migration cost:** Touched 14 files, 30 mentions across docs + dashboard. Single-pass rename. Deliverable name "Presence Verdict Pack" preserved.
- **Source:** [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md), [GLOSSARY.md](GLOSSARY.md) "Presence Rx" entry.

## Open Questions

These are unresolved and may force new decisions:

### Q-001: Does Peec MCP count toward the 3-partner minimum?
- **Why open:** Hackathon rules say 3 eligible partner technologies; Peec is the required track tool. If Peec also counts, we have 4 (Peec + Gemini + Tavily + Lovable) and Lovable becomes optional. If Peec does not count, we must have all three of Gemini + Tavily + Lovable in real code paths, with Entire fallback.
- **How to resolve:** Ask the organisers on the hackathon Discord.
- **Owner:** Amit (in-person at the venue).

### Q-002: Submission form link
- **Why open:** The pre-event form link may be stale.
- **How to resolve:** Verify on the hackathon Discord at the opening session and again before submission.
- **Owner:** Amit.

### Q-003: Lovable feasibility within the time budget
- **Why open:** Even at Feasibility 6, Lovable integration could slip past the Saturday 17:00 decision gate.
- **How to resolve:** Hard checkpoint at 17:00. If Lovable is not pushing data, swap to Entire (review/sign-off workflow) per D-009 fallback.
- **Owner:** Whoever is on the dashboard lane.

### Q-004: Public-safety scan on generated artifacts
- **Why open:** Generated `PRESENCE_VERDICT.md` / `ACTION_BRIEF.md` / `EVIDENCE_LEDGER.json` may pull text from Peec chats, Tavily search results, or Gemini analyses that could echo private fingerprints.
- **How to resolve:** Run [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) on every generated artifact before pushing public. Specifically grep for `private | internal | client | secret | token | password | absolute paths`.
- **Owner:** Cursor / Composer (external QA lane).

## Decision Hygiene

- Every locked decision has an ID, a rationale, and a source doc.
- When a decision changes, update this file and bump the pack version in [INDEX.md](INDEX.md).
- Open questions move to "locked" only after they have a documented answer and an updated source doc.
