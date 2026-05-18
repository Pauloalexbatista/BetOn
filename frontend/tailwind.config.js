/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F3F3F3",
        cardBg: "#FFFFFF",
        borderBg: "#E4E8F0",
        gold: {
          light: "#FFE57F",
          DEFAULT: "#D4AF37",
          dark: "#AA8C2C"
        },
        emerald: {
          light: "#34D399",
          DEFAULT: "#10B981",
          dark: "#059669"
        },
        neonBlue: "#304FFE"
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        outfit: ["var(--font-outfit)", "sans-serif"]
      }
    },
  },
  plugins: [],
}
