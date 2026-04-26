import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Presence Rx — AI Visibility Diagnosis",
  description:
    "Diagnose how brands show up in AI-mediated discovery. Find blind spots, check claims, prescribe actions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} font-sans bg-peec-bg text-peec-fg antialiased`}
      >
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
