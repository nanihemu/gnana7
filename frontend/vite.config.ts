import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev server proxies /api to the Django API so the SPA can live at :5173.
// Set VITE_API_ROOT to point at the real backend in production.
export default defineConfig({
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
