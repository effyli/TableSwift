import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        danger: "#E94560", // Red
        success: "#53CB7D", // Green

        black: {
          DEFAULT: "#111111", // Primary black
          light: "#151515", // Slightly lighter
          lighter: "#202020", // Even lighter
        },

        // Neutral grays
        gray: {
          DEFAULT: "#E0E0E0", // Medium gray
          light: "#F5F5F5", // Light gray
        },

        // Pure white for accents
        white: "#FFFFFF",
      },
    },
  },
  plugins: [],
};

export default config;
