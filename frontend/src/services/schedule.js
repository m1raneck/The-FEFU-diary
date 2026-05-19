const API_URL = import.meta.env.VITE_API_URL || 'http://localhost'

export async function getSchedule() {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_URL}/api/schedule`, { headers: { 'Authorization': `Bearer ${token}` } })                    

  if (!response.ok) {
    throw new Error('Не удалось загрузить расписание')
  }

  return response.json()
}
