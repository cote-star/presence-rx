"""Pydantic contracts for generated Presence Rx artifacts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class StrictModel(BaseModel):
    """Base model that rejects misspelled or unexpected fields."""

    model_config = ConfigDict(extra="forbid")


class GapType(StrEnum):
    PERCEPTION = "perception"
    INDEXING = "indexing"
    VOLUME_FREQUENCY = "volume_frequency"


class EvidenceTier(StrEnum):
    STRONG = "strong"
    MODERATE = "moderate"
    LIMITED = "limited"
    BLOCKED = "blocked"


class PublicationStatus(StrEnum):
    PUBLISHABLE = "publishable"
    DIRECTIONAL_WITH_CAVEAT = "directional_with_caveat"
    DIAGNOSTICS_ONLY = "diagnostics_only"
    BLOCKED = "blocked"


class ClaimStatus(StrEnum):
    ACTIONABLE = "actionable"
    DIRECTIONAL = "directional"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    BLOCKED = "blocked"


class Prompt(StrictModel):
    prompt_id: str = Field(min_length=1)
    text: str | None = Field(default=None, min_length=1)
    source: str = Field(min_length=1)
    unavailable_reason: str | None = None

    @model_validator(mode="after")
    def enforce_prompt_text_or_reason(self) -> Prompt:
        if self.text is None and not self.unavailable_reason:
            raise ValueError("missing prompt text requires unavailable_reason")
        return self


class PromptCluster(StrictModel):
    cluster_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    stage: str = Field(min_length=1)
    prompt_type: str = Field(min_length=1)
    prompts: list[Prompt] = Field(default_factory=list)

    @field_validator("prompts")
    @classmethod
    def require_prompts(cls, value: list[Prompt]) -> list[Prompt]:
        if not value:
            raise ValueError("cluster must include at least one prompt")
        return value


class PromptUniverse(StrictModel):
    brand: str = Field(min_length=1)
    competitors: list[str] = Field(default_factory=list)
    clusters: list[PromptCluster] = Field(default_factory=list)


class StudyRow(StrictModel):
    cluster_id: str = Field(min_length=1)
    cluster_label: str = Field(min_length=1)
    cluster_stage: str = Field(min_length=1)
    cluster_prompt_type: str = Field(min_length=1)
    cluster_prompt_count: int | None = Field(default=None, ge=0)
    visibility_target_share: float | None = Field(default=None, ge=0, le=1)
    visibility_target_avg_position: float | None = Field(default=None, ge=0)
    visibility_competitor_owner: str | None = None
    gap_type: GapType | None = None
    gap_type_source: (
        Literal["scope_final", "gemini", "tavily", "derived", "not_applicable"] | None
    ) = None
    gap_type_rationale: str | None = None
    confidence_tier: EvidenceTier
    evidence_refs: list[str] = Field(default_factory=list)
    input_gate_status: Literal["passed", "failed", "skipped"]
    evidence_tier: EvidenceTier
    publication_status: PublicationStatus
    recommendation_available: bool
    unavailable_reason: str | None = None
    action_recommendation: str | None = None
    action_monitor_prompt: str | None = None
    desired_association: bool = True
    strategic_importance: str = "medium"
    strategic_note: str | None = None
    strategic_status: str | None = None
    positioning_frame: str | None = None
    ambition_level: str = "challenger"
    claim_ceiling: str = "category_challenger"
    tempting_claim: str | None = None
    safe_claim: str | None = None

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("study row must include at least one evidence ref")
        return value

    @model_validator(mode="after")
    def enforce_metric_and_action_rules(self) -> StudyRow:
        metric_fields = [
            self.cluster_prompt_count,
            self.visibility_target_share,
            self.visibility_target_avg_position,
        ]
        if any(metric is None for metric in metric_fields) and not self.unavailable_reason:
            raise ValueError("missing metrics require unavailable_reason")

        if self.gap_type and (not self.gap_type_source or not self.gap_type_rationale):
            raise ValueError("gap_type requires gap_type_source and gap_type_rationale")

        if self.recommendation_available:
            missing = []
            if not self.action_recommendation:
                missing.append("action_recommendation")
            if not self.action_monitor_prompt:
                missing.append("action_monitor_prompt")
            if self.publication_status == PublicationStatus.BLOCKED:
                missing.append("non_blocked_publication_status")
            if missing:
                raise ValueError(
                    "available recommendations require " + ", ".join(missing)
                )

        return self


class StudySsot(StrictModel):
    rows: list[StudyRow] = Field(default_factory=list)


class EvidenceItem(StrictModel):
    evidence_ref: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    url: HttpUrl | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class Claim(StrictModel):
    claim_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    status: ClaimStatus
    cluster_id: str = Field(min_length=1)
    methods: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    confidence_tier: EvidenceTier
    publication_status: PublicationStatus
    publication_language: str = Field(min_length=1)
    why_not_stronger: str | None = None

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("claim must include at least one evidence ref")
        return value


class BlockedClaim(StrictModel):
    claim_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    blocked_reason: str = Field(min_length=1)
    safe_rewrite: str = Field(min_length=1)
    next_evidence_to_collect: str = Field(min_length=1)


class EvidenceLedgerMetadata(StrictModel):
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)
    ledger_template_version: str = Field(min_length=1)
    used_classification: bool
    classifier_version: str = Field(min_length=1)


class EvidenceLedger(StrictModel):
    metadata: EvidenceLedgerMetadata
    generated_at: datetime
    brand: str = Field(min_length=1)
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    blocked_claims: list[BlockedClaim] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_blocked_claim_register(self) -> EvidenceLedger:
        blocked_claim_ids = {
            claim.claim_id for claim in self.claims if claim.status == ClaimStatus.BLOCKED
        }
        registered_ids = {claim.claim_id for claim in self.blocked_claims}
        missing = sorted(blocked_claim_ids - registered_ids)
        if missing:
            raise ValueError(
                "blocked claims must be mirrored in blocked_claims register: "
                + ", ".join(missing)
            )
        return self


class ManifestSource(StrictModel):
    snapshot_id: str | None = None
    prompt_count: int | None = Field(default=None, ge=0)
    query_count: int | None = Field(default=None, ge=0)
    source_count: int | None = Field(default=None, ge=0)
    analysis_runs: int | None = Field(default=None, ge=0)
    dashboard_url: HttpUrl | None = None


class Freshness(StrictModel):
    status: str = Field(min_length=1)
    generated_at: datetime
    newer_snapshot_available: bool


class Comparability(StrictModel):
    comparable_to_previous: bool
    reason: str | None = None


class PipelineSummary(StrictModel):
    raw_prompts: int = Field(ge=0)
    clusters: int = Field(ge=0)
    evidence_gated: int = Field(ge=0)
    actionable_recommendations: int = Field(ge=0)


class Manifest(StrictModel):
    brand: str = Field(min_length=1)
    competitors: list[str] = Field(default_factory=list)
    generated_at: datetime
    artifact_version: str = Field(min_length=1)
    taxonomy_version: str = Field(min_length=1)
    campaign_type_mapping_version: str | None = None
    peec_snapshot_id: str = Field(min_length=1)
    published: bool
    sources: dict[str, ManifestSource] = Field(default_factory=dict)
    confidence_counts: dict[str, int] = Field(default_factory=dict)
    quality_counts: dict[str, int] = Field(default_factory=dict)
    unavailable_reason_counts: dict[str, int] = Field(default_factory=dict)
    freshness: Freshness
    comparability: Comparability
    pipeline_summary: PipelineSummary
    artifacts: list[str] = Field(default_factory=list)


class HeroCards(StrictModel):
    guardrail_pass_rate_pct: int = Field(ge=0, le=100)
    cluster_pass_rate_pct: int = Field(ge=0, le=100)
    actionable_recommendations: int = Field(ge=0)
    method_conflict_count: int = Field(ge=0)
    blocked_claim_count: int = Field(ge=0)


class FunnelStage(StrictModel):
    stage: str = Field(min_length=1)
    count: int = Field(ge=0)
    dropped_count: int = Field(default=0, ge=0)
    drop_reasons: dict[str, int] = Field(default_factory=dict)


class PipelineFunnel(StrictModel):
    stages: list[FunnelStage] = Field(default_factory=list)


class SourceOfRecordItem(StrictModel):
    field: str = Field(min_length=1)
    source: Literal["peec_mcp", "gemini", "tavily", "derived"]
    rationale: str = Field(min_length=1)


class SourceOfRecord(StrictModel):
    sources: list[SourceOfRecordItem] = Field(default_factory=list)


class GeminiMetadata(StrictModel):
    generated_at: datetime
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)
    run_mode: Literal["live", "test"]
    requested_model: str = Field(min_length=1)
    response_model_version: str | None = None
    prompt_template_version: str = Field(min_length=1)
    temperature: float = Field(ge=0)
    request_count: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    sdk_package: str = Field(min_length=1)
    sdk_version: str = Field(min_length=1)


class GeminiSummary(StrictModel):
    analyzed_rows: int = Field(ge=0)
    supported_gap_types: int = Field(ge=0)
    conflicted_gap_types: int = Field(ge=0)
    insufficient_gap_types: int = Field(ge=0)


class GeminiFinding(StrictModel):
    finding_id: str = Field(min_length=1)
    cluster_id: str = Field(min_length=1)
    cluster_label: str = Field(min_length=1)
    gap_type: GapType
    source_of_record: Literal["gemini"]
    perception_themes: list[str] = Field(default_factory=list)
    missing_associations: list[str] = Field(default_factory=list)
    competitor_association: str | None = None
    safe_scenario_wording: str = Field(min_length=1)
    gap_type_support: Literal["supports", "conflicts", "insufficient"]
    rationale: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("perception_themes", "missing_associations", "evidence_refs")
    @classmethod
    def require_non_empty_lists(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Gemini findings require non-empty list fields")
        return value


class GeminiAnalysis(StrictModel):
    metadata: GeminiMetadata
    summary: GeminiSummary
    findings: list[GeminiFinding] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_summary_counts(self) -> GeminiAnalysis:
        expected = {
            "analyzed_rows": len(self.findings),
            "supported_gap_types": sum(
                1 for finding in self.findings if finding.gap_type_support == "supports"
            ),
            "conflicted_gap_types": sum(
                1 for finding in self.findings if finding.gap_type_support == "conflicts"
            ),
            "insufficient_gap_types": sum(
                1 for finding in self.findings if finding.gap_type_support == "insufficient"
            ),
        }
        actual = self.summary.model_dump()
        if actual != expected:
            raise ValueError(f"Gemini summary does not match findings: {actual}")
        return self


class TavilyMetadata(StrictModel):
    generated_at: datetime
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)
    run_mode: Literal["live", "test"]
    sdk_package: str = Field(min_length=1)
    sdk_version: str = Field(min_length=1)
    query_template_version: str = Field(min_length=1)
    search_depth: Literal["basic", "advanced"]
    max_results: int = Field(ge=1, le=20)
    query_timeout_seconds: int = Field(ge=1)
    include_raw_content: bool
    include_answer: bool
    include_images: bool
    include_usage: bool
    request_count: int = Field(ge=0)
    successful_query_count: int = Field(ge=0)
    failed_query_count: int = Field(ge=0)
    failed_query_ref: str | None = None
    response_time_seconds: float | None = Field(default=None, ge=0)
    api_credits_used: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def enforce_query_count_invariant(self) -> TavilyMetadata:
        if self.request_count != self.successful_query_count + self.failed_query_count:
            raise ValueError("request_count must equal successful_query_count + failed_query_count")
        if self.failed_query_count and not self.failed_query_ref:
            raise ValueError("failed queries require failed_query_ref")
        if not self.failed_query_count and self.failed_query_ref:
            raise ValueError("failed_query_ref requires failed_query_count")
        return self


class TavilySummary(StrictModel):
    analyzed_rows: int = Field(ge=0)
    planned_queries: int = Field(ge=0)
    sources: int = Field(ge=0)
    supported_findings: int = Field(ge=0)
    conflicted_findings: int = Field(ge=0)
    insufficient_findings: int = Field(ge=0)


class TavilySource(StrictModel):
    source_ref: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: HttpUrl
    domain: str = Field(min_length=1)
    snippet: str = Field(min_length=1)
    score: float | None = Field(default=None, ge=0)
    query_ref: str = Field(min_length=1)
    source_role: Literal["target", "competitor", "neutral"]
    snippet_review_status: Literal["raw", "reviewed", "redacted"] = "raw"


class TavilyFinding(StrictModel):
    finding_id: str = Field(min_length=1)
    cluster_id: str = Field(min_length=1)
    cluster_label: str = Field(min_length=1)
    gap_type: GapType
    source_of_record: Literal["tavily"]
    target_query: str = Field(min_length=1)
    competitor_query: str = Field(min_length=1)
    public_proof_support: Literal["supports", "conflicts", "insufficient"]
    proof_gap_summary: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)
    sources: list[TavilySource] = Field(default_factory=list)

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Tavily findings require evidence refs")
        return value


class TavilyEvidence(StrictModel):
    metadata: TavilyMetadata
    summary: TavilySummary
    findings: list[TavilyFinding] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_summary_counts(self) -> TavilyEvidence:
        findings = self.findings
        expected = {
            "analyzed_rows": len(findings),
            "planned_queries": self.metadata.request_count,
            "sources": sum(len(finding.sources) for finding in findings),
            "supported_findings": sum(
                1 for finding in findings if finding.public_proof_support == "supports"
            ),
            "conflicted_findings": sum(
                1 for finding in findings if finding.public_proof_support == "conflicts"
            ),
            "insufficient_findings": sum(
                1 for finding in findings if finding.public_proof_support == "insufficient"
            ),
        }
        actual = self.summary.model_dump()
        if actual != expected:
            raise ValueError(f"Tavily summary does not match findings: {actual}")
        return self


class GapClassificationMetadata(StrictModel):
    generated_at: datetime
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)
    classifier_version: str = Field(min_length=1)
    used_gemini: bool
    used_tavily: bool


class MethodSignal(StrictModel):
    method: Literal["peec", "gemini", "tavily"]
    signal: Literal["supports", "conflicts", "insufficient", "unavailable"]
    evidence_refs: list[str] = Field(default_factory=list)
    unavailable_reason: (
        Literal[
            "artifact_not_provided",
            "row_not_in_artifact",
            "method_returned_no_finding",
        ]
        | None
    ) = None

    @model_validator(mode="after")
    def enforce_unavailable_reason(self) -> MethodSignal:
        if self.signal == "unavailable" and not self.unavailable_reason:
            raise ValueError("unavailable method signals require unavailable_reason")
        if self.signal != "unavailable" and self.unavailable_reason:
            raise ValueError("unavailable_reason is only allowed for unavailable signals")
        if self.signal != "unavailable" and not self.evidence_refs:
            raise ValueError("available method signals require evidence_refs")
        return self


class ClassifiedGap(StrictModel):
    cluster_id: str = Field(min_length=1)
    cluster_label: str = Field(min_length=1)
    provisional_gap_type: GapType
    classification_status: Literal["confirmed", "provisional", "conflicted", "insufficient"]
    confidence_tier: EvidenceTier
    method_signals: list[MethodSignal] = Field(default_factory=list)
    method_agreement_score: float = Field(ge=0, le=1)
    classification_rationale: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("method_signals")
    @classmethod
    def require_three_method_signals(cls, value: list[MethodSignal]) -> list[MethodSignal]:
        methods = [signal.method for signal in value]
        if methods != ["peec", "gemini", "tavily"]:
            raise ValueError("classified gaps require method signals in peec/gemini/tavily order")
        return value

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("classified gaps require evidence_refs")
        return value


class GapClassificationSummary(StrictModel):
    classified_gaps: int = Field(ge=0)
    confirmed: int = Field(ge=0)
    provisional: int = Field(ge=0)
    conflicted: int = Field(ge=0)
    insufficient: int = Field(ge=0)


class GapClassification(StrictModel):
    metadata: GapClassificationMetadata
    summary: GapClassificationSummary
    classified_gaps: list[ClassifiedGap] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_summary_counts(self) -> GapClassification:
        expected = {
            "classified_gaps": len(self.classified_gaps),
            "confirmed": sum(
                1 for gap in self.classified_gaps if gap.classification_status == "confirmed"
            ),
            "provisional": sum(
                1 for gap in self.classified_gaps if gap.classification_status == "provisional"
            ),
            "conflicted": sum(
                1 for gap in self.classified_gaps if gap.classification_status == "conflicted"
            ),
            "insufficient": sum(
                1 for gap in self.classified_gaps if gap.classification_status == "insufficient"
            ),
        }
        actual = self.summary.model_dump()
        if actual != expected:
            raise ValueError(f"gap classification summary does not match gaps: {actual}")
        return self


class ValueMetricsMetadata(StrictModel):
    generated_at: datetime
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)
    metrics_version: str = Field(min_length=1)
    used_gemini: bool
    used_tavily: bool
    used_classification: bool


class ValueMetricRow(StrictModel):
    cluster_id: str = Field(min_length=1)
    cluster_label: str = Field(min_length=1)
    gap_type: GapType | None = None
    parent_topic: str = Field(min_length=1)
    trend_label: Literal["stronghold", "blind_spot", "proof_gap", "contested", "watch"]
    trend_zone: Literal[
        "stronghold",
        "slow_burn",
        "snapshot_blind_spot",
        "proof_gap",
        "contested",
    ]
    zone_basis: Literal[
        "single_snapshot_visibility",
        "cross_prompt_snapshot",
        "method_conflict",
        "proof_coverage",
    ]
    decision_bucket: Literal["act_now", "test_next", "monitor", "deprioritize", "block"]
    decision_bucket_reason: str = Field(min_length=1)
    primary_gap: str = Field(min_length=1)
    recommended_next_move: str = Field(min_length=1)
    relevance_score: int = Field(ge=0, le=100)
    source_trust_score: int = Field(ge=0, le=100)
    proof_strength_score: int = Field(ge=0, le=100)
    method_agreement_score: int = Field(ge=0, le=100)
    opportunity_score: int = Field(ge=0, le=100)
    labeling_source: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    strategic_status: str | None = None

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("value metric rows require evidence_refs")
        return value


class ValueMetricsSummary(StrictModel):
    rows: int = Field(ge=0)
    average_opportunity_score: int = Field(ge=0, le=100)
    contested_rows: int = Field(ge=0)
    proof_gap_rows: int = Field(ge=0)


class ValueAddedMetrics(StrictModel):
    metadata: ValueMetricsMetadata
    summary: ValueMetricsSummary
    rows: list[ValueMetricRow] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_summary_counts(self) -> ValueAddedMetrics:
        average = (
            round(sum(row.opportunity_score for row in self.rows) / len(self.rows))
            if self.rows
            else 0
        )
        expected = {
            "rows": len(self.rows),
            "average_opportunity_score": average,
            "contested_rows": sum(1 for row in self.rows if row.trend_label == "contested"),
            "proof_gap_rows": sum(1 for row in self.rows if row.trend_label == "proof_gap"),
        }
        actual = self.summary.model_dump()
        if actual != expected:
            raise ValueError(f"value metrics summary does not match rows: {actual}")
        return self


class CompetitorLandscapeMetadata(StrictModel):
    generated_at: datetime
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)
    landscape_version: str = Field(min_length=1)
    used_tavily: bool
    used_classification: bool


class CompetitorTopic(StrictModel):
    cluster_id: str = Field(min_length=1)
    cluster_label: str = Field(min_length=1)
    target_visibility_share: float | None = Field(default=None, ge=0, le=1)
    competitor_owner: str | None = None
    competitor_visibility_share: float | None = Field(default=None, ge=0, le=1)
    visibility_delta: float | None = None
    ownership_status: Literal[
        "target_owned",
        "competitor_owned",
        "contested",
        "unknown",
    ]
    proof_source_count: int = Field(ge=0)
    classification_status: str = Field(min_length=1)
    confidence_tier: EvidenceTier
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("competitor topics require evidence_refs")
        return value


class CompetitorLandscapeSummary(StrictModel):
    topics: int = Field(ge=0)
    target_owned: int = Field(ge=0)
    competitor_owned: int = Field(ge=0)
    contested: int = Field(ge=0)


class CompetitorLandscape(StrictModel):
    metadata: CompetitorLandscapeMetadata
    summary: CompetitorLandscapeSummary
    topics: list[CompetitorTopic] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_summary_counts(self) -> CompetitorLandscape:
        expected = {
            "topics": len(self.topics),
            "target_owned": sum(
                1 for topic in self.topics if topic.ownership_status == "target_owned"
            ),
            "competitor_owned": sum(
                1 for topic in self.topics if topic.ownership_status == "competitor_owned"
            ),
            "contested": sum(
                1 for topic in self.topics if topic.ownership_status == "contested"
            ),
        }
        actual = self.summary.model_dump()
        if actual != expected:
            raise ValueError(f"competitor landscape summary does not match topics: {actual}")
        return self


class PrescriptionMetadata(StrictModel):
    generated_at: datetime
    source_manifest_ref: str = Field(min_length=1)
    peec_snapshot_id: str = Field(min_length=1)


class PrescriptionSummary(StrictModel):
    planned_prompts: int = Field(ge=0)
    planned_topics: int = Field(ge=0)
    planned_tags: int = Field(ge=0)


class PlannedTopic(StrictModel):
    operation_id: str = Field(min_length=1)
    execution_status: Literal["planned"]
    topic_slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    source_cluster_id: str = Field(min_length=1)
    gap_type: GapType
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("planned topic must include evidence refs")
        return value


class PlannedTag(StrictModel):
    operation_id: str = Field(min_length=1)
    execution_status: Literal["planned"]
    tag_slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    kind: Literal["gap", "geo", "campaign"]
    description: str = Field(min_length=1)


class PlannedPrompt(StrictModel):
    operation_id: str = Field(min_length=1)
    execution_status: Literal["planned"]
    prompt_slug: str = Field(min_length=1)
    text: str = Field(min_length=1)
    prompt_language: Literal["en"]
    prompt_text_source: Literal["templated", "peec_observed", "gemini_generated"]
    country_code: Literal["US", "DE", "GB"]
    topic_slug: str = Field(min_length=1)
    gap_type: GapType
    tag_refs: list[str] = Field(default_factory=list)
    source_cluster_id: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("tag_refs", "evidence_refs")
    @classmethod
    def require_refs(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("planned prompt must include refs")
        return value


class PrescriptionPlan(StrictModel):
    metadata: PrescriptionMetadata
    summary: PrescriptionSummary
    planned_topics: list[PlannedTopic] = Field(default_factory=list)
    planned_tags: list[PlannedTag] = Field(default_factory=list)
    planned_prompts: list[PlannedPrompt] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_summary_counts(self) -> PrescriptionPlan:
        expected = {
            "planned_prompts": len(self.planned_prompts),
            "planned_topics": len(self.planned_topics),
            "planned_tags": len(self.planned_tags),
        }
        actual = self.summary.model_dump()
        if actual != expected:
            raise ValueError(f"prescription summary does not match plan counts: {actual}")
        return self


ARTIFACT_MODELS: dict[str, type[BaseModel]] = {
    "prompt_universe": PromptUniverse,
    "study_ssot": StudySsot,
    "evidence_ledger": EvidenceLedger,
    "manifest": Manifest,
    "hero_cards": HeroCards,
    "pipeline_funnel": PipelineFunnel,
    "source_of_record": SourceOfRecord,
    "gap_classification": GapClassification,
    "value_added_metrics": ValueAddedMetrics,
    "competitor_landscape": CompetitorLandscape,
    "gemini_analysis": GeminiAnalysis,
    "tavily_evidence": TavilyEvidence,
    "prescription_plan": PrescriptionPlan,
}


def model_for_artifact(artifact_type: str) -> type[BaseModel]:
    normalized = artifact_type.lower().replace("-", "_")
    if normalized == "evidence_ledger_json":
        normalized = "evidence_ledger"
    try:
        return ARTIFACT_MODELS[normalized]
    except KeyError as exc:
        valid = ", ".join(sorted(ARTIFACT_MODELS))
        raise ValueError(
            f"unknown artifact type '{artifact_type}'. Expected one of: {valid}"
        ) from exc


def validate_payload(payload: dict[str, Any], artifact_type: str) -> BaseModel:
    model = model_for_artifact(artifact_type)
    return model.model_validate(payload)
