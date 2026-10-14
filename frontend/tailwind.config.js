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
        app: {
          bg: '#090A0F',
          surface: '#11131A',
          elevated: '#181B24',
          subtle: '#1E2230',
        },
        border: {
          subtle: '#232738',
          strong: '#33394D',
        },
        financial: {
          solvency: '#10B981',
          shortfall: '#EF4444',
          warning: '#F59E0B',
          agent: '#6366F1',
          agentSubtle: '#818CF8',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'Courier New', 'monospace'],
      }
    },
  },
  plugins: [],
}
