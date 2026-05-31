import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#4C3AFF",
        secondary: "#6C5CE7",
        accent: "#FFB800",
        danger: "#FF3B30",
        success: "#2ECC71",
        bg: "#F5F6FA",
        card: "#FFFFFF",
      },
      fontFamily: {
        sans: ["Inter", "SF Pro Display", "-apple-system", "BlinkMacSystemFont",
               "Segoe UI", "Roboto", "sans-serif"],
      },
      boxShadow: {
        card: "0 4px 12px rgba(0,0,0,0.08)",
        hover: "0 6px 18px rgba(0,0,0,0.12)",
      },
      borderRadius: { xl2: "16px" },
      keyframes: {
        fadeIn: { "0%": { opacity: "0", transform: "translateY(6px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideUp: { "0%": { opacity: "0", transform: "translateY(16px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        pulseRing: { "0%,100%": { boxShadow: "0 0 0 0 rgba(255,59,48,0.5)" }, "50%": { boxShadow: "0 0 0 7px rgba(255,59,48,0)" } },
        scanLine: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(170px)" } },
      },
      animation: {
        fadeIn: "fadeIn 0.4s ease-out both",
        slideUp: "slideUp 0.35s ease-out both",
        pennyPulse: "pulseRing 1.6s ease-in-out infinite",
        scan: "scanLine 2.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
