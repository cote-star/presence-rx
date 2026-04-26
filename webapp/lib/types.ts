// TypeScript interfaces derived from presence_rx/contracts.py

export interface StudyRow {
  cluster_id: string;
  cluster_label: string;
  cluster_stage: string;
  cluster_prompt_type: string;
  cluster_prompt_count: number | null;
  visibility_target_share: number | null;
  visibility_target_avg_position: number | null;
  visibility_competitor_owner: string | null;
  gap_type: "perception" | "indexing" | "volume_frequency" | null;
  gap_type_source: string | null;
  gap_type_rationale: string | null;
  confidence_tier: string;
  evidence_refs: string[];
  input_gate_status: string;
  evidence_tier: string;
  publication_status: string;
  recommendation_available: boolean;
  unavailable_reason: string | null;
  action_recommendation: string | null;
  action_monitor_prompt: string | null;
  desired_association: boolean;
  strategic_importance: string;
  strategic_note: string | null;
  strategic_status: string | null;
}

export interface ClassifiedGap {
  cluster_id: string;
  cluster_label: string;
  provisional_gap_type: string;
  classification_status: string;
  confidence_tier: string;
  method_signals: MethodSignal[];
  method_agreement_score: number;
  classification_rationale: string;
  evidence_refs: string[];
}

export interface MethodSignal {
  method: string;
  signal: string;
  evidence_refs: string[];
  unavailable_reason: string | null;
}

export interface Claim {
  claim_id: string;
  claim: string;
  status: string;
  cluster_id: string;
  methods: string[];
  evidence_refs: string[];
  confidence_tier: string;
  publication_status: string;
  publication_language: string;
  why_not_stronger: string | null;
}

export interface BlockedClaim {
  claim_id: string;
  claim: string;
  blocked_reason: string;
  safe_rewrite: string;
  next_evidence_to_collect: string;
}

export interface MetricRow {
  cluster_id: string;
  cluster_label: string;
  gap_type: string | null;
  parent_topic: string;
  trend_label: string;
  trend_zone: string;
  zone_basis: string;
  decision_bucket: string;
  decision_bucket_reason: string;
  primary_gap: string;
  recommended_next_move: string;
  relevance_score: number;
  source_trust_score: number;
  proof_strength_score: number;
  method_agreement_score: number;
  opportunity_score: number;
  labeling_source: string;
  evidence_refs: string[];
  rationale: string;
  strategic_status: string | null;
}

export interface CompetitorTopic {
  cluster_id: string;
  cluster_label: string;
  target_visibility_share: number | null;
  competitor_owner: string | null;
  competitor_visibility_share: number | null;
  visibility_delta: number | null;
  ownership_status: string;
  proof_source_count: number;
  classification_status: string;
  confidence_tier: string;
  evidence_refs: string[];
}

export interface GeminiFinding {
  finding_id: string;
  cluster_id: string;
  cluster_label: string;
  gap_type: string;
  source_of_record: string;
  perception_themes: string[];
  missing_associations: string[];
  competitor_association: string | null;
  safe_scenario_wording: string;
  gap_type_support: string;
  rationale: string;
  evidence_refs: string[];
}

export interface BrandData {
  brand_name: string;
  case_id: string;
  study: { rows: StudyRow[] };
  classification: { classified_gaps: ClassifiedGap[]; summary: Record<string, number> } | null;
  metrics: { rows: MetricRow[]; summary: { average_opportunity_score: number } } | null;
  landscape: { topics: CompetitorTopic[] } | null;
  ledger: { claims: Claim[]; evidence: any[]; blocked_claims: BlockedClaim[] } | null;
  prescription: any | null;
  tavily: { summary: { sources: number }; findings: any[] } | null;
  gemini: { findings: GeminiFinding[]; summary: Record<string, number> } | null;
  manifest: any;
}

export interface BrandConfig {
  case_id: string;
  brand_name: string;
  category: string;
  peec_project_id: string;
  competitors: string[];
  audience_segments: string[];
  buying_journey_stages: string[];
  priority_topics: string[];
  known_market_tension: string;
  channels_to_activate: string[];
}
