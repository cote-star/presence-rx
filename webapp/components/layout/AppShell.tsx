"use client";

import { BrandProvider } from "@/hooks/useBrand";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <BrandProvider>
      <div className="grid grid-cols-[220px_1fr] min-h-screen">
        <Sidebar />
        <main className="bg-peec-surface border-l border-peec-hairline min-w-0">
          <Topbar />
          <div className="max-w-[1280px] mx-auto px-6 py-5">{children}</div>
        </main>
      </div>
    </BrandProvider>
  );
}
