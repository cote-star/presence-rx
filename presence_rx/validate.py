"""Command-line validation for Presence Rx generated artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console

from presence_rx.contracts import ARTIFACT_MODELS, validate_payload

app = typer.Typer(help="Validate Presence Rx JSON artifacts against Step 1 contracts.")
console = Console()


def _infer_artifact_type(path: Path) -> str:
    name = path.name.lower()
    stem = path.stem.lower()
    if name == "evidence_ledger.json":
        return "evidence_ledger"
    if stem in ARTIFACT_MODELS:
        return stem
    raise typer.BadParameter(
        "Could not infer artifact type from filename. "
        "Pass --artifact-type with one of: "
        + ", ".join(sorted(ARTIFACT_MODELS))
    )


@app.command()
def validate(
    path: Annotated[Path, typer.Argument(help="Path to a JSON artifact.")],
    artifact_type: Annotated[
        str | None,
        typer.Option(
            "--artifact-type",
            "-t",
            help="Artifact contract to use. Inferred from filename when omitted.",
        ),
    ] = None,
) -> None:
    """Validate one JSON artifact."""

    resolved_type = artifact_type or _infer_artifact_type(path)
    try:
        payload = json.loads(path.read_text())
        validate_payload(payload, resolved_type)
    except FileNotFoundError:
        console.print(f"[red]Missing file:[/red] {path}")
        raise typer.Exit(1) from None
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON:[/red] {path}: {exc}")
        raise typer.Exit(1) from None
    except (ValidationError, ValueError) as exc:
        console.print(f"[red]Validation failed for {resolved_type}:[/red]")
        console.print(str(exc))
        raise typer.Exit(1) from None

    console.print(f"[green]OK[/green] {path} matches {resolved_type}")


if __name__ == "__main__":
    app()
