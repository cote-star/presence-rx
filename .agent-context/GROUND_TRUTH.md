# Ground Truth - Real Peec Data

Real, MCP-verified data on the locked Nothing Phone project. Copy-paste these IDs into code; do not retype.

> Verified: 2026-04-25 (Saturday afternoon)
> Source: [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md)

## MCP Connection

- **Server:** `https://api.peec.ai/mcp`
- **Transport:** HTTP
- **Auth:** OAuth 2.0 (browser consent, complete)
- **Setup:** `claude mcp add peec-ai --transport http https://api.peec.ai/mcp`
- **Config:** `~/.claude.json` under the big-berlin-hack project

## Project IDs

| Project | ID | Status |
| --- | --- | --- |
| **Nothing Phone (LOCKED)** | `or_faaa7625-bc84-4f64-a754-a412d423c641` | Demo target |
| Attio | `or_47ccb54e-0f32-4c95-b460-6a070499d084` | Reference only |
| BYD/BMW (mislabeled) | `or_52698861-707c-4006-bc7e-3563aad6cd44` | Reference only |
| TwoBreath | `or_d59b90de-aacd-4dc1-8cdb-90784ed9b3db` | Empty |

## Nothing Phone Brand IDs

| Brand | ID | is_own | Visibility | SoV | Sentiment | Position |
| --- | --- | --- | --- | --- | --- | --- |
| **Nothing Phone** | `kw_d9414ede-8870-47a8-b377-14f887986e67` | true | 20% | 8% | 64 | 2.4 |
| Apple | `kw_08d6903d-8f51-439c-8f15-3a50cfb49d4c` | false | 50% | 23% | 66 | 3.6 |
| Google | `kw_2727503a-c380-4711-b092-b349f0f94f21` | false | 39% | 20% | 67 | 5.4 |
| Samsung | `kw_71b137f7-c9f7-4aac-b0e3-12d22d5cd3fb` | false | 36% | 16% | 68 | 4.6 |
| Pixel | `kw_c7c314cb-633f-4fc7-8a9d-db55e45974a8` | false | 30% | 14% | 67 | 6.9 |
| Sony | `kw_d4c5113b-8708-4fb3-a626-6c9d6551b309` | false | 22% | 9% | 68 | 4.8 |
| Bose | `kw_c93220e8-f20f-404d-a331-e2ff1adc2acf` | false | 12% | 4% | 68 | 4.5 |
| Xiaomi | `kw_41eca0bc-dd21-46f6-a1c2-3d519bfcfb2c` | false | 11% | 2% | 67 | 5.1 |
| OnePlus | `kw_d02c02ea-19c8-47cf-8d82-fb9a6db023fd` | false | 9% | 2% | 68 | 4.3 |
| Logitech | `kw_50e84900-e069-459f-94f7-2a1c5c8522b3` | false | 9% | 2% | 70 | 4.7 |

> **Pixel + Google overlap note:** Pixel is a Google sub-brand. In demo narrative, treat Pixel as Google's hardware line to avoid double-counting.

## Nothing Phone Topic IDs

| Topic | ID | Visibility | SoV | Position | Verdict |
| --- | --- | --- | --- | --- | --- |
| **Smartphone Design** | `to_be2fd0d7-8cf6-4c0c-bbe1-8f03ae7850ef` | **72%** | **85%** | **1.9** | **STRONGHOLD** |
| Mobile Ecosystem | `to_b1b39ec0-bfd9-430b-8e42-e709bf3560ed` | 12% | 7% | 3.8 | Blind spot (Apple 72%) |
| Consumer Tech Innovation | `to_22c5c578-d9a3-4128-896c-823c92f20ea2` | 10% | 5% | 3.7 | Blind spot (Apple 45%) |
| **Minimalist Hardware** | `to_e927582c-97f4-41ee-804c-bbe378e43242` | **6%** | **2%** | 4.1 | **IRONIC GAP (Apple 39%)** |
| Wireless Audio | `to_736e7e42-5109-4853-b9a4-7a48ef0a316f` | 1% | 0% | 2.0 | Invisible (Apple 53%) |

## Engine Breakdown (Nothing Phone Overall)

| Engine | Visibility | SoV | Position | Sentiment |
| --- | --- | --- | --- | --- |
| Gemini | 26% | 36% | 2.5 | **56** (lowest) |
| ChatGPT | 18% | 39% | 2.5 | 66 |
| Google AI Overview | 17% | 25% | 2.1 | **71** (highest) |

> **Sentiment sub-finding:** 15-point gap between Gemini (56) and Google AI Overview (71). Gemini frames the brand more critically. Free differentiation insight for the demo.

## Channel Profile

| Channel Type | Top domains | Nothing Phone present? |
| --- | --- | --- |
| UGC | YouTube (522 retrievals), Reddit (313), Medium (144), nothing.community (64) | Yes - community strength; nothing.community has citation rate 1.21 (highest among UGC) |
| Editorial | rtings (89), pcmag (83), techradar (78), tomsguide (73) | Mixed - major editorial gaps |
| Reference | Wikipedia (63) | Yes - baseline |
| Own (corporate) | nothing.community / nothing.tech | Yes - own site cited |

### Editorial Gap Domains (competitors cited, Nothing Phone absent)

