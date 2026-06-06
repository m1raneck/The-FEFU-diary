import { apiGet, apiPost, apiPut } from './api'

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

export async function getGradeScale(scheduleId) {
  return apiGet(`/api/grades/scale?schedule_id=${scheduleId}`)
}

export async function saveGradeScale(scheduleId, rules) {
  return apiPut('/api/grades/scale', { schedule_id: scheduleId, rules })
}

export async function getGradeCategories(scheduleId) {
  return apiGet(`/api/grades/categories?schedule_id=${scheduleId}`)
}

export async function saveGradeCategories(scheduleId, categories) {
  return apiPut('/api/grades/categories', { schedule_id: scheduleId, categories })
}

export async function convertScore(scheduleId, rawScore) {
  return apiPost('/api/grades/convert', { schedule_id: scheduleId, raw_score: rawScore })
}

export async function calculateFinalGrade(scheduleId, entries) {
  return apiPost('/api/grades/calculate-final', { schedule_id: scheduleId, entries })
}

export async function saveGrade({
  studentId,
  scheduleId,
  grade,
  rawScore,
  categoryId,
  gradeDate,
  comment = '',
  autoConvert = false,
}) {
  return apiPost('/api/grades', {
    student_id: studentId,
    schedule_id: scheduleId,
    grade,
    raw_score: rawScore,
    category_id: categoryId,
    grade_date: gradeDate,
    comment,
    auto_convert: autoConvert,
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
