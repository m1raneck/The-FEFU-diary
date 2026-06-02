const API_URL = import.meta.env.VITE_API_URL || 'http://localhost'

function authHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
}

export async function getStudents() {
  const response = await fetch(`${API_URL}/api/users/students`, {
    headers: authHeaders()
  })
  if (!response.ok) throw new Error('Не удалось загрузить студентов')
  return response.json()
}

export async function getGrades(scheduleId) {
  const url = scheduleId
    ? `${API_URL}/api/grades?schedule_id=${scheduleId}`
    : `${API_URL}/api/grades`
  const response = await fetch(url, { headers: authHeaders() })
  if (!response.ok) throw new Error('Не удалось загрузить оценки')
  return response.json()
}

export async function getAttendance(scheduleId) {
  const url = scheduleId
    ? `${API_URL}/api/attendance?schedule_id=${scheduleId}`
    : `${API_URL}/api/attendance`
  const response = await fetch(url, { headers: authHeaders() })
  if (!response.ok) throw new Error('Не удалось загрузить посещаемость')
  return response.json()
}

export async function saveGrade({ studentId, scheduleId, grade, gradeDate, comment = '' }) {
  const response = await fetch(`${API_URL}/api/grades`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({
      student_id: studentId,
      schedule_id: scheduleId,
      grade,
      grade_date: gradeDate,
      comment
    })
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Не удалось сохранить оценку')
  }
  return response.json()
}

export async function saveAttendance({ studentId, scheduleId, status, date, comment = '' }) {
  const response = await fetch(`${API_URL}/api/attendance`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({
      student_id: studentId,
      schedule_id: scheduleId,
      status,
      record_date: date,
      comment
    })
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Не удалось сохранить посещаемость')
  }
  return response.json()
}

export async function bulkSaveGrades({ scheduleId, gradeDate, grades }) {
  const response = await fetch(`${API_URL}/api/grades/bulk`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({
      schedule_id: scheduleId,
      grade_date: gradeDate,
      grades
    })
  })
  return response.json()
}
