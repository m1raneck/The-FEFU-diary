const API_URL = import.meta.env.VITE_API_URL || 'http://localhost'

export async function login(email, password) {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login: email, password })
  })

  const data = await response.json()

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
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Не авторизован')

  const response = await fetch(`${API_URL}/api/users/me`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!response.ok) throw new Error('Не удалось загрузить профиль')

  const data = await response.json()
  if (data.status !== 'success') throw new Error(data.message || 'Ошибка профиля')
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

export function getToken() {
  return localStorage.getItem('token')
}
