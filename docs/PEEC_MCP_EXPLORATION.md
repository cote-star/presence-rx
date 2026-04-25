# Peec MCP Exploration Results

**Date:** 2026-04-25  
**Status:** MCP authenticated, data verified, brand locked  
**Product:** Presence Rx  
**Tagline:** Diagnose. Prescribe. Refuse.  
**Sub-tagline:** Find your brand's blind spots in AI answers.  
**Deliverable:** Presence Verdict  
**Demo brand:** Nothing Phone  
**Concept:** The Invisible Champion  

---

## Strategic Decision: Nothing Phone, Not Attio

Other hackathon teams will default to Attio (the obvious B2B CRM project). We chose Nothing Phone because:

1. **Unique demo** — judges won't see the same brand repeated across teams
2. **Stronger data story** — the "Invisible Champion" pattern (best position but lowest visibility) is more compelling than a generic challenger narrative
3. **Killer demo moment** — Nothing Phone has 6% visibility in Minimalist Hardware, the topic most aligned with its brand identity. Apple has 39%. That irony is the blocked-claim moment.
4. **Brand recognition** — every judge knows Nothing Phone's transparent design. The story is instantly relatable.

## MCP Status

- **Server:** `https://api.peec.ai/mcp` (http transport, OAuth 2.0)
- **Auth:** Complete. All tools accessible.
- **Key constraint:** No `create_project` tool exists. Can add brands/prompts/topics to existing projects, but new prompts need daily runs to generate data. We must use existing project data.
- **Key capability:** Can create new brands/prompts/topics within existing projects.

## Nothing Phone Project

**Project ID:** `or_faaa7625-bc84-4f64-a754-a412d423c641`

### Brands (10)

| Brand | ID | is_own | Visibility | SoV | Sentiment | Position |
|-------|-----|--------|-----------|-----|-----------|----------|
| **Nothing Phone** | `kw_d9414ede-8870-47a8-b377-14f887986e67` | **true** | **20%** | **8%** | 64 | **2.4** |
| Apple | `kw_08d6903d-8f51-439c-8f15-3a50cfb49d4c` | false | 50% | 23% | 66 | 3.6 |
| Google | `kw_2727503a-c380-4711-b092-b349f0f94f21` | false | 39% | 20% | 67 | 5.4 |
| Samsung | `kw_71b137f7-c9f7-4aac-b0e3-12d22d5cd3fb` | false | 36% | 16% | 68 | 4.6 |
| Pixel | `kw_c7c314cb-633f-4fc7-8a9d-db55e45974a8` | false | 30% | 14% | 67 | 6.9 |
| Sony | `kw_d4c5113b-8708-4fb3-a626-6c9d6551b309` | false | 22% | 9% | 68 | 4.8 |
| Bose | `kw_c93220e8-f20f-404d-a331-e2ff1adc2acf` | false | 12% | 4% | 68 | 4.5 |
| Xiaomi | `kw_41eca0bc-dd21-46f6-a1c2-3d519bfcfb2c` | false | 11% | 2% | 67 | 5.1 |
| OnePlus | `kw_d02c02ea-19c8-47cf-8d82-fb9a6db023fd` | false | 9% | 2% | 68 | 4.3 |
| Logitech | `kw_50e84900-e069-459f-94f7-2a1c5c8522b3` | false | 9% | 2% | 70 | 4.7 |

### Key Insight: The Invisible Champion

Nothing Phone has the **best position** (2.4 — mentioned first) of any brand but the **5th lowest visibility** (20%). When AI mentions it, it ranks #1. But 80% of AI answers don't mention it at all.

### Topic Breakdown — Nothing Phone

| Topic | ID | Visibility | SoV | Position | Verdict |
|-------|-----|-----------|-----|----------|---------|
| **Smartphone Design** | `to_be2fd0d7-8cf6-4c0c-bbe1-8f03ae7850ef` | **72%** | **85%** | **1.9** | **OWNS IT** |
| Mobile Ecosystem | `to_b1b39ec0-bfd9-430b-8e42-e709bf3560ed` | 12% | 7% | 3.8 | Blind spot (Apple 72%) |
| Consumer Tech Innovation | `to_22c5c578-d9a3-4128-896c-823c92f20ea2` | 10% | 5% | 3.7 | Blind spot (Apple 45%) |
| **Minimalist Hardware** | `to_e927582c-97f4-41ee-804c-bbe378e43242` | **6%** | **2%** | 4.1 | **IRONIC GAP** (Apple 39%) |
| Wireless Audio | `to_736e7e42-5109-4853-b9a4-7a48ef0a316f` | 1% | 0% | 2.0 | Invisible (Apple 53%) |

