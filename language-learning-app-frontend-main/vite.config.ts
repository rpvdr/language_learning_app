import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: mode === 'development'
          ? 'http://localhost:8000' // локально
          : 'http://backend:8000',  // docker-compose
        changeOrigin: true,
        secure: false,
      },
    },
  },
}))
