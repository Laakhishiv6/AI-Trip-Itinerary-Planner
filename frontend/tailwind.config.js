/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060914',
          900: '#0b0e1c',
          800: '#0d1224',
          700: '#101828',
          600: '#141d2e',
          500: '#1a2540',
          400: '#1e2d4a',
          300: '#243352',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
