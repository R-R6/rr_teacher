import { createSSRApp } from 'vue'
import App from './App.vue'
import { createStore } from './store/index.js'

export function createApp() {
  const app = createSSRApp(App)
  const store = createStore()
  app.config.globalProperties.$store = store
  app.provide('store', store)
  return { app }
}
