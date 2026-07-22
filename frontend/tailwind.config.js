/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7ff',
          100: '#ebf0ff',
          200: '#d6e0ff',
          300: '#b3c7ff',
          400: '#85a3ff',
          500: '#5275ff',
          600: '#2b44ff',
          700: '#1a2bee',
          800: '#1421c2',
          900: '#151f9a',
          950: '#0c0f5e',
        }
      }
    },
  },
  plugins: [],
}
