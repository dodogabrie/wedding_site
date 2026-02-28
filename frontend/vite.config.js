import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    hmr: {
      // When behind nginx, HMR WebSocket must target the nginx port
      clientPort: 5180,
      path: '/__vite_hmr',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8022',
        changeOrigin: true
      },
      '/photos': {
        target: 'http://localhost:8022',
        changeOrigin: true
      }
    }
  }
})
