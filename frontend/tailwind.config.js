/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkBg: "#060A13",       // Dark obsidian background
        darkSurface: "#0E1424",  // Surface panels
        darkAccent: "#1A2540",   // Soft highlight
        brandBlue: "#00E5FF",    // Lyra primary core cyan
        brandPurple: "#7000FF",  // Lyra secondary accent
        brandIndigo: "#3F51B5",  // Lyra brand Indigo
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        premium: '0 4px 30px rgba(0, 0, 0, 0.4)',
        glow: '0 0 15px rgba(0, 229, 255, 0.25)',
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
