import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import SchedulePage from '@/views/SchedulePage.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: SchedulePage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Защита маршрутов — если нет токена, редирект на логин
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next('/')
  } else {
    next()
  }
})

export default router
