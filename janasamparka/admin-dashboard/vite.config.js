import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Enable access from outside container
    port: 3000,
    watch: {
      usePolling: true, // Enable hot-reload in Docker
    },
    proxy: {
      '/api': {
        target: process.env.DOCKER_ENV === 'true' 
          ? 'http://backend:8000' 
          : 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
