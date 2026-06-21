import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import StudentGradesPage from '@/views/StudentGradesPage.vue'
import { getStoredUser, isStudent } from '@/services/auth'
import AllGradesPage from '@/views/AllGradesPage.vue'

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
    component: () => import('@/views/SchedulePage.vue')
  },
  {
    path: '/my-grades',
    name: 'MyGrades',
    component: StudentGradesPage,
    meta: { requiresAuth: true, studentOnly: true }
  },
  {
    path: '/all-grades',
    name: 'AllGrades',
    component: AllGradesPage,
    meta: { requiresAuth: true, role: 'teacher' },
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next('/')
    return
  }
  if (to.meta.studentOnly && !isStudent(getStoredUser())) {
    next('/schedule')
    return
  }
  next()
})

export default router