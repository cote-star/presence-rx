"use client";

import { HelpCircle } from "lucide-react";
import { useState, useRef, useEffect } from "react";

const GLOSSARY: Record<string, string> = {
  "Avg visibility":
    "Mean share-of-voice across all tracked topics. Higher means the brand appears more often in AI answers.",
  "Avg position":
    "Average rank when the brand is mentioned. 1.0 = always first; lower is better.",
  "Confirmed gaps":
    "Blind spots validated by at least two independent methods (Peec study + Tavily web check).",
  "Claims to avoid":
    "Marketing claims flagged as ownership overclaims. Using these risks credibility.",
  "Avg action priority":
    "Composite 0-100 score weighting gap severity, competitive pressure, and strategic relevance.",
  "Claims reviewed":
    "Total number of marketing claims evaluated in the evidence ledger.",
  "Directional claims":
    "Claims with sufficient evidence to use in external communications, with hedged language.",
  "Blocked claims":
    "Claims that overstate ownership and must not be published externally.",
  "Monitor only":
    "Claims tied to deprioritized topics. Tracked but not actively pursued.",
  "Methods used":
    "Number of independent analysis methods (e.g. Peec visibility, Tavily web search, Gemini classification).",
  "Sources checked":
    "Total evidence references collected from web searches and AI provider responses.",
  "Action Priority":
    "Per-topic 0-100 score combining gap size, competitor strength, and strategic weight.",
  "Owner":
    "The brand that currently dominates AI answers for this topic cluster.",
  "Perception gap":
    "The brand is known but described incorrectly or with outdated traits.",
  "Indexing gap":
    "The brand exists online but AI models fail to retrieve or cite it.",
  "Volume / Frequency gap":
    "Not enough recent content for AI models to surface the brand consistently.",
  "Directional":
    "A claim safe to publish with hedged language, backed by evidence.",
  "Blocked":
    "A claim that overclaims ownership and must not be used externally.",
  "Strong evidence":
    "Claim backed by multiple converging sources with high confidence.",
  "Confidence tier":
    "How robust the evidence is: strong, directional, or blocked.",
  "Publication language":
    "Suggested phrasing for external use that respects evidence boundaries.",
  "Cluster":
    "A group of related search queries that map to one topic (e.g. 'best budget phone').",
  "Visibility share":
    "Percentage of AI-generated answers that mention the brand for a given topic.",
  "Competitor owner":
    "The brand with the highest visibility share for a topic cluster.",
  "Gap type":
    "Classification of why the brand is missing: perception, indexing, or volume/frequency.",
  "Strategic status":
    "Whether a topic is a priority battleground, an emerging opportunity, or deprioritized.",
  "Buying journey stage":
    "Where in the funnel the audience is: awareness, consideration, or decision.",
  Visibility:
    "Percentage of AI-generated answers that mention the brand for a given topic.",
  "Signal Alignment":
    "How consistently independent methods agree on the gap classification. 100% = all methods agree.",
  "Strategic Context":
    "Brand-specific reasoning for why a topic matters or is deprioritized.",
  "Evidence Level":
    "Strength of supporting evidence: strong (multi-source convergence), directional (partial support), or blocked.",
  "Engagement Score":
    "Modeled signal estimating which audiences are most useful to activate next, based on audience fit, gap severity, channel match, and evidence confidence. Illustrative, not measured.",
  "Journey Stage":
    "Where in the buying funnel the audience sits: awareness, consideration, comparison, or purchase.",
  "Non-Priority":
    "A topic the brand has intentionally deprioritized. Tracked for monitoring but not actively pursued.",
  "Claim ceiling":
    "The strongest claim the evidence supports. Going beyond this risks credibility.",
  Perception:
    "AI answers describe the brand with wrong or outdated traits. Fix: messaging correction and reframing.",
  Discovery:
    "AI models fail to find or cite the brand despite it existing online. Fix: structured data and citation optimization.",
  Attention:
    "Not enough recent content for AI models to surface the brand consistently. Fix: content creation and distribution.",
};

export function TermTooltip({ term }: { term: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const definition = GLOSSARY[term];

  useEffect(() => {
    if (!open) return;
    function handleClickOutside(e: MouseEvent) {
      if (
        ref.current &&
        !ref.current.contains(e.target as Node) &&
        tooltipRef.current &&
        !tooltipRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  if (!definition) return null;

  return (
    <span ref={ref} className="relative inline-flex items-center ml-1">
      <span
        role="button"
        tabIndex={0}
        aria-label={`What is ${term}?`}
        onClick={(e) => { e.stopPropagation(); setOpen((prev) => !prev); }}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.stopPropagation(); setOpen((prev) => !prev); } }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className="text-peec-muted hover:text-pill-indigo transition-colors cursor-pointer"
      >
        <HelpCircle size={13} />
      </span>
      {open && (
        <div
          ref={tooltipRef}
          role="tooltip"
          className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 z-50 w-56 rounded-peec-lg bg-gray-900 text-white text-xs leading-relaxed p-2.5 shadow-lg pointer-events-none"
        >
          <div className="font-semibold mb-0.5">{term}</div>
          <div className="text-gray-300">{definition}</div>
          <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-gray-900" />
        </div>
      )}
    </span>
  );
}
