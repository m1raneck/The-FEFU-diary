const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  return data
}

export function logout() {
  localStorage.removeItem('token')
}

export function getToken() {
  return localStorage.getItem('token')
}
