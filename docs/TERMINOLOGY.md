# Presence Rx — Terminology Reference

Public-facing labels used in the dashboard, markdown deliverables, and documentation. Internal JSON artifact keys are stable and never exposed to end users.

## Display Label Map

| Internal key (stable) | Old label | Public label | Rationale |
|----------------------|-----------|--------------|-----------|
| relevance_score | Relevance | Intent Fit | How well the topic matches brand identity |
| source_trust_score | Source Trust | Citation Authority | Peec-aligned; citation rate is industry standard |
| proof_strength_score | Proof Strength | Evidence Coverage | Standard evidence-based marketing term |
| method_agreement_score | Agreement | Signal Alignment | 3 independent signals agree/disagree |
| opportunity_score | Opportunity | Action Priority | What should the user act on first |
| decision_bucket | Decision | Recommended Action | act_now / test_next / monitor / block |
| confidence_tier | Confidence | Evidence Level | strong / moderate / limited / blocked |
| guardrail | Guardrail | Claim Check | Safety verification layer |
| blocked_claim | Blocked claim | Claim To Avoid | Demo-friendly, scope-aligned |
| prescription | Prescriptions | Action Plan | User-facing action output |
| value_added_metrics | Value-added metrics | Priority Signals | Not consulting jargon |
| proof_gap | Proof gap | Evidence Gap | Standard term |
| indexing (gap_type) | Indexing | Discovery | Content exists but AI doesn't surface it |
| volume_frequency (gap_type) | Volume / Frequency | Attention | Product exists but public signal is sparse |

## Peec-Standard Terms (keep unchanged)

These are industry/product standard — do not rename:
- Visibility, Share of Voice, Sentiment, Position
- Citation Rate, Retrieval Rate, Source Visibility
- Prompt Volume, Prompt Coverage
- Brand Mention Rate, Answer Inclusion

## Rule

JSON artifact keys never change. Translation happens at the rendering layer only.
