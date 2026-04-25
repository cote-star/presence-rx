"""Run gated Tavily public-evidence enrichment over Peec blind-spot rows."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol
from urllib.parse import urlsplit, urlunsplit

import typer
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

from presence_rx.contracts import (
    Manifest,
    StudyRow,
    StudySsot,
    TavilyEvidence,
    TavilyFinding,
    TavilyMetadata,
    TavilySource,
    TavilySummary,
)
from presence_rx.ingest_peec import parse_generated_at, slugify

console = Console()

OUTPUT_NAME = "tavily_evidence.json"
QUERY_TEMPLATE_VERSION = "tavily_blind_spot:v1"
SDK_PACKAGE = "tavily-python"
SEARCH_DEPTH: Literal["basic"] = "basic"
MAX_RESULTS = 5
QUERY_TIMEOUT_SECONDS = 30
INCLUDE_RAW_CONTENT = False
INCLUDE_ANSWER = False
INCLUDE_IMAGES = False
INCLUDE_USAGE = True
MAX_SNIPPET_CHARS = 500


class TavilySearchResult(BaseModel):
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    content: str = Field(min_length=1)
    score: float | None = Field(default=None, ge=0)


class TavilyResponsePayload(BaseModel):
    results: list[TavilySearchResult] = Field(default_factory=list)
    response_time: float | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    usage: dict[str, Any] | None = None


@dataclass(frozen=True)
class TavilyQuery:
    row: StudyRow
    query_ref: str
    query: str
    source_role: Literal["target", "competitor"]


@dataclass(frozen=True)
class TavilyClientResponse:
    payload: dict[str, Any]


class TavilyClient(Protocol):
    def search(
        self,
        *,
        query: str,
        search_depth: str,
        max_results: int,
        timeout: int,
    ) -> TavilyClientResponse:
        """Return one Tavily search response."""


class TavilyEnrichmentError(RuntimeError):
    """Raised when a Tavily run fails before a complete artifact can be written."""


class TavilyApiClient:
    def __init__(self, api_key: str) -> None:
        from tavily import TavilyClient as SdkTavilyClient

        self._client = SdkTavilyClient(api_key=api_key)

    def search(
        self,
        *,
        query: str,
        search_depth: str,
        max_results: int,
        timeout: int,
    ) -> TavilyClientResponse:
        response = self._client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            # No domain filters in Step 6; the open-web artifact is gitignored
            # and every snippet stays raw until human review.
            include_raw_content=INCLUDE_RAW_CONTENT,
            include_answer=INCLUDE_ANSWER,
            include_images=INCLUDE_IMAGES,
            include_usage=INCLUDE_USAGE,
            timeout=timeout,
        )
        return TavilyClientResponse(payload=response)


def _blind_spot_rows(study: StudySsot) -> list[StudyRow]:
    return [row for row in study.rows if row.gap_type is not None]


def _study_row_ref(row: StudyRow) -> str:
    return f"study_ssot:row:{row.cluster_id.removeprefix('cluster:')}"


def _topic_ref(row: StudyRow) -> str:
    return f"peec:topic:{slugify(row.cluster_label)}"


def _finding_id(row: StudyRow) -> str:
    return f"tavily:evidence:{slugify(row.cluster_label)}:v1"


def _evidence_refs(row: StudyRow, manifest: Manifest) -> list[str]:
    refs = [manifest.peec_snapshot_id, _topic_ref(row), _study_row_ref(row), _finding_id(row)]
    return list(dict.fromkeys(refs))


def _target_query(row: StudyRow, manifest: Manifest) -> str:
    return f'"{manifest.brand}" "{row.cluster_label}" reviews proof'


def _competitor_query(row: StudyRow) -> str:
    competitor = row.visibility_competitor_owner or "leading competitor"
    return f'"{competitor}" "{row.cluster_label}" reviews proof'


def build_queries(study: StudySsot, manifest: Manifest) -> list[TavilyQuery]:
    queries: list[TavilyQuery] = []
    for row in _blind_spot_rows(study):
        row_slug = row.cluster_id.removeprefix("cluster:")
        queries.append(
            TavilyQuery(
                row=row,
                query_ref=f"row:{row_slug}:target_query",
                query=_target_query(row, manifest),
                source_role="target",
            )
        )
        queries.append(
            TavilyQuery(
                row=row,
                query_ref=f"row:{row_slug}:competitor_query",
                query=_competitor_query(row),
                source_role="competitor",
            )
        )
    return queries


def canonicalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), path, "", ""))


def _domain(url: str) -> str:
    return urlsplit(url).netloc.lower()


def _truncate_snippet(content: str) -> str:
    cleaned = " ".join(content.split())
    if len(cleaned) <= MAX_SNIPPET_CHARS:
        return cleaned
    return cleaned[: MAX_SNIPPET_CHARS - 3].rstrip() + "..."


def _parse_response(payload: dict[str, Any], query: TavilyQuery) -> TavilyResponsePayload:
    try:
        return TavilyResponsePayload.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Tavily response failed schema validation for {query.query_ref}") from exc


def _credits_from_response(payload: TavilyResponsePayload) -> float:
    if payload.cost is not None:
        return payload.cost
    usage = payload.usage or {}
    credits = usage.get("credits") or usage.get("credit_cost") or usage.get("api_credits")
    return float(credits or 0)


def _source_from_result(
    result: TavilySearchResult,
    query: TavilyQuery,
    source_index: int,
) -> TavilySource:
    canonical_url = canonicalize_url(result.url)
    return TavilySource(
        source_ref=f"tavily:source:{query.query_ref}:{source_index:02d}",
        title=result.title,
        url=canonical_url,
        domain=_domain(canonical_url),
        snippet=_truncate_snippet(result.content),
        score=result.score,
        query_ref=query.query_ref,
        source_role=query.source_role,
        snippet_review_status="raw",
    )


def _support_from_sources(
    sources: list[TavilySource],
) -> Literal["supports", "conflicts", "insufficient"]:
    target_count = sum(1 for source in sources if source.source_role == "target")
    competitor_count = sum(1 for source in sources if source.source_role == "competitor")
    if target_count and competitor_count:
        return "supports"
    if competitor_count and not target_count:
        return "supports"
    if target_count and not competitor_count:
        return "conflicts"
    return "insufficient"


def _summary_for_sources(sources: list[TavilySource]) -> str:
    target_count = sum(1 for source in sources if source.source_role == "target")
    competitor_count = sum(1 for source in sources if source.source_role == "competitor")
    return (
        f"Tavily returned {target_count} target-role sources and "
        f"{competitor_count} competitor-role sources for this blind spot."
    )


def _finding_from_sources(
    row: StudyRow,
    manifest: Manifest,
    target_query: str,
    competitor_query: str,
    sources: list[TavilySource],
) -> TavilyFinding:
    if row.gap_type is None:
        raise ValueError(f"cannot enrich row without gap_type: {row.cluster_id}")
    support = _support_from_sources(sources)
    return TavilyFinding(
        finding_id=_finding_id(row),
        cluster_id=row.cluster_id,
        cluster_label=row.cluster_label,
        gap_type=row.gap_type,
        source_of_record="tavily",
        target_query=target_query,
        competitor_query=competitor_query,
        public_proof_support=support,
        proof_gap_summary=_summary_for_sources(sources),
        rationale=("Raw public-web snippets support proof-gap analysis only after human review."),
        evidence_refs=_evidence_refs(row, manifest),
        sources=sources,
    )


def build_tavily_evidence(
    study: StudySsot,
    manifest: Manifest,
    *,
    client: TavilyClient,
    generated_at: datetime | None = None,
    run_mode: Literal["live", "test"] = "test",
    max_results: int = MAX_RESULTS,
    query_timeout_seconds: int = QUERY_TIMEOUT_SECONDS,
) -> TavilyEvidence:
    queries = build_queries(study, manifest)
    grouped_sources: dict[str, list[TavilySource]] = {
        row.cluster_id: [] for row in _blind_spot_rows(study)
    }
    row_queries: dict[str, dict[str, str]] = {
        row.cluster_id: {
            "target": _target_query(row, manifest),
            "competitor": _competitor_query(row),
        }
        for row in _blind_spot_rows(study)
    }
    successful_query_count = 0
    response_time_seconds = 0.0
    api_credits_used = 0.0

    for query in queries:
        try:
            response = client.search(
                query=query.query,
                search_depth=SEARCH_DEPTH,
                max_results=max_results,
                timeout=query_timeout_seconds,
            )
            payload = _parse_response(response.payload, query)
            successful_query_count += 1
            response_time_seconds += payload.response_time or 0
            api_credits_used += _credits_from_response(payload)
            existing = len(grouped_sources[query.row.cluster_id])
            grouped_sources[query.row.cluster_id].extend(
                _source_from_result(result, query, existing + index + 1)
                for index, result in enumerate(payload.results[:max_results])
            )
        except Exception as exc:
            raise TavilyEnrichmentError(
                f"Tavily enrichment failed after {successful_query_count} of {len(queries)} "
                f"queries; failed_query_ref={query.query_ref}; output not written"
            ) from exc

    findings = [
        _finding_from_sources(
            row,
            manifest,
            target_query=row_queries[row.cluster_id]["target"],
            competitor_query=row_queries[row.cluster_id]["competitor"],
            sources=grouped_sources[row.cluster_id],
        )
        for row in _blind_spot_rows(study)
    ]

    metadata = TavilyMetadata(
        generated_at=generated_at or manifest.generated_at,
        source_manifest_ref=manifest.peec_snapshot_id,
        peec_snapshot_id=manifest.peec_snapshot_id,
        run_mode=run_mode,
        sdk_package=SDK_PACKAGE,
        sdk_version=version(SDK_PACKAGE),
        query_template_version=QUERY_TEMPLATE_VERSION,
        search_depth=SEARCH_DEPTH,
        max_results=max_results,
        query_timeout_seconds=query_timeout_seconds,
        include_raw_content=INCLUDE_RAW_CONTENT,
        include_answer=INCLUDE_ANSWER,
        include_images=INCLUDE_IMAGES,
        include_usage=INCLUDE_USAGE,
        request_count=len(queries),
        successful_query_count=successful_query_count,
        failed_query_count=0,
        failed_query_ref=None,
        response_time_seconds=response_time_seconds,
        api_credits_used=api_credits_used,
    )

    return TavilyEvidence(
        metadata=metadata,
        summary=TavilySummary(
            analyzed_rows=len(findings),
            planned_queries=metadata.request_count,
            sources=sum(len(finding.sources) for finding in findings),
            supported_findings=sum(
                1 for finding in findings if finding.public_proof_support == "supports"
            ),
            conflicted_findings=sum(
                1 for finding in findings if finding.public_proof_support == "conflicts"
            ),
            insufficient_findings=sum(
                1 for finding in findings if finding.public_proof_support == "insufficient"
            ),
        ),
        findings=findings,
    )


def write_tavily_evidence(evidence: TavilyEvidence, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(evidence.model_dump(mode="json"), indent=2) + "\n")
    return path


def print_query_preview(
    queries: list[TavilyQuery],
    *,
    max_results: int,
    query_timeout_seconds: int,
) -> None:
    console.print("[yellow]Tavily live call preview[/yellow]")
    console.print(f"search_depth: {SEARCH_DEPTH}")
    console.print(f"max_results: {max_results}")
    console.print(f"query_timeout_seconds: {query_timeout_seconds}")
    console.print(f"query_template_version: {QUERY_TEMPLATE_VERSION}")
    console.print(f"estimated_request_count: {len(queries)}")
    for query in queries:
        console.print(f"- {query.query_ref} [{query.source_role}]: {query.query}")


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
        typer.Option("--out", help="Directory for tavily_evidence.json."),
    ] = Path("data/generated"),
    live: Annotated[
        bool,
        typer.Option("--live", help="Allow a live Tavily API run when billing is confirmed."),
    ] = False,
    yes_confirm_billing: Annotated[
        bool,
        typer.Option(
            "--yes-confirm-billing",
            help="Required with --live before any paid Tavily API request is made.",
        ),
    ] = False,
    max_results: Annotated[
        int,
        typer.Option("--max-results", help="Maximum Tavily results per query."),
    ] = MAX_RESULTS,
    query_timeout_seconds: Annotated[
        int,
        typer.Option("--query-timeout-seconds", help="Timeout per Tavily query."),
    ] = QUERY_TIMEOUT_SECONDS,
    generated_at: Annotated[
        str | None,
        typer.Option("--generated-at", help="Optional ISO timestamp override."),
    ] = None,
) -> None:
    """Preview or run gated Tavily public-evidence enrichment."""

    load_dotenv()
    if max_results < 1 or max_results > 20:
        console.print("[red]Invalid --max-results:[/red] expected a value from 1 to 20.")
        raise typer.Exit(1)
    if query_timeout_seconds < 1:
        console.print("[red]Invalid --query-timeout-seconds:[/red] expected a positive value.")
        raise typer.Exit(1)

    study_artifact = StudySsot.model_validate_json(study.read_text())
    manifest_artifact = Manifest.model_validate_json(manifest.read_text())
    queries = build_queries(study_artifact, manifest_artifact)

    if not live or not yes_confirm_billing:
        print_query_preview(
            queries,
            max_results=max_results,
            query_timeout_seconds=query_timeout_seconds,
        )
        if live and not yes_confirm_billing:
            console.print(
                "[yellow]No Tavily request sent.[/yellow] Re-run with "
                "--yes-confirm-billing to confirm the paid network boundary."
            )
        else:
            console.print("[yellow]Dry run only.[/yellow] Add --live and --yes-confirm-billing.")
        return

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        console.print("[red]Missing TAVILY_API_KEY for confirmed live Tavily run.[/red]")
        raise typer.Exit(1)

    resolved_generated_at = parse_generated_at(generated_at) if generated_at else None
    client = TavilyApiClient(api_key=api_key)
    try:
        evidence = build_tavily_evidence(
            study_artifact,
            manifest_artifact,
            client=client,
            generated_at=resolved_generated_at,
            run_mode="live",
            max_results=max_results,
            query_timeout_seconds=query_timeout_seconds,
        )
    except Exception as exc:
        console.print(f"[red]Tavily enrichment failed before writing output:[/red] {exc}")
        raise typer.Exit(1) from exc

    path = write_tavily_evidence(evidence, out)
    console.print(f"[green]wrote[/green] {path}")
    console.print(
        "[yellow]Review before tracking:[/yellow] this file is gitignored until "
        "docs/PUBLIC_SAFETY_CHECKLIST.md is applied by a human."
    )


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
