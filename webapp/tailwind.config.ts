import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "peec-bg": "#FFFFFF",
        "peec-surface": "#FDFDFD",
        "peec-fg": "#171717",
        "peec-muted": "rgba(23,23,23,0.6)",
        "peec-subtle": "rgba(23,23,23,0.5)",
        "peec-hover": "rgba(23,23,23,0.08)",
        "peec-tint": "rgba(23,23,23,0.04)",
        "peec-hairline": "rgba(23,23,23,0.08)",
        "pill-green": "rgb(22,163,74)",
        "pill-green-bg": "rgba(22,163,74,0.10)",
        "pill-red": "#FB2C36",
        "pill-red-bg": "rgba(251,44,54,0.10)",
        "pill-orange": "rgb(234,88,12)",
        "pill-orange-bg": "rgba(234,88,12,0.10)",
        "pill-indigo": "rgb(79,70,229)",
        "pill-indigo-bg": "rgba(79,70,229,0.10)",
        "pill-purple": "rgb(124,58,237)",
        "pill-purple-bg": "rgba(124,58,237,0.10)",
        "pill-cyan": "rgb(0,146,184)",
        "pill-cyan-bg": "rgba(0,146,184,0.10)",
      },
      fontFamily: {
        sans: [
          "Geist Variable",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
      },
      borderRadius: {
        "peec-sm": "6px",
        "peec-md": "8px",
        "peec-lg": "10px",
        "peec-xl": "12px",
      },
      fontSize: {
        "peec-xs": "12px",
        "peec-sm": "13px",
        "peec-base": "14px",
        "peec-lg": "16px",
        "peec-xl": "20px",
      },
      boxShadow: {
        "peec-ring":
          "inset 0 0 0 1px rgba(23,23,23,0), 0 1px 3px 0 rgba(23,23,23,0.06), 0 0 0 1px rgba(23,23,23,0.08)",
      },
    },
  },
  plugins: [],
};
export default config;
