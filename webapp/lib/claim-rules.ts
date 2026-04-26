// Deterministic claim guardrail logic — no LLM calls
import type { BrandData } from "./types";

export type ClaimVerdict = "safe" | "needs_evidence" | "blocked" | "off_strategy";

export interface ClaimResult {
  verdict: ClaimVerdict;
  reason: string;
  safeRewrite?: string;
  matchedTopic?: string;
  visibility?: number;
  competitor?: string;
}

const OWNERSHIP_WORDS = [
  "leading",
  "best",
  "top",
  "dominant",
  "#1",
  "number one",
  "go-to",
  "premier",
  "leader",
];

export function checkClaim(claimText: string, brandData: BrandData): ClaimResult {
  const lower = claimText.toLowerCase();

  // 1. Check against known blocked claims
  if (brandData.ledger?.blocked_claims) {
    for (const bc of brandData.ledger.blocked_claims) {
      const claimWords = bc.claim.toLowerCase().split(" ").slice(0, 5).join(" ");
      if (lower.includes(claimWords) || lower.includes(bc.claim.toLowerCase())) {
        return {
          verdict: "blocked",
          reason: bc.blocked_reason,
          safeRewrite: bc.safe_rewrite,
          matchedTopic: bc.claim_id,
        };
      }
    }
  }

  // 2. Check if claim targets a non-priority topic
  if (brandData.study?.rows) {
    for (const row of brandData.study.rows) {
      if (lower.includes(row.cluster_label.toLowerCase()) && !(row.desired_association ?? true)) {
        return {
          verdict: "off_strategy",
          reason: `${row.cluster_label} is not a strategic priority for ${brandData.brand_name}. ${row.strategic_note || "This topic is intentionally deprioritized."}`,
          matchedTopic: row.cluster_label,
        };
      }
    }
  }

  // 3. Check ownership/superlative claims against CEILING
  const hasOwnership = OWNERSHIP_WORDS.some((w) => lower.includes(w));

  if (brandData.study?.rows) {
    for (const row of brandData.study.rows) {
      if (!lower.includes(row.cluster_label.toLowerCase())) continue;

      const ceiling = row.claim_ceiling ?? "category_challenger";
      const strategicStatus = row.strategic_status ?? null;

      // Leadership claims blocked when ceiling doesn't allow it
      if (hasOwnership && ceiling !== "category_leader") {
        return {
          verdict: "blocked",
          reason: `Ownership/leadership claims exceed the allowed claim ceiling for ${row.cluster_label}. This topic's positioning is "${row.ambition_level ?? "challenger"}" — leadership claims are not supported.`,
          safeRewrite: row.safe_claim ?? `${brandData.brand_name} is building presence in ${row.cluster_label.toLowerCase()}.`,
          matchedTopic: row.cluster_label,
          visibility: row.visibility_target_share ?? undefined,
          competitor: row.visibility_competitor_owner ?? undefined,
        };
      }

      // Strategic gap + ownership claim = blocked
      if (hasOwnership && strategicStatus === "strategic_gap") {
        const vis = row.visibility_target_share ?? 0;
        return {
          verdict: "blocked",
          reason: `${brandData.brand_name} has ${Math.round(vis * 100)}% visibility in ${row.cluster_label}${row.visibility_competitor_owner ? ` while ${row.visibility_competitor_owner} dominates` : ""}. This is a strategic gap — ownership claims are not yet supported.`,
          safeRewrite: row.safe_claim ?? `${brandData.brand_name} is emerging in ${row.cluster_label.toLowerCase()}.`,
          matchedTopic: row.cluster_label,
          visibility: vis,
          competitor: row.visibility_competitor_owner ?? undefined,
        };
      }

      // Strategic gap without ownership language = needs evidence
      if (strategicStatus === "strategic_gap") {
        return {
          verdict: "needs_evidence",
          reason: `${row.cluster_label} is a strategic gap for ${brandData.brand_name}. Directional claims are allowed but need supporting evidence.${row.positioning_frame ? ` Recommended framing: "${row.positioning_frame}"` : ""}`,
          matchedTopic: row.cluster_label,
          visibility: row.visibility_target_share ?? undefined,
        };
      }

      // Owned strength = safe
      if (strategicStatus === "owned_strength") {
        return {
          verdict: "safe",
          reason: `${brandData.brand_name} has strong visibility in ${row.cluster_label}. This claim is within the brand's owned territory.`,
          matchedTopic: row.cluster_label,
          visibility: row.visibility_target_share ?? undefined,
        };
      }

      // Emerging opportunity = needs evidence
      if (strategicStatus === "emerging_opportunity") {
        return {
          verdict: "needs_evidence",
          reason: `${row.cluster_label} is an emerging opportunity. Claims need additional evidence before publication.`,
          matchedTopic: row.cluster_label,
          visibility: row.visibility_target_share ?? undefined,
        };
      }
    }
  }

  // 4. Default: needs evidence
  return {
    verdict: "needs_evidence",
    reason: "This claim could not be matched to a tracked topic. Collect evidence before using it publicly.",
  };
}
