# Contributor Guide - Peec AI

Read this before touching code. This is the public project guidance for Presence Rx.

## Context

- Play side only. No work credentials, work connectors, or private SaaS endpoints.
- Hackathon "no early start": no application code or mock data before official start. Boilerplate is allowed.
- Track locked: Peec. Brand locked: Nothing Phone. Submission deadline: Sunday 14:00 CEST.
- Active plan: [docs/SCOPE_FINAL.md](docs/SCOPE_FINAL.md) is the source of truth for what to build.
- Partner stack: Peec MCP, Gemini, Tavily, Lovable, with Entire as the dashboard fallback if needed.

## Contribution Areas

| Area | Responsibility |
| --- | --- |
| Data pipeline | Peec ingestion, normalization, artifact contracts, generated JSON |
| Evidence layer | Tavily enrichment, Gemini analysis, source-of-record mapping |
| Guardrails | Evidence tiers, blocked claims, safe rewrites, publication status |
| Dashboard | Lovable surface and public-safe future-directions preview |
| Review | Partner-tech honesty, public-safety scan, generated artifact validation |

## Branching

- Default branch: `main`.
- Use short feature branches by work area, such as `pipeline/ingestion`, `evidence/tavily`, or `dashboard/lovable`.
- Rebase on `main` before opening a PR. Squash on merge.

## Partner-Tech Honesty Rule

Partner counts only if used in a real code path or visible workflow. Peec MCP is the required track tool. Aikido is side-only.

## Submission Guard

- README must list every API, framework, and tool actually used.
- Generated artifacts must pass validation before demo or submission.
- Public-safety scan must be clean before pushing public.
- 2-minute video must match real behavior.
- Submit before Sunday 14:00 CEST.
