import re
import subprocess
from pathlib import Path


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(path) for path in result.stdout.splitlines()]


def test_no_non_partner_agent_traces_in_tracked_files() -> None:
    lower_forbidden = [
        "clau" + "de",
        "co" + "dex",
        "an" + "thropic",
        ".clau" + "de",
        ".agent-" + "chorus",
        "compo" + "ser",
    ]
    exact_forbidden = [
        "Cur" + "sor",
        "Com" + "poser",
    ]

    hits: list[str] = []
    for path in _tracked_files():
        if not path.is_file():
            continue
        content = path.read_text(errors="ignore")
        content_lower = content.lower()
        for term in lower_forbidden:
            if term in content_lower:
                hits.append(f"{path}: {term}")
        for term in exact_forbidden:
            if re.search(rf"\b{re.escape(term)}\b", content):
                hits.append(f"{path}: {term}")

    assert hits == []
