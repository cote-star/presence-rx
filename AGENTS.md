# Agent Coordination - Peec AI

Multi-agent repo. Read this and the parent [AGENT_BRIEFING.md](../AGENT_BRIEFING.md) before touching code.

## Context

- Play side. No work credentials. No work connectors.
- Hackathon "no early start": no application code or mock data before official start. Boilerplate is allowed.
- Track lock at Saturday 12:30 CEST. Peec activates only if both Buena and Qontext are unfavorable and partner-tech eligibility holds.

## Lanes

| Agent | Lane | Responsibility |
|-------|------|----------------|
| Claude | Architecture + backend | Analysis pipeline, guardrails, verdict pack |
| Codex | Implementation + review | Modules, tests, code review |
| Gemini | Research + validation | Peec MCP exploration, brand data checks |
| Claude (design) | Frontend/UX | Lovable dashboard surface |
| Cursor / Composer | External QA | Pull-based skeptical review at gates |
| Human (Amit) | Decisions + pitch | Track lock, mentor questions, demo, final submission |

## Branching

- Default branch: `main`.
- One feature branch per agent lane: `claude/<topic>`, `codex/<topic>`, `gemini/<topic>`.
- Rebase on `main` before opening a PR. Squash on merge.

## Partner-Tech Honesty Rule

Partner counts only if used in a real code path or visible workflow. Confirm with organisers whether Peec MCP itself counts toward the 3-tech minimum. Aikido is side-only.

## Submission Guard

- README must list every API, framework, and tool actually used.
- 2-minute video must match real behavior.
- Submit before Sunday 14:00 CEST.
