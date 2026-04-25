"""Brand configuration contract and loader for multi-brand pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class BrandConfig(BaseModel):
    """Reusable brand configuration for the Presence Rx pipeline."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1)
    brand_name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    peec_project_id: str = Field(min_length=1)
    competitors: list[str] = Field(min_length=1)
    audience_segments: list[str] = Field(default_factory=list)
    buying_journey_stages: list[str] = Field(default_factory=list)
    priority_topics: list[str] = Field(default_factory=list)
    known_market_tension: str = Field(min_length=1)
    channels_to_activate: list[str] = Field(default_factory=list)


def load_brand_config(case_id: str, config_dir: Path = CONFIG_DIR) -> BrandConfig:
    """Load a brand config from config/{case_id}.json."""
    path = config_dir / f"{case_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Brand config not found: {path}")
    return BrandConfig.model_validate_json(path.read_text())


def list_brands(config_dir: Path = CONFIG_DIR) -> list[str]:
    """List registered brand case IDs from config/brands.json."""
    path = config_dir / "brands.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data.get("brands", [])
