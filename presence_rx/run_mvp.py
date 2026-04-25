"""Run the local Presence Rx MVP from available review-only artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.build_action_brief import build_action_brief, write_action_brief
from presence_rx.build_competitor_landscape import (
    build_competitor_landscape,
    write_competitor_landscape,
)
from presence_rx.build_evidence_ledger import build_evidence_ledger, write_evidence_ledger
from presence_rx.build_mvp_dashboard import build_dashboard, write_dashboard
from presence_rx.build_value_metrics import build_value_added_metrics, write_value_added_metrics
from presence_rx.build_verdict import build_presence_verdict, write_presence_verdict
from presence_rx.classify_gaps import build_gap_classification, write_gap_classification
from presence_rx.contracts import (
    GeminiAnalysis,
    Manifest,
    PipelineFunnel,
    StudySsot,
    TavilyEvidence,
)
from presence_rx.ingest_peec import (
    update_hero_cards_post_pipeline,
    update_manifest_post_pipeline,
    update_pipeline_funnel_post_pipeline,
)
from presence_rx.plan_prescriptions import build_prescription_plan, write_prescription_plan
from presence_rx.synthesize_gemini_analysis import (
    build_synthetic_gemini_analysis,
    write_synthetic_gemini_analysis,
)

console = Console()

REPORT_NAME = "mvp_run_report.json"


def _read_optional(path: Path, model):
    if not path.exists():
        return None
    return model.model_validate_json(path.read_text())


def run_mvp(
    *,
    study_path: Path,
    manifest_path: Path,
    generated_dir: Path,
    dashboard_dir: Path,
    allow_synthetic_gemini: bool,
) -> dict[str, object]:
    study = StudySsot.model_validate_json(study_path.read_text())
    manifest = Manifest.model_validate_json(manifest_path.read_text())

    gemini_path = generated_dir / "gemini_analysis.json"
    tavily_path = generated_dir / "tavily_evidence.json"
    gemini = _read_optional(gemini_path, GeminiAnalysis)
    gemini_mode = "live_or_existing"
    if gemini is None and allow_synthetic_gemini:
        gemini = build_synthetic_gemini_analysis(study, manifest)
        write_synthetic_gemini_analysis(gemini, generated_dir)
        gemini_mode = "synthetic_quota_fallback"

    tavily = _read_optional(tavily_path, TavilyEvidence)

    classification = build_gap_classification(
        study,
        manifest,
        gemini=gemini,
        tavily=tavily,
    )
    classification_path = write_gap_classification(classification, generated_dir)

    ledger = build_evidence_ledger(study, manifest, classification)
    ledger_path = write_evidence_ledger(ledger, generated_dir)

    metrics = build_value_added_metrics(
        study,
        manifest,
        classification=classification,
        gemini=gemini,
        tavily=tavily,
    )
    metrics_path = write_value_added_metrics(metrics, generated_dir)

    landscape = build_competitor_landscape(
        study,
        manifest,
        classification=classification,
        tavily=tavily,
    )
    landscape_path = write_competitor_landscape(landscape, generated_dir)

    dashboard_path = write_dashboard(
        build_dashboard(
            study,
            classification=classification,
            ledger=ledger,
            metrics=metrics,
            landscape=landscape,
            tavily=tavily,
            prescription=build_prescription_plan(study, manifest),
            gemini=gemini,
        ),
        dashboard_dir,
    )

    # --- Post-pipeline artifact refresh ---
    prescription = build_prescription_plan(study, manifest)
    updated_manifest = update_manifest_post_pipeline(
        manifest,
        tavily=tavily,
        gemini=gemini,
        classification=classification,
        ledger=ledger,
        prescription=prescription,
    )
    manifest_out = generated_dir / "manifest.json"
    manifest_out.write_text(
        json.dumps(updated_manifest.model_dump(mode="json"), indent=2) + "\n"
    )

    updated_hero = update_hero_cards_post_pipeline(
        classification=classification, ledger=ledger,
    )
    hero_out = generated_dir / "hero_cards.json"
    hero_out.write_text(
        json.dumps(updated_hero.model_dump(mode="json"), indent=2) + "\n"
    )

    funnel_path = generated_dir / "pipeline_funnel.json"
    if funnel_path.exists():
        old_funnel = PipelineFunnel.model_validate_json(funnel_path.read_text())
    else:
        old_funnel = PipelineFunnel(stages=[])
    updated_funnel = update_pipeline_funnel_post_pipeline(
        old_funnel, classification=classification, ledger=ledger, prescription=prescription,
    )
    funnel_path.write_text(
        json.dumps(updated_funnel.model_dump(mode="json"), indent=2) + "\n"
    )

    # Write prescription plan
    prescription_path = write_prescription_plan(prescription, generated_dir)

    # --- Generate markdown deliverables ---
    verdict_content = build_presence_verdict(
        study, updated_manifest,
        classification=classification, ledger=ledger,
        metrics=metrics, gemini=gemini,
    )
    verdict_path = write_presence_verdict(verdict_content, generated_dir)

    action_brief_content = build_action_brief(
        study, updated_manifest,
        classification=classification, ledger=ledger,
        metrics=metrics, prescription=prescription,
    )
    action_brief_path = write_action_brief(action_brief_content, generated_dir)

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "mvp_built",
        "peec_source": "verified_docs_grounded_snapshot",
        "peec_mcp_callable_in_this_runtime": False,
        "gemini_mode": gemini_mode,
        "tavily_mode": "live_or_existing" if tavily is not None else "unavailable",
        "artifacts": {
            "gap_classification": str(classification_path),
            "evidence_ledger": str(ledger_path),
            "value_added_metrics": str(metrics_path),
            "competitor_landscape": str(landscape_path),
            "dashboard": str(dashboard_path),
            "prescription_plan": str(prescription_path),
            "presence_verdict": str(verdict_path),
            "action_brief": str(action_brief_path),
        },
        "counts": {
            "study_rows": len(study.rows),
            "classified_gaps": classification.summary.classified_gaps,
            "ledger_claims": len(ledger.claims),
            "blocked_claims": len(ledger.blocked_claims),
            "tavily_sources": tavily.summary.sources if tavily is not None else 0,
            "average_opportunity_score": metrics.summary.average_opportunity_score,
        },
        "review_notes": [
            "Review-only artifacts are gitignored.",
            "Dashboard avoids raw Tavily snippets and Gemini prose.",
            "Replace synthetic Gemini artifact with a live Gemini run before public claims.",
        ],
    }
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    (dashboard_dir / REPORT_NAME).write_text(json.dumps(report, indent=2) + "\n")
    return report


def main(
    study: Annotated[Path, typer.Option("--study")] = Path("data/generated/study_ssot.json"),
    manifest: Annotated[Path, typer.Option("--manifest")] = Path("data/generated/manifest.json"),
    generated_dir: Annotated[Path, typer.Option("--generated-dir")] = Path("data/generated"),
    dashboard_dir: Annotated[Path, typer.Option("--dashboard-dir")] = Path("artifacts/local"),
    allow_synthetic_gemini: Annotated[
        bool,
        typer.Option(
            "--allow-synthetic-gemini",
            help="Use deterministic Gemini-shaped labels if live Gemini is unavailable.",
        ),
    ] = True,
) -> None:
    report = run_mvp(
        study_path=study,
        manifest_path=manifest,
        generated_dir=generated_dir,
        dashboard_dir=dashboard_dir,
        allow_synthetic_gemini=allow_synthetic_gemini,
    )
    console.print("[green]MVP built[/green]")
    console.print(json.dumps(report["counts"], indent=2))


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
