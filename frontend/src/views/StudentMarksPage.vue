<template>
  <div class="modal-overlay" :class="{ 'is-mobile': isMobile }" @click.self="$emit('close')">
    <div class="marks-card">
      <div class="card-header">
        <div class="subject-badge">{{ subjectName }}</div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div v-if="loading" class="state-message">Загрузка...</div>
      <div v-else-if="error" class="state-message error">{{ error }}</div>
      <div v-else-if="rows.length === 0" class="state-message">Нет оценок по этому предмету</div>

      <div v-else class="table-container">
        <table class="marks-table">
          <thead>
            <tr>
              <th>Дата</th>
              <th class="col-center">Оценка</th>
              <th class="col-center">Посещение</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.date">
              <td class="date-cell">{{ row.dateLabel }}</td>
              <td class="grade-cell col-center">
                <span v-if="!isMobile" class="grade-value" :class="gradeClass(row.grade)">{{ row.grade ?? '—' }}</span>
                <span v-else class="grade-chip" :class="gradeChipClass(row.grade)">{{ formatGrade(row.grade) }}</span>
              </td>
              <td class="attendance-cell col-center">
                <span v-if="!isMobile" class="attendance-icon" :class="row.present === true ? 'present' : (row.present === false ? 'absent' : '')">{{ row.present === true ? '✓' : (row.present === false ? '✗' : '—') }}</span>
                <span v-else class="attendance-chip" :class="attendanceChipClass(row.present)">{{ attendanceText(row.present) }}</span>
              </td>
              <td class="comment-cell">{{ row.comment || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="avg !== null" class="card-footer">
        <span class="stat">Средний балл: <b>{{ avg }}</b></span>
        <span class="divider">|</span>
        <span class="stat">Посещаемость: <b>{{ attendancePct }}%</b></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { getGrades, getAttendance, getLessonComments, normalizeDate } from '@/services/marks'

const props = defineProps({
  subjectName: { type: String, default: '' },
  scheduleId: { type: Number, required: true }
})
defineEmits(['close'])

const loading = ref(true)
const error = ref('')
const rows = ref([])
const isMobile = ref(false)

const avg = computed(() => {
  const nums = rows.value.map(r => r.grade).filter(g => g != null && !isNaN(g))
  if (!nums.length) return null
  return Math.round(nums.reduce((a, b) => a + b, 0) / nums.length)
})

const attendanceCount = computed(() =>
  rows.value.filter(r => r.present === true).length
)

const attendancePct = computed(() => {
  const known = rows.value.filter(r => r.present !== null)
  if (!known.length) return 0
  return Math.round((attendanceCount.value / known.length) * 100)
})

function gradeClass(grade) {
  if (grade == null) return ''
  if (grade >= 80) return 'good'
  if (grade >= 60) return 'mid'
  return 'low'
}

function gradeChipClass(grade) {
  if (grade === '+') return 'chip-plus'
  if (grade === '-') return 'chip-minus'
  const num = parseFloat(grade)
  if (!isNaN(num)) {
    if (num >= 4) return 'chip-good'
    return 'chip-bad'
  }
  return 'chip-empty'
}
function formatGrade(grade) {
  if (grade === '+') return '+'
  if (grade === '-') return '−'
  if (grade == null) return '—'
  return grade
}
function attendanceChipClass(present) {
  if (present === null) return ''
  return present ? 'chip-present' : 'chip-absent'
}
function attendanceText(present) {
  if (present === null) return '—'
  return present ? '✓' : '✗'
}

function formatDate(iso) {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [grades, attendance, lessonComments] = await Promise.all([
      getGrades(props.scheduleId),
      getAttendance(props.scheduleId),
      getLessonComments(props.scheduleId),
    ])

    const dateSet = new Set()
    grades.forEach(g => dateSet.add(normalizeDate(g.grade_date)))
    attendance.forEach(a => dateSet.add(normalizeDate(a.date)))
    lessonComments.forEach(c => dateSet.add(normalizeDate(c.lesson_date)))
    const dates = [...dateSet].filter(Boolean).sort()

    rows.value = dates.map(iso => {
      const g = grades.find(x => normalizeDate(x.grade_date) === iso)
      const a = attendance.find(x => normalizeDate(x.date) === iso)
      const c = lessonComments.find(x => normalizeDate(x.lesson_date) === iso)
      return {
        date: iso,
        dateLabel: formatDate(iso),
        grade: g?.grade ?? null,
        comment: c?.comment || '',
        present: a ? (a.status === 'present' || a.status === 'late') : null
      }
    })
  } catch (e) {
    error.value = e.message || 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

function checkIfMobile() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkIfMobile()
  window.addEventListener('resize', checkIfMobile)
  load()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkIfMobile)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-image: url('@/assets/image.png');
  background-size: cover;
  background-position: center;
  background-color: #97b0c9;
  background-blend-mode: overlay;
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  font-family: 'Inter', system-ui, sans-serif;
}

.marks-card {
  width: 100%;
  max-width: 720px;
  max-height: 80vh;
  background: linear-gradient(145deg, rgba(245, 250, 255, 0.65) 22%, rgba(210, 230, 245, 0.45) 79%, rgba(180, 205, 225, 0.65) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 28px;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem;
  background: rgba(227, 240, 255, 0.35);
  border-bottom: 1px solid rgba(86, 112, 193, 0.25);
  flex-shrink: 0;
}

.subject-badge {
  background: rgba(102, 137, 202, 0.8);
  border-radius: 44px;
  padding: 10px 28px;
  font-size: 20px;
  font-weight: 700;
  color: #f0f5fc;
  letter-spacing: -0.3px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.close-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.9);
  font-size: 24px;
  font-weight: 600;
  color: #2c3e4f;
  cursor: pointer;
  transition: 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.close-btn:hover {
  background: rgba(255, 255, 255, 0.85);
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.state-message {
  padding: 3rem 2rem;
  text-align: center;
  font-size: 18px;
  font-weight: 500;
  color: #2c3e4f;
  background: rgba(255,255,255,0.4);
}
.state-message.error {
  color: #b13b3b;
}

.table-container {
  margin: 1.8rem 2rem;
  overflow-x: auto;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(2px);
  border: 0.5px solid rgba(111, 138, 202, 0.9);
  flex: 1;
}

.marks-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px;
}

.marks-table th {
  background: rgba(206, 225, 255, 0.5);
  padding: 14px 12px;
  font-weight: 700;
  color: #1f4a6e;
  border-bottom: 1px solid rgba(102, 139, 190, 0.4);
}

.marks-table td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid rgba(116, 149, 197, 0.3);
  background: rgba(255, 255, 255, 0.6);
  color: #1a2c44;
}

.grade-value {
  font-weight: 700;
  font-size: 18px;
}
.grade-value.good { color: #1f6e43; }
.grade-value.mid  { color: #b76e00; }
.grade-value.low  { color: #b13b3b; }

.attendance-icon {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  border-radius: 50%;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}
.attendance-icon.present {
  background: #5fba8a;
  color: white;
}
.attendance-icon.absent {
  background: #e58e8e;
  color: white;
}
.attendance-icon:not(.present):not(.absent) {
  background: rgba(200, 200, 210, 0.6);
  color: #4a6f8c;
}

.comment-cell {
  max-width: 200px;
  word-break: break-word;
  font-style: italic;
  color: #4a6f8c;
}

.card-footer {
  padding: 1rem 2rem;
  background: rgba(227, 240, 255, 0.4);
  border-top: 1px solid rgba(86, 112, 193, 0.3);
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  color: #1f4a6e;
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-shrink: 0;
}
.stat b {
  font-weight: 800;
  color: #283347;
}
.divider {
  opacity: 0.5;
}


.modal-overlay.is-mobile {
  background: url('@/assets/phone.PNG') left center / cover no-repeat;
  background-color: #6b8cae;
  background-blend-mode: lighten;
  padding: 0.5rem;
}

.modal-overlay.is-mobile .marks-card {
  max-width: 100%;
  max-height: 55vh;
  border-radius: 24px;
  background: rgba(243, 247, 255, 0.55);
  backdrop-filter: blur(12px);
  border: none;
  box-shadow: none;
}

.modal-overlay.is-mobile .card-header {
  padding: 0.6rem 0.8rem;
  border-bottom: none;
}

.modal-overlay.is-mobile .subject-badge {
  font-size: 14px;
  padding: 5px 14px;
  border-radius: 20px;
}

.modal-overlay.is-mobile .close-btn {
  width: 30px;
  height: 30px;
  font-size: 16px;
}

.modal-overlay.is-mobile .table-container {
  padding: 0.3rem;
  margin: 0 0.3rem 0.3rem;
  border-radius: 12px;
  overflow-x: visible;
}

.modal-overlay.is-mobile .marks-table {
  table-layout: fixed;
  border-radius: 12px;
  overflow: hidden;
}

.modal-overlay.is-mobile .date-cell { width: 20%; }
.modal-overlay.is-mobile .grade-cell { width: 22%; }
.modal-overlay.is-mobile .attendance-cell { width: 18%; }
.modal-overlay.is-mobile .comment-cell { width: 40%; }

.modal-overlay.is-mobile .marks-table th {
  white-space: nowrap;
}

.modal-overlay.is-mobile .marks-table th,
.modal-overlay.is-mobile .marks-table td {
  padding: 5px 4px;
  font-size: 10px;
}

.grade-chip,
.attendance-chip {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 40px;
  font-weight: 600;
  font-size: 10px;
  min-width: 40px;
  text-align: center;
}
.chip-good, .chip-plus { background: #8bc9a5; color: #1d4d2d; }
.chip-bad, .chip-minus { background: #e8b0b0; color: #a14242; }
.chip-empty { background: #b8cfe8; color: #2c4e6e; }
.chip-present { background: #8bc9a5; color: #1d4d2d; font-size: 13px; padding: 2px 8px; }
.chip-absent { background: #e8b0b0; color: #a14242; font-size: 13px; padding: 2px 8px; }

.modal-overlay.is-mobile .marks-table tbody tr:last-child td {
  border-bottom: none;
}

.modal-overlay.is-mobile .card-footer {
  padding: 0.5rem 0.8rem;
  font-size: 12px;
  gap: 8px;
}

@media (max-width: 640px) {
  .marks-card {
    max-width: 95%;
  }
}
</style>