### Demo Moments

1. **Stronghold**: Smartphone Design — 72% visibility, 85% SoV, position 1.9. Nothing Phone OWNS this topic.
2. **Ironic blind spot**: Minimalist Hardware — 6% visibility for the brand built on minimalism. Apple has 6x more. This is the blocked-claim moment.
3. **Ghost topic**: Wireless Audio — 1% visibility despite Nothing Ear product line. Apple at 53%.
4. **Blocked claim**: "Nothing Phone is the go-to minimalist tech brand" — BLOCKED because data contradicts it.
5. **Safe rewrite**: "Nothing Phone dominates Smartphone Design but is invisible in the broader minimalist category."

## Other Available Projects (for reference)

| Project | ID | Own Brand | Brands | Topics | Prompts | Note |
|---------|-----|-----------|--------|--------|---------|------|
| Attio | `or_47ccb54e...` | Attio | 5 | 5 | 50 | Other teams will use this |
| BYD/BMW | `or_52698861...` | BMW | 13 | 5 | 50 | Mislabeled (BMW is own, not BYD) |
| TwoBreath | `or_d59b90de...` | TwoBreath | 1 | 0 | 0 | Empty |

## Pipeline: Peec Data to Presence Verdict

```
PEEC DATA (Nothing Phone)          OUR VALUE-ADD (build this)
──────────────────────────          ──────────────────────────
50 prompts, 5 topics        ──►    parent-topic classification (Gemini)
10 brands, full metrics      ──►    campaign taxonomy mapping
Topic breakdown              ──►    blind spot identification
  72% Smartphone Design             stronghold / blind spot / gap labels
  12% Mobile Ecosystem              
  10% Consumer Tech                 
   6% Minimalist Hardware    ──►    BLOCKED CLAIM: "minimalist leader"
   1% Wireless Audio                
Brand reports                ──►    method comparison (Peec + Gemini + Tavily)
get_actions                  ──►    guardrail engine (3-field check)
list_chats / get_chat        ──►    evidence ledger + source-of-record
                                    Presence Verdict + action brief
```

## Peec Data Model

- **Prompts** = questions tracked daily across AI engines
- **Topics** = folder-like groupings (1 prompt = 1 topic)
- **Tags** = cross-cutting labels
- **Brands** = own (is_own=true) + competitors
- **Sources** = URLs AI engines retrieved
- **Citations** = sources referenced inline

### Metrics
- `visibility` — 0-1 ratio (x100 for %). >50% strong, <20% weak
- `share_of_voice` — 0-1 ratio. >25% = leadership
- `sentiment` — 0-100 (most brands 65-85)
- `position` — rank, lower = better. >5 = not top-of-mind
- `retrieval_rate`, `citation_rate` — averages, NOT percentages. Can exceed 1.0.

### AI Engines tracked
ChatGPT, GPT-4o, Perplexity, Gemini, Google AI Overview, Google AI Mode, DeepSeek, Grok, Copilot, Qwen, LLaMA, and other Peec-supported engines

## Next Steps for Build

1. **Pull `get_actions`** for Nothing Phone — see Peec's own recommendations
2. **Pull `list_chats`** — sample individual AI responses for evidence chain
3. **Pull `get_domain_report`** with gap filter — find where competitors are cited but Nothing Phone isn't
4. **Build ingestion** — wire Peec topic data into the pipeline
5. **Gemini analysis** — parent-topic classification, perception themes
6. **Tavily enrichment** — public proof for minimalist hardware gap
7. **Guardrail engine** — generate blocked claim and safe rewrite
8. **Artifacts** — PRESENCE_VERDICT.md, ACTION_BRIEF.md, EVIDENCE_LEDGER.json, manifest.json
