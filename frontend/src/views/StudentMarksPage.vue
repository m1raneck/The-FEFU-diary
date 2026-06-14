<template>
  <div class="student-marks-wrapper">
    <div class="marks-header">
      <div class="subject-pill">{{ subjectName }}</div>
      <button class="close-btn" @click="$emit('close')">✕</button>
    </div>

    <div v-if="loading" class="state-msg">Загрузка...</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>
    <div v-else-if="dates.length === 0" class="state-msg">Пока нет оценок по этому предмету</div>

    <div v-else class="table-scroll">
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
            <td>{{ row.dateLabel }}</td>
            <td>
              <span class="grade-val" :class="gradeClass(row.grade)">
                {{ row.grade ?? '—' }}
              </span>
            </td>
            <td>
              <span class="presence" :class="row.present ? 'yes' : 'no'">
                {{ row.present === null ? '—' : (row.present ? '✓' : '✗') }}
              </span>
            </td>
            <td class="comment">{{ row.comment || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="avg !== null" class="summary">
      Средний балл: <b>{{ avg }}</b>
      <span class="sep">|</span>
      Посещаемость: <b>{{ attendancePct }}%</b>
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
const dates = ref([])
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

function formatDate(iso) {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function gradeClass(grade) {
  if (grade == null) return ''
  if (grade >= 80) return 'good'
  if (grade >= 60) return 'mid'
  return 'low'
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
    dates.value = [...dateSet].sort()

    rows.value = dates.value.map(iso => {
      const g = grades.find(x => x.grade_date === iso)
      const a = attendance.find(x => x.date === iso)
      return {
        date: iso,
        dateLabel: formatDate(iso),
        grade: g?.grade ?? null,
        comment: g?.comment || a?.comment || '',
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
.student-marks-wrapper {
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  background: #91a6c5;
  border-radius: 24px;
  overflow: hidden;
  font-family: system-ui, 'Inter', sans-serif;
}
.marks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #5f7b9f66;
  border-bottom: 1px solid rgba(66, 107, 157, 0.5);
}
.subject-pill {
  font-size: 16px;
  font-weight: 600;
  color: #1e4a76;
  background: #9ab0cc;
  padding: 6px 20px;
  border-radius: 40px;
}
.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #9eaab7;
  background: transparent;
  color: #c4cfe0;
  cursor: pointer;
}
.state-msg {
  padding: 32px;
  text-align: center;
  color: #1e3a5f;
}
.state-msg.error { color: #b13b3b; }
.table-scroll {
  overflow: auto;
  margin: 20px;
  border-radius: 16px;
  border: 1px solid #5f7b9f;
  background: #3c5b84;
}
.marks-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.marks-table th {
  background: #dae4ed;
  padding: 12px;
  color: #17365f;
  font-weight: 600;
}
.marks-table td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid #c9d5e4;
  background: #dbe5ee;
  color: #1a2c44;
}
.comment { font-size: 12px; color: #4a6f8c; }
.grade-val { font-weight: 700; }
.grade-val.good { color: #1f6e43; }
.grade-val.mid { color: #b76e00; }
.grade-val.low { color: #b13b3b; }
.presence.yes { color: #1f9755; font-weight: 700; }
.presence.no { color: #cc4d4d; font-weight: 700; }
.summary {
  padding: 14px 24px;
  background: #6882a9;
  color: #243966;
  font-size: 13px;
  border-top: 1px solid #4f7098;
}
.sep { margin: 0 12px; opacity: 0.5; }
</style>
