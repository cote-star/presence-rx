# Onboarding - Your First 30 Minutes

You just finished reading the agent-context pack. Here is the shortest path to your first useful contribution.

## Step 0: Confirm Your Lane (1 min)

Open [LANES.md](LANES.md) and find the row that matches you. Note the lane-specific reading list - the canonical doc you should consult most often.

If you do not have a lane, you are likely an ad-hoc reviewer or human contributor. Default to read-only until briefed.

## Step 1: Sanity-check Ground Truth (3 min)

Open [GROUND_TRUTH.md](GROUND_TRUTH.md). Verify:

- Project ID for Nothing Phone: `or_faaa7625-bc84-4f64-a754-a412d423c641`
- Brand IDs and topic IDs are present (10 brands, 5 topics)
- Engine breakdown is captured (Gemini / ChatGPT / Google AI Overview)
- Channel and gap-domain data is present

If any of this looks wrong, **stop**, do not start coding, and re-read [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md). Ground truth wins; this pack is downstream.

## Step 2: Confirm Active Plan (3 min)

Open [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md). Specifically:

- Confirm Tier 1, 2, 3, 4 layout
- Note the **Eligibility-critical lane** callout (Gemini + Tavily + Lovable, Entire fallback by 17:00)
- Note the **Tier 3 = setup, not result** caveat
- Skim the 16-step build priority order; find your lane's items

If you disagree with the locked scope, write the disagreement to [DECISIONS.md](DECISIONS.md) under "Open Questions" with a Q-XXX ID. Do not silently change scope.

## Step 3: Check What's Built (2 min)

Open [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md). Look for:

- Phase 1 audit (data exploration) - should be mostly complete
- Phase 2 brand strategy - locked on Nothing Phone
- Phase 3 partner wiring - status of Gemini / Tavily / Lovable / Peec MCP
- Phase 4 pipeline build - status of `src/` modules
- Phase 5 artifacts - generated files in `data/generated/`
- Phase 6 demo proof path
- Phase 7 submission gates
- Phase 8 side challenge (optional)

This is the cross-agent status board. Pick an unchecked item in your lane.

## Step 4: Check Branches (1 min)

Run:

```bash
git status
git log --oneline -10
git branch -a
```

If another agent has a branch open on the module you were going to build, coordinate before duplicating work. See [LANES.md](LANES.md) "Coordination Rules".

## Step 5: Pick Your First Task (5 min)

Match your lane to the highest-priority unchecked item in [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md):

| Lane | Likely first task |
| --- | --- |
| Architecture + backend (Claude) | Step 1: Peec ingestion. Wire `get_brand_report` (topic + model dimensions), `get_domain_report`, `get_url_report`, `get_actions` into normalized JSON structures matching [../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md). Also owns Step 5: gap-type classifier (Tier 1.5, demo centerpiece) — emits `gap_type` field on every blind-spot row from Peec + Tavily + Gemini outputs. |
| Implementation + review (Codex) | Step 6: Guardrail engine. Implement the three-field check (input_gate, evidence_tier, publication_status) plus the method ladder. Consumes `gap_type` as input. Tests for each tier. |
| Research + validation (Gemini lane) | Step 3: Gemini perception integration. Test prompt classification and perception theme extraction on Nothing Phone topic data. Drives the perception side of the gap-type classifier. Eligibility-critical. |
| Frontend / UX (Claude design) | Step 10: ✓ done. Peec design tokens captured 2026-04-25 in [../docs/design.md](../docs/design.md). Step 11: Lovable dashboard — set up the Lovable project (code `COMM-BIG-PVDK`), wire it to read `study_ssot.json` + `hero_cards.json`, apply tokens from `design.md` (Sections 9–11). Eligibility-critical with 17:00 decision gate. Step 12: Build the static `/future-directions` page from [../docs/FUTURE_DIRECTIONS.md](../docs/FUTURE_DIRECTIONS.md) — concept-only, banner, no real benchmark data. |
| External QA (Cursor / Composer) | Step 16: public-safety scan. Set up the grep harness against [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md). Run after each artifact-generation pass. Verify no agency-attribution / specific-client-engagement / engagement-bound-data fingerprints in any committed file. **Note:** generic industry vendor names (Morning Consult, Pathmatics, brand-lift methodology) are *not* flagged — these are public companies and standard methodology terms referenced industry-wide. |
| Decisions + pitch (Amit) | Resolve open questions Q-001 (Peec eligibility) and Q-002 (submission form link) on the hackathon Discord. Capture private finalist demo (Step 21) Sunday afternoon if advancing. |

## Step 6: Open a Branch and Start (15 min)

```bash
git checkout -b <lane>/<topic>
# example: git checkout -b claude/ingestion
```

Code or doc-write against the canonical artifact contracts. Read from JSON, write to JSON. No silent blanks (use `null` plus `unavailable_reason`).

When you finish, open a PR. Squash on merge.

## Common Pitfalls

- **Building outside scope.** Every feature must trace to a SCOPE_FINAL item. If it does not, write the proposal as an open question first.
- **Editing Markdown artifacts by hand.** `PRESENCE_VERDICT.md` and `ACTION_BRIEF.md` are generated from `study_ssot.json`. Never hand-edit. If the Markdown is wrong, fix the SSOT or the generator.
- **Promoting a partner tech without a real code path.** Lovable in the README only is not Lovable. See D-009.
- **Pushing without the public-safety scan.** Anything generated may echo private fingerprints. Always grep first.
- **Calling `delete_*` on Peec MCP.** Don't. Use `create_*` only.
- **Ignoring the 17:00 Lovable decision gate.** If the dashboard lane is stuck, swap to Entire (D-005, D-009).

## When You're Stuck

1. Check [DECISIONS.md](DECISIONS.md) - the answer might already be locked.
2. Check [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) - the answer might be in the tier framing or the build order.
3. Check [GROUND_TRUTH.md](GROUND_TRUTH.md) - the answer might be in the real Peec data.
4. Open an open question in [DECISIONS.md](DECISIONS.md) with a Q-XXX ID and route to Amit (decision lane).

## How to Hand Off

When you finish your shift, leave a short note in [DECISIONS.md](DECISIONS.md) under "Open Questions" if you hit a blocker, or update [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md) checkbox state for what landed. For a richer handoff, the chorus pack ([../.agent-chorus/providers/](../.agent-chorus/providers/)) preserves the session record automatically — name your branch and PR clearly so the next agent can pick up:

```text
<lane>/<topic>
example: claude/ingestion, codex/guardrails, gemini/perception
```

Keep the handoff in version control (commits, PR descriptions, checklist updates), not in floating Markdown files.

## What Done Looks Like

- Your task in [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md) is checked off.
- Your code or doc edits are merged to `main`.
- The next dependent task (if any) is unblocked.
- Your generated output passes the public-safety scan.

Now go ship.
