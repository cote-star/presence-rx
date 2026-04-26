"use client";

import { useBrand } from "@/hooks/useBrand";

const BRAND_LABELS: Record<string, string> = {
  "nothing-phone": "Nothing Phone",
  attio: "Attio",
  bmw: "BMW",
};

export function BrandTabs() {
  const { brands, currentBrand, switchBrand } = useBrand();

  return (
    <div className="flex items-center gap-0.5 p-0.5 rounded-peec-md bg-peec-tint">
      {brands.map((caseId) => (
        <button
          key={caseId}
          onClick={() => switchBrand(caseId)}
          className={`px-3 h-7 rounded-peec-sm text-peec-sm font-medium transition-all ${
            currentBrand === caseId
              ? "bg-white text-peec-fg shadow-peec-ring"
              : "text-peec-muted hover:text-peec-fg"
          }`}
        >
          {BRAND_LABELS[caseId] || caseId}
        </button>
      ))}
    </div>
  );
}
