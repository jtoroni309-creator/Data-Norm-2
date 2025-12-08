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
        // Aura AI Brand Color Palette
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        accent: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7c3aed',
          800: '#6b21a8',
          900: '#581c87',
          950: '#3b0764',
        },
        violet: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          950: '#2e1065',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'fluent': '8px',
        'fluent-sm': '4px',
        'fluent-lg': '12px',
      },
      boxShadow: {
        'fluent-2': '0 1.6px 3.6px rgba(0, 0, 0, 0.06), 0 0.3px 0.9px rgba(0, 0, 0, 0.05)',
        'fluent-4': '0 3.2px 7.2px rgba(0, 0, 0, 0.08), 0 0.6px 1.8px rgba(0, 0, 0, 0.06)',
        'fluent-8': '0 6.4px 14.4px rgba(0, 0, 0, 0.1), 0 1.2px 3.6px rgba(0, 0, 0, 0.08)',
        'fluent-16': '0 12.8px 28.8px rgba(0, 0, 0, 0.13), 0 2.4px 7.2px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
