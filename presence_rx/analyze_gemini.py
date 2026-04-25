"""Run gated Gemini analysis over Peec blind-spot rows."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Literal, Protocol

import typer
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

from presence_rx.contracts import (
    GeminiAnalysis,
    GeminiFinding,
    GeminiMetadata,
    GeminiSummary,
    Manifest,
    StudyRow,
    StudySsot,
)
from presence_rx.ingest_peec import parse_generated_at, slugify

console = Console()

OUTPUT_NAME = "gemini_analysis.json"
PROMPT_TEMPLATE_VERSION = "gemini_blind_spot_analysis:v1"
TEMPERATURE = 0.0
SDK_PACKAGE = "google-genai"

PROMPT_TEMPLATE = """\
You are analyzing public-safe Peec visibility data for a hackathon demo.

Return only valid JSON with this exact shape:
{{
  "perception_themes": ["short theme", "short theme"],
  "missing_associations": ["short missing association"],
  "competitor_association": "short public-safe competitor association or null",
  "safe_scenario_wording": "one cautious sentence suitable for diagnostics",
  "gap_type_support": "supports|conflicts|insufficient",
  "rationale": "one cautious sentence explaining the support/conflict"
}}

Rules:
- Use only the input fields below.
- Do not claim causality, private data access, sales impact, or consumer truth.
- Do not invent exact prompt text or web evidence.
- Treat Peec visibility metrics as the source of record for visibility.
- Keep competitor wording factual, cautious, and non-defamatory.

