# Presence Rx

### Find your brand's blind spots in AI answers — with receipts at every step.

---

AI answers are the new discovery surface. When someone asks ChatGPT, Gemini, or Perplexity for a product recommendation, your brand is either in the answer or it isn't.

**Presence Rx** turns that signal into a marketing decision system.

It doesn't just show where you appear. It tells you *why* you're missing, *what kind* of problem it is, *what to do next*, and *what you've earned the right to claim* — backed by evidence, not assumptions.

> **Diagnose. Prescribe. Refuse.**

---

## The Problem

A brand marketer today faces a new kind of blind spot:

- *"We rank #1 when mentioned, but only 20% of AI answers mention us at all."*
- *"AI says we're innovative, but associates our core trait with a competitor."*
- *"Our product exists, but AI can't find it."*

Visibility data tells you *where* the gap is. It doesn't tell you what kind of gap it is, what to do about it, or what you can safely say externally. That's what Presence Rx adds.

---

## What Presence Rx Does

| | |
|---|---|
| **Diagnose** | Classify each gap as a perception, discovery, or attention problem |
| **Prescribe** | Recommend the next marketing action by channel, audience, and topic |
| **Refuse** | Block unsupported ownership claims before they reach the market |
| **Monitor** | Track recovery through evidence-led prompts and claim boundaries |

Every recommendation comes with a source-of-record trail: what Peec measured, what public evidence confirms, and where the two agree or disagree.

---

## The Demo Moment

Presence Rx can say **no**.

A marketer types:

> *"Nothing Phone is the go-to minimalist tech brand."*

Presence Rx **blocks the claim** — because Peec visibility data shows the minimalist-hardware association is still owned by Apple in AI answers. Then it provides a safer rewrite:

> *"Nothing Phone brings a distinctive take on minimalism — transparent, stripped-back, intentionally different. The gap between brand intent and AI perception is the opportunity."*

That's the product philosophy: not just what to say, but what the brand has **earned the right to say**.

---

## The Product

Six pages, one workflow. Every screen answers a marketer's question.

**Action Brief** — *What should I do first?*
Priority gaps, claims to avoid, where to engage, who to reach.

**Conversation Blocks** — *What's actually happening in AI answers?*
Each topic with visibility, competitor owner, gap type, signal alignment, perception themes, and strategic context.

**Claims & Simulator** — *What can I safely say?*
Test any marketing claim against evidence. Blocked claims get a reason and a safer rewrite.

**Charts** — *Show me the data.*
Visibility, gap mix, action priority, competitor landscape, and topic signal profiles.

**Directions** — *Where is this going?*
Audience engagement signals and channel allocation previews, labeled as modeled projections.

**Export** — *Give me the receipts.*
Download the evidence ledger, action brief, and full case data.

---

## Case Studies

Three brands, three market contexts.

### Nothing Phone — The Invisible Champion
Ranks #1 when mentioned but appears in only 20% of AI answers. Strong in smartphone design, strategically under-recognized for minimalist hardware and wireless audio. Includes 40 Tavily web-evidence sources and Gemini perception analysis.

### Attio — The Modern Challenger
A SaaS CRM loved by operators but invisible in AI-mediated discovery dominated by Salesforce and HubSpot. Product-led CRM positioning, startup competition, and evidence-bounded claims.

### BMW — Heritage vs. Electrification
Strong legacy brand with driving-dynamics reputation, but Tesla dominates AI answers about EVs. Luxury EV transition gap, premium SUV competition, and heritage defense.

---

## Architecture

![Presence Rx architecture](docs/submission-architecture.svg)

```
Brand strategy + audience profile
        |
Prompt and topic universe
        |
Peec AI visibility data (source of truth)
        |
Public proof + perception analysis
        |
Presence Rx decision engine
        |
Claim guardrails + action priorities
        |
Dashboard + evidence ledger + action brief
```

### Source-of-Record Discipline

| Source | Role |
|--------|------|
| **Peec AI** | Visibility truth — topics, positions, competitors, engine coverage |
| **Tavily** | Public web evidence — editorial citations, proof-gap enrichment |
| **Gemini** | Perception analysis — themes, missing associations, narrative diagnostics |
| **Presence Rx** | Decision layer — strategic status, gap classification, claim ceilings, safe rewrites |

Every metric in the dashboard traces back to a named source. The system never blends signals without attribution.

---

## Glossary

| Concept | What It Means for a Marketer |
|---------|------------------------------|
| **Strategic Gap** | A topic you want to own, but AI answers currently favor a competitor |
| **Owned Strength** | A topic where you already dominate — defend it |
| **Perception Gap** | AI describes you with wrong or outdated traits |
| **Discovery Gap** | AI can't find you despite your content existing |
| **Attention Gap** | Not enough recent signal for AI to surface you |
| **Claim Ceiling** | The strongest claim the evidence supports without overstatement |

---

## Run It

```bash
cd webapp && npm install && npm run dev
```

Open [localhost:3000](http://localhost:3000). Select a brand. Start diagnosing.

<details>
<summary>Data pipeline and verification</summary>

```bash
# Pipeline
uv sync --dev
make run
make validate

# Verify
cd webapp && npm run build && npm run lint
make test && make lint
```

</details>

---

## Built With

[Peec AI](https://peec.ai) — AI visibility data via MCP |
[Gemini](https://deepmind.google/technologies/gemini/) — perception analysis and gap classification |
[Tavily](https://tavily.com) — public web evidence enrichment |
[Next.js](https://nextjs.org) + [Recharts](https://recharts.org) — dashboard

---

**Solo build by Amit Prusty + AI agents.**
Peec AI track, Big Berlin Hack 2026. Berlin, April 25–26.
