/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          main: '#050507',
          secondary: '#0A0A0C',
          card: '#111116',
        },
        primary: {
          DEFAULT: '#0000EE',
          bright: '#3D3DFF',
          dark: '#0000AD',
          darker: '#08085E',
          darkest: '#05053D',
        },
        accent: {
          DEFAULT: '#53AC85',
          dark: '#469070',
          darker: '#38755B',
          darkest: '#2B5945',
          deep: '#172B22',
        },
        neutral: {
          100: '#FFFFFF',
          200: '#9E9E9E',
          300: '#808080',
          400: '#575757',
          500: '#333333',
          600: '#212121',
        },
        semantic: {
          success: '#22C55E',
          warning: '#F59E0B',
          critical: '#FF4136',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
