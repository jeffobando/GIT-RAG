import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'IBM Plex Sans'", "'Segoe UI'", "sans-serif"],
      },
      boxShadow: {
        panel: "0 10px 30px -18px rgba(15, 23, 42, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
