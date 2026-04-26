"use client";

import { useBrand } from "@/hooks/useBrand";
import { BrandTabs } from "./BrandTabs";

export function Topbar() {
  const { data, loading } = useBrand();
  const tavilySources = data?.tavily?.summary?.sources ?? 0;
  const dataMode = tavilySources > 0 ? "Live + synthetic" : "Synthetic seed";

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between gap-4 min-h-[56px] px-6 bg-peec-surface/90 backdrop-blur border-b border-peec-hairline">
      <div className="flex items-center gap-3">
        <span className="font-medium tracking-tight">Presence Rx</span>
        <span className="text-peec-muted text-peec-sm">AI Visibility Diagnosis</span>
      </div>
      <div className="flex items-center gap-3">
        <BrandTabs />
        <span className="text-peec-xs text-peec-muted px-2 py-1 rounded-peec-md bg-peec-tint">
          {loading ? "Loading..." : dataMode}
        </span>
      </div>
    </header>
  );
}
