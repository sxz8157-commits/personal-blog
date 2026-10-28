import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: '/',
  publicDir: false,
  plugins: [vue()],
  worker: { format: 'es' },
  // 当前 CSS 压缩器会丢弃标准 backdrop-filter，保留声明以兼容玻璃效果。
  build: { cssMinify: false },
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, '.')
    }
  },
  server: {
    port: 4000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false
      },
      '/toux': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false
      }
    }
  }
})
