import { createApp } from 'vue'
import './assets/styles/variables.css'
import './assets/styles/components.css'
import App from './App.vue'
import router from './router'
import frontendSeoService from './services/seoService'

const app = createApp(App)

// 初始化SEO配置
frontendSeoService.initializeSeo()

app.use(router).mount('#app')
