# Presence Rx

> **Diagnose. Prescribe. Refuse.**

Your brand is either in the AI answer or it isn't. Presence Rx tells you why — and what to do about it.

[![Animated Presence Rx walkthrough showing gap analysis, strategic actions, channel activation, and claim simulation](docs/demo-assets/presence-rx-walkthrough.webp)](docs/demo-assets/gap-analysis.png)

---

Ask ChatGPT or Gemini for a phone recommendation. Nothing Phone appears in 20% of answers. When it does appear, it ranks #2. Sounds decent — until you realize Apple owns the "minimalist hardware" conversation at 39% while Nothing Phone sits at 6%.

That's not a visibility problem. That's a **perception gap**. And it needs a completely different fix than a discovery gap or an attention gap.

Presence Rx makes that distinction, then turns it into action.

---

## Find the blind spots

Pull Peec AI visibility data. Classify every topic: stronghold, perception gap, discovery gap, or attention gap. See which competitor owns each conversation and how confident the diagnosis is.

Nothing Phone owns Smartphone Design at 72%. But Minimalist Hardware? Apple has it. Wireless Audio? 1% visibility — the product exists, the signal doesn't.

![Presence Rx gap analysis showing Smartphone Design as an owned strength and Mobile Ecosystem as a discovery gap](docs/demo-assets/gap-analysis.png)

## Get the right fix for each gap

A perception gap needs positioning work and trait-language proof. A discovery gap needs schema, canonical pages, and source-of-truth structure. An attention gap needs sustained editorial and community signal.

Each topic gets a priority score, the competitor who owns the conversation, and a concrete next move.

![Presence Rx strategic action view grouping Discovery, Perception, and Attention gaps with priorities and next moves](docs/demo-assets/strategic-action.png)

## Know where to activate

Map each gap type to channels and audiences. Editorial for perception repair. UGC and Reddit for attention gaps. Owned content for discovery. Peec monitoring prompts to measure whether activation is closing the gap.

![Presence Rx channel activation view showing where to engage and which audiences to reach](docs/demo-assets/channel-activation.png)

## Block what you haven't earned

*"Nothing Phone is the go-to minimalist tech brand."*

Blocked. Apple owns that AI-answer association at 39% vs 6%. Presence Rx gives a safer rewrite the brand can actually use — and explains why.

The system would rather kill a claim than let an overclaim through.

![Presence Rx claim simulator blocking an unsupported minimalist-tech ownership claim and providing a safer rewrite](docs/demo-assets/claim-simulation.png)

---

## Try It

```bash
cd webapp && npm install && npm run dev
```

Open [localhost:3000](http://localhost:3000). Pick Nothing Phone, Attio, or BMW.

Requires Node.js 18.17+. The Python pipeline (`uv sync --dev && make run`) requires Python 3.11+.

---

## Architecture

![Presence Rx architecture](docs/submission-architecture.svg)

**Peec AI** provides the visibility truth. **Tavily** enriches with public web evidence. **Gemini** runs perception analysis. **Presence Rx** is the decision layer: gap classification, action priority, channel mapping, and claim ceilings. Every metric traces to a named source.

---

## Built With

[Peec AI](https://peec.ai) MCP | [Tavily](https://tavily.com) | [Gemini](https://deepmind.google/technologies/gemini/) | [Next.js](https://nextjs.org) | React | Tailwind CSS | Recharts | Python | Pydantic

---

**Peec AI track — Big Berlin Hack 2026.** Solo build by Amit Prusty with AI-assisted development.
