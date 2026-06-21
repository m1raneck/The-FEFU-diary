import { apiGet, apiPublicPost } from './api'

export async function login(email, password) {
  const data = await apiPublicPost('/api/auth/login', { login: email, password })

  if (data.status !== 'success') {
    throw new Error(data.message || 'Ошибка авторизации')
  }

  localStorage.setItem('token', data.data.token)
  await fetchAndStoreProfile()
  return data
}

export async function fetchAndStoreProfile() {
  const profile = await getMe()
  localStorage.setItem('user', JSON.stringify(profile))
  return profile
}

export async function getMe() {
  const data = await apiGet('/api/users/me')
  if (data.status !== 'success') {
    throw new Error(data.message || 'Ошибка профиля')
  }
  return data.data
}

export function getStoredUser() {
  const raw = localStorage.getItem('user')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function isStudent(user = getStoredUser()) {
  return user?.roles?.includes('student') ?? false
}

export function isTeacher(user = getStoredUser()) {
  return user?.roles?.includes('teacher') ?? false
}

export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export async function requestPasswordReset(email) {
  const data = await apiPublicPost('/api/auth/forgot-password', { email })
  if (data.status !== 'success') {
    throw new Error(data.message || 'Ошибка отправки ссылки')
  }
  return data
}

export { getToken } from './api'