| Domain | Type | Retrievals | Citation rate | Cited brands |
| --- | --- | --- | --- | --- |
| rtings.com | Editorial | 89 | 0.76 | Apple, Samsung, Bose, Sony |
| whathifi.com | Editorial | 38 | 1.36 | Apple, Bose, Sony |
| samsung.com | Corporate | 34 | 0.94 | Samsung, Google, Apple |
| zdnet.com | Editorial | 19 | 0.79 | Google, Samsung, Apple |
| wallpaper.com | Editorial | 14 | 0.86 | Google, Samsung, Apple |
| dezeen.com | Design | n/a | n/a | Cited for design content; Nothing Phone absent |
| yankodesign.com | Design | n/a | n/a | Cited for design content; Nothing Phone absent |

### High-Citation Gap URLs (page categories where Nothing Phone is absent)

- LISTICLE: "best smartphone OS ranked", "best smartphones for photographers 2026", "10 best gadgets April 2026"
- COMPARISON: "Android vs iOS", "which brands best value for money"
- Design outlets: dezeen.com CES gadgets coverage, yankodesign.com Gen Z gadgets
- whathifi.com: "which headphones have transparency mode" - Apple, Bose, Sony cited; **Nothing Ear absent**

## Geography

- **Current:** US-only data.
- **Expandable:** via `create_prompt` with country codes DE / GB / IN / etc. Prescription-layer setup, not result.

## AI Engines Tracked by Peec

ChatGPT, GPT-4o, Perplexity, Gemini, Google AI Overview, Google AI Mode, DeepSeek, Claude Haiku/Sonnet, Grok, Copilot, Qwen, LLaMA. Nothing Phone has data on the three above (Gemini, ChatGPT, Google AI Overview); other engines need additional prompt runs.

## Peec Metrics Reference

| Metric | Range | Meaning |
| --- | --- | --- |
| `visibility` | 0-1 ratio (×100 for display) | >50% strong, <20% weak |
| `share_of_voice` | 0-1 ratio | >25% = leadership |
| `sentiment` | 0-100 | most brands 65-85, below 50 = problem |
| `position` | rank, lower = better | >5 = not top-of-mind |
| `retrieval_rate` | average | NOT a percentage, can exceed 1.0 |
| `citation_rate` | average | NOT a percentage, can exceed 1.0 |

## MCP Read Tools

| Tool | Returns |
| --- | --- |
| `list_projects` | All projects accessible to the user |
| `list_brands(project_id)` | Brands in the project (own + competitors) |
| `list_topics(project_id)` | Pre-built prompt groupings |
| `list_prompts(project_id)` | Prompt text + topic + volume |
| `list_tags(project_id)` | Cross-cutting labels |
| `list_models(project_id)` | AI engines tracked |
| `get_brand_report(project_id, brand_id, dimensions=[...])` | Visibility / SoV / sentiment / position by topic / model / date / country |
| `get_domain_report(project_id, ...)` | Domain citation analysis (gap filter available) |
| `get_url_report(project_id, ...)` | URL-level citation analysis (gap filter available) |
| `get_url_content(url)` | Scraped Markdown of a cited source |
| `list_chats(project_id, ...)` | Individual AI responses per prompt / model / date |
| `get_chat(chat_id)` | Full response text + brands_mentioned + sources + queries |
| `get_actions(project_id, scope?)` | Peec's own opportunity-scored recommendations |
| `list_search_queries(...)` | What the AI searched while answering |
| `list_shopping_queries(...)` | Product queries and results |

## MCP Write Tools (Constrained)

| Tool | Use case |
| --- | --- |
| `create_brand(project_id, ...)` | Add a competitor brand inside the existing Nothing Phone project |
| `create_prompt(project_id, ...)` | Add a monitoring prompt for a blind-spot topic; geo expansion |
| `create_topic(project_id, ...)` | Add a sub-topic inside the project |
| `create_tag(project_id, ...)` | Add a custom tag (campaign taxonomy mapping) |

> **No `create_project`.** All writes happen inside the locked Nothing Phone project. New prompts populate only after Peec's daily run.

## Quick Snippets for Code

### Pull the topic-level brand report

```text
get_brand_report(
  project_id="or_faaa7625-bc84-4f64-a754-a412d423c641",
  brand_id="kw_d9414ede-8870-47a8-b377-14f887986e67",
  dimensions=["topic_id"]
)
```

### Pull the engine-level brand report

```text
get_brand_report(
  project_id="or_faaa7625-bc84-4f64-a754-a412d423c641",
  brand_id="kw_d9414ede-8870-47a8-b377-14f887986e67",
  dimensions=["model_id"]
)
```

### Pull Peec's own actions for the project

```text
get_actions(
  project_id="or_faaa7625-bc84-4f64-a754-a412d423c641"
)
```

### Pull the editorial-gap domain report

```text
get_domain_report(
  project_id="or_faaa7625-bc84-4f64-a754-a412d423c641",
  filter="gap"
)
```

### Sample a chat for evidence

```text
list_chats(project_id="or_faaa7625-bc84-4f64-a754-a412d423c641", limit=5)
get_chat(chat_id=<id from list_chats>)
```

## What Counts as Ground Truth

- This file: yes, but cross-check with [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md) when in doubt.
- Anything in code or generated artifacts: only after running real MCP calls and capturing output.
- Anything in the dashboard, README narrative, or marketing prose: secondary - always trace back to MCP responses or to this file.

## When to Update

After any new MCP exploration that adds verified data. Bump the verified date at the top.
