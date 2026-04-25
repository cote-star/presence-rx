# Peec MCP Tool Map

Server URL: `https://api.peec.ai/mcp`
Transport: Streamable HTTP
Auth: OAuth 2.0 (browser consent on first use)
Setup: `claude mcp add peec-ai --transport http https://api.peec.ai/mcp`

## Key Discovery: Peec Already Has Structure

Peec is NOT a raw data dump. It has built-in structure we should use, not rebuild:
- **Projects** contain brands, prompts, topics, tags, and models
- **Topics** are prompt groupings (our "prompt clusters" map to these)
- **Tags** are cross-cutting labels (our "campaign types" can map to these)
- **Chats** are individual AI responses with full content, brands mentioned, sources, and queries
- **Brand reports** already compute visibility, sentiment, position, and share of voice
- **Actions** are Peec's own opportunity-scored recommendations

## Pipeline Mapping: Peec Tools to Our Artifacts

### Step 1: Ingest (Peec MCP)

| Our concept | Peec tool | What it gives us |
|---|---|---|
| Project selection | `list_projects` | Find the sample brand project |
| Brand setup | `list_brands` | Target brand + competitors with domains and aliases |
| Prompt universe | `list_prompts` | All prompts with text, topic, tags, volume |
| Topic groups | `list_topics` | Pre-built prompt groupings from Peec |
| Tags | `list_tags` | Cross-cutting labels for filtering |
| AI models tracked | `list_models` | Which AI engines Peec monitors |

### Step 2: Observation Data (Peec MCP)

| Our concept | Peec tool | What it gives us |
|---|---|---|
| Prompt-level observations | `list_chats` | Individual AI responses per prompt/model/date |
| Full answer content | `get_chat` | Response text, brands_mentioned, sources, queries, products |
| Sub-queries | `list_search_queries` | What the AI searched while answering |
| Shopping queries | `list_shopping_queries` | Product queries and results |

### Step 3: Visibility Metrics (Peec MCP)

| Our concept | Peec tool | What it gives us |
|---|---|---|
| Brand visibility baseline | `get_brand_report` | visibility, mention_count, share_of_voice, sentiment, position |
| Competitor ownership | `get_brand_report` (filtered) | Compare brand vs competitor across dimensions |
| Source citations | `get_domain_report` | Which domains AI engines cite |
| URL-level citations | `get_url_report` | Specific URLs cited with rates |
| Source content | `get_url_content` | Scraped markdown of cited sources |

### Step 4: Peec's Own Actions

| Our concept | Peec tool | What it gives us |
|---|---|---|
| Peec recommendations | `get_actions` | Opportunity-scored action recommendations |

## Report Dimensions

`get_brand_report` supports breakdown by:
- `date` - time slices (enables surge vs slow-burn analysis)
- `model_id` - per AI engine (GPT vs Gemini vs Perplexity)
- `topic_id` - per prompt topic (our cluster-level metrics)
- `tag_id` - per tag (our campaign-type metrics)
- `prompt_id` - per individual prompt
- `country_code` - per geography
- `chat_id` - per individual response

This is powerful. We can get visibility metrics broken down by topic AND model, which directly enables our method comparison.

## Report Filters

Reports accept:
- `in` / `not_in` operators for categorical fields
- `gt` / `gte` / `lt` / `lte` for numeric fields
- Fields: `brand_id`, `model_id`, `topic_id`, `tag_id`, `prompt_id`, `country_code`

## Data Shape: Compact Columnar JSON

Most tools return:
```json
{
  "columns": ["id", "name", "visibility", ...],
  "rows": [[1, "Nothing Phone", 0.20, ...], ...],
  "rowCount": 42
}
```

## What This Changes About Our Pipeline

### We DON'T need to build:
- Prompt clustering from scratch (Peec has `topics`)
- Basic visibility scoring (Peec has `get_brand_report`)
- Source citation tracking (Peec has `get_domain_report` + `get_url_report`)
- Raw action ideas (Peec has `get_actions`)

### We DO need to build:
- **Parent-topic classification** on top of Peec topics (Gemini)
- **Campaign taxonomy mapping** from Peec topics/tags to our campaign types
- **Method comparison** across Peec visibility + Gemini perception + Tavily public evidence
- **Guardrail engine** that grades claims using the three-field check
- **Evidence ledger** linking claims to Peec chat refs, Tavily sources, Gemini analysis
- **Blocked claims register** for findings that fail the method ladder
- **Study + action brief generation** from the structured SSOT
- **Pipeline funnel** showing how Peec data narrows to recommendations

### Revised pipeline:
```
list_projects -> pick sample brand project
list_brands -> target + competitors
list_prompts + list_topics + list_tags -> prompt universe
list_chats + get_chat -> raw observations with full content
get_brand_report (by topic, model) -> visibility baseline
get_actions -> Peec's own recommendations as a starting signal
  |
  v  (OUR VALUE-ADD STARTS HERE)
  |
Gemini: classify topics -> parent themes -> campaign taxonomy
Tavily: public evidence for proof/gap analysis
Method comparison: Peec visibility vs Gemini perception vs Tavily evidence
Guardrail engine: three-field check + decision buckets
  |
  v
EVIDENCE_LEDGER.json + PRESENCE_VERDICT.md + ACTION_BRIEF.md + manifest.json
```

## First Commands To Run

After OAuth:
1. `list_projects` - find the sample brand project
2. `list_brands` (project_id) - see target + competitors
3. `list_topics` (project_id) - see what prompt clusters Peec already has
4. `list_prompts` (project_id) - see prompt texts and volumes
5. `get_brand_report` (project_id, dimensions: ["topic_id"]) - visibility by topic
6. `get_actions` (project_id) - Peec's own action ideas

## Write Tools (Constrained)

Peec MCP exposes `create_*` write tools for **brands, prompts, topics, and tags inside existing projects** - there is **no `create_project` tool**. Org-owner access is confirmed, but we cannot spin up a new project from scratch via MCP.

Implications:

- We are bound to the four existing projects: Attio, BYD/BMW, TwoBreath, Nothing Phone.
- Strategy B from `INTEGRATION_CHECKLIST.md` (full custom project) is closed off.
- We can still extend coverage **inside** the locked Nothing Phone project: add new brands, prompts, topics, or tags. New prompts only populate after Peec's daily run, so this isn't a same-day demo path - but it is the foundation for value-add #1 (`prompts_to_add.json` feedback loop).

Use cases (revised):

- **Targeted prompt extension:** add specific prompts to the Nothing Phone project to seed a coverage gap. The API call itself is a proof point even if the data isn't live yet.
- **Custom-tag overlay:** add `create_tag` entries that map to our campaign taxonomy, then filter `get_brand_report` by `tag_id` for tighter rollups.
- **Brand expansion:** add a new competitor brand to the Nothing Phone project if a useful comparator surfaces during analysis.

Rules:

- Use `create_*` tools, never `delete_*`.
- Tag custom artifacts with a clear `bbh-2026-` prefix where supported.
- Custom inputs must be public-safe (no private orgs, no internal taxonomy, no work-context names).
- See `INTEGRATION_CHECKLIST.md` Phase 2 for the brand-strategy decision tree.
