# Campaign Taxonomy For Peec

This taxonomy gives the Peec study a planning layer above prompt clusters and parent topics. It lets the system translate AI answer visibility gaps into campaign-style actions that a marketer can understand, compare, and monitor.

## Why It Helps

Peec shows how a brand appears across AI answer surfaces. The campaign taxonomy answers:

- What kind of marketing move does this finding imply?
- Can granular findings roll up to executive categories?
- Which prompt clusters should be monitored for each campaign type?
- When should the system fall back from specific campaign types to broader categories?

Recommended hierarchy:

```text
4 campaign categories
  -> 10 campaign types
    -> 14 visibility topics
      -> prompt clusters and claims
```

## Campaign Categories And Types

Every output that uses this mapping should include `campaign_type_mapping_version`. Findings generated with different mapping versions should not be compared without noting the version change.

| campaign category | campaign type | visibility topics | Peec use |
| --- | --- | --- | --- |
| Brand & Commercial | `corporate_reputation` | Executive leadership, corporate narrative, brand purpose | Build authority and trust in broad category prompts. |
| Brand & Commercial | `product_innovation` | Product delivery, R&D, innovation | Win product-comparison and feature-discovery prompts. |
| Brand & Commercial | `brand_marketing` | Brand marketing, promotions, cultural activations | Improve awareness and association in top-of-funnel prompts. |
| Corporate & Financial | `financial_communications` | Financial performance | Support investor/business-health prompts where relevant. |
| Corporate & Financial | `growth_expansion` | Market expansion, industry trends | Own market-entry, category-growth, and macro-trend prompts. |
| Corporate & Financial | `esg_citizenship` | Sustainability, ethics, governance | Support values, responsibility, and ESG-adjacent prompts. |
| Risk & Regulatory | `crisis_management` | Crisis, risk, workplace or consumer safety | Defend against negative or risk-owned AI associations. |
| Risk & Regulatory | `public_affairs` | Legal, regulatory, policy, political activity | Support regulatory, compliance, and policy prompts. |
| Stakeholder & Culture | `employer_brand` | Workforce, culture, labor relations | Support talent, workplace, and culture prompts. |
| Stakeholder & Culture | `customer_experience` | Customer service and experience | Win buyer-friction, loyalty, support, and CX prompts. |
| Fallback | `other` | Unmapped or ambiguous topic | Hold sparse findings out of precise campaign rollups. |

## Visibility Topic Mapping

Each visibility topic should map to exactly one campaign type. This keeps feature construction and rollups clean.

| visibility topic | campaign type | campaign category |
| --- | --- | --- |
| Customer Service and Experience | `customer_experience` | Stakeholder & Culture |
| Product and Service Delivery | `product_innovation` | Brand & Commercial |
| Branding, Marketing, and Promotions | `brand_marketing` | Brand & Commercial |
| Innovation, Research, and Development | `product_innovation` | Brand & Commercial |
| Financial Performance | `financial_communications` | Corporate & Financial |
| Market Expansion or Contraction | `growth_expansion` | Corporate & Financial |
| Executive Leadership and Board Updates | `corporate_reputation` | Brand & Commercial |
| Sustainability, Ethics, and Governance | `esg_citizenship` | Corporate & Financial |
| Crisis and Risk Management | `crisis_management` | Risk & Regulatory |
| Legal and Regulatory Compliance | `public_affairs` | Risk & Regulatory |
| Political Activities | `public_affairs` | Risk & Regulatory |
| Workplace and Consumer Safety | `crisis_management` | Risk & Regulatory |
| Workforce, Culture, and Labor Relations | `employer_brand` | Stakeholder & Culture |
| Industry-Wide Trends and Regulations | `growth_expansion` | Corporate & Financial |

## Fallback Granularity

Use campaign types by default. Roll up to campaign categories when:

- too few Peec observations exist for a specific campaign type
- method agreement is weak at type level but clearer at category level
- prompt clusters are too sparse or fragmented
- the action brief would otherwise overstate precision

This gives the demo a strong guardrail:

> We can recommend at campaign-category level when campaign-type evidence is too thin.

Use `campaign_type: "other"` only when neither type nor category is defensible. `other` findings can appear in diagnostics, but should not drive the action brief without review.

## Sign And Risk Direction

Campaign findings should carry a directional sign:

- `+1` for favorable visibility or a gap the brand can credibly improve.
- `-1` for risk, crisis, compliance, safety, or negative ownership signals.
- `0` when the system is only monitoring.

This prevents a risk-owned cluster from being presented like a normal growth opportunity.

## Nothing Phone Starter Mapping

For Nothing Phone (locked demo brand), the likely high-value campaign types mapped to real Peec topics are:

| campaign type | Peec topic | likely action |
| --- | --- | --- |
| `product_innovation` | Smartphone Design (stronghold, 72% vis) | Defend leadership: lead with transparent-design proof and Glyph interface depth. |
| `brand_marketing` | Minimalist Hardware (ironic gap, 6% vis vs Apple 39%) | Publish minimalist-hardware positioning content; close the brand-identity-vs-AI-presence gap. |
| `product_innovation` | Wireless Audio (1% vis, Apple 53%) | Publish Nothing Ear comparison content to seed audio category visibility. |
| `growth_expansion` | Consumer Tech Innovation (10% vis) | Own disruptor / sustainability / startup-challenger narrative in trend prompts. |
| `corporate_reputation` | Mobile Ecosystem (12% vis, Apple 72%) | Build cross-device / launcher-customization proof to chip away at Apple's category ownership. |

Lower priority unless Peec data shows strong signal:

- `financial_communications`
- `esg_citizenship`
- `public_affairs`
- `employer_brand`

## How It Connects To Artifacts

Add campaign fields to the SSOT and evidence ledger:

- `campaign_category`
- `campaign_type`
- `visibility_topic`
- `campaign_type_mapping_version`
- `campaign_signal_sign`
- `fallback_campaign_category`
- `campaign_granularity`: `type` or `category`
- `campaign_granularity_reason`

Use these fields in:

- `PRESENCE_VERDICT.md` for diagnosis and rollups.
- `ACTION_BRIEF.md` for marketer-facing plays.
- dashboard filters if a Lovable/local UI is built.
- `method_comparison.json` for guardrails when type-level evidence is sparse.

## Demo Moment

Show one finding at campaign-type level, then show a sparse finding rolled up to campaign-category level. This demonstrates that the system can be precise when evidence supports it and conservative when it does not.
