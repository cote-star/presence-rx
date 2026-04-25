"""Generate a Peec-styled local MVP dashboard from Presence Rx artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    CompetitorLandscape,
    EvidenceLedger,
    GapClassification,
    GeminiAnalysis,
    PrescriptionPlan,
    StudySsot,
    TavilyEvidence,
    ValueAddedMetrics,
)

console = Console()

OUTPUT_NAME = "mvp_dashboard.html"


def _read_optional(path: Path | None, model):
    if path is None or not path.exists():
        return None
    return model.model_validate_json(path.read_text())


def _json_script(name: str, value: object) -> str:
    payload = json.dumps(value, default=str).replace("</", "<\\/")
    return (
        f'<script id="{name}" type="application/json">'
        + payload
        + "</script>"
    )


def _html(
    study: StudySsot,
    classification: GapClassification | None,
    ledger: EvidenceLedger | None,
    metrics: ValueAddedMetrics | None,
    landscape: CompetitorLandscape | None,
    tavily: TavilyEvidence | None,
    prescription: PrescriptionPlan | None = None,
    gemini: GeminiAnalysis | None = None,
) -> str:
    tavily_public_summary = (
        {
            "summary": tavily.summary.model_dump(mode="json"),
            "metadata": {
                "run_mode": tavily.metadata.run_mode,
                "search_depth": tavily.metadata.search_depth,
                "request_count": tavily.metadata.request_count,
                "successful_query_count": tavily.metadata.successful_query_count,
                "failed_query_count": tavily.metadata.failed_query_count,
            },
        }
        if tavily
        else None
    )
    data = {
        "study": study.model_dump(mode="json"),
        "classification": classification.model_dump(mode="json") if classification else None,
        "ledger": ledger.model_dump(mode="json") if ledger else None,
        "metrics": metrics.model_dump(mode="json") if metrics else None,
        "landscape": landscape.model_dump(mode="json") if landscape else None,
        "tavily": tavily_public_summary,
        "prescription": prescription.model_dump(mode="json") if prescription else None,
        "gemini": {
            "findings": [f.model_dump(mode="json") for f in gemini.findings],
            "summary": gemini.summary.model_dump(mode="json"),
        } if gemini else None,
    }
    return (
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Presence Rx - MVP Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --peec-bg: #FFFFFF;
      --peec-surface: #FDFDFD;
      --peec-fg: #171717;
      --peec-fg-muted: rgba(23, 23, 23, 0.6);
      --peec-fg-subtle: rgba(23, 23, 23, 0.5);
      --peec-hover: rgba(23, 23, 23, 0.08);
      --peec-tint: rgba(23, 23, 23, 0.04);
      --peec-hairline: rgba(23, 23, 23, 0.08);
      --peec-font: "Geist Variable", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --peec-text-xs: 12px;
      --peec-text-sm: 13px;
      --peec-text-base: 14px;
      --peec-text-lg: 16px;
      --peec-text-xl: 20px;
      --peec-tracking: -0.025em;
      --peec-radius-sm: 6px;
      --peec-radius-md: 8px;
      --peec-radius-lg: 10px;
      --peec-radius-xl: 12px;
      --peec-ring: inset 0 0 0 1px rgba(23,23,23,0),
        0 1px 3px 0 rgba(23,23,23,0.06),
        0 0 0 1px rgba(23,23,23,0.08);
      --peec-shadow-sm: 0 0 .5px 0 #00000040, 0 0 2px 0 #0000001a, 0 0 4px 0 #0000000d, 0 4px 8px 0 #00000005;
      --green-bg: rgba(22, 163, 74, 0.10);
      --green: rgb(22, 163, 74);
      --red-bg: rgba(251, 44, 54, 0.10);
      --red: #FB2C36;
      --orange-bg: rgba(234, 88, 12, 0.10);
      --orange: rgb(234, 88, 12);
      --indigo-bg: rgba(79, 70, 229, 0.10);
      --indigo: rgb(79, 70, 229);
      --cyan-bg: rgba(0, 146, 184, 0.10);
      --cyan: rgb(0, 146, 184);
      --purple-bg: rgba(124, 58, 237, 0.10);
      --purple: rgb(124, 58, 237);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-width: 320px;
      background: var(--peec-bg);
      color: var(--peec-fg);
      font: 400 var(--peec-text-base) / 1.5 var(--peec-font);
      letter-spacing: 0;
    }

    button, input { font: inherit; }

    .app-shell {
      display: grid;
      grid-template-columns: 204px minmax(0, 1fr);
      min-height: 100vh;
      background: var(--peec-bg);
    }

    .sidebar {
      position: sticky;
      top: 0;
      height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 18px;
      padding: 16px 12px;
      background: var(--peec-bg);
    }

    .project-switcher {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 36px;
      padding: 6px 8px;
      border-radius: var(--peec-radius-xl);
      box-shadow: var(--peec-ring);
      background: var(--peec-surface);
    }

    .avatar {
      width: 22px;
      height: 22px;
      border-radius: var(--peec-radius-sm);
      background: var(--peec-fg);
      color: #FDFDFD;
      display: grid;
      place-items: center;
      font-size: 12px;
      font-weight: 600;
      flex: 0 0 auto;
    }

    .project-name {
      min-width: 0;
      flex: 1;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .nav-group {
      display: grid;
      gap: 3px;
    }

    .nav-label {
      padding: 0 8px 3px;
      color: var(--peec-fg-subtle);
      font-size: var(--peec-text-sm);
      font-weight: 500;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      padding: 0 8px;
      border-radius: var(--peec-radius-xl);
      color: var(--peec-fg);
      font-weight: 500;
      text-decoration: none;
    }

    .nav-item.active { background: var(--peec-hover); }
    .nav-item:hover { background: var(--peec-tint); }

    .nav-dot {
      width: 16px;
      height: 16px;
      border-radius: 5px;
      background: var(--peec-tint);
      box-shadow: inset 0 0 0 1px var(--peec-hairline);
      flex: 0 0 auto;
    }

    .sidebar-footer {
      margin-top: auto;
      padding: 10px 8px;
      border-radius: var(--peec-radius-xl);
      background: var(--peec-tint);
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-xs);
    }

    .workspace {
      min-width: 0;
      background: var(--peec-surface);
      box-shadow: inset 1px 0 0 var(--peec-hairline);
    }

    .topbar {
      position: sticky;
      top: 0;
      z-index: 5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 56px;
      padding: 12px 24px;
      background: color-mix(in srgb, var(--peec-surface) 92%, transparent);
      backdrop-filter: blur(4px);
      box-shadow: inset 0 -1px 0 var(--peec-hairline);
    }

    .page-kicker {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      letter-spacing: var(--peec-tracking);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .btn {
      height: 30px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 0 9px;
      border: 0;
      border-radius: var(--peec-radius-md);
      background: var(--peec-surface);
      color: var(--peec-fg);
      box-shadow: var(--peec-ring);
      font-weight: 500;
      cursor: default;
      white-space: nowrap;
    }

    .btn.primary {
      background: var(--peec-fg);
      color: #FDFDFD;
      box-shadow: inset 0 0 0 1px rgba(253,253,253,0.12), 0 0 0 1px #171717, 0 1px 3px rgba(23,23,23,0.08);
    }

    .content {
      width: min(100%, 1280px);
      margin: 0 auto;
      padding: 20px 24px 36px;
    }

    .filterbar {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }

    .filter-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 30px;
      padding: 0 9px;
      border-radius: var(--peec-radius-md);
      background: #FFFFFF;
      box-shadow: var(--peec-ring);
      color: var(--peec-fg);
      font-weight: 500;
    }

    .journey-rail {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 16px;
    }

    .journey-step {
      min-height: 72px;
      padding: 12px;
      border-radius: var(--peec-radius-xl);
      background: #FFFFFF;
      box-shadow: var(--peec-ring);
    }

    .step-index {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      margin-bottom: 7px;
      border-radius: var(--peec-radius-sm);
      background: var(--peec-fg);
      color: #FDFDFD;
      font-size: var(--peec-text-xs);
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }

    .step-title {
      font-size: var(--peec-text-sm);
      font-weight: 600;
      line-height: 1.3;
    }

    .step-copy {
      margin-top: 2px;
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-xs);
      line-height: 1.35;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(360px, .9fr);
      gap: 16px;
      align-items: stretch;
      margin-bottom: 24px;
    }

    .hero-copy {
      padding: 18px 0;
    }

    h1 {
      margin: 0 0 8px;
      font-size: 24px;
      line-height: 1.2;
      font-weight: 600;
      letter-spacing: var(--peec-tracking);
    }

    .subtitle {
      max-width: 760px;
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-base);
    }

    .verdict-panel {
      min-height: 100%;
      padding: 16px;
      border-radius: var(--peec-radius-xl);
      background: #FFFFFF;
      box-shadow: var(--peec-ring);
      display: grid;
      gap: 14px;
    }

    .verdict-row {
      display: grid;
      grid-template-columns: 132px minmax(0, 1fr);
      gap: 12px;
      align-items: start;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(23,23,23,0.06);
    }

    .verdict-row:last-child {
      padding-bottom: 0;
      border-bottom: 0;
    }

    .verdict-label {
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-sm);
      font-weight: 500;
    }

    .verdict-value {
      font-weight: 500;
      line-height: 1.45;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 24px;
    }

    .metric-card, .panel {
      background: #FFFFFF;
      border-radius: var(--peec-radius-xl);
      box-shadow: var(--peec-ring);
    }

    .metric-card {
      min-height: 112px;
      padding: 14px;
      display: grid;
      align-content: space-between;
      gap: 12px;
    }

    .metric-label {
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-xs);
      font-weight: 500;
    }

    .metric-value {
      font-size: 24px;
      line-height: 1.15;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      letter-spacing: var(--peec-tracking);
    }

    .metric-sub {
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-xs);
    }

    .section-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.08fr) minmax(340px, .92fr);
      gap: 16px;
      margin-bottom: 16px;
    }

    .panel {
      min-width: 0;
      padding: 16px;
      margin-bottom: 16px;
    }

    .panel-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    .panel-title {
      margin: 0;
      font-size: var(--peec-text-lg);
      line-height: 1.35;
      font-weight: 600;
      letter-spacing: var(--peec-tracking);
    }

    .panel-subtitle {
      margin: 2px 0 0;
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-base);
    }

    .segmented {
      display: inline-flex;
      align-items: center;
      gap: 2px;
      padding: 2px;
      border-radius: var(--peec-radius-md);
      background: var(--peec-tint);
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-sm);
      font-weight: 500;
      white-space: nowrap;
    }

    .segmented span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 24px;
      height: 24px;
      border-radius: var(--peec-radius-sm);
    }

    .segmented span.active {
      background: var(--peec-hover);
      color: var(--peec-fg);
    }

    .chart {
      width: 100%;
      height: 324px;
      overflow: hidden;
    }

    .chart.tall { height: 380px; }

    .card-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .decision-card {
      min-width: 0;
      padding: 14px;
      border-radius: var(--peec-radius-xl);
      background: var(--peec-tint);
      box-shadow: inset 0 0 0 1px rgba(23,23,23,0.04);
      display: grid;
      gap: 10px;
    }

    .decision-card-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    .decision-card h3 {
      margin: 0;
      font-size: var(--peec-text-base);
      line-height: 1.35;
      font-weight: 600;
      letter-spacing: 0;
    }

    .decision-card p {
      margin: 0;
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-sm);
    }

    .decision-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .stat-list {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
    }

    .stat-box {
      padding: 10px;
      border-radius: var(--peec-radius-lg);
      background: #FFFFFF;
      box-shadow: inset 0 0 0 1px rgba(23,23,23,0.06);
    }

    .stat-box .metric-label {
      display: block;
      margin-bottom: 4px;
    }

    .stat-box strong {
      font-size: var(--peec-text-lg);
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }

    .evidence-summary {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 14px;
    }

    .summary-tile {
      padding: 12px;
      border-radius: var(--peec-radius-lg);
      background: var(--peec-tint);
      box-shadow: inset 0 0 0 1px rgba(23,23,23,0.04);
    }

    .summary-tile strong {
      display: block;
      margin-top: 4px;
      font-size: var(--peec-text-lg);
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }

    .review-grid {
      display: grid;
      gap: 12px;
    }

    .claim-review-card {
      padding: 14px;
      border-radius: var(--peec-radius-xl);
      background: #FFFFFF;
      box-shadow: inset 0 0 0 1px rgba(23,23,23,0.08);
      display: grid;
      gap: 12px;
    }

    .claim-review-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    .claim-review-title {
      margin: 0;
      font-size: var(--peec-text-base);
      line-height: 1.4;
      font-weight: 600;
    }

    .method-chain {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
    }

    .method-step {
      min-height: 88px;
      padding: 10px;
      border-radius: var(--peec-radius-lg);
      background: var(--peec-tint);
      box-shadow: inset 0 0 0 1px rgba(23,23,23,0.04);
    }

    .method-step-title {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 5px;
      font-size: var(--peec-text-sm);
      font-weight: 600;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--peec-fg-subtle);
      flex: 0 0 auto;
    }

    .status-dot.supports { background: var(--green); }
    .status-dot.directional { background: var(--green); }
    .status-dot.conflicts { background: var(--red); }
    .status-dot.blocked { background: var(--red); }
    .status-dot.insufficient { background: var(--orange); }
    .status-dot.unavailable { background: var(--peec-fg-subtle); }

    .audit-details {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid rgba(23,23,23,0.06);
    }

    .audit-details summary {
      width: max-content;
      max-width: 100%;
      list-style: none;
      cursor: default;
    }

    .audit-details summary::-webkit-details-marker {
      display: none;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: auto;
      font-size: var(--peec-text-base);
    }

    th, td {
      padding: 10px 8px;
      border-bottom: 1px solid rgba(23,23,23,0.06);
      text-align: left;
      vertical-align: top;
    }

    th {
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-sm);
      font-weight: 500;
      white-space: nowrap;
    }

    tr:hover td { background: rgba(23,23,23,0.03); }

    .number { font-variant-numeric: tabular-nums; white-space: nowrap; }
    .muted { color: var(--peec-fg-muted); }
    .nowrap { white-space: nowrap; }

    .topic-cell {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-width: 170px;
      font-weight: 500;
    }

    .swatch {
      width: 12px;
      height: 12px;
      border-radius: 4px;
      flex: 0 0 auto;
      background: var(--peec-fg);
    }

    .pill {
      display: inline-flex;
      align-items: center;
      max-width: 100%;
      min-height: 24px;
      padding: 2px 7px;
      border-radius: var(--peec-radius-md);
      background: var(--peec-tint);
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-sm);
      font-weight: 500;
      line-height: 1.35;
      white-space: nowrap;
    }

    .pill.perception, .pill.block, .pill.competitor-owned, .pill.owner-competitor { background: var(--red-bg); color: var(--red); }
    .pill.indexing, .pill.test-next { background: var(--orange-bg); color: var(--orange); }
    .pill.volume-frequency, .pill.watch, .pill.proof-gap { background: var(--purple-bg); color: var(--purple); }
    .pill.strong, .pill.confirmed, .pill.stronghold, .pill.target-owned, .pill.owner-target, .pill.act-now, .pill.directional { background: var(--green-bg); color: var(--green); }
    .pill.monitor, .pill.moderate { background: var(--cyan-bg); color: var(--cyan); }
    .pill.blind-spot, .pill.slow-burn { background: var(--indigo-bg); color: var(--indigo); }

    .table-wrap {
      overflow-x: auto;
      margin: 0 -8px;
      padding: 0 8px;
    }

    .footer-note {
      margin-top: 10px;
      color: var(--peec-fg-muted);
      font-size: var(--peec-text-xs);
    }

    @media (max-width: 1020px) {
      .app-shell { grid-template-columns: 1fr; }
      .sidebar {
        position: static;
        height: auto;
        display: block;
        padding: 12px;
        box-shadow: inset 0 -1px 0 var(--peec-hairline);
      }
      .nav-group, .sidebar-footer { display: none; }
      .workspace { box-shadow: none; }
      .hero, .section-grid { grid-template-columns: 1fr; }
      .journey-rail { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .card-grid { grid-template-columns: 1fr; }
      .stat-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .evidence-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .method-chain { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 640px) {
      .topbar { align-items: flex-start; flex-direction: column; padding: 12px 16px; }
      .content { padding: 16px; }
      .journey-rail { grid-template-columns: 1fr; }
      .metric-grid { grid-template-columns: 1fr; }
      .verdict-row { grid-template-columns: 1fr; }
      .stat-list { grid-template-columns: 1fr; }
      .evidence-summary { grid-template-columns: 1fr; }
      .method-chain { grid-template-columns: 1fr; }
      .panel-header { flex-direction: column; }
      .chart { height: 300px; }
      h1 { font-size: 20px; }
    }
    .action-group { margin-bottom: 20px; }
    .action-group-header {
      display: flex; align-items: center; gap: 8px;
      margin-bottom: 8px; padding-bottom: 8px;
      border-bottom: 1px solid rgba(23,23,23,0.06);
    }
    .action-group-title {
      margin: 0; font-size: var(--peec-text-lg);
      font-weight: 600; letter-spacing: var(--peec-tracking);
    }
    .action-group-intervention {
      margin: 0 0 10px; color: var(--peec-fg-muted);
      font-size: var(--peec-text-sm);
    }
    .all-clear-banner {
      padding: 12px 14px; border-radius: var(--peec-radius-xl);
      background: var(--green-bg); color: var(--green);
      font-weight: 500; margin-bottom: 16px;
    }
  </style>
</head>
<body>
<div class="app-shell">
  <aside class="sidebar" aria-label="Presence Rx navigation">
    <div class="project-switcher">
      <div class="avatar">P</div>
      <div class="project-name">Presence Rx</div>
      <div class="muted">v1</div>
    </div>
    <nav class="nav-group">
      <div class="nav-label">Overview</div>
      <a class="nav-item active" href="#overview"><span class="nav-dot"></span>Overview</a>
      <a class="nav-item" href="#action-brief"><span class="nav-dot"></span>Action brief</a>
    </nav>
    <nav class="nav-group">
      <div class="nav-label">Diagnosis</div>
      <a class="nav-item" href="#blind-spots"><span class="nav-dot"></span>Blind spots</a>
      <a class="nav-item" href="#perception"><span class="nav-dot"></span>Perception</a>
    </nav>
    <nav class="nav-group">
      <div class="nav-label">Evidence</div>
      <a class="nav-item" href="#claims"><span class="nav-dot"></span>Claims</a>
      <a class="nav-item" href="#evidence"><span class="nav-dot"></span>Claim review</a>
    </nav>
    <nav class="nav-group">
      <div class="nav-label">Analytics</div>
      <a class="nav-item" href="#analytics"><span class="nav-dot"></span>Charts</a>
    </nav>
    <nav class="nav-group">
      <div class="nav-label">Actions</div>
      <a class="nav-item" href="#prescriptions"><span class="nav-dot"></span>Action plan</a>
      <a class="nav-item" href="#monitoring"><span class="nav-dot"></span>Monitoring</a>
    </nav>
    <nav class="nav-group">
      <div class="nav-label">About</div>
      <a class="nav-item" href="#about"><span class="nav-dot"></span>Study definition</a>
      <a class="nav-item" href="#export"><span class="nav-dot"></span>Export</a>
    </nav>
    <div class="sidebar-footer">Big Berlin Hack 2026<br>Public-safe local MVP</div>
  </aside>
  <main class="workspace">
    <header class="topbar">
      <div class="page-kicker"><span class="nav-dot"></span>Presence Rx MVP dashboard</div>
      <div class="header-actions">
        <button class="btn">Export</button>
        <button class="btn primary">+ Create monitoring prompt</button>
      </div>
    </header>
    <div class="content">
      <div class="filterbar" aria-label="Dashboard filters">
        <div class="filter-pill">Brand: Nothing Phone</div>
        <div class="filter-pill">Time: Apr 25</div>
        <div class="filter-pill">Market: US</div>
        <div class="filter-pill">Models: 3</div>
        <div class="filter-pill">Topics: 5</div>
      </div>

      <div class="journey-rail" aria-label="Presence Rx workflow">
        <div class="journey-step"><span class="step-index">1</span><div class="step-title">Define</div><div class="step-copy">Scope the brand, market, models, and Peec snapshot.</div></div>
        <div class="journey-step"><span class="step-index">2</span><div class="step-title">Diagnose</div><div class="step-copy">Find prompt clusters where visibility or association breaks.</div></div>
        <div class="journey-step"><span class="step-index">3</span><div class="step-title">Verify</div><div class="step-copy">Check claims with Peec, Gemini, Tavily, and publication rules.</div></div>
        <div class="journey-step"><span class="step-index">4</span><div class="step-title">Prescribe</div><div class="step-copy">Translate each gap type into a concrete intervention.</div></div>
        <div class="journey-step"><span class="step-index">5</span><div class="step-title">Monitor</div><div class="step-copy">Create prompts and tags to track recovery in Peec.</div></div>
      </div>

      <section class="hero" id="overview">
        <div class="hero-copy">
          <span class="pill confirmed">Presence Verdict</span>
          <h1>The invisible champion</h1>
          <p class="subtitle">Presence Rx turns Peec visibility data into a guarded recommendation workflow. It defines the AI-answer problem, diagnoses why the brand is missing, verifies what can be said safely, and prescribes what Peec should monitor next.</p>
        </div>
        <div class="verdict-panel" id="verdict">
          <div class="verdict-row">
            <div class="verdict-label">Verdict</div>
            <div class="verdict-value">Nothing Phone is visible as a design stronghold, but under-owned across four commercial AI-answer surfaces.</div>
          </div>
          <div class="verdict-row">
            <div class="verdict-label">Primary risk</div>
            <div class="verdict-value">AI answers may rank the brand highly when mentioned while omitting it from broader buyer-category prompts.</div>
          </div>
          <div class="verdict-row">
            <div class="verdict-label">Best next move</div>
            <div class="verdict-value">Prioritize verified blind spots by gap type, then create Peec monitoring prompts for recovery.</div>
          </div>
        </div>
      </section>

      <div class="metric-grid" id="cards"></div>

      <section class="panel" id="action-brief">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Action brief</h2>
            <p class="panel-subtitle">What to do about each blind spot, grouped by intervention class.</p>
          </div>
        </div>
        <div id="blockedClaimsBanner"></div>
        <div id="actionBriefCards"></div>
      </section>

      <section class="panel" id="blind-spots">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Blind spot decisions</h2>
            <p class="panel-subtitle">Each prompt cluster is framed as a decision card: problem, proof depth, intervention, and next move.</p>
          </div>
        </div>
        <div class="card-grid" id="blindSpotCards"></div>
      </section>

      <section class="panel" id="perception">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Perception analysis</h2>
            <p class="panel-subtitle">How AI models perceive each topic and what associations are missing for Nothing Phone.</p>
          </div>
        </div>
        <div class="table-wrap">
          <table id="perceptionTable"></table>
        </div>
      </section>

      <section class="panel" id="claims">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Claim checks</h2>
            <p class="panel-subtitle">What the team can say safely in a deck, brief, or demo.</p>
          </div>
        </div>
        <div class="table-wrap">
          <table id="claimTable"></table>
        </div>
        <div class="footer-note">This local surface intentionally uses aggregate source counts and reviewed claim language.</div>
      </section>

      <section class="panel" id="evidence">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Claim review</h2>
            <p class="panel-subtitle">Why each recommendation is trustworthy, what evidence was checked, and what language is allowed.</p>
          </div>
        </div>
        <div class="evidence-summary" id="evidenceSummary"></div>
        <details>
          <summary class="pill monitor" style="margin-bottom:8px">Show detailed claim reviews</summary>
          <div class="review-grid" id="claimReviewCards"></div>
        </details>
        <details class="audit-details">
          <summary class="pill monitor">Show audit trail</summary>
          <div class="table-wrap">
            <table id="evidenceTable"></table>
          </div>
        </details>
      </section>

      <div id="analytics">
        <div class="section-grid" id="topics">
          <section class="panel">
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Topic visibility</h2>
                <p class="panel-subtitle">Where the brand appears now and where it disappears.</p>
              </div>
            </div>
            <div id="visibilityChart" class="chart"></div>
          </section>
          <section class="panel">
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Action priority</h2>
                <p class="panel-subtitle">Which blind spot deserves work first.</p>
              </div>
            </div>
            <div id="opportunityChart" class="chart"></div>
          </section>
        </div>

        <div class="section-grid" id="competitors">
          <section class="panel">
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Competitor landscape</h2>
                <p class="panel-subtitle">Shows whether Nothing Phone or a competitor owns the answer surface.</p>
              </div>
            </div>
            <div id="landscapeChart" class="chart"></div>
          </section>
          <section class="panel">
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Method outcomes</h2>
                <p class="panel-subtitle">Shows whether independent methods agreed before a recommendation was made.</p>
              </div>
            </div>
            <div id="methodChart" class="chart"></div>
          </section>
        </div>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Priority signals</h2>
              <p class="panel-subtitle">Multi-axis scoring per topic: intent fit, citation authority, evidence coverage, signal alignment, and action priority.</p>
            </div>
          </div>
          <div id="radarChart" class="chart tall"></div>
        </section>

        <details class="audit-details">
          <summary class="pill monitor">Show operator-level trend routing</summary>
          <section class="panel" style="margin-top:12px">
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Trend routing</h2>
                <p class="panel-subtitle">Internal taxonomy and routing fields behind each recommendation.</p>
              </div>
            </div>
            <div class="table-wrap">
              <table id="gapTable"></table>
            </div>
          </section>
        </details>
      </div>

      <section class="panel" id="prescriptions">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Action plan</h2>
            <p class="panel-subtitle">The action queue: what to create in Peec so recovery can be monitored.</p>
          </div>
          <span class="pill monitor">setup</span>
        </div>
        <div class="table-wrap">
          <table id="prescriptionTable"></table>
        </div>
      </section>

      <section class="panel" id="monitoring">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Monitoring setup</h2>
            <p class="panel-subtitle">The prescribed Peec objects that close the loop after the next platform run.</p>
          </div>
        </div>
        <div class="card-grid" id="monitoringCards"></div>
      </section>

      <details id="about">
        <summary class="pill monitor" style="margin-bottom:8px">Show study definition</summary>
        <section class="panel" id="define">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Study definition</h2>
              <p class="panel-subtitle">What was measured, where, and which evidence layers power the result.</p>
            </div>
            <span class="pill confirmed">validated</span>
          </div>
          <div class="table-wrap">
            <table id="pipelineTable"></table>
          </div>
        </section>
      </details>

      <section class="panel" id="export">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Presence Verdict Pack</h2>
            <p class="panel-subtitle">Submission-ready outputs generated from the same pipeline state.</p>
          </div>
          <span class="pill confirmed">single source</span>
        </div>
        <div class="card-grid" id="exportCards"></div>
      </section>
    </div>
  </main>
</div>
"""
        + _json_script("presence-data", data)
        + """
<script>
const data = JSON.parse(document.getElementById('presence-data').textContent);
const studyRows = data.study.rows || [];
const classified = Object.fromEntries((data.classification?.classified_gaps || []).map(g => [g.cluster_id, g]));
const metrics = Object.fromEntries((data.metrics?.rows || []).map(r => [r.cluster_id, r]));
const landscape = Object.fromEntries((data.landscape?.topics || []).map(r => [r.cluster_id, r]));
const claims = data.ledger?.claims || [];
const evidence = data.ledger?.evidence || [];
const prescription = data.prescription || null;
const tavilySources = data.tavily?.summary?.sources || 0;
const confirmed = Object.values(classified).filter(g => g.classification_status === 'confirmed').length;
const avgOpp = data.metrics?.summary?.average_opportunity_score || 0;
const blocked = claims.filter(c => c.status === 'blocked').length;

const palette = {
  fg: '#171717',
  muted: 'rgba(23,23,23,0.6)',
  grid: 'rgba(23,23,23,0.08)',
  green: 'rgb(22, 163, 74)',
  red: '#FB2C36',
  orange: 'rgb(234, 88, 12)',
  indigo: 'rgb(79, 70, 229)',
  cyan: 'rgb(0,146,184)',
  purple: 'rgb(124,58,237)',
  gray: 'rgba(23,23,23,0.5)'
};

const topicColors = {
  stronghold: palette.green,
  perception: palette.red,
  indexing: palette.orange,
  volume_frequency: palette.purple,
  blind_spot: palette.indigo,
  watch: palette.cyan
};

const statusColors = {
  confirmed: palette.green,
  provisional: palette.orange,
  conflicted: palette.red,
  insufficient: palette.gray
};

const compact = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 });

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[char]));
}

function slug(value) {
  return String(value || 'other').toLowerCase().replaceAll('_', '-').replaceAll(' ', '-');
}

function pill(value, fallback = 'other') {
  const text = value || fallback;
  return `<span class="pill ${slug(text)}">${escapeHtml(text)}</span>`;
}

function tonePill(label, tone = 'other') {
  return `<span class="pill ${slug(tone)}">${escapeHtml(label)}</span>`;
}

function clusterOwner(row, owner) {
  if (owner?.ownership_status === 'target_owned' || (!row.gap_type && (row.visibility_target_share || 0) >= 0.5)) {
    return {
      name: brandName,
      label: `${brandName} owns`,
      tone: 'owner-target',
      visibility: row.visibility_target_share
    };
  }
  if (owner?.competitor_owner || row.visibility_competitor_owner) {
    const name = owner.competitor_owner || row.visibility_competitor_owner;
    return {
      name,
      label: `${name} owns`,
      tone: owner?.ownership_status === 'contested' ? 'watch' : 'owner-competitor',
      visibility: owner.competitor_visibility_share
    };
  }
  return {
    name: 'Unclear owner',
    label: 'Unclear owner',
    tone: 'unknown',
    visibility: owner?.competitor_visibility_share
  };
}

function topicCell(row) {
  const key = row.gap_type || 'stronghold';
  const color = topicColors[key] || palette.gray;
  return `<span class="topic-cell"><span class="swatch" style="background:${color}"></span>${escapeHtml(row.cluster_label)}</span>`;
}

function interventionLabel(gapType) {
  if (gapType === 'indexing') return 'Canonical source and citation optimization';
  if (gapType === 'perception') return 'Positioning and association correction';
  if (gapType === 'volume_frequency') return 'Proof creation and distribution';
  return 'Maintain and monitor';
}

function problemCopy(row, metric, owner) {
  if (!row.gap_type) {
    return `${brandName} already owns this answer surface. Keep it as the benchmark for future Peec runs.`;
  }
  const ownerText = clusterOwner(row, owner).name;
  return `${ownerText} is currently the visible owner of this prompt cluster. The recommended action is ${metric?.decision_bucket || 'unclassified'}, with ${metric?.primary_gap || 'a visibility gap'} as the primary gap.`;
}

function sourceLabel(refOrType) {
  const value = String(refOrType || '');
  if (value.startsWith('peec:snapshot')) return 'Peec visibility snapshot';
  if (value.startsWith('peec:topic')) return 'Topic-level visibility';
  if (value.startsWith('peec:brand')) {
    const brand = value.split(':').at(-1)?.replaceAll('-', ' ');
    return brand ? `${brand.charAt(0).toUpperCase() + brand.slice(1)} visibility` : 'Competitor visibility';
  }
  if (value.startsWith('gemini:')) return 'Perception analysis';
  if (value.startsWith('tavily:')) return 'Public web evidence';
  if (value.startsWith('study_ssot:')) return 'Normalized study row';
  if (value === 'peec_mcp') return 'Peec MCP';
  if (value === 'derived') return 'Derived study data';
  return value.replaceAll('_', ' ') || 'Evidence';
}

function sourceExplanation(ref) {
  const value = String(ref || '');
  if (value.startsWith('peec:snapshot')) return 'The baseline Peec run used for all visibility and ranking numbers.';
  if (value.startsWith('peec:topic')) return 'The topic-level visibility signal for this prompt cluster.';
  if (value.startsWith('peec:brand')) return 'The competitor ownership signal used for comparison.';
  if (value.startsWith('gemini:')) return 'The association check that helps classify the type of blind spot.';
  if (value.startsWith('tavily:')) return 'The public-source check used to avoid unsupported claims.';
  if (value.startsWith('study_ssot:')) return 'The normalized row that ties pipeline artifacts together.';
  return 'Supporting source reference carried through the evidence ledger.';
}

function statusCopy(status) {
  if (status === 'supports') return 'Supports the classification';
  if (status === 'conflicts') return 'Conflicts with the classification';
  if (status === 'insufficient') return 'Weak or incomplete signal';
  if (status === 'unavailable') return 'Signal unavailable';
  return 'Reviewed signal';
}

function methodCopy(signal) {
  if (!signal) return 'No method signal was available for this step.';
  if (signal.method === 'peec') return 'Peec provided the visibility, rank, topic, and competitor signal.';
  if (signal.method === 'gemini') return 'Gemini checked the perception and missing-association pattern.';
  if (signal.method === 'tavily') return 'Tavily checked whether public web evidence supports the finding.';
  return statusCopy(signal.signal);
}

const plotLayoutBase = {
  paper_bgcolor: '#FFFFFF',
  plot_bgcolor: '#FFFFFF',
  font: { family: 'Geist Variable, system-ui, sans-serif', size: 12, color: palette.fg },
  margin: { t: 12, r: 14, b: 70, l: 42 },
  xaxis: {
    tickfont: { color: palette.muted, size: 12 },
    gridcolor: 'rgba(23,23,23,0)',
    zerolinecolor: palette.grid
  },
  yaxis: {
    tickfont: { color: palette.muted, size: 12 },
    gridcolor: palette.grid,
    zerolinecolor: palette.grid
  }
};

const plotConfig = { displayModeBar: false, responsive: true };
const labels = studyRows.map(r => r.cluster_label);
const brandName = 'Nothing Phone';
const competitorNames = [...new Set(studyRows.map(r => r.visibility_competitor_owner).filter(Boolean))];
const competitorLegendName = competitorNames.length === 1 ? competitorNames[0] : 'Named competitor';

const totalVis = studyRows.reduce((acc, r) => acc + (r.visibility_target_share || 0), 0);
const avgVis = studyRows.length ? Math.round(totalVis / studyRows.length * 100) : 0;
const avgPosition = studyRows.length
  ? (studyRows.reduce((acc, r) => acc + (r.visibility_target_avg_position || 0), 0) / studyRows.length).toFixed(1)
  : '0';
document.getElementById('cards').innerHTML = [
  ['Overall visibility', `${avgVis}%`, `${studyRows.length} topics tracked`],
  ['Avg position', avgPosition, '#1 when mentioned'],
  ['Confirmed gaps', `${confirmed} / ${Object.keys(classified).length || studyRows.filter(r => r.gap_type).length}`, '3-method classifier'],
  ['Tavily sources', compact.format(tavilySources), 'aggregate only'],
  ['Avg opportunity', compact.format(avgOpp), '0 to 100 score']
].map(([label, value, sub]) => `
  <div class="metric-card">
    <div class="metric-label">${escapeHtml(label)}</div>
    <div>
      <div class="metric-value">${escapeHtml(value)}</div>
      <div class="metric-sub">${escapeHtml(sub)}</div>
    </div>
  </div>
`).join('');

// --- Action Brief ---
const GAP_TYPE_ORDER = ['perception', 'indexing', 'volume_frequency'];
const GAP_TYPE_NAMES = {
  perception: 'Perception',
  indexing: 'Indexing',
  volume_frequency: 'Volume / Frequency'
};
const INTERVENTION_CLASS = {
  perception: 'Positioning + messaging correction; reframing content with explicit trait language',
  indexing: 'Schema markup, structured data, AI-citation optimization, source-of-truth canonicalization',
  volume_frequency: 'Content creation + distribution + amplification; sustained editorial outreach; UGC seeding'
};

const blockedClaims = data.ledger?.blocked_claims || [];
document.getElementById('blockedClaimsBanner').innerHTML = blockedClaims.length
  ? blockedClaims.map(bc => `
    <div class="decision-card" style="margin-bottom:10px;border-left:3px solid var(--red)">
      <div class="decision-card-header"><h3>${escapeHtml(bc.claim_id)}</h3>${pill('blocked')}</div>
      <p><strong>Blocked claim:</strong> ${escapeHtml(bc.claim)}</p>
      <p><strong>Safe rewrite:</strong> ${escapeHtml(bc.safe_rewrite)}</p>
    </div>`).join('')
  : '<div class="all-clear-banner">All clear — no blocked claims. All gap classifications confirmed by 3-method agreement.</div>';

const rowsByGap = {};
studyRows.forEach(row => {
  if (row.gap_type) {
    (rowsByGap[row.gap_type] = rowsByGap[row.gap_type] || []).push(row);
  }
});

document.getElementById('actionBriefCards').innerHTML = GAP_TYPE_ORDER.map(gapType => {
  const gapRows = rowsByGap[gapType] || [];
  if (!gapRows.length) return '';
  const name = GAP_TYPE_NAMES[gapType];
  const intervention = INTERVENTION_CLASS[gapType];
  const topicNames = gapRows.map(r => r.cluster_label).join(', ');
  return `
    <div class="action-group">
      <div class="action-group-header">
        <h3 class="action-group-title">${escapeHtml(name)} gaps</h3>
        ${pill(gapType)}
      </div>
      <p class="action-group-intervention"><strong>Intervention:</strong> ${escapeHtml(intervention)}</p>
      <p class="muted" style="margin:0 0 10px">Topics: ${escapeHtml(topicNames)}</p>
      <div class="card-grid">
        ${gapRows.map(row => {
          const metric = metrics[row.cluster_id] || {};
          const owner = landscape[row.cluster_id] || {};
          const clusterOwnerInfo = clusterOwner(row, owner);
          const claim = claims.find(c => c.cluster_id === row.cluster_id);
          return `<article class="decision-card">
            <div class="decision-card-header">
              <h3>${escapeHtml(row.cluster_label)}</h3>
              ${pill(metric.decision_bucket || 'monitor')}
            </div>
            <div class="decision-meta">
              ${pill(metric.trend_zone || 'snapshot')}
              ${tonePill(clusterOwnerInfo.label, clusterOwnerInfo.tone)}
            </div>
            <div class="stat-list">
              <div class="stat-box"><span class="metric-label">Action Priority</span><strong>${escapeHtml(metric.opportunity_score ?? 0)}</strong></div>
              <div class="stat-box"><span class="metric-label">${escapeHtml(brandName)}</span><strong>${Math.round((row.visibility_target_share || 0) * 100)}%</strong></div>
              <div class="stat-box"><span class="metric-label">Cluster owner</span><strong>${escapeHtml(clusterOwnerInfo.name)}</strong></div>
            </div>
            <p><strong>Next move:</strong> ${escapeHtml(metric.recommended_next_move || 'Monitor this cluster.')}</p>
            ${claim ? '<p><strong>Safe language:</strong> ' + escapeHtml(claim.publication_language) + '</p>' : ''}
          </article>`;
        }).join('')}
      </div>
    </div>`;
}).join('');

document.getElementById('pipelineTable').innerHTML = `
  <tbody>
    <tr><th>Brand</th><td>${escapeHtml(brandName)}</td></tr>
    <tr><th>Market</th><td>US</td></tr>
    <tr><th>Peec topics</th><td class="number">${studyRows.length}</td></tr>
    <tr><th>Models</th><td class="number">3 AI engines</td></tr>
    <tr><th>Classified gaps</th><td class="number">${confirmed}</td></tr>
    <tr><th>Claim checks</th><td class="number">${claims.length}</td></tr>
    <tr><th>Blocked claims</th><td class="number">${blocked}</td></tr>
  </tbody>
`;

document.getElementById('blindSpotCards').innerHTML = studyRows.map(row => {
  const metric = metrics[row.cluster_id] || {};
  const owner = landscape[row.cluster_id] || {};
  const clusterOwnerInfo = clusterOwner(row, owner);
  const visibility = Math.round((row.visibility_target_share || 0) * 100);
  const ownerVisibility = clusterOwnerInfo.visibility == null
    ? '-'
    : `${Math.round(clusterOwnerInfo.visibility * 100)}%`;
  return `
    <article class="decision-card">
      <div class="decision-card-header">
        <h3>${escapeHtml(row.cluster_label)}</h3>
        ${pill(metric.decision_bucket || 'monitor')}
      </div>
      <div class="decision-meta">
        ${pill(row.gap_type || 'stronghold')}
        ${pill(metric.trend_zone || 'snapshot')}
        ${tonePill(clusterOwnerInfo.label, clusterOwnerInfo.tone)}
      </div>
      <p>${escapeHtml(problemCopy(row, metric, owner))}</p>
      <div class="stat-list">
        <div class="stat-box"><span class="metric-label">${escapeHtml(brandName)}</span><strong>${visibility}%</strong></div>
        <div class="stat-box"><span class="metric-label">Cluster owner</span><strong>${escapeHtml(clusterOwnerInfo.name)}</strong></div>
        <div class="stat-box"><span class="metric-label">Owner visibility</span><strong>${escapeHtml(ownerVisibility)}</strong></div>
        <div class="stat-box"><span class="metric-label">Action Priority</span><strong>${escapeHtml(metric.opportunity_score ?? 0)}</strong></div>
      </div>
      <p><strong>Intervention:</strong> ${escapeHtml(interventionLabel(row.gap_type))}</p>
      <p><strong>Next move:</strong> ${escapeHtml(metric.recommended_next_move || 'Monitor this cluster in the next Peec run.')}</p>
    </article>
  `;
}).join('');

Plotly.newPlot('visibilityChart', [{
  type: 'bar',
  x: labels,
  y: studyRows.map(r => Math.round((r.visibility_target_share || 0) * 100)),
  marker: { color: studyRows.map(r => topicColors[r.gap_type || 'stronghold'] || palette.gray) },
  text: studyRows.map(r => `${Math.round((r.visibility_target_share || 0) * 100)}%`),
  textposition: 'outside',
  hovertemplate: '<b>%{x}</b><br>Visibility: %{y}%<extra></extra>'
}], {
  ...plotLayoutBase,
  yaxis: { ...plotLayoutBase.yaxis, title: 'Visibility %', range: [0, 88] }
}, plotConfig);

Plotly.newPlot('opportunityChart', [{
  type: 'bar',
  x: labels,
  y: studyRows.map(r => metrics[r.cluster_id]?.opportunity_score || 0),
  marker: { color: studyRows.map(r => topicColors[metrics[r.cluster_id]?.trend_label || 'blind_spot'] || palette.cyan) },
  text: studyRows.map(r => metrics[r.cluster_id]?.opportunity_score || 0),
  textposition: 'outside',
  hovertemplate: '<b>%{x}</b><br>Action priority: %{y}<extra></extra>'
}], {
  ...plotLayoutBase,
  yaxis: { ...plotLayoutBase.yaxis, title: 'Score', range: [0, 105] }
}, plotConfig);

Plotly.newPlot('landscapeChart', [{
  type: 'bar',
  name: brandName,
  x: labels,
  y: studyRows.map(r => Math.round((r.visibility_target_share || 0) * 100)),
  marker: { color: palette.green },
  hovertemplate: `<b>%{x}</b><br>${escapeHtml(brandName)}: %{y}%<extra></extra>`
}, {
  type: 'bar',
  name: competitorLegendName,
  x: labels,
  y: studyRows.map(r => Math.round((landscape[r.cluster_id]?.competitor_visibility_share || 0) * 100)),
  marker: { color: palette.red },
  hovertemplate: `<b>%{x}</b><br>${escapeHtml(competitorLegendName)}: %{y}%<extra></extra>`
}], {
  ...plotLayoutBase,
  barmode: 'group',
  legend: { orientation: 'h', x: 0, y: 1.16 },
  yaxis: { ...plotLayoutBase.yaxis, title: 'Visibility %', range: [0, 88] }
}, plotConfig);

const methodLabels = ['confirmed', 'provisional', 'conflicted', 'insufficient'];
const methodCounts = methodLabels.map(status =>
  Object.values(classified).filter(g => g.classification_status === status).length
);
Plotly.newPlot('methodChart', [{
  type: 'pie',
  labels: methodLabels,
  values: methodCounts,
  hole: 0.62,
  marker: { colors: methodLabels.map(label => statusColors[label]) },
  textinfo: 'label+value',
  hovertemplate: '<b>%{label}</b><br>%{value} rows<extra></extra>'
}], {
  paper_bgcolor: '#FFFFFF',
  plot_bgcolor: '#FFFFFF',
  font: { family: 'Geist Variable, system-ui, sans-serif', size: 12, color: palette.fg },
  margin: { t: 8, r: 8, b: 8, l: 8 },
  showlegend: false
}, plotConfig);

document.getElementById('gapTable').innerHTML = `
  <thead>
    <tr>
      <th>Topic</th>
      <th>Gap type</th>
      <th>Parent topic</th>
      <th>Trend</th>
      <th>Recommended Action</th>
      <th>Primary gap</th>
      <th class="number">Action Priority</th>
      <th>Cluster owner</th>
      <th class="number">Proof</th>
    </tr>
  </thead>
  <tbody>${studyRows.map(r => {
    const m = metrics[r.cluster_id] || {};
    const l = landscape[r.cluster_id] || {};
    const ownerInfo = clusterOwner(r, l);
    return `<tr>
      <td>${topicCell(r)}</td>
      <td>${pill(r.gap_type || 'stronghold')}</td>
      <td>${pill(m.parent_topic || 'unmapped')}</td>
      <td>${pill(m.trend_zone || m.trend_label || 'n/a')}</td>
      <td>${pill(m.decision_bucket || 'n/a')}</td>
      <td>${escapeHtml(m.primary_gap || 'n/a')}</td>
      <td class="number">${escapeHtml(m.opportunity_score ?? 0)}</td>
      <td>${tonePill(ownerInfo.label, ownerInfo.tone)}</td>
      <td class="number">${escapeHtml(l.proof_source_count || 0)} sources</td>
    </tr>`;
  }).join('')}</tbody>
`;

document.getElementById('claimTable').innerHTML = `
  <thead>
    <tr>
      <th>Claim</th>
      <th>Status</th>
      <th>Publication</th>
      <th>Evidence Level</th>
      <th>Allowed language</th>
    </tr>
  </thead>
  <tbody>${claims.map(c => `<tr>
    <td>${escapeHtml(c.claim)}</td>
    <td>${pill(c.status)}</td>
    <td>${pill(c.publication_status)}</td>
    <td>${pill(c.confidence_tier)}</td>
    <td>${escapeHtml(c.publication_language)}</td>
  </tr>`).join('')}</tbody>
`;

const evidenceByRef = Object.fromEntries(evidence.map(item => [item.evidence_ref, item]));
document.getElementById('evidenceSummary').innerHTML = [
  ['Claims reviewed', claims.length],
  ['Directional claims', claims.filter(c => c.status === 'directional').length],
  ['Blocked claims', blocked],
  ['Methods used', [...new Set(claims.flatMap(c => c.methods || []))].join(', ') || '-'],
  ['Public sources checked', tavilySources]
].map(([label, value]) => `
  <div class="summary-tile">
    <span class="metric-label">${escapeHtml(label)}</span>
    <strong>${escapeHtml(value)}</strong>
  </div>
`).join('');

document.getElementById('claimReviewCards').innerHTML = claims.map(claim => {
  const gap = classified[claim.cluster_id] || {};
  const metric = metrics[claim.cluster_id] || {};
  const signals = gap.method_signals || [];
  const technicalRefs = (claim.evidence_refs || []).map(ref => {
    const item = evidenceByRef[ref] || {};
    return `<li><strong>${escapeHtml(sourceLabel(ref))}</strong>: ${escapeHtml(sourceExplanation(ref))} <span class="muted">(${escapeHtml(item.evidence_ref || ref)})</span></li>`;
  }).join('');
  const methodSteps = ['peec', 'gemini', 'tavily', 'guardrail'].map(method => {
    if (method === 'guardrail') {
      return `<div class="method-step">
        <div class="method-step-title"><span class="status-dot ${slug(claim.status)}"></span>Claim check</div>
        <p>${escapeHtml(claim.publication_status === 'blocked' ? 'Blocks unsafe language.' : 'Allows directional language with caveat.')}</p>
      </div>`;
    }
    const signal = signals.find(item => item.method === method);
    return `<div class="method-step">
      <div class="method-step-title"><span class="status-dot ${slug(signal?.signal || 'unavailable')}"></span>${escapeHtml(sourceLabel(method === 'peec' ? 'peec_mcp' : method + ':'))}</div>
      <p>${escapeHtml(methodCopy(signal))}</p>
      <p class="muted">${escapeHtml(statusCopy(signal?.signal))}</p>
    </div>`;
  }).join('');
  return `<article class="claim-review-card">
    <div class="claim-review-header">
      <h3 class="claim-review-title">${escapeHtml(claim.claim)}</h3>
      <div class="decision-meta">${pill(claim.status)}${pill(claim.confidence_tier)}</div>
    </div>
    <div class="method-chain">${methodSteps}</div>
    <div>
      <div class="metric-label">What this means</div>
      <p>${escapeHtml(metric.recommended_next_move || 'Use this as a reviewed directional finding, not an absolute market claim.')}</p>
    </div>
    <div>
      <div class="metric-label">Allowed language</div>
      <p>${escapeHtml(claim.publication_language)}</p>
    </div>
    <details class="audit-details">
      <summary class="pill monitor">Show audit trail</summary>
      <ul style="margin:10px 0 0;padding-left:18px">${technicalRefs}</ul>
    </details>
  </article>`;
}).join('');

document.getElementById('evidenceTable').innerHTML = `
  <thead>
    <tr>
      <th>Plain label</th>
      <th>Source</th>
      <th>What it tells us</th>
      <th>Audit ref</th>
    </tr>
  </thead>
  <tbody>${evidence.map(item => `<tr>
    <td>${escapeHtml(sourceLabel(item.evidence_ref))}</td>
    <td>${pill(item.source_type)}</td>
    <td>${escapeHtml(sourceExplanation(item.evidence_ref))}</td>
    <td class="nowrap">${escapeHtml(item.evidence_ref)}</td>
  </tr>`).join('')}</tbody>
`;

const prescriptionRows = prescription ? [
  ...(prescription.planned_topics || []).map(item => ({
    type: 'topic',
    operation_id: item.operation_id,
    name: item.name,
    gap_type: item.gap_type,
    country_code: '-',
    status: item.execution_status,
    source_cluster_id: item.source_cluster_id
  })),
  ...(prescription.planned_tags || []).map(item => ({
    type: 'tag',
    operation_id: item.operation_id,
    name: item.name,
    gap_type: item.kind,
    country_code: '-',
    status: item.execution_status,
    source_cluster_id: '-'
  })),
  ...(prescription.planned_prompts || []).map(item => ({
    type: 'prompt',
    operation_id: item.operation_id,
    name: item.text,
    gap_type: item.gap_type,
    country_code: item.country_code,
    status: item.execution_status,
    source_cluster_id: item.source_cluster_id
  }))
] : [];

document.getElementById('prescriptionTable').innerHTML = `
  <thead>
    <tr>
      <th>Type</th>
      <th>Operation</th>
      <th>Name / prompt</th>
      <th>Gap</th>
      <th>Geo</th>
      <th>Status</th>
      <th>Cluster</th>
    </tr>
  </thead>
  <tbody>${prescriptionRows.map(item => `<tr>
    <td>${pill(item.type)}</td>
    <td class="nowrap">${escapeHtml(item.operation_id)}</td>
    <td>${escapeHtml(item.name)}</td>
    <td>${pill(item.gap_type)}</td>
    <td>${escapeHtml(item.country_code)}</td>
    <td>${pill(item.status)}</td>
    <td class="nowrap">${escapeHtml(item.source_cluster_id)}</td>
  </tr>`).join('')}</tbody>
`;

const prescriptionSummary = prescription?.summary || {
  planned_topics: 0,
  planned_tags: 0,
  planned_prompts: 0
};
const promptGeos = prescription
  ? [...new Set((prescription.planned_prompts || []).map(item => item.country_code))].sort()
  : [];

document.getElementById('monitoringCards').innerHTML = [
  ['Topics', prescriptionSummary.planned_topics || 0, 'New Peec topic objects for blind-spot clusters.'],
  ['Tags', prescriptionSummary.planned_tags || 0, 'Gap-type and geography tags for campaign routing.'],
  ['Prompts', prescriptionSummary.planned_prompts || 0, 'Monitoring prompts to track recovery after the next run.'],
  ['Geographies', promptGeos.join(', ') || '-', 'US baseline plus expansion markets prepared for setup.']
].map(([label, value, copy]) => `
  <article class="decision-card">
    <div class="decision-card-header">
      <h3>${escapeHtml(label)}</h3>
      ${pill('planned')}
    </div>
    <div class="metric-value">${escapeHtml(value)}</div>
    <p>${escapeHtml(copy)}</p>
  </article>
`).join('');

// Perception analysis table
const geminiFindings = Object.fromEntries(
  (data.gemini?.findings || []).map(f => [f.cluster_id, f])
);
document.getElementById('perceptionTable').innerHTML = `
  <thead>
    <tr>
      <th>Topic</th>
      <th>Gap type</th>
      <th>Perception themes</th>
      <th>Missing associations</th>
      <th>Diagnostic wording</th>
    </tr>
  </thead>
  <tbody>${studyRows.filter(r => r.gap_type).map(r => {
    const f = geminiFindings[r.cluster_id] || {};
    const themes = (f.perception_themes || []).map(t => `<li>${escapeHtml(t)}</li>`).join('');
    const missing = (f.missing_associations || []).map(m => `<li>${escapeHtml(m)}</li>`).join('');
    return `<tr>
      <td>${topicCell(r)}</td>
      <td>${pill(r.gap_type)}</td>
      <td><ul style="margin:0;padding-left:16px">${themes || '<li>-</li>'}</ul></td>
      <td><ul style="margin:0;padding-left:16px">${missing || '<li>-</li>'}</ul></td>
      <td><em>${escapeHtml(f.safe_scenario_wording || '-')}</em></td>
    </tr>`;
  }).join('')}</tbody>
`;

// Radar chart for value-added metrics
const radarCategories = ['Intent Fit', 'Citation Authority', 'Evidence Coverage', 'Signal Alignment', 'Action Priority'];
const radarTraces = studyRows.map(r => {
  const m = metrics[r.cluster_id] || {};
  const vals = [
    m.relevance_score || 0,
    m.source_trust_score || 0,
    m.proof_strength_score || 0,
    m.method_agreement_score || 0,
    m.opportunity_score || 0
  ];
  return {
    type: 'scatterpolar',
    r: [...vals, vals[0]],
    theta: [...radarCategories, radarCategories[0]],
    name: r.cluster_label,
    fill: 'toself',
    opacity: 0.5,
    line: { color: topicColors[r.gap_type || 'stronghold'] || palette.gray }
  };
});
Plotly.newPlot('radarChart', radarTraces, {
  paper_bgcolor: '#FFFFFF',
  plot_bgcolor: '#FFFFFF',
  font: { family: 'Geist Variable, system-ui, sans-serif', size: 12, color: palette.fg },
  margin: { t: 40, r: 60, b: 40, l: 60 },
  polar: {
    bgcolor: '#FFFFFF',
    radialaxis: { visible: true, range: [0, 100], gridcolor: palette.grid },
    angularaxis: { gridcolor: palette.grid }
  },
  legend: { orientation: 'h', x: 0, y: -0.15, font: { size: 11 } },
  showlegend: true
}, plotConfig);

document.getElementById('exportCards').innerHTML = [
  ['Presence verdict', 'PRESENCE_VERDICT.md', 'Executive diagnosis, topic findings, evidence chain, and methodology.'],
  ['Action brief', 'ACTION_BRIEF.md', 'Actions grouped by gap type, claim boundaries, and monitoring plan.'],
  ['Evidence ledger', 'EVIDENCE_LEDGER.json', 'Machine-readable claims, source refs, confidence tiers, and publication status.'],
  ['Dashboard', 'mvp_dashboard.html', 'The current webapp view rendered from generated artifacts.']
].map(([label, artifact, copy]) => `
  <article class="decision-card">
    <div class="decision-card-header">
      <h3>${escapeHtml(label)}</h3>
      ${pill('artifact')}
    </div>
    <p><strong>${escapeHtml(artifact)}</strong></p>
    <p>${escapeHtml(copy)}</p>
  </article>
`).join('');
</script>
</body>
</html>
"""
    )


