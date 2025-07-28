import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import IpLookup from '../views/IpLookup.vue'
import Guide from '../views/Guide.vue'
import FAQ from '../views/FAQ.vue'
import About from '../views/About.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/ip-lookup',
      name: 'IpLookup',
      component: IpLookup
    },
    {
      path: '/guide',
      name: 'Guide',
      component: Guide
    },
    {
      path: '/faq',
      name: 'FAQ',
      component: FAQ
    },
    {
      path: '/about',
      name: 'About',
      component: About
    }
  ]
})

export default router
