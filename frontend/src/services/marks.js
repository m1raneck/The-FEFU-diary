import { apiGet, apiPost } from './api'

export async function getStudents() {
  return apiGet('/api/users/students')
}

export async function getGrades(scheduleId) {
  const query = scheduleId ? `?schedule_id=${scheduleId}` : ''
  return apiGet(`/api/grades${query}`)
}

export async function getAttendance(scheduleId) {
  const query = scheduleId ? `?schedule_id=${scheduleId}` : ''
  return apiGet(`/api/attendance${query}`)
}

export async function saveGrade({ studentId, scheduleId, grade, gradeDate, comment = '' }) {
  return apiPost('/api/grades', {
    student_id: studentId,
    schedule_id: scheduleId,
    grade,
    grade_date: gradeDate,
    comment,
  })
}

export async function saveAttendance({ studentId, scheduleId, status, date, comment = '' }) {
  return apiPost('/api/attendance', {
    student_id: studentId,
    schedule_id: scheduleId,
    status,
    record_date: date,
    comment,
  })
}

export async function bulkSaveGrades({ scheduleId, gradeDate, grades }) {
  return apiPost('/api/grades/bulk', {
    schedule_id: scheduleId,
    grade_date: gradeDate,
    grades,
  })
}