def build_dashboard(
    study: StudySsot,
    *,
    classification: GapClassification | None = None,
    ledger: EvidenceLedger | None = None,
    metrics: ValueAddedMetrics | None = None,
    landscape: CompetitorLandscape | None = None,
    tavily: TavilyEvidence | None = None,
    prescription: PrescriptionPlan | None = None,
    gemini: GeminiAnalysis | None = None,
) -> str:
    return _html(
        study, classification, ledger, metrics, landscape, tavily, prescription,
        gemini=gemini,
    )


def write_dashboard(content: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(content)
    return path


def main(
    study: Annotated[Path, typer.Option("--study")] = Path("data/generated/study_ssot.json"),
    out: Annotated[Path, typer.Option("--out")] = Path("artifacts/local"),
    classification: Annotated[Path | None, typer.Option("--classification")] = Path(
        "data/generated/gap_classification.json"
    ),
    ledger: Annotated[Path | None, typer.Option("--ledger")] = Path(
        "data/generated/EVIDENCE_LEDGER.json"
    ),
    metrics: Annotated[Path | None, typer.Option("--metrics")] = Path(
        "data/generated/value_added_metrics.json"
    ),
    landscape: Annotated[Path | None, typer.Option("--landscape")] = Path(
        "data/generated/competitor_landscape.json"
    ),
    tavily: Annotated[Path | None, typer.Option("--tavily")] = Path(
        "data/generated/tavily_evidence.json"
    ),
    prescription: Annotated[Path | None, typer.Option("--prescription")] = Path(
        "data/generated/prescription_plan.json"
    ),
) -> None:
    content = build_dashboard(
        StudySsot.model_validate_json(study.read_text()),
        classification=_read_optional(classification, GapClassification),
        ledger=_read_optional(ledger, EvidenceLedger),
        metrics=_read_optional(metrics, ValueAddedMetrics),
        landscape=_read_optional(landscape, CompetitorLandscape),
        tavily=_read_optional(tavily, TavilyEvidence),
        prescription=_read_optional(prescription, PrescriptionPlan),
    )
    path = write_dashboard(content, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
