# Peec PM Visual Board

Use this as a fast walkthrough with the Peec PM. Goal: validate that the product shape matches what Peec data can actually support.

## One-Liner

**Presence Rx — Diagnose. Prescribe. Refuse.** Peec shows where a brand appears in AI answers; Presence Rx turns that into an evidence-backed action brief — diagnoses each blind spot, classifies it by gap type (perception / indexing / volume), prescribes the right intervention, and refuses to promote claims that are not safe to make. Sub-tagline: *find your brand's blind spots in AI answers.*

## What I Am Building

```text
Peec visibility data
  -> prompt clusters
  -> competitor ownership
  -> public proof checks
  -> guardrails
  -> marketer action brief
```

Not a generic content generator. Not a vanity dashboard. The output is a short, defensible study that says:

- where the brand appears
- how competitors are framed
- what claim is safe to make
- what action to test next
- what not to claim yet

## Product Screen In 30 Seconds

```text
+----------------------------------------------------------+
| Presence Verdict: Nothing Phone                          |
| Find your brand's blind spots in AI answers              |
+----------------+----------------+------------------------+
| 42 prompts     | 9 clusters     | 3 supported actions    |
| 2 blocked      | 1 conflict     | fresh snapshot         |
+----------------+----------------+------------------------+

Prompt cluster                 Owner      Tier       Move
---------------------------------------------------------------
Startup CRM consideration      Rival      moderate   test next
Implementation support         Rival      strong     act now
Enterprise trust               unclear    limited    monitor

Selected action:
Create public proof for implementation support.

Receipts:
Peec prompt refs -> public source refs -> Gemini analysis -> guardrail
```

## Why This Uses Peec Well

Peec is the source of truth for AI-answer visibility:

- target brand mention
- competitor mention
- position/rank if available
- answer framing
- prompt-level observations
- prompt clusters over time or by snapshot

The rest of the stack supports Peec:

- **Gemini:** classify themes, parent topics, missing associations, scenario wording.
- **Tavily:** collect public proof and proof gaps.
- **Dashboard:** show the study, proof chain, and blocked claims.

## The Differentiator

Most tools stop at "you are visible here."

This system adds:

```text
Visibility signal
  -> evidence quality
  -> source of record
  -> allowed language
  -> action or block decision
```

Example:

```text
Tempting claim:
"The brand owns implementation support."

System decision:
Blocked - methods conflict and Peec sample is thin.

Safe rewrite:
"Implementation support is a contested prompt cluster."

Next step:
Run more prompts and publish proof assets.
```

## What I Need From Peec PM

### 1. Data Reality

- Which sample brand has the richest usable Peec data?
- Does Peec expose prompt text, answer text, mention position, competitor mentions, and timestamps/snapshots?
- Are prompt clusters already available, or should I create them?

### 2. Best Demo Use Case

Which story lands best for Peec?

- B2B challenger brand against incumbents
- consumer brand perception gap
- category ownership and competitor comparison
- monitoring after a content/action change

### 3. Guardrail Fit

Does this framing match Peec's view?

- Peec owns visibility metrics.
- Gemini owns analysis language, not visibility truth.
- Tavily owns public evidence, not AI-answer truth.
- The product should block weak claims instead of overclaiming.

### 4. Partner-Tech Rule

- Does Peec MCP count as required track tool only, or also toward partner-tech eligibility?
- Is a Lovable dashboard enough as the third partner-tech path if Gemini and Tavily are used in generation?

## Fast Validation Questions

Ask these directly:

1. "Is `prompt cluster -> competitor owner -> action brief` a useful Peec story?"
2. "What Peec fields should I absolutely show in the proof chain?"
3. "Which sample brand will make this look strongest?"
4. "Can I cite prompt-level Peec refs in generated artifacts?"
5. "What should I avoid claiming about Peec data?"
6. "Would a blocked-claim demo make Peec look more credible or too cautious?"

## PM Decision I Need

```text
Best brand:
Best Peec fields to show:
Best demo story:
Peec claim boundaries:
Partner-tech eligibility answer:
```

## Final Demo Promise

In 2 minutes, the judge sees:

1. Peec snapshot becomes prompt clusters.
2. Clusters reveal competitor-owned answer territory.
3. Public evidence and Gemini analysis explain the gap.
4. Guardrails downgrade or block weak claims.
5. The marketer gets a concrete action brief with receipts.

