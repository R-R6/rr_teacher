import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig } from '../frontend/node_modules/vite/dist/node/index.js'
import vue from '../frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs'

const projectRoot = fileURLToPath(new URL('.', import.meta.url))
const sharedNodeModules = path.resolve(projectRoot, '../frontend/node_modules')

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(projectRoot, 'src'),
      vue: path.resolve(sharedNodeModules, 'vue/dist/vue.esm-bundler.js'),
      'vue-router': path.resolve(sharedNodeModules, 'vue-router/dist/vue-router.mjs'),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/uploads': 'http://127.0.0.1:8000',
    },
  },
  preview: {
    port: 4174,
  },
})
