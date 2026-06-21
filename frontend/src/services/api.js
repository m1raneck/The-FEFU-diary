const API_URL = import.meta.env.VITE_API_URL ?? ''

export function getToken() {
  return localStorage.getItem('token')
}

export function getAuthHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

function handleUnauthorized() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  if (!window.location.pathname.startsWith('/login')) {
    window.location.href = '/login'
  }
}

function formatApiError(err, status) {
  const detail = Array.isArray(err.detail)
    ? err.detail.map(d => d.msg || JSON.stringify(d)).join('; ')
    : (err.detail || err.message)
  return detail || `Ошибка запроса (${status})`
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  })

  if (response.status === 401) {
    handleUnauthorized()
    throw new Error('Сессия истекла')
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(formatApiError(err, response.status))
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }
  return response
}

export async function apiGet(path) {
  return apiRequest(path)
}

export async function apiPost(path, body) {
  return apiRequest(path, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

/** POST without Authorization header — for login/register */
export async function apiPublicPost(path, body) {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(formatApiError(err, response.status))
  }

  return response.json()
}

export async function apiPut(path, body) {
  return apiRequest(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

export async function apiDelete(path) {
  return apiRequest(path, { method: 'DELETE' })
}

export { API_URL }
