// Human-friendly display labels — mirrors presence_rx/display_labels.py

export function humanGapType(gapType: string | null): string {
  const labels: Record<string, string> = {
    perception: "Perception",
    indexing: "Indexing",
    volume_frequency: "Volume / Frequency",
  };
  return gapType ? labels[gapType] || gapType : "Stronghold";
}

export function humanDecision(bucket: string): string {
  const labels: Record<string, string> = {
    act_now: "Act now",
    test_next: "Test next",
    monitor: "Monitor",
    block: "Block",
  };
  return labels[bucket] || bucket.replace(/_/g, " ");
}

export function humanTrend(label: string): string {
  const labels: Record<string, string> = {
    blind_spot: "Blind spot",
    proof_gap: "Evidence gap",
    stronghold: "Stronghold",
    watch: "Watch",
    slow_burn: "Emerging",
  };
  return labels[label] || label.replace(/_/g, " ");
}

export function gapTypeColor(gapType: string | null): string {
  const colors: Record<string, string> = {
    perception: "pill-red",
    indexing: "pill-orange",
    volume_frequency: "pill-purple",
  };
  return gapType ? colors[gapType] || "pill-cyan" : "pill-green";
}

export function gapTypeBgColor(gapType: string | null): string {
  const colors: Record<string, string> = {
    perception: "pill-red-bg",
    indexing: "pill-orange-bg",
    volume_frequency: "pill-purple-bg",
  };
  return gapType ? colors[gapType] || "pill-cyan-bg" : "pill-green-bg";
}
