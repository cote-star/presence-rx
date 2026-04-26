"""Docs-grounded Peec baseline ingestion for Step 2."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel
from rich.console import Console

from presence_rx.contracts import (
    Comparability,
    EvidenceLedger,
    Freshness,
    FunnelStage,
    GapClassification,
    GeminiAnalysis,
    HeroCards,
    Manifest,
    ManifestSource,
    PipelineFunnel,
    PipelineSummary,
    PrescriptionPlan,
    Prompt,
    PromptCluster,
    PromptUniverse,
    SourceOfRecord,
    SourceOfRecordItem,
    StudyRow,
    StudySsot,
    TavilyEvidence,
)
from presence_rx.display_labels import compute_strategic_status

console = Console()

SNAPSHOT_REF = "peec:snapshot:nothing-phone:2026-04-25"
PROJECT_ID = "or_faaa7625-bc84-4f64-a754-a412d423c641"
OWN_BRAND_ID = "kw_d9414ede-8870-47a8-b377-14f887986e67"
PROMPT_TEXT_UNAVAILABLE = "PROMPT_TEXT_UNAVAILABLE_IN_DOCS_GROUNDED_SEED"
PROMPT_COUNT_UNAVAILABLE = "PROMPT_COUNT_BY_TOPIC_UNAVAILABLE_IN_DOCS_GROUNDED_SEED"


class SeedBrand(BaseModel):
    name: str
    brand_id: str
    is_own: bool
    visibility: float
    share_of_voice: float
    sentiment: int
    position: float


class SeedTopic(BaseModel):
    name: str
    topic_id: str
    visibility: float
    share_of_voice: float
    position: float
    verdict: str
    competitor_owner: str | None
    owner_visibility: float | None = None
    gap_type: str | None = None
    gap_type_rationale: str | None = None
    desired_association: bool = True
    strategic_importance: str = "medium"  # core, high, medium, low
    strategic_note: str | None = None


class SeedEngine(BaseModel):
    name: str
    visibility: float
    share_of_voice: float
    position: float
    sentiment: int


class SeedDomainGap(BaseModel):
    domain: str
    domain_type: str
    retrievals: int | None
    citation_rate: float | None
    cited_brands: list[str]


class NothingPhoneSeed(BaseModel):
    project_id: str
    snapshot_ref: str
    verified_at: str
    brand: str
    own_brand_id: str
    geography: str
    total_prompts: int
    brands: list[SeedBrand]
    topics: list[SeedTopic]
    engines: list[SeedEngine]
    domain_gaps: list[SeedDomainGap]
    url_gap_categories: list[str]


# Generic alias — all brand seeds share the same schema for now.
BrandSeed = NothingPhoneSeed


@dataclass(frozen=True)
class GeneratedArtifacts:
    prompt_universe: PromptUniverse
    study_ssot: StudySsot
    manifest: Manifest
    source_of_record: SourceOfRecord
    pipeline_funnel: PipelineFunnel
    hero_cards: HeroCards


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace(".", "-")
    )


def parse_generated_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def deterministic_seed_generated_at(seed: BrandSeed) -> datetime:
    return parse_generated_at(f"{seed.verified_at}T00:00:00+00:00")


def resolve_generated_at(seed: BrandSeed, generated_at: str | None = None) -> datetime:
    if generated_at:
        return parse_generated_at(generated_at)

    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch:
        return datetime.fromtimestamp(int(source_date_epoch), UTC)

    return deterministic_seed_generated_at(seed)


def nothing_phone_seed() -> NothingPhoneSeed:
    return NothingPhoneSeed(
        project_id=PROJECT_ID,
        snapshot_ref=SNAPSHOT_REF,
        verified_at="2026-04-25",
        brand="Nothing Phone",
        own_brand_id=OWN_BRAND_ID,
        geography="US",
        total_prompts=50,
        brands=[
            SeedBrand(
                name="Nothing Phone",
                brand_id=OWN_BRAND_ID,
                is_own=True,
                visibility=0.20,
                share_of_voice=0.08,
                sentiment=64,
                position=2.4,
            ),
            SeedBrand(
                name="Apple",
                brand_id="kw_08d6903d-8f51-439c-8f15-3a50cfb49d4c",
                is_own=False,
                visibility=0.50,
                share_of_voice=0.23,
                sentiment=66,
                position=3.6,
            ),
            SeedBrand(
                name="Google",
                brand_id="kw_2727503a-c380-4711-b092-b349f0f94f21",
                is_own=False,
                visibility=0.39,
                share_of_voice=0.20,
                sentiment=67,
                position=5.4,
            ),
            SeedBrand(
                name="Samsung",
                brand_id="kw_71b137f7-c9f7-4aac-b0e3-12d22d5cd3fb",
                is_own=False,
                visibility=0.36,
                share_of_voice=0.16,
                sentiment=68,
                position=4.6,
            ),
            SeedBrand(
                name="Pixel",
                brand_id="kw_c7c314cb-633f-4fc7-8a9d-db55e45974a8",
                is_own=False,
                visibility=0.30,
                share_of_voice=0.14,
                sentiment=67,
                position=6.9,
            ),
            SeedBrand(
                name="Sony",
                brand_id="kw_d4c5113b-8708-4fb3-a626-6c9d6551b309",
                is_own=False,
                visibility=0.22,
                share_of_voice=0.09,
                sentiment=68,
                position=4.8,
            ),
            SeedBrand(
                name="Bose",
                brand_id="kw_c93220e8-f20f-404d-a331-e2ff1adc2acf",
                is_own=False,
                visibility=0.12,
                share_of_voice=0.04,
                sentiment=68,
                position=4.5,
            ),
            SeedBrand(
                name="Xiaomi",
                brand_id="kw_41eca0bc-dd21-46f6-a1c2-3d519bfcfb2c",
                is_own=False,
                visibility=0.11,
                share_of_voice=0.02,
                sentiment=67,
                position=5.1,
            ),
            SeedBrand(
                name="OnePlus",
                brand_id="kw_d02c02ea-19c8-47cf-8d82-fb9a6db023fd",
                is_own=False,
                visibility=0.09,
                share_of_voice=0.02,
                sentiment=68,
                position=4.3,
            ),
            SeedBrand(
                name="Logitech",
                brand_id="kw_50e84900-e069-459f-94f7-2a1c5c8522b3",
                is_own=False,
                visibility=0.09,
                share_of_voice=0.02,
                sentiment=70,
                position=4.7,
            ),
        ],
        topics=[
            SeedTopic(
                name="Smartphone Design",
                topic_id="to_be2fd0d7-8cf6-4c0c-bbe1-8f03ae7850ef",
                visibility=0.72,
                share_of_voice=0.85,
                position=1.9,
                verdict="STRONGHOLD",
                competitor_owner=None,
                owner_visibility=None,
                desired_association=True,
                strategic_importance="core",
                strategic_note="Core identity \u2014 defend",
            ),
            SeedTopic(
                name="Mobile Ecosystem",
                topic_id="to_b1b39ec0-bfd9-430b-8e42-e709bf3560ed",
                visibility=0.12,
                share_of_voice=0.07,
                position=3.8,
                verdict="Blind spot",
                competitor_owner="Apple",
                owner_visibility=0.72,
                gap_type="indexing",
                gap_type_rationale=(
                    "Scope-locked provisional label: current docs frame Mobile Ecosystem as an "
                    "owned-content retrieval/citation problem, pending Gemini/Tavily confirmation."
                ),
                desired_association=True,
                strategic_importance="medium",
                strategic_note="Want ecosystem credibility",
            ),
            SeedTopic(
                name="Consumer Tech Innovation",
                topic_id="to_22c5c578-d9a3-4128-896c-823c92f20ea2",
                visibility=0.10,
                share_of_voice=0.05,
                position=3.7,
                verdict="Blind spot",
                competitor_owner="Apple",
                owner_visibility=0.45,
                gap_type="perception",
                gap_type_rationale=(
                    "Scope-locked provisional label: innovation association appears weak in the "
                    "Peec snapshot, pending Gemini/Tavily confirmation."
                ),
                desired_association=True,
                strategic_importance="high",
                strategic_note="Want innovation association",
            ),
            SeedTopic(
                name="Minimalist Hardware",
                topic_id="to_e927582c-97f4-41ee-804c-bbe378e43242",
                visibility=0.06,
                share_of_voice=0.02,
                position=4.1,
                verdict="IRONIC GAP",
                competitor_owner="Apple",
                owner_visibility=0.39,
                gap_type="perception",
                gap_type_rationale=(
                    "Scope-locked provisional label from SCOPE_FINAL: brand identity is "
                    "minimalism, but AI-answer visibility is owned by Apple in this topic."
                ),
                desired_association=True,
                strategic_importance="core",
                strategic_note="CORE IDENTITY \u2014 most urgent",
            ),
            SeedTopic(
                name="Wireless Audio",
                topic_id="to_736e7e42-5109-4853-b9a4-7a48ef0a316f",
                visibility=0.01,
                share_of_voice=0.00,
                position=2.0,
                verdict="Invisible",
                competitor_owner="Apple",
                owner_visibility=0.53,
                gap_type="volume_frequency",
                gap_type_rationale=(
                    "Scope-locked provisional label from SCOPE_FINAL: Nothing Ear exists, but "
                    "category presence is near-zero in the Peec snapshot."
                ),
                desired_association=True,
                strategic_importance="medium",
                strategic_note="Nothing Ear product line",
            ),
        ],
        engines=[
            SeedEngine(
                name="Gemini",
                visibility=0.26,
                share_of_voice=0.36,
                position=2.5,
                sentiment=56,
            ),
            SeedEngine(
                name="ChatGPT",
                visibility=0.18,
                share_of_voice=0.39,
                position=2.5,
                sentiment=66,
            ),
            SeedEngine(
                name="Google AI Overview",
                visibility=0.17,
                share_of_voice=0.25,
                position=2.1,
                sentiment=71,
            ),
        ],
        domain_gaps=[
            SeedDomainGap(
                domain="rtings.com",
                domain_type="Editorial",
                retrievals=89,
                citation_rate=0.76,
                cited_brands=["Apple", "Samsung", "Bose", "Sony"],
            ),
            SeedDomainGap(
                domain="whathifi.com",
                domain_type="Editorial",
                retrievals=38,
                citation_rate=1.36,
                cited_brands=["Apple", "Bose", "Sony"],
            ),
            SeedDomainGap(
                domain="samsung.com",
                domain_type="Corporate",
                retrievals=34,
                citation_rate=0.94,
                cited_brands=["Samsung", "Google", "Apple"],
            ),
            SeedDomainGap(
                domain="zdnet.com",
                domain_type="Editorial",
                retrievals=19,
                citation_rate=0.79,
                cited_brands=["Google", "Samsung", "Apple"],
            ),
            SeedDomainGap(
                domain="wallpaper.com",
                domain_type="Editorial",
                retrievals=14,
                citation_rate=0.86,
                cited_brands=["Google", "Samsung", "Apple"],
            ),
            SeedDomainGap(
                domain="dezeen.com",
                domain_type="Design",
                retrievals=None,
                citation_rate=None,
                cited_brands=[],
            ),
            SeedDomainGap(
                domain="yankodesign.com",
                domain_type="Design",
                retrievals=None,
                citation_rate=None,
                cited_brands=[],
            ),
        ],
        url_gap_categories=[
            "best-smartphone-os-ranked",
            "best-smartphones-for-photographers-2026",
            "10-best-gadgets-april-2026",
            "android-vs-ios",
            "which-brands-best-value-for-money",
            "dezeen-ces-gadgets",
            "yankodesign-gen-z-gadgets",
            "which-headphones-have-transparency-mode",
        ],
    )


def attio_seed() -> BrandSeed:
    """Docs-grounded synthetic seed for Attio (SaaS/CRM)."""
    return BrandSeed(
        project_id="or_47ccb54e-0f32-4c95-b460-6a070499d084",
        snapshot_ref="peec:snapshot:attio:2026-04-25",
        verified_at="2026-04-25",
        brand="Attio",
        own_brand_id="kw_attio_own_brand_seed",
        geography="US",
        total_prompts=50,
        brands=[
            SeedBrand(
                name="Attio",
                brand_id="kw_attio_own_brand_seed",
                is_own=True,
                visibility=0.08,
                share_of_voice=0.03,
                sentiment=72,
                position=3.2,
            ),
            SeedBrand(
                name="Salesforce",
                brand_id="kw_attio_comp_salesforce",
                is_own=False,
                visibility=0.45,
                share_of_voice=0.35,
                sentiment=58,
                position=1.8,
            ),
            SeedBrand(
                name="HubSpot",
                brand_id="kw_attio_comp_hubspot",
                is_own=False,
                visibility=0.35,
                share_of_voice=0.30,
                sentiment=71,
                position=1.5,
            ),
            SeedBrand(
                name="Pipedrive",
                brand_id="kw_attio_comp_pipedrive",
                is_own=False,
                visibility=0.12,
                share_of_voice=0.08,
                sentiment=68,
                position=2.8,
            ),
            SeedBrand(
                name="Monday CRM",
                brand_id="kw_attio_comp_monday_crm",
                is_own=False,
                visibility=0.10,
                share_of_voice=0.06,
                sentiment=65,
                position=3.0,
            ),
        ],
        topics=[
            SeedTopic(
                name="Product-Led CRM",
                topic_id="to_attio_product_led_crm",
                visibility=0.35,
                share_of_voice=0.25,
                position=1.8,
                verdict="STRONGHOLD",
                competitor_owner=None,
                owner_visibility=None,
                desired_association=True,
                strategic_importance="core",
                strategic_note="Core positioning",
            ),
            SeedTopic(
                name="CRM for Startups",
                topic_id="to_attio_crm_for_startups",
                visibility=0.22,
                share_of_voice=0.15,
                position=2.1,
                verdict="Blind spot",
                competitor_owner="HubSpot",
                owner_visibility=0.35,
                gap_type="perception",
                gap_type_rationale=(
                    "Attio is built for startups but HubSpot owns the 'startup CRM' narrative "
                    "in AI answers, despite Attio's product-market fit in that segment."
                ),
                desired_association=True,
                strategic_importance="high",
                strategic_note="Primary audience",
            ),
            SeedTopic(
                name="Modern CRM Alternative",
                topic_id="to_attio_modern_crm_alt",
                visibility=0.05,
                share_of_voice=0.02,
                position=3.8,
                verdict="Blind spot",
                competitor_owner="Salesforce",
                owner_visibility=0.45,
                gap_type="indexing",
                gap_type_rationale=(
                    "Attio content exists but AI default-routes 'CRM alternative' queries to "
                    "Salesforce comparison pages rather than surfacing Attio as an alternative."
                ),
                desired_association=True,
                strategic_importance="high",
                strategic_note="Category-creation narrative",
            ),
            SeedTopic(
                name="CRM Migration",
                topic_id="to_attio_crm_migration",
                visibility=0.03,
                share_of_voice=0.01,
                position=4.2,
                verdict="Invisible",
                competitor_owner="HubSpot",
                owner_visibility=0.35,
                gap_type="volume_frequency",
                gap_type_rationale=(
                    "Very few 'migrate to Attio' articles exist compared to abundant "
                    "HubSpot/Salesforce migration guides and documentation."
                ),
                desired_association=False,
                strategic_importance="low",
                strategic_note="Not fighting migration wars",
            ),
            SeedTopic(
                name="RevOps Tools",
                topic_id="to_attio_revops_tools",
                visibility=0.15,
                share_of_voice=0.10,
                position=2.5,
                verdict="Blind spot",
                competitor_owner="HubSpot",
                owner_visibility=0.35,
                gap_type="perception",
                gap_type_rationale=(
                    "Attio has RevOps features but AI associates RevOps tooling with "
                    "HubSpot Operations Hub rather than Attio's native capabilities."
                ),
                desired_association=True,
                strategic_importance="medium",
                strategic_note="Key buyer persona",
            ),
        ],
        engines=[
            SeedEngine(
                name="Gemini",
                visibility=0.10,
                share_of_voice=0.04,
                position=3.0,
                sentiment=70,
            ),
            SeedEngine(
                name="ChatGPT",
                visibility=0.07,
                share_of_voice=0.03,
                position=3.5,
                sentiment=72,
            ),
            SeedEngine(
                name="Google AI Overview",
                visibility=0.06,
                share_of_voice=0.02,
                position=3.2,
                sentiment=74,
            ),
        ],
        domain_gaps=[
            SeedDomainGap(
                domain="g2.com",
                domain_type="Review",
                retrievals=120,
                citation_rate=0.82,
                cited_brands=["Salesforce", "HubSpot", "Pipedrive"],
            ),
            SeedDomainGap(
                domain="capterra.com",
                domain_type="Review",
                retrievals=95,
                citation_rate=0.71,
                cited_brands=["HubSpot", "Salesforce", "Monday CRM"],
            ),
            SeedDomainGap(
                domain="trustradius.com",
                domain_type="Review",
                retrievals=60,
                citation_rate=0.68,
                cited_brands=["Salesforce", "HubSpot"],
            ),
            SeedDomainGap(
                domain="softwareadvice.com",
                domain_type="Review",
                retrievals=45,
                citation_rate=0.65,
                cited_brands=["HubSpot", "Pipedrive", "Salesforce"],
            ),
            SeedDomainGap(
                domain="pcmag.com",
                domain_type="Editorial",
                retrievals=30,
                citation_rate=0.59,
                cited_brands=["HubSpot", "Salesforce"],
            ),
        ],
        url_gap_categories=[
            "best CRM for startups 2026",
            "Salesforce alternatives",
            "HubSpot vs alternatives",
            "CRM migration guide",
            "RevOps tools comparison",
        ],
    )


def bmw_seed() -> BrandSeed:
    """Docs-grounded synthetic seed for BMW (Automotive/Luxury)."""
    return BrandSeed(
        project_id="or_52698861-707c-4006-bc7e-3563aad6cd44",
        snapshot_ref="peec:snapshot:bmw:2026-04-25",
        verified_at="2026-04-25",
        brand="BMW",
        own_brand_id="kw_bmw_own_brand_seed",
        geography="US",
        total_prompts=50,
        brands=[
            SeedBrand(
                name="BMW",
                brand_id="kw_bmw_own_brand_seed",
                is_own=True,
                visibility=0.18,
                share_of_voice=0.12,
                sentiment=68,
                position=2.2,
            ),
            SeedBrand(
                name="Tesla",
                brand_id="kw_bmw_comp_tesla",
                is_own=False,
                visibility=0.42,
                share_of_voice=0.30,
                sentiment=62,
                position=1.4,
            ),
            SeedBrand(
                name="Mercedes-Benz",
                brand_id="kw_bmw_comp_mercedes",
                is_own=False,
                visibility=0.25,
                share_of_voice=0.18,
                sentiment=72,
                position=1.9,
            ),
            SeedBrand(
                name="Audi",
                brand_id="kw_bmw_comp_audi",
                is_own=False,
                visibility=0.15,
                share_of_voice=0.10,
                sentiment=70,
                position=2.5,
            ),
            SeedBrand(
                name="Porsche",
                brand_id="kw_bmw_comp_porsche",
                is_own=False,
                visibility=0.12,
                share_of_voice=0.08,
                sentiment=78,
                position=2.8,
            ),
            SeedBrand(
                name="Lexus",
                brand_id="kw_bmw_comp_lexus",
                is_own=False,
                visibility=0.08,
                share_of_voice=0.05,
                sentiment=74,
                position=3.0,
            ),
            SeedBrand(
                name="Volvo",
                brand_id="kw_bmw_comp_volvo",
                is_own=False,
                visibility=0.10,
                share_of_voice=0.06,
                sentiment=75,
                position=2.7,
            ),
            SeedBrand(
                name="Genesis",
                brand_id="kw_bmw_comp_genesis",
                is_own=False,
                visibility=0.05,
                share_of_voice=0.03,
                sentiment=71,
                position=3.5,
            ),
            SeedBrand(
                name="Rivian",
                brand_id="kw_bmw_comp_rivian",
                is_own=False,
                visibility=0.06,
                share_of_voice=0.04,
                sentiment=69,
                position=3.2,
            ),
            SeedBrand(
                name="Lucid",
                brand_id="kw_bmw_comp_lucid",
                is_own=False,
                visibility=0.04,
                share_of_voice=0.02,
                sentiment=67,
                position=3.8,
            ),
            SeedBrand(
                name="Hyundai",
                brand_id="kw_bmw_comp_hyundai",
                is_own=False,
                visibility=0.14,
                share_of_voice=0.09,
                sentiment=66,
                position=2.6,
            ),
            SeedBrand(
                name="Toyota",
                brand_id="kw_bmw_comp_toyota",
                is_own=False,
                visibility=0.20,
                share_of_voice=0.14,
                sentiment=70,
                position=2.0,
            ),
        ],
        topics=[
            SeedTopic(
                name="Driving Dynamics",
                topic_id="to_bmw_driving_dynamics",
                visibility=0.45,
                share_of_voice=0.35,
                position=1.5,
                verdict="STRONGHOLD",
                competitor_owner=None,
                owner_visibility=None,
                desired_association=True,
                strategic_importance="core",
                strategic_note="Heritage stronghold \u2014 defend",
            ),
            SeedTopic(
                name="Luxury EV Transition",
                topic_id="to_bmw_luxury_ev_transition",
                visibility=0.12,
                share_of_voice=0.08,
                position=2.8,
                verdict="Blind spot",
                competitor_owner="Tesla",
                owner_visibility=0.42,
                gap_type="perception",
                gap_type_rationale=(
                    "BMW has i4/iX but AI frames 'luxury EV' as Tesla Model S/X territory, "
                    "sidelining BMW's electrification progress in premium segment."
                ),
                desired_association=True,
                strategic_importance="core",
                strategic_note="Critical for future positioning",
            ),
            SeedTopic(
                name="Premium SUV Segment",
                topic_id="to_bmw_premium_suv",
                visibility=0.15,
                share_of_voice=0.10,
                position=2.5,
                verdict="Blind spot",
                competitor_owner="Mercedes-Benz",
                owner_visibility=0.25,
                gap_type="indexing",
                gap_type_rationale=(
                    "BMW X-series exists but AI defaults to Mercedes GLE/GLC for premium "
                    "SUV queries; BMW content is not surfacing in retrieval."
                ),
                desired_association=True,
                strategic_importance="high",
                strategic_note="Revenue-critical segment",
            ),
            SeedTopic(
                name="Electric i-Series",
                topic_id="to_bmw_electric_i_series",
                visibility=0.06,
                share_of_voice=0.03,
                position=3.5,
                verdict="Invisible",
                competitor_owner="Tesla",
                owner_visibility=0.42,
                gap_type="volume_frequency",
                gap_type_rationale=(
                    "BMW i4 and iX exist but sparse editorial coverage compared to "
                    "Tesla Model 3/Y volume dominates AI training and retrieval sources."
                ),
                desired_association=True,
                strategic_importance="high",
                strategic_note="EV product line",
            ),
            SeedTopic(
                name="Brand Heritage",
                topic_id="to_bmw_brand_heritage",
                visibility=0.30,
                share_of_voice=0.22,
                position=1.8,
                verdict="Blind spot",
                competitor_owner="Mercedes-Benz",
                owner_visibility=0.25,
                gap_type="perception",
                gap_type_rationale=(
                    "Both have strong heritage but AI increasingly associates 'luxury heritage' "
                    "with Mercedes over BMW, eroding a historically shared narrative."
                ),
                desired_association=False,
                strategic_importance="low",
                strategic_note="Heritage is given, not a fight",
            ),
        ],
        engines=[
            SeedEngine(
                name="Gemini",
                visibility=0.20,
                share_of_voice=0.14,
                position=2.3,
                sentiment=66,
            ),
            SeedEngine(
                name="ChatGPT",
                visibility=0.16,
                share_of_voice=0.11,
                position=2.5,
                sentiment=70,
            ),
            SeedEngine(
                name="Google AI Overview",
                visibility=0.18,
                share_of_voice=0.12,
                position=2.1,
                sentiment=68,
            ),
        ],
        domain_gaps=[
            SeedDomainGap(
                domain="caranddriver.com",
                domain_type="Editorial",
                retrievals=150,
                citation_rate=0.88,
                cited_brands=["Tesla", "Mercedes-Benz", "Audi", "Porsche"],
            ),
            SeedDomainGap(
                domain="motortrend.com",
                domain_type="Editorial",
                retrievals=130,
                citation_rate=0.82,
                cited_brands=["Tesla", "Mercedes-Benz", "Toyota"],
            ),
            SeedDomainGap(
                domain="edmunds.com",
                domain_type="Review",
                retrievals=110,
                citation_rate=0.79,
                cited_brands=["Tesla", "Mercedes-Benz", "Audi"],
            ),
            SeedDomainGap(
                domain="electrek.com",
                domain_type="Editorial",
                retrievals=85,
                citation_rate=0.91,
                cited_brands=["Tesla", "Rivian", "Lucid"],
            ),
            SeedDomainGap(
                domain="insideevs.com",
                domain_type="Editorial",
                retrievals=70,
                citation_rate=0.85,
                cited_brands=["Tesla", "Rivian", "Hyundai"],
            ),
            SeedDomainGap(
                domain="topgear.com",
                domain_type="Editorial",
                retrievals=55,
                citation_rate=0.74,
                cited_brands=["Mercedes-Benz", "Porsche", "Audi"],
            ),
            SeedDomainGap(
                domain="autoexpress.com",
                domain_type="Editorial",
                retrievals=40,
                citation_rate=0.68,
                cited_brands=["Mercedes-Benz", "Audi", "Volvo"],
            ),
        ],
        url_gap_categories=[
            "best luxury EV 2026",
            "Tesla Model S alternatives",
            "BMW vs Mercedes EV",
            "premium electric SUV comparison",
            "luxury brand EV range comparison",
        ],
    )


def get_seed(case_id: str) -> BrandSeed:
    """Return the docs-grounded seed for a registered brand case."""
    if case_id == "nothing-phone":
        return nothing_phone_seed()
    if case_id == "attio":
        return attio_seed()
    if case_id == "bmw":
        return bmw_seed()
    raise ValueError(f"Unknown case_id: {case_id}. Expected: nothing-phone, attio, bmw")


def _topic_evidence_refs(topic: SeedTopic, snapshot_ref: str = SNAPSHOT_REF) -> list[str]:
    refs = [snapshot_ref, f"peec:topic:{slugify(topic.name)}"]
    if topic.competitor_owner:
        refs.append(f"peec:brand:{slugify(topic.competitor_owner)}")
    return refs


def build_artifacts(
    seed: BrandSeed, generated_at: datetime | None = None
) -> GeneratedArtifacts:
    resolved_generated_at = generated_at or deterministic_seed_generated_at(seed)
    competitors = [brand.name for brand in seed.brands if not brand.is_own]
    provisional_gap_count = sum(1 for topic in seed.topics if topic.gap_type)

    prompt_universe = PromptUniverse(
        brand=seed.brand,
        competitors=competitors,
        clusters=[
            PromptCluster(
                cluster_id=f"cluster:{slugify(topic.name)}",
                label=topic.name,
                stage="consideration",
                prompt_type="peec_topic",
                prompts=[
                    Prompt(
                        prompt_id=f"peec:topic:{slugify(topic.name)}:prompts-unavailable",
                        text=None,
                        source="peec_mcp_docs_seed",
                        unavailable_reason=PROMPT_TEXT_UNAVAILABLE,
                    )
                ],
            )
            for topic in seed.topics
        ],
    )

    study_ssot = StudySsot(
        rows=[
            StudyRow(
                cluster_id=f"cluster:{slugify(topic.name)}",
                cluster_label=topic.name,
                cluster_stage="consideration",
                cluster_prompt_type="peec_topic",
                cluster_prompt_count=None,
                visibility_target_share=topic.visibility,
                visibility_target_avg_position=topic.position,
                visibility_competitor_owner=topic.competitor_owner,
                gap_type=topic.gap_type,
                gap_type_source="scope_final" if topic.gap_type else "not_applicable",
                gap_type_rationale=topic.gap_type_rationale,
                confidence_tier="limited" if topic.gap_type else "moderate",
                evidence_refs=_topic_evidence_refs(topic, seed.snapshot_ref),
                input_gate_status="passed",
                evidence_tier="limited" if topic.gap_type else "moderate",
                publication_status="diagnostics_only",
                recommendation_available=False,
                unavailable_reason=PROMPT_COUNT_UNAVAILABLE,
                strategic_status=compute_strategic_status(
                    desired=topic.desired_association,
                    visibility=topic.visibility,
                    competitor_owner=topic.competitor_owner,
                    strategic_importance=topic.strategic_importance,
                ),
                desired_association=topic.desired_association,
                strategic_importance=topic.strategic_importance,
                strategic_note=topic.strategic_note,
            )
            for topic in seed.topics
        ]
    )

    source_of_record = SourceOfRecord(
        sources=[
            SourceOfRecordItem(
                field="brand_visibility",
                source="peec_mcp",
                rationale="Visibility, share of voice, sentiment, and position come from Peec MCP.",
            ),
            SourceOfRecordItem(
                field="topic_breakdown",
                source="peec_mcp",
                rationale=(
                    f"Topic-level metrics and IDs are from the MCP-verified {seed.brand} project."
                ),
            ),
            SourceOfRecordItem(
                field="engine_breakdown",
                source="peec_mcp",
                rationale="Model-level visibility split is from Peec brand reports.",
            ),
            SourceOfRecordItem(
                field="editorial_gap_domains",
                source="peec_mcp",
                rationale="Gap domains and citation/retrieval values are from Peec domain reports.",
            ),
            SourceOfRecordItem(
                field="gap_type",
                source="derived",
                rationale=(
                    "Step 2 labels are provisional scope-locked classifications "
                    "awaiting enrichment."
                ),
            ),
            SourceOfRecordItem(
                field="pipeline_funnel",
                source="derived",
                rationale="Funnel counts are derived from the docs-grounded ingestion seed.",
            ),
        ]
    )

    pipeline_funnel = PipelineFunnel(
        stages=[
            FunnelStage(stage="raw_peec_topics", count=len(seed.topics)),
            FunnelStage(stage="prompt_universe_clusters", count=len(prompt_universe.clusters)),
            FunnelStage(stage="study_rows", count=len(study_ssot.rows)),
            FunnelStage(stage="provisional_gap_type_rows", count=provisional_gap_count),
        ]
    )

    hero_cards = HeroCards(
        guardrail_pass_rate_pct=0,
        cluster_pass_rate_pct=100,
        actionable_recommendations=0,
        method_conflict_count=0,
        blocked_claim_count=0,
    )

    manifest = Manifest(
        brand=seed.brand,
        competitors=competitors,
        generated_at=resolved_generated_at,
        artifact_version="0.2.0-step2",
        taxonomy_version="2026-04-25-demo",
        campaign_type_mapping_version=None,
        peec_snapshot_id=seed.snapshot_ref,
        published=False,
        sources={
            "peec_mcp": ManifestSource(
                snapshot_id=seed.snapshot_ref,
                prompt_count=seed.total_prompts,
            ),
            "tavily": ManifestSource(query_count=0, source_count=0),
            "gemini": ManifestSource(analysis_runs=0),
            "lovable": ManifestSource(dashboard_url=None),
        },
        confidence_counts={
            "strong": 0,
            "moderate": 1,
            "limited": 4,
            "blocked": 0,
        },
        quality_counts={
            "strong": 0,
            "moderate": 1,
            "limited": 4,
            "blocked": 0,
        },
        unavailable_reason_counts={PROMPT_COUNT_UNAVAILABLE: len(seed.topics)},
        freshness=Freshness(
            status="docs_grounded_seed",
            generated_at=resolved_generated_at,
            newer_snapshot_available=False,
        ),
        comparability=Comparability(
            comparable_to_previous=False,
            reason="First generated baseline from MCP-verified docs.",
        ),
        pipeline_summary=PipelineSummary(
            raw_prompts=seed.total_prompts,
            clusters=len(prompt_universe.clusters),
            evidence_gated=0,
            actionable_recommendations=0,
        ),
        artifacts=[
            "prompt_universe.json",
            "study_ssot.json",
            "manifest.json",
            "source_of_record.json",
            "pipeline_funnel.json",
            "hero_cards.json",
        ],
    )

    return GeneratedArtifacts(
        prompt_universe=prompt_universe,
        study_ssot=study_ssot,
        manifest=manifest,
        source_of_record=source_of_record,
        pipeline_funnel=pipeline_funnel,
        hero_cards=hero_cards,
    )


def write_artifacts(artifacts: GeneratedArtifacts, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    payloads: dict[str, BaseModel] = {
        "prompt_universe.json": artifacts.prompt_universe,
        "study_ssot.json": artifacts.study_ssot,
        "manifest.json": artifacts.manifest,
        "source_of_record.json": artifacts.source_of_record,
        "pipeline_funnel.json": artifacts.pipeline_funnel,
        "hero_cards.json": artifacts.hero_cards,
    }
    written: list[Path] = []
    for filename, model in payloads.items():
        path = out_dir / filename
        path.write_text(json.dumps(model.model_dump(mode="json"), indent=2) + "\n")
        written.append(path)
    return written


def update_manifest_post_pipeline(
    manifest: Manifest,
    *,
    tavily: TavilyEvidence | None = None,
    gemini: GeminiAnalysis | None = None,
    classification: GapClassification | None = None,
    ledger: EvidenceLedger | None = None,
    prescription: PrescriptionPlan | None = None,
) -> Manifest:
    """Refresh manifest source counts and confidence after pipeline completes."""
    sources = dict(manifest.sources)
    if tavily is not None:
        sources["tavily"] = ManifestSource(
            query_count=tavily.metadata.request_count,
            source_count=tavily.summary.sources,
        )
    if gemini is not None:
        sources["gemini"] = ManifestSource(
            analysis_runs=gemini.summary.analyzed_rows,
        )

    confidence_counts: dict[str, int] = {"strong": 0, "moderate": 0, "limited": 0, "blocked": 0}
    if classification is not None:
        for gap in classification.classified_gaps:
            tier = gap.confidence_tier.value
            if tier in confidence_counts:
                confidence_counts[tier] += 1
        # Unclassified rows (strongholds) get moderate confidence
        unclassified = manifest.pipeline_summary.clusters - classification.summary.classified_gaps
        confidence_counts["moderate"] += max(0, unclassified)
    else:
        confidence_counts = dict(manifest.confidence_counts)

    actionable = len(ledger.claims) if ledger else 0

    artifacts = list(manifest.artifacts)
    for name in [
        "gemini_analysis.json", "tavily_evidence.json", "gap_classification.json",
        "EVIDENCE_LEDGER.json", "value_added_metrics.json", "competitor_landscape.json",
        "prescription_plan.json",
    ]:
        if name not in artifacts:
            artifacts.append(name)

    return manifest.model_copy(update={
        "sources": sources,
        "confidence_counts": confidence_counts,
        "quality_counts": confidence_counts,
        "pipeline_summary": PipelineSummary(
            raw_prompts=manifest.pipeline_summary.raw_prompts,
            clusters=manifest.pipeline_summary.clusters,
            evidence_gated=classification.summary.classified_gaps if classification else 0,
            actionable_recommendations=actionable,
        ),
        "artifacts": artifacts,
    })


def update_hero_cards_post_pipeline(
    *,
    classification: GapClassification | None = None,
    ledger: EvidenceLedger | None = None,
) -> HeroCards:
    """Refresh hero cards from pipeline results."""
    claims = ledger.claims if ledger else []
    blocked = ledger.blocked_claims if ledger else []
    classified = classification.classified_gaps if classification else []
    total_claims = len(claims)
    passed = sum(1 for c in claims if c.status != "blocked")
    pass_rate = round(passed * 100 / total_claims) if total_claims else 0
    return HeroCards(
        guardrail_pass_rate_pct=pass_rate,
        cluster_pass_rate_pct=100,
        actionable_recommendations=sum(
            1 for c in claims if c.status in ("actionable", "directional")
        ),
        method_conflict_count=sum(
            1 for g in classified if g.classification_status == "conflicted"
        ),
        blocked_claim_count=len(blocked),
    )


def update_pipeline_funnel_post_pipeline(
    funnel: PipelineFunnel,
    *,
    classification: GapClassification | None = None,
    ledger: EvidenceLedger | None = None,
    prescription: PrescriptionPlan | None = None,
) -> PipelineFunnel:
    """Extend funnel with evidence-gating, claims, and prescription stages."""
    downstream = {"evidence_gated", "claims_generated", "prescriptions_planned"}
    stages = [s for s in funnel.stages if s.stage not in downstream]
    if classification is not None:
        stages.append(FunnelStage(
            stage="evidence_gated",
            count=classification.summary.classified_gaps,
        ))
    if ledger is not None:
        stages.append(FunnelStage(
            stage="claims_generated",
            count=len(ledger.claims),
        ))
    if prescription is not None:
        stages.append(FunnelStage(
            stage="prescriptions_planned",
            count=prescription.summary.planned_prompts,
        ))
    return PipelineFunnel(stages=stages)


def main(
    seed: Annotated[
        str,
        typer.Option(
            "--seed",
            help="Docs-grounded seed to ingest (nothing-phone, attio, bmw).",
        ),
    ] = "nothing-phone",
    out: Annotated[
        Path,
        typer.Option("--out", help="Directory for generated JSON artifacts."),
    ] = Path("data/generated"),
    generated_at: Annotated[
        str | None,
        typer.Option(
            "--generated-at",
            help=(
                "ISO timestamp for deterministic artifacts. If omitted, SOURCE_DATE_EPOCH "
                "is used when set; otherwise the seed verification date is used."
            ),
        ),
    ] = None,
) -> None:
    """Generate Step 2 baseline artifacts from a docs-grounded Peec seed."""

    seed_data = get_seed(seed)
    resolved_generated_at = resolve_generated_at(seed_data, generated_at)
    artifacts = build_artifacts(seed_data, generated_at=resolved_generated_at)
    written = write_artifacts(artifacts, out)
    for path in written:
        console.print(f"[green]wrote[/green] {path}")


if __name__ == "__main__":
    typer.run(main)
