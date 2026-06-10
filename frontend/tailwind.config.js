/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Syne", "sans-serif"],
        body: ["DM Sans", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      colors: {
        bg: "#080b12",
        surface: "#0f1520",
        "surface-alt": "#161d2e",
        border: "#1e2a3d",
        "border-light": "#2a3a52",
        accent: "#22d3ee",
        "accent-dim": "#0e7490",
        verified: "#22c55e",
        disputed: "#f59e0b",
        false: "#ef4444",
        unverified: "#94a3b8",
      },
      fontSize: {
        display: "clamp(2.5rem, 8vw, 5rem)",
        heading: "clamp(1.5rem, 4vw, 2.5rem)",
        score: "clamp(3rem, 10vw, 6rem)",
      },
      letterSpacing: {
        tight: "-0.04em",
        wide: "0.08em",
        widest: "0.15em",
      },
      borderRadius: {
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "24px",
      },
      animation: {
        "fade-up": "fade-up 0.6s ease-out forwards",
        "fade-in": "fade-in 0.4s ease-out forwards",
        "scale-in": "scale-in 0.5s ease-out forwards",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
