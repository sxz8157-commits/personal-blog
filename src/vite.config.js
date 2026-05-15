import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: './',
  publicDir: '../public',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.')
    }
  },
  server: {
    port: 4000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/toux': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})