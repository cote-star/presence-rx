"use client";

import { BrandProvider } from "@/hooks/useBrand";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <BrandProvider>
      <div className="lg:grid lg:grid-cols-[220px_1fr] min-h-screen">
        <div className="hidden lg:block">
          <Sidebar />
        </div>
        <main className="bg-peec-surface lg:border-l border-peec-hairline min-w-0">
          <Topbar />
          <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-5">
            {children}
          </div>
        </main>
      </div>
    </BrandProvider>
  );
}
