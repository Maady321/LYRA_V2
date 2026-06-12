/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: 'var(--bg-primary)',
        darkSurface: 'var(--bg-secondary)',
        darkAccent: 'var(--bg-tertiary)',
        
        'panel-bg': 'var(--panel-bg)',
        'panel-hover': 'var(--panel-hover)',

        'gold-primary': 'var(--gold-primary)',
        'gold-elite': 'var(--gold-elite)',
        'gold-bright': 'var(--gold-bright)',
        'gold-deep': 'var(--gold-deep)',
        
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        
        'border-primary': 'var(--border-primary)',
        'border-hover': 'var(--border-hover)',

        // Keep explicit system colors for critical/warning states where necessary, 
        // though we want the dominant UI to be Black/Gold.
        socCritical: '#FF5252',
        socWarning: '#FFB020',
        socInfo: '#FFD700', // Info mapped to gold-primary
        socSuccess: '#FFD700', // Success mapped to gold-primary
      },
      boxShadow: {
        glow: '0 0 10px rgba(255,215,0,.25), 0 0 25px rgba(255,215,0,.15)',
        premium: '0 0 15px rgba(255,215,0,.35), 0 0 40px rgba(255,215,0,.20), 0 0 80px rgba(255,215,0,.10)',
        threat: '0 0 20px rgba(255,82,82,.4)',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
