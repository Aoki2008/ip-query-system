import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: 'localhost',
    port: 8080,
    strictPort: false,
    open: false
  },
  preview: {
    host: 'localhost',
    port: 8080
  }
})
