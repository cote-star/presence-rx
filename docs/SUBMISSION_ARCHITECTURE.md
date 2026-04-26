# Presence Rx Submission Architecture

Use `docs/submission-architecture.svg` as the architecture visual in the 2-minute submission video.

## One-Sentence Architecture

Presence Rx compares what the brand wants to mean, what audiences ask AI, and what AI actually says, then turns that gap into evidence-graded actions and claim guardrails.

## Diagram Layers

| Layer | What it means | Demo phrasing |
| --- | --- | --- |
| Strategy Profile | Brand intent, desired associations, ambition level, positioning frame | "We start with what the brand actually wants to be known for." |
| Audience Layer | Personas, audience profiles, buying contexts | "Then we map who the claim has to resonate with." |
| Prompt Universe | Audience questions translated into measurable AI-search topics | "That becomes the prompt and topic universe we measure." |
| Peec MCP | Source of truth for AI visibility, topics, competitors, engines, domains, URLs, chats | "Peec tells us what AI answers actually say." |
| Tavily | Public web evidence, competitor proof, editorial gaps | "Tavily checks whether public proof exists on the open web." |
| Gemini | Perception themes and missing associations | "Gemini interprets the perception gap without replacing Peec metrics." |
| Presence Rx Decision Engine | Strategic status, gap type, competitor owner, action priority | "Our decision engine classifies what kind of marketing problem this is." |
| Claim Guardrail | Allowed, needs evidence, blocked, off-strategy | "Then the system refuses claims the brand has not earned." |
| Lovable | Executive dashboard | "Lovable is the marketer-facing workflow for diagnosis, evidence, and claim testing." |
| Verdict Pack | Markdown and JSON outputs | "Everything is exportable and auditable." |
| Peec Writes | Monitoring prompts and campaign tags | "The loop closes by setting up what Peec should monitor next." |

## 20-Second Video Script

Architecturally, Presence Rx starts before the dashboard. We define the brand profile and the audience profile: what the brand wants to mean, and who it needs to matter to. That becomes a prompt universe. Peec is the source of truth for how the brand appears in AI answers. Tavily adds public proof, Gemini identifies perception themes, and the Presence Rx decision engine classifies the gap type, priority, and competitor owner. Then the claim guardrail decides what can be said, what needs evidence, and what must be blocked. The output is a Lovable dashboard, an evidence ledger, an action brief, and Peec monitoring prompts.

## Key Claims To Make

- Peec owns visibility truth.
- Tavily adds public proof.
- Gemini interprets perception themes.
- Presence Rx owns classification, prioritization, and claim safety.
- Lovable turns the pipeline into a marketer-facing workflow.

## Claims To Avoid

- Do not say Gemini measures AI visibility.
- Do not say Tavily proves every claim.
- Do not say the system guarantees marketing truth.
- Do not imply all demo brands have equal live partner data.

