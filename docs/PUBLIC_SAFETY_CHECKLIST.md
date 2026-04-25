# Public Safety Checklist

Use this before committing, pushing, recording the demo, or making partner-tech claims.

## Never Include

- private repo names or local filesystem paths
- client names unless they are Peec-provided sample brands or public competitors used in the demo
- work credentials, connector names, internal account IDs, or private API endpoints
- copied private code, notebooks, data extracts, dashboard screenshots, or prompt text
- claims that imply private datasets were used
- private ticket IDs, private page titles, or internal project names
- org names, team names, or people names from work context

## Safe To Include

- public Peec sample brands and public competitors
- public web evidence collected through Tavily
- Gemini-generated analysis based on public/Peec-provided inputs
- original code written during the hackathon
- generic analytics patterns: evidence ledgers, guardrails, parent-topic taxonomies, method agreement, fallback tiers, pipeline funnels, decision buckets, source-of-record maps

## Claim Hygiene

Every recommendation must answer:

- Which Peec prompt cluster supports it?
- Which parent topic or fallback topic source supports it?
- Which campaign type or category fallback supports it?
- Which evidence refs support it?
- Which methods agree or disagree?
- What is the confidence tier?
- What is the publication status?
- What language is allowed?

If the answer is incomplete, downgrade or block the claim.

## Artifact Completeness Check

Before submission, confirm:

- [ ] Every recommendation has `claim_id`, `cluster_id`, `evidence_refs`, `source_of_record`, `confidence_tier`, and `publication_status`.
- [ ] Every missing metric has `null` plus an `unavailable_reason` - no silent blanks, zeros, or hidden failures.
- [ ] Every action uses allowed language for its tier: prioritize, test, explore, monitor, or block.
- [ ] No blocked claim appears in `ACTION_BRIEF.md` except inside a clearly labeled "Claims To Avoid" section.
- [ ] `manifest.json` includes snapshot IDs, taxonomy versions, artifact version, freshness status, quality counts, and unavailable-reason counts.
- [ ] `study_ssot.json` can regenerate both Markdown output and dashboard panels without hand-edited values.
- [ ] Decision buckets are based on evidence and guardrails, not on how impressive the recommendation sounds.
- [ ] Public sources are summarized, not copied, and every source-backed claim points to a stable reference.
- [ ] The demo can show one complete proof path and one blocked/downgraded proof path.

## Public Inference Test

Beyond string scanning, ask: **could a reader infer a private client, workstream, source system, ticket, repository, or team from this artifact?** If yes, rewrite the example as generic product language. This catches leaks that string matching misses - structural patterns, taxonomy names, or domain-specific terminology that fingerprint a private project.

## Final Review Command Ideas

Before making the repo public, search for obvious leaks:

```bash
rg -n "private|internal|client|secret|token|password|<absolute-private-path>|<org-name>|<internal-project>|<client-name>" .
```

Then manually inspect every hit. Generic words like `client` may be fine in safety docs, but no private identifier should remain.

## Automated Pre-Commit Harness

A pre-commit hook at [.githooks/pre-commit](../.githooks/pre-commit) enforces the rules above on every commit:

1. Runs `gitleaks` against staged changes to catch credentials, API keys, tokens.
2. Greps staged additions for forbidden fingerprint patterns: agency names, Cannes-specific event references, work-side connector names (atl-api / gh-work / dbx-work / sentry-api / m365-api / figma-api / slack-api), and `/Users/` paths.

**Allowed (do not flag):** `Morning Consult`, `Pathmatics`, `brand lift` — generic vendor / methodology references used industry-wide.

**Setup after cloning the repo (one-time):**

```bash
git config core.hooksPath .githooks
```

This is required because git does not auto-set `core.hooksPath` from in-repo configuration. Each agent or developer must run this once after cloning. Verify with `git config --local --get core.hooksPath` (should print `.githooks`).

**If a legitimate edit triggers a false positive** (e.g., a doc that needs to discuss the rule itself), use placeholder syntax (`<absolute-path>`, `<agency-name>`) rather than the literal pattern. The hook excludes two files from its scan: itself (`.githooks/pre-commit`) and this policy doc (`docs/PUBLIC_SAFETY_CHECKLIST.md`) — both must name the patterns by definition. All other docs are scanned.

**To bypass for a known-safe commit** (rare): `git commit --no-verify`. Document why in the commit message, and review the commit before pushing.
