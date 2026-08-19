/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta Tutunaku — inspirada en alebrijes
        alebrije: {
          coral:    '#FF6B6B',
          teal:     '#4ECDC4',
          sky:      '#45B7D1',
          mint:     '#96CEB4',
          gold:     '#FFEAA7',
          violet:   '#A29BFE',
          magenta:  '#FD79A8',
          lime:     '#55EFC4',
          orange:   '#FDCB6E',
          purple:   '#6C5CE7',
        },
        primary: {
          50:  '#fff1f1',
          100: '#ffe0e0',
          200: '#ffc7c7',
          300: '#ff9e9e',
          400: '#ff6b6b',
          500: '#ff3d3d',
          600: '#ed1515',
          700: '#c80d0d',
          800: '#a50f0f',
          900: '#881414',
        },
        dark: {
          bg:       '#0F0F1A',
          surface:  '#1A1A2E',
          card:     '#16213E',
          border:   '#0F3460',
          muted:    '#2D2D44',
        },
      },
      fontFamily: {
        display: ['"Baloo 2"', 'cursive'],
        body:    ['"Nunito"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'bounce-slow':    'bounce 2s infinite',
        'pulse-slow':     'pulse 3s infinite',
        'wiggle':         'wiggle 1s ease-in-out infinite',
        'float':          'float 3s ease-in-out infinite',
        'heart-beat':     'heartbeat 1.5s ease-in-out infinite',
        'slide-up':       'slideUp 0.4s ease-out',
        'slide-down':     'slideDown 0.3s ease-out',
        'fade-in':        'fadeIn 0.5s ease-out',
        'scale-in':       'scaleIn 0.3s ease-out',
        'confetti':       'confetti 0.8s ease-out forwards',
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'rotate(-5deg)' },
          '50%':      { transform: 'rotate(5deg)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-12px)' },
        },
        heartbeat: {
          '0%, 100%': { transform: 'scale(1)' },
          '14%':      { transform: 'scale(1.15)' },
          '28%':      { transform: 'scale(1)' },
          '42%':      { transform: 'scale(1.1)' },
          '70%':      { transform: 'scale(1)' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          from: { opacity: '0', transform: 'translateY(-10px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.85)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        confetti: {
          '0%':   { transform: 'scale(0) rotate(0deg)', opacity: '1' },
          '100%': { transform: 'scale(1.4) rotate(360deg)', opacity: '0' },
        },
      },
      boxShadow: {
        'alebrije': '0 0 20px rgba(255, 107, 107, 0.4), 0 0 40px rgba(78, 205, 196, 0.2)',
        'glow-coral': '0 0 15px rgba(255, 107, 107, 0.5)',
        'glow-teal':  '0 0 15px rgba(78, 205, 196, 0.5)',
        'glow-gold':  '0 0 15px rgba(253, 203, 110, 0.5)',
        'card':       '0 4px 24px rgba(0,0,0,0.08)',
        'card-dark':  '0 4px 24px rgba(0,0,0,0.4)',
      },
      backgroundImage: {
        'alebrije-gradient': 'linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #A29BFE 100%)',
        'dark-gradient':     'linear-gradient(135deg, #0F0F1A 0%, #1A1A2E 50%, #0F3460 100%)',
        'gold-gradient':     'linear-gradient(135deg, #FDCB6E 0%, #E17055 100%)',
      },
    },
  },
  plugins: [],
}
