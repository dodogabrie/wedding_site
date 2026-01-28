/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sage: {
          DEFAULT: '#8B9A7D',
          light: '#9DAD8F',
          dark: '#7A8A6D',
        },
        forest: {
          DEFAULT: '#3D4F3D',
          light: '#4D5F4D',
          dark: '#2D3F2D',
        },
        cream: {
          DEFAULT: '#F5F2EB',
          dark: '#EBE8E1',
        },
      },
      fontFamily: {
        script: ['Aniyah', 'cursive'],
        serif: ['Anaktoria', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}
