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
      fontSize: {
        'xs': ['0.875rem', { lineHeight: '1.25rem' }],
        'sm': ['1rem', { lineHeight: '1.5rem' }],
        'base': ['1.125rem', { lineHeight: '1.75rem' }],
        'lg': ['1.375rem', { lineHeight: '2rem' }],
        'xl': ['1.5rem', { lineHeight: '2rem' }],
        '2xl': ['1.75rem', { lineHeight: '2.25rem' }],
        '3xl': ['2rem', { lineHeight: '2.5rem' }],
        '4xl': ['2.5rem', { lineHeight: '1.2' }],
        '5xl': ['3rem', { lineHeight: '1.2' }],
        '6xl': ['3.75rem', { lineHeight: '1.2' }],
        '7xl': ['4.5rem', { lineHeight: '1.2' }],
        '8xl': ['6rem', { lineHeight: '1.2' }],
        '9xl': ['8rem', { lineHeight: '1.2' }],
      },
    },
  },
  plugins: [],
}
