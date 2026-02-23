import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // All /api/* requests are forwarded to Flask during development.
      // This avoids CORS issues — the browser only ever talks to :5173.
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Output goes into frontend/dist/ — Flask serves this in production.
    outDir: 'dist',
  },
})
