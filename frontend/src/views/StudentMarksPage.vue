<template>
  <div class="modal-overlay" @click.self="$emit('close')">
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
              <th>Оценка</th>
              <th>Посещение</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.date">
              <td class="date-cell">{{ row.dateLabel }}</td>
              <td class="grade-cell">
                <span class="grade-value" :class="gradeClass(row.grade)">{{ row.grade ?? '—' }}</span>
              </td>
              <td class="attendance-cell">
                <span class="attendance-icon" :class="row.present === true ? 'present' : (row.present === false ? 'absent' : '')">
                  {{ row.present === true ? '✓' : (row.present === false ? '✗' : '—') }}
                </span>
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
import { ref, computed, onMounted } from 'vue'
import { getGrades, getAttendance } from '@/services/marks'

const props = defineProps({
  subjectName: { type: String, default: '' },
  scheduleId: { type: Number, required: true }
})
defineEmits(['close'])

const loading = ref(true)
const error = ref('')
const rows = ref([])

const avg = computed(() => {
  const nums = rows.value.map(r => r.grade).filter(g => g != null && !isNaN(g))
  if (!nums.length) return null
  return Math.round(nums.reduce((a, b) => a + b, 0) / nums.length)
})

const attendancePct = computed(() => {
  const known = rows.value.filter(r => r.present !== null)
  if (!known.length) return 0
  const present = known.filter(r => r.present).length
  return Math.round((present / known.length) * 100)
})

function gradeClass(grade) {
  if (grade == null) return ''
  if (grade >= 80) return 'good'
  if (grade >= 60) return 'mid'
  return 'low'
}

function formatDate(iso) {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [grades, attendance] = await Promise.all([
      getGrades(props.scheduleId),
      getAttendance(props.scheduleId)
    ])

    const dateSet = new Set()
    grades.forEach(g => dateSet.add(g.grade_date))
    attendance.forEach(a => dateSet.add(a.date))
    const dates = [...dateSet].sort()

    rows.value = dates.map(iso => {
      const g = grades.find(x => x.grade_date === iso)
      const a = attendance.find(x => x.date === iso)
      return {
        date: iso,
        dateLabel: formatDate(iso),
        grade: g?.grade ?? null,
        comment: g?.comment || '',
        present: a ? (a.status === 'present' || a.status === 'late') : null
      }
    })
  } catch (e) {
    error.value = e.message || 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.modal-overlay {
  inset: 0;
  background-image: url('@/assets/image.png');
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.marks-card {
  width: 100%;
  background: linear-gradient(145deg,
    rgba(255, 255, 255, 0.65) 22%,
    rgba(188, 207, 226, 0.45) 79%,
    rgba(149, 169, 195, 0.55) 100%);
  backdrop-filter: blur(12px) brightness(105%);
  border: 1px solid rgba(255, 255, 255, 0.85);
  border-radius: 30px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transition: all 0.2s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: rgba(227, 240, 255, 0.25);
  border-bottom: 1px solid rgba(86, 112, 193, 0.3);
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
}
.stat b {
  font-weight: 800;
  color: #283347;
}
.divider {
  opacity: 0.5;
}

@media (max-width: 640px) {
  .marks-card {
    max-width: 95%;
  }
  .card-header {
    padding: 1rem 1.2rem;
  }
  .subject-badge {
    font-size: 16px;
    padding: 6px 18px;
  }
  .close-btn {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
  .table-container {
    margin: 1rem;
  }
  .marks-table th,
  .marks-table td {
    padding: 8px 6px;
    font-size: 12px;
  }
  .attendance-icon {
    width: 26px;
    height: 26px;
    line-height: 26px;
    font-size: 14px;
  }
  .card-footer {
    font-size: 13px;
    gap: 10px;
  }
}
</style>