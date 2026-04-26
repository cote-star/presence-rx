# Presence Rx

**From AI visibility gaps to earned marketing action, with receipts.**

Presence Rx turns Peec AI visibility data into a marketer-facing decision system. It does not just show where a brand appears in AI answers. It explains why the brand is missing, what kind of problem the gap represents, what to do next, what to monitor, and what the brand has earned the right to claim.

> **Diagnose. Prescribe. Refuse.**

## What We Built

Presence Rx is an AI marketer workflow for brands navigating AI-mediated discovery.

Peec shows the visibility signal: where a brand appears, where competitors dominate, and which topics, engines, and sources shape AI answers. Presence Rx adds the decision layer on top:

- **Diagnose** strategic gaps across topics, competitors, and AI-answer visibility.
- **Classify** each gap as a perception, discovery, or attention problem.
- **Prescribe** the next marketing action by channel, audience, and topic.
- **Refuse** unsupported ownership claims before they reach the market.
- **Monitor** recovery through evidence-led prompts and claim boundaries.

The result is a dashboard and evidence pack that a marketer can use immediately: action priorities, conversation blocks, claim checks, evidence receipts, audience guidance, and exportable artifacts.

## Why It Matters

AI answers are becoming a discovery surface for brands. Visibility alone is not enough. A marketer needs to know:

- Is this a real strategic gap or a topic we should ignore?
- Is the brand missing because of perception, discoverability, or lack of public signal?
- Which audience and channel should we activate first?
- What can we safely claim today?
- What would be an overclaim?

Presence Rx answers those questions with source-of-record discipline. Peec remains the visibility truth. Public evidence, perception analysis, and claim guardrails are layered on top without blurring what came from where.

## Product Surface

The webapp is the primary demo surface.

| Page | What It Does |
| --- | --- |
| **Action Brief** | Starts with the user outcome: priority gaps, claims to avoid, where to engage, and who to reach. |
| **Conversation Blocks** | Explains each topic with visibility, competitor owner, gap type, signal alignment, perception themes, and strategic context. |
| **Claims & Simulator** | Lets a marketer test claims against evidence. Blocks overclaims and suggests safer wording. |
| **Charts** | Shows visibility, gap mix, action priority, competitor landscape, and signal profiles. |
| **Directions** | Shows clearly labeled future-direction previews for audience and channel planning. |
| **Export** | Downloads the evidence ledger, action brief, and full case data. |

## Case Studies

The dashboard ships with three brand case studies:

- **Nothing Phone** — the core live-evidence story. Strong in smartphone design, but strategically under-recognized for minimalist hardware and wireless audio.
- **Attio** — a SaaS CRM example showing product-led CRM strength, startup CRM competition, and non-priority migration claims.
- **BMW** — an automotive example showing driving-dynamics heritage, luxury EV transition gaps, and premium SUV competition.

Nothing Phone includes Tavily public-evidence enrichment with 40 web sources. Attio and BMW demonstrate the same strategic-intent and claim-guardrail system across additional brand categories.

## The Core Demo Moment

Presence Rx can say no.

Example:

> "Nothing Phone is the go-to minimalist tech brand."

Presence Rx blocks the claim because Peec visibility shows the minimalist-hardware association is still owned by Apple in AI answers. It then provides a safer rewrite:

> "Nothing Phone brings a distinctive take on minimalism — transparent, stripped-back, intentionally different. The gap between brand intent and AI perception is the opportunity."

That is the product's philosophy: not just what to say, but what the brand has earned the right to say.

## How It Works

![Presence Rx architecture](docs/submission-architecture.svg)

For the recording-friendly version, open [docs/submission-architecture.html](docs/submission-architecture.html).

```text
Brand strategy + audience profile
        ↓
Prompt and topic universe
        ↓
Peec AI visibility data
        ↓
Public proof + perception analysis
        ↓
Presence Rx decision engine
        ↓
Claim guardrails + action priorities
        ↓
Dashboard + evidence ledger + action brief
```

### Source-of-Record Map

| Layer | Role |
| --- | --- |
| **Peec MCP / Peec data** | Source of truth for AI visibility, topics, competitors, positions, and source signals. |
| **Tavily** | Public web evidence and editorial proof-gap enrichment. |
| **Gemini analysis layer** | Perception themes, missing associations, and narrative diagnostics. |
| **Presence Rx** | Strategic status, gap type, action priority, claim ceiling, and safe rewrite logic. |
| **Next.js webapp** | Marketer-facing dashboard and claim-simulator workflow. |

## Key Concepts

| Concept | Meaning |
| --- | --- |
| **Strategic Gap** | A topic the brand wants to be known for, but where AI answers currently favor a competitor or miss the brand. |
| **Owned Strength** | A topic where the brand already has strong AI visibility and should defend the position. |
| **Non-Priority** | A monitored topic that is not worth actively fighting for. |
| **Perception Gap** | The brand exists in the market, but AI associates the desired trait with someone else. |
| **Discovery Gap** | The brand has relevant content, but AI systems do not retrieve or cite it reliably. |
| **Attention Gap** | The product or proof exists, but there is not enough public signal for AI answers to surface it. |
| **Claim Ceiling** | The strongest claim the evidence supports without overstatement. |

## Repository Structure

```text
presence_rx/              Python pipeline and artifact builders
tests/                    Contract, behavior, and pipeline tests
data/generated/           Generated case-study artifacts
webapp/                   Next.js dashboard
webapp/public/data/       Dashboard-ready brand data
docs/                     Method notes, demo scripts, and submission assets
```

## Run The Dashboard

```bash
cd webapp
npm install
npm run dev
```

Open the local URL printed by Next.js, usually:

```text
http://localhost:3000
```

Build and typecheck:

```bash
cd webapp
npm run build
npm run lint
```

## Run The Data Pipeline

Install Python dependencies:

```bash
uv sync --dev
```

Run the pipeline:

```bash
make run
```

Validate generated artifacts:

```bash
make validate
```

Run tests and lint:

```bash
make test
make lint
```

## Generated Outputs

Core generated artifacts include:

- `PRESENCE_VERDICT.md`
- `ACTION_BRIEF.md`
- `EVIDENCE_LEDGER.json`
- `study_ssot.json`
- `value_added_metrics.json`
- `competitor_landscape.json`
- `manifest.json`

The webapp consumes the dashboard-ready JSON files in `webapp/public/data/`.

## Submission Notes

- The dashboard is the primary demo surface.
- Future-direction screens are clearly labeled as illustrative previews.
- Peec visibility data remains the measurement source of record.
- Public web evidence is summarized and referenced; raw source text is not copied into the product narrative.
- Claim checks are evidence-scored and intentionally conservative.

## Team

Built for the Peec AI track at Big Berlin Hack 2026.
