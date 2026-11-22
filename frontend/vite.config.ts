import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev server proxies /api to the Django API so the SPA can live at :5173.
// Set VITE_API_ROOT to point at the real backend in production.
// In production (Docker) the app is served by Django, so VITE_BASE=/static/ to
// make asset URLs resolve under Django's STATIC_URL.
export default defineConfig({
  base: process.env.VITE_BASE || '/',
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        // 127.0.0.1 (not localhost) avoids IPv6 (::1) resolution issues.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
