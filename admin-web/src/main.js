import { createApp } from 'vue'

import App from './App.vue'
import router from './router/index.js'
import { hydrateAuthState } from './stores/auth.js'
import './styles/global.css'

hydrateAuthState()

createApp(App).use(router).mount('#app')
