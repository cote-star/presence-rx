"use client";

import { useState } from "react";
import { useBrand } from "@/hooks/useBrand";
import { downloadJSON, captureScreenshot } from "@/lib/export-utils";
import {
  Download,
  FileText,
  Database,
  Camera,
  Package,
  ClipboardList,
} from "lucide-react";

function ExportCard({
  icon: Icon,
  title,
  description,
  buttonLabel,
  onClick,
  disabled,
  busy,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  buttonLabel: string;
  onClick: () => void;
  disabled?: boolean;
  busy?: boolean;
}) {
  return (
    <div className="bg-white rounded-peec-xl shadow-peec-ring p-5 flex flex-col justify-between min-h-[180px]">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Icon size={18} className="text-pill-indigo" />
          <h3 className="font-semibold">{title}</h3>
        </div>
        <p className="text-peec-sm text-peec-muted">{description}</p>
      </div>
      <button
        onClick={onClick}
        disabled={disabled || busy}
        className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-peec-lg bg-peec-fg text-white text-peec-sm font-medium hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
      >
        {busy ? (
          <>
            <span className="animate-spin inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
            Processing...
          </>
        ) : (
          <>
            <Download size={14} />
            {buttonLabel}
          </>
        )}
      </button>
    </div>
  );
}

export default function ExportPage() {
  const { data, currentBrand, loading } = useBrand();
  const [capturing, setCapturing] = useState(false);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-peec-tint rounded animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-44 bg-peec-tint rounded-peec-xl animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  const brandSlug = currentBrand;

  return (
    <div className="space-y-6">
      <div>
        <span className="inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-indigo-bg text-pill-indigo mb-2">
          Export Hub
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          Download Artifacts
        </h1>
        <p className="text-peec-muted mt-1">
          Export the {data.brand_name} Presence Verdict Pack as individual
          downloadable artifacts.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* 1. Presence Verdict */}
        <ExportCard
          icon={FileText}
          title="Presence Verdict"
          description={`Summary of AI visibility diagnosis for ${data.brand_name}. ${data.study.rows.length} topics analysed across ${data.study.rows.filter((r) => r.gap_type).length} identified blind spots.`}
          buttonLabel="View Full Verdict"
          onClick={() => {
            window.location.href = "/";
          }}
        />

        {/* 2. Action Brief */}
        <ExportCard
          icon={ClipboardList}
          title="Action Brief"
          description={`Prioritised action recommendations based on gap classification. ${data.classification?.classified_gaps.filter((g) => g.classification_status === "confirmed").length ?? 0} confirmed gaps with interventions.`}
          buttonLabel="View Action Brief"
          onClick={() => {
            window.location.href = "/";
          }}
        />

        {/* 3. Evidence Ledger */}
        <ExportCard
          icon={Database}
          title="Evidence Ledger"
          description={`Full evidence ledger: ${data.ledger?.claims.length ?? 0} claims, ${data.ledger?.evidence.length ?? 0} evidence items, and ${data.ledger?.blocked_claims.length ?? 0} blocked claims.`}
          buttonLabel="Download JSON"
          disabled={!data.ledger}
          onClick={() => {
            if (data.ledger) {
              downloadJSON(data.ledger, `${brandSlug}-evidence-ledger.json`);
            }
          }}
        />

        {/* 4. Current Page Screenshot */}
        <ExportCard
          icon={Camera}
          title="Page Screenshot"
          description="Capture the current page as a PNG image. Useful for presentations and reports."
          buttonLabel={capturing ? "Capturing..." : "Capture PNG"}
          busy={capturing}
          onClick={async () => {
            setCapturing(true);
            try {
              await captureScreenshot(
                "main",
                `${brandSlug}-screenshot.png`
              );
            } finally {
              setCapturing(false);
            }
          }}
        />

        {/* 5. Pipeline Data */}
        <ExportCard
          icon={Package}
          title="Pipeline Data"
          description={`Complete pipeline output for ${data.brand_name} including study, classification, metrics, landscape, ledger, and Gemini findings.`}
          buttonLabel="Download JSON"
          onClick={() => {
            downloadJSON(data, `${brandSlug}-data.json`);
          }}
        />
      </div>
    </div>
  );
}
