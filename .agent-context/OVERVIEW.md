# Overview - Presence Rx

## The Product in One Paragraph

**Presence Rx** is a discipline layer on top of Peec AI that finds a brand's blind spots in AI-generated answers and turns them into an evidence-graded action brief with receipts at every step. Peec already shows you visibility metrics and even outputs opportunity-scored recommendations; we add what Peec does not: blocked claims with safe rewrites, public-web triangulation via Tavily, multi-axis blind-spot diagnosis (topic / channel / engine / geography / authority / evidence), and a feedback loop that writes new monitoring prompts back into Peec. The deliverable is a **Presence Verdict Pack**: `PRESENCE_VERDICT.md` + `ACTION_BRIEF.md` + `EVIDENCE_LEDGER.json` + `manifest.json`.

## Tagline

> **Diagnose. Prescribe. Refuse.**
>
> Sub-tagline: *Find your brand's blind spots in AI answers.*

## The Demo Brand

**Nothing Phone**, locked over the obvious Attio default because (a) other teams will pile onto Attio, (b) Nothing Phone is the "Invisible Champion" - best position 2.4 (mentioned first when mentioned) but only 20% overall visibility, and (c) the irony hits in the demo: 6% visibility in **Minimalist Hardware** for the brand built on minimalism, while Apple holds 39% of that exact topic. That gap is the blocked-claim moment.

## The 6-Axis Blind-Spot Model

Most Peec wrappers stop at topic visibility. We diagnose six axes and explain what each means for a marketer:

| Axis | Question we answer |
| --- | --- |
| Topic | Where is the brand invisible? |
| Channel | Which content types miss the brand? |
| Engine | Which AI engines ignore the brand? |
| Geography | Which markets cannot see the brand? |
| Authority | Is the brand's content trusted, or just retrieved? |
| Evidence | What does the AI actually say when asked? |

## What Makes Us Different

A judge is going to ask "isn't this just a Peec wrapper?" Seven honest answers:

1. **Receipts** - every recommendation traces through claim -> Peec ref -> Tavily public proof -> Gemini analysis -> source-of-record -> guardrail -> allowed language.
2. **Blocked-claims register** - we refuse attractive-but-thin claims with reasons and safe rewrites. Peec's `get_actions` is opportunity-scored but never says "do not claim this yet."
3. **Gap-type classifier** - every blind spot carries a `gap_type` field: `perception`, `indexing`, or `volume_frequency`. Tier 1 diagnoses *where* a brand is invisible; Tier 1.5 classifies *what kind of fix is needed*. Each gap type triggers a different intervention class. **No other Peec wrapper does this** — and it's buildable today using only the data already in the pipeline.
4. **Public-web triangulation (Tavily)** - Peec is closed-loop on AI-answer surfaces. We add external public proof, finding the editorial gaps (rtings, whathifi, dezeen) where competitors are cited and Nothing Phone is not.
5. **Campaign taxonomy** - Peec topics are technical groupings; our 4-category x 10-type x 14-visibility-topic mapping turns them into marketer-language plays with fallback rules.
6. **Pipeline funnel transparency** - "42 prompts -> 9 clusters -> 7 topic-classified -> 5 evidence-gated -> 3 actionable." We show what got dropped, why, and what evidence would unblock it.
7. **Feedback loop into Peec** - we emit `prompts_to_add.json`, then call `create_prompt` to actually register monitoring prompts in the Peec project. The system improves the data it depends on. **No other Peec wrapper does this.**

The pitch line: *Peec tells you what's worth doing in AI answers; we tell you which of those you can actually defend, what kind of fix each one needs, what to test instead, and what not to claim yet.*

## The Demo Moment

Two beats, in order:

1. **Gap-type classifier (0:30-0:50 in the storyboard).** "Nothing Phone has four blind spots — but not all blind spots are the same. Minimalist Hardware is a *perception* problem. Mobile Ecosystem is an *indexing* problem. Wireless Audio is a *volume* problem. Each needs a different fix." This is the new sharp moment. Judges grok it in 5 seconds.
2. **Blocked claim (0:55-1:15).** Take a Peec-recommended action straight from `get_actions`, run it through our triangulation, watch it get **downgraded or blocked** because Tavily public-proof is thin or methods conflict, then show the safe rewrite and what evidence would unblock it. Our system disciplining Peec's own output.

Together those two beats are the most credible 50 seconds we have.

## Why It Wins

Most teams will ship a polished marketing brief. Polished briefs read generic. We're shipping a system that **refuses** to make weak claims, shows its work, and uses Peec more deeply than any other team will (channel, engine, authority, evidence axes plus write-back loop closure). Discipline, not flash.

## What This Project Is Not

- Not a generic content generator
- Not a vanity dashboard
- Not a Peec replacement (Peec is the source of truth for visibility; we never override it)
- Not a one-shot Markdown generator (the Markdown reads from structured JSON and is regenerable)

## Where to Read Next

- For locked decisions and rationale: [DECISIONS.md](DECISIONS.md)
- For real Peec data and IDs: [GROUND_TRUTH.md](GROUND_TRUTH.md)
- For your lane: [LANES.md](LANES.md)
