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
              <td class="grade-cell col-center">
  <span v-if="!isMobile" class="grade-value" :class="gradeClass(row.grade)">{{ row.grade ?? '—' }}</span>
  <span v-else class="grade-chip" :class="gradeChipClass(row.grade)">{{ formatGrade(row.grade) }}</span>
</td>
<td class="attendance-cell col-center">
  <span v-if="!isMobile" class="attendance-icon" :class="row.present === true ? 'present' : (row.present === false ? 'absent' : '')">{{ row.present === true ? '✓' : (row.present === false ? '✗' : '—') }}</span>
  <span v-else class="attendance-chip" :class="attendanceChipClass(row.present)">{{ attendanceText(row.present) }}</span>
</td>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { getGrades, getAttendance, getLessonComments, normalizeDate } from '@/services/marks'

const props = defineProps({
  subjectName: { type: String, default: '' },
  scheduleId: { type: Number, required: true }
})
defineEmits(['close'])
const isMobile = ref(false)
const loading = ref(true)
const error = ref('')
const rows = ref([])

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
  if (grade >= 4) return 'good'
  if (grade >= 3) return 'mid'
  return 'low'
}

function checkIfMobile() {
  isMobile.value = window.innerWidth < 768
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
onMounted(() => {
  checkIfMobile()
  window.addEventListener('resize', checkIfMobile)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkIfMobile)
})

</script>

<style scoped>
.modal-overlay {
  inset: 0;
  background-image: url('@/assets/image.png');
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
  background: linear-gradient(145deg, rgba(245, 250, 255, 0.65) 22%, rgba(210, 230, 245, 0.45) 79%, rgba(180, 205, 225, 0.65) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 28px;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem;
  background: rgba(227, 240, 255, 0.35);
  border-bottom: 1px solid rgba(86, 112, 193, 0.25);
}

.subject-badge {
  background: rgba(255, 255, 255, 0.5);
  padding: 8px 18px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  color: #1f4a6e;
  border: 1px solid rgba(100, 160, 200, 0.6);
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(to bottom, #ebf5ff, #abc7f2);
  border: 0.5px solid rgba(26, 104, 157, 0.6);
  font-size: 18px;
  color: #1f4a6e;
  cursor: pointer;
}

.state-message {
  padding: 2rem;
  text-align: center;
  color: #1f4a6e;
}

.state-message.error {
  color: #c0392b;
}

.table-container {
  padding: 1rem 1.5rem;
}

.marks-table {
  width: 100%;
  border-collapse: collapse;
}

.marks-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: 12px;
  color: #3d6a8c;
  border-bottom: 2px solid rgba(100, 160, 200, 0.35);
}

.marks-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(150, 180, 210, 0.3);
  color: #1a2c44;
}

.date-cell {
  font-weight: 500;
}

.grade-value {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.6);
}

.grade-value.good { color: #1e7a4a; }
.grade-value.mid { color: #2c6e9e; }
.grade-value.low { color: #c0392b; }

.attendance-icon {
  display: inline-block;
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  border-radius: 8px;
  font-weight: 700;
  font-size: 16px;
}

.attendance-icon.present {
  background: rgba(46, 160, 90, 0.2);
  color: #1e7a4a;
}

.attendance-icon.absent {
  background: rgba(200, 60, 60, 0.15);
  color: #c0392b;
}

.comment-cell {
  font-size: 13px;
  color: #4a6080;
  max-width: 200px;
}

.card-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(100, 160, 200, 0.25);
  display: flex;
  gap: 12px;
  align-items: center;
  color: #1f4a6e;
  font-size: 14px;
}

.divider {
  color:
   #8aa8c4;
}
/* ===== Мобильная адаптация StudentMarksPage ===== */
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
}
.modal-overlay.is-mobile .marks-table {
  table-layout: fixed;
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
.modal-overlay.is-mobile .card-footer {
  padding: 0.5rem 0.8rem;
  font-size: 12px;
  gap: 8px;
}
</style>
