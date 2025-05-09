/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-color': 'var(--primary-color)',
        'secondary-color': 'var(--secondary-color)',
        'background-color': 'var(--background-color)',
        'sidebar-color': 'var(--sidebar-color)',
        'border-color': 'var(--border-color)',
        'text-color': 'var(--text-color)',
      }
    },
  },
  plugins: [],
}

