/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1a7f4f',
        secondary: '#f5a623'
      }
    }
  },
  plugins: []
}
