"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileWarning,
  Search,
  BarChart3,
  Rocket,
  ClipboardCheck,
  Download,
} from "lucide-react";

const NAV_GROUPS = [
  {
    label: "Overview",
    items: [
      { href: "/", label: "Action Brief", icon: LayoutDashboard },
    ],
  },
  {
    label: "Diagnosis",
    items: [
      { href: "/diagnosis", label: "Blind Spots", icon: Search },
    ],
  },
  {
    label: "Evidence",
    items: [
      { href: "/evidence", label: "Claims & Simulator", icon: ClipboardCheck },
    ],
  },
  {
    label: "Analytics",
    items: [
      { href: "/analytics", label: "Charts", icon: BarChart3 },
    ],
  },
  {
    label: "Future",
    items: [
      { href: "/future", label: "Directions", icon: Rocket },
    ],
  },
  {
    label: "Export",
    items: [
      { href: "/export", label: "Download", icon: Download },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 h-screen flex flex-col gap-4 p-4 bg-peec-bg overflow-y-auto">
      <div className="flex items-center gap-2 px-2 py-1.5 rounded-peec-xl shadow-peec-ring bg-peec-surface">
        <div className="w-6 h-6 rounded-peec-sm bg-peec-fg text-white flex items-center justify-center text-xs font-semibold">
          P
        </div>
        <span className="font-medium text-sm truncate">Presence Rx</span>
        <span className="text-peec-muted text-xs ml-auto">v2</span>
      </div>

      {NAV_GROUPS.map((group) => (
        <nav key={group.label} className="grid gap-0.5">
          <div className="px-2 pb-0.5 text-peec-subtle text-peec-sm font-medium">
            {group.label}
          </div>
          {group.items.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-2 h-8 rounded-peec-xl font-medium text-sm transition-colors ${
                  active
                    ? "bg-peec-hover text-peec-fg"
                    : "text-peec-fg hover:bg-peec-tint"
                }`}
              >
                <item.icon size={16} className="text-peec-muted" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      ))}

      <div className="mt-auto px-2 py-2 rounded-peec-xl bg-peec-tint text-peec-muted text-peec-xs">
        Big Berlin Hack 2026
        <br />
        Peec AI Track
      </div>
    </aside>
  );
}