Input row:
- brand: {brand}
- competitors in manifest: {competitors}
- Peec snapshot id: {peec_snapshot_id}
- topic cluster id: {cluster_id}
- topic label: {cluster_label}
- provisional gap_type: {gap_type}
- provisional gap rationale: {gap_type_rationale}
- target visibility share: {visibility_target_share}
- target average position: {visibility_target_avg_position}
- competitor owner from Peec seed: {visibility_competitor_owner}
- evidence refs: {evidence_refs}
"""


class GeminiResponsePayload(BaseModel):
    perception_themes: list[str] = Field(min_length=1)
    missing_associations: list[str] = Field(min_length=1)
    competitor_association: str | None = None
    safe_scenario_wording: str = Field(min_length=1)
    gap_type_support: Literal["supports", "conflicts", "insufficient"]
    rationale: str = Field(min_length=1)


@dataclass(frozen=True)
class GeminiRequest:
    row: StudyRow
    prompt: str


@dataclass(frozen=True)
class GeminiClientResponse:
    text: str
    response_model_version: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class GeminiClient(Protocol):
    def analyze(self, *, model: str, prompt: str) -> GeminiClientResponse:
        """Return one structured Gemini response for one prompt."""


class GeminiAnalysisError(RuntimeError):
    """Raised when a Gemini run fails before a complete artifact can be written."""


class GoogleGeminiClient:
    def __init__(self, api_key: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)

    def analyze(self, *, model: str, prompt: str) -> GeminiClientResponse:
        from google.genai import types

        response = self._client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=TEMPERATURE,
                response_mime_type="application/json",
            ),
        )
        usage = getattr(response, "usage_metadata", None)
        return GeminiClientResponse(
            text=response.text or "",
            response_model_version=(
                getattr(response, "model_version", None)
                or getattr(response, "model", None)
                or getattr(response, "model_name", None)
            ),
            input_tokens=int(getattr(usage, "prompt_token_count", 0) or 0),
            output_tokens=int(getattr(usage, "candidates_token_count", 0) or 0),
        )

    def close(self) -> None:
        close = getattr(self._client, "close", None)
        if close:
            close()


def _blind_spot_rows(study: StudySsot) -> list[StudyRow]:
    return [row for row in study.rows if row.gap_type is not None]


def _study_row_ref(row: StudyRow) -> str:
    return f"study_ssot:row:{row.cluster_id.removeprefix('cluster:')}"


def _topic_ref(row: StudyRow) -> str:
    return f"peec:topic:{slugify(row.cluster_label)}"


def _finding_id(row: StudyRow) -> str:
    return f"gemini:analysis:{slugify(row.cluster_label)}:v1"


def _evidence_refs(row: StudyRow, manifest: Manifest) -> list[str]:
    refs = [manifest.peec_snapshot_id, _topic_ref(row), _study_row_ref(row), _finding_id(row)]
    return list(dict.fromkeys(refs))


def build_requests(study: StudySsot, manifest: Manifest) -> list[GeminiRequest]:
    return [
        GeminiRequest(
            row=row,
            prompt=PROMPT_TEMPLATE.format(
                brand=manifest.brand,
                competitors=", ".join(manifest.competitors),
                peec_snapshot_id=manifest.peec_snapshot_id,
                cluster_id=row.cluster_id,
                cluster_label=row.cluster_label,
                gap_type=row.gap_type,
                gap_type_rationale=row.gap_type_rationale,
                visibility_target_share=row.visibility_target_share,
                visibility_target_avg_position=row.visibility_target_avg_position,
                visibility_competitor_owner=row.visibility_competitor_owner,
                evidence_refs=", ".join(row.evidence_refs),
            ),
        )
        for row in _blind_spot_rows(study)
    ]


def _parse_json_response(text: str, row: StudyRow) -> GeminiResponsePayload:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini returned invalid JSON for {row.cluster_id}: {exc}") from exc
    try:
        return GeminiResponsePayload.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Gemini response failed schema validation for {row.cluster_id}") from exc


def _finding_from_response(
    row: StudyRow,
    manifest: Manifest,
    payload: GeminiResponsePayload,
) -> GeminiFinding:
    if row.gap_type is None:
        raise ValueError(f"cannot analyze row without gap_type: {row.cluster_id}")
    return GeminiFinding(
        finding_id=_finding_id(row),
        cluster_id=row.cluster_id,
        cluster_label=row.cluster_label,
        gap_type=row.gap_type,
        source_of_record="gemini",
        perception_themes=payload.perception_themes,
        missing_associations=payload.missing_associations,
        competitor_association=payload.competitor_association,
        safe_scenario_wording=payload.safe_scenario_wording,
        gap_type_support=payload.gap_type_support,
        rationale=payload.rationale,
        evidence_refs=_evidence_refs(row, manifest),
    )


def build_gemini_analysis(
    study: StudySsot,
    manifest: Manifest,
    *,
    model: str,
    client: GeminiClient,
    generated_at: datetime | None = None,
    run_mode: Literal["live", "test"] = "test",
) -> GeminiAnalysis:
    requests = build_requests(study, manifest)
    findings: list[GeminiFinding] = []
    response_model_versions: list[str] = []
    input_tokens = 0
    output_tokens = 0

    for request in requests:
        try:
            response = client.analyze(model=model, prompt=request.prompt)
            if not response.text.strip():
                raise ValueError(f"Gemini returned empty text for {request.row.cluster_id}")
            payload = _parse_json_response(response.text, request.row)
            findings.append(_finding_from_response(request.row, manifest, payload))
            if response.response_model_version:
                response_model_versions.append(response.response_model_version)
            input_tokens += response.input_tokens
            output_tokens += response.output_tokens
        except Exception as exc:
            raise GeminiAnalysisError(
                f"Gemini analysis failed after {len(findings)} of {len(requests)} rows; "
                f"failed_row={request.row.cluster_id}; output not written"
            ) from exc

    return GeminiAnalysis(
        metadata=GeminiMetadata(
            generated_at=generated_at or manifest.generated_at,
            source_manifest_ref=manifest.peec_snapshot_id,
            peec_snapshot_id=manifest.peec_snapshot_id,
            run_mode=run_mode,
            requested_model=model,
            response_model_version=", ".join(sorted(set(response_model_versions))) or None,
            prompt_template_version=PROMPT_TEMPLATE_VERSION,
            temperature=TEMPERATURE,
            request_count=len(requests),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            sdk_package=SDK_PACKAGE,
            sdk_version=version(SDK_PACKAGE),
        ),
        summary=GeminiSummary(
            analyzed_rows=len(findings),
            supported_gap_types=sum(
                1 for finding in findings if finding.gap_type_support == "supports"
            ),
            conflicted_gap_types=sum(
                1 for finding in findings if finding.gap_type_support == "conflicts"
            ),
            insufficient_gap_types=sum(
                1 for finding in findings if finding.gap_type_support == "insufficient"
            ),
        ),
        findings=findings,
    )


def write_gemini_analysis(analysis: GeminiAnalysis, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(analysis.model_dump(mode="json"), indent=2) + "\n")
    return path


def print_request_preview(requests: list[GeminiRequest], model: str) -> None:
    console.print("[yellow]Gemini live call preview[/yellow]")
    console.print(f"model: {model}")
    console.print(f"temperature: {TEMPERATURE}")
    console.print(f"prompt_template_version: {PROMPT_TEMPLATE_VERSION}")
    console.print(f"estimated_request_count: {len(requests)}")
    for request in requests:
        prompt_preview = " ".join(request.prompt.split())[:260]
        console.print(f"- {request.row.cluster_id}: {prompt_preview}...")


def _resolve_model(model: str | None) -> str | None:
    return model or os.environ.get("GEMINI_MODEL")


def main(
    study: Annotated[
        Path,
        typer.Option("--study", help="Path to Step 2 study_ssot.json."),
    ] = Path("data/generated/study_ssot.json"),
    manifest: Annotated[
        Path,
        typer.Option("--manifest", help="Path to Step 2 manifest.json."),
    ] = Path("data/generated/manifest.json"),
    out: Annotated[
        Path,
        typer.Option("--out", help="Directory for gemini_analysis.json."),
    ] = Path("data/generated"),
    model: Annotated[
        str | None,
        typer.Option("--model", help="Gemini model to call. May also use GEMINI_MODEL."),
    ] = None,
    live: Annotated[
        bool,
        typer.Option("--live", help="Allow a live Gemini API run when billing is confirmed."),
    ] = False,
    yes_confirm_billing: Annotated[
        bool,
        typer.Option(
            "--yes-confirm-billing",
            help="Required with --live before any paid Gemini API request is made.",
        ),
    ] = False,
    generated_at: Annotated[
        str | None,
        typer.Option("--generated-at", help="Optional ISO timestamp override."),
    ] = None,
) -> None:
    """Preview or run gated Gemini analysis over Peec blind-spot rows."""

    load_dotenv()
    resolved_model = _resolve_model(model)
    if not resolved_model:
        console.print("[red]Missing model:[/red] pass --model or set GEMINI_MODEL.")
        raise typer.Exit(1)

    study_artifact = StudySsot.model_validate_json(study.read_text())
    manifest_artifact = Manifest.model_validate_json(manifest.read_text())
    requests = build_requests(study_artifact, manifest_artifact)

    if not live or not yes_confirm_billing:
        print_request_preview(requests, resolved_model)
        if live and not yes_confirm_billing:
            console.print(
                "[yellow]No Gemini request sent.[/yellow] Re-run with "
                "--yes-confirm-billing to confirm the paid network boundary."
            )
        else:
            console.print("[yellow]Dry run only.[/yellow] Add --live and --yes-confirm-billing.")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[red]Missing GEMINI_API_KEY for confirmed live Gemini run.[/red]")
        raise typer.Exit(1)

    resolved_generated_at = parse_generated_at(generated_at) if generated_at else None
    client = GoogleGeminiClient(api_key=api_key)
    try:
        analysis = build_gemini_analysis(
            study_artifact,
            manifest_artifact,
            model=resolved_model,
            client=client,
            generated_at=resolved_generated_at,
            run_mode="live",
        )
    except Exception as exc:
        console.print(f"[red]Gemini analysis failed before writing output:[/red] {exc}")
        raise typer.Exit(1) from exc
    finally:
        client.close()

    path = write_gemini_analysis(analysis, out)
    console.print(f"[green]wrote[/green] {path}")
    console.print(
        "[yellow]Review before tracking:[/yellow] this file is gitignored until "
        "docs/PUBLIC_SAFETY_CHECKLIST.md is applied by a human."
    )


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
