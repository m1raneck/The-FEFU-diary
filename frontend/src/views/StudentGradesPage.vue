<template>
  <div class="screen" :class="{ 'is-mobile': isMobile }">
    <div class="grades-card">
      <div class="card-header">
        <div class="header-left">
          <router-link to="/" class="logo-link">
            <img src="@/assets/icon.png" alt="Logo" class="logo-icon" />
            <span class="logo-text">UniDiary</span>
          </router-link>
        </div>
        <div class="header-right">
          <button class="schedule-btn" @click="goToSchedule">Расписание</button>
          <button class="logout-btn" @click="logout">Выйти</button>
          <div class="user-avatar">
            <span class="avatar-initials">{{ initials }}</span>
          </div>
        </div>
      </div>

      <div class="header-section">
        <h1 class="page-title">Оценки</h1>
        <p v-if="user?.student_info?.group_name" class="group-label">
          Группа: {{ user.student_info.group_name }}
        </p>
      </div>

      <div v-if="loading" class="state-message">Загрузка...</div>
      <div v-else-if="error" class="state-message error">{{ error }}</div>
      <div v-else-if="subjects.length === 0" class="state-message">Оценок пока нет</div>

      <div v-else class="subjects-list">
        <div v-for="subj in subjects" :key="subj.scheduleId" class="subject-card">
          <div class="subject-header">
            <h2>{{ subj.name }}</h2>
          </div>
          <div class="table-wrapper">
            <table class="grades-table">
              <thead>
                <tr><th>Дата</th><th>Оценка</th><th>Посещение</th><th>Комментарий</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in subj.rows" :key="row.date">
                  <td class="date-cell">{{ row.dateLabel }}</td>
                  <td class="grade-cell">
                    <span class="grade-chip" :class="gradeChipClass(row.grade)">
                      {{ formatGrade(row.grade) }}
                    </span>
                  </td>
                  <td class="attendance-cell">
                    <span class="attendance-chip" :class="attendanceChipClass(row.present)">
                      {{ attendanceText(row.present) }}
                    </span>
                  </td>
                  <td class="comment-cell">{{ row.comment || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-footer">
            <span>Средний балл: <b>{{ subj.avg ?? '—' }}</b></span>
            <span class="sep">|</span>
            <span>Посещаемость: <b>{{ subj.attendancePct }}%</b></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getSchedule } from '@/services/schedule'
import { getGrades, getAttendance, getLessonComments, normalizeDate } from '@/services/marks'
import { getStoredUser, fetchAndStoreProfile, logout as authLogout, isStudent } from '@/services/auth'

export default {
  name: 'StudentGradesPage',
  data() {
    return {
      user: getStoredUser(),
      loading: true,
      error: '',
      subjects: [],
      isMobile: false
    }
  },
  computed: {
    initials() {
      const name = this.user?.full_name || ''
      return name.split(' ').filter(Boolean).map(w => w[0]).slice(0, 2).join('').toUpperCase() || 'СТ'
    }
  },
  async mounted() {
    this.checkIfMobile()
    window.addEventListener('resize', this.checkIfMobile)
    if (!isStudent(this.user)) {
      this.$router.replace('/schedule')
      return
    }
    try {
      if (!this.user) this.user = await fetchAndStoreProfile()
      await this.loadGrades()
    } catch (e) {
      this.error = e.message || 'Ошибка загрузки'
    } finally {
      this.loading = false
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.checkIfMobile)
  },
  methods: {
    checkIfMobile() {
      this.isMobile = window.innerWidth < 768
    },
    gradeChipClass(grade) {
      if (grade === '+') return 'chip-plus'
      if (grade === '-') return 'chip-minus'
      const num = parseFloat(grade)
      if (!isNaN(num)) {
        if (num >= 4) return 'chip-good'
        return 'chip-bad'
      }
      return 'chip-empty'
    },
    formatGrade(grade) {
      if (grade === '+') return '+'
      if (grade === '-') return '−'
      if (grade == null) return '—'
      return grade
    },
    attendanceChipClass(present) {
      if (present === null) return ''
      return present ? 'chip-present' : 'chip-absent'
    },
    attendanceText(present) {
      if (present === null) return '—'
      return present ? '✓' : '✗'
    },
    formatDate(iso) {
      const [y, m, d] = iso.split('-')
      return `${d}.${m}.${y}`
    },
    async loadGrades() {
      this.loading = true
      this.error = ''
      try {
        const [schedule, grades, attendance, lessonComments] = await Promise.all([
          getSchedule(),
          getGrades(),
          getAttendance(),
          getLessonComments(),
        ])

        const scheduleMap = Object.fromEntries(schedule.map(s => [s.id, s]))
        const bySchedule = {}

        for (const g of grades) {
          if (!bySchedule[g.schedule_id]) bySchedule[g.schedule_id] = { grades: [], attendance: [], comments: [] }
          bySchedule[g.schedule_id].grades.push(g)
        }
        for (const a of attendance) {
          if (!bySchedule[a.schedule_id]) bySchedule[a.schedule_id] = { grades: [], attendance: [], comments: [] }
          bySchedule[a.schedule_id].attendance.push(a)
        }
        for (const c of lessonComments) {
          if (!bySchedule[c.schedule_id]) bySchedule[c.schedule_id] = { grades: [], attendance: [], comments: [] }
          bySchedule[c.schedule_id].comments.push(c)
        }

        this.subjects = Object.entries(bySchedule).map(([scheduleId, data]) => {
          const sch = scheduleMap[scheduleId]
          const dateSet = new Set()
          data.grades.forEach(g => dateSet.add(normalizeDate(g.grade_date)))
          data.attendance.forEach(a => dateSet.add(normalizeDate(a.date)))
          data.comments.forEach(c => dateSet.add(normalizeDate(c.lesson_date)))
          const dates = [...dateSet].filter(Boolean).sort()

          const rows = dates.map(iso => {
            const g = data.grades.find(x => normalizeDate(x.grade_date) === iso)
            const a = data.attendance.find(x => normalizeDate(x.date) === iso)
            const c = data.comments.find(x => normalizeDate(x.lesson_date) === iso)
            return {
              date: iso,
              dateLabel: this.formatDate(iso),
              grade: g?.grade ?? null,
              comment: c?.comment || '',
              present: a ? (a.status === 'present' || a.status === 'late') : null
            }
          })

          const gradeNums = rows.map(r => r.grade).filter(v => v != null)
          const avg = gradeNums.length
            ? Math.round(gradeNums.reduce((a, b) => a + b, 0) / gradeNums.length)
            : null
          const known = rows.filter(r => r.present !== null)
          const attendanceCount = known.filter(r => r.present).length
          const attendancePct = known.length
            ? Math.round((attendanceCount / known.length) * 100)
            : 0

          return {
            scheduleId: Number(scheduleId),
            name: sch?.subject?.name || `Предмет #${scheduleId}`,
            room: sch?.room?.number || '',
            rows,
            avg,
            attendancePct,
            attendanceCount,
            attendancePoints: attendanceCount,
          }
        }).sort((a, b) => a.name.localeCompare(b.name))
      } catch (e) {
        this.error = e.message || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },
    goToSchedule() {
      this.$router.push('/schedule')
    },
    logout() {
      authLogout()
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.screen {
  min-height: 100vh;
  background-image: url('@/assets/image.png');
  background-size: cover;
  background-position: center;
  background-color: #6b8cae;
  background-blend-mode: overlay;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  font-family: 'Inter', system-ui, sans-serif;
}

.grades-card {
  width: 100%;
  max-width: 1100px;
  background: linear-gradient(145deg, rgba(245,250,255,0.65) 22%, rgba(210,230,245,0.45) 79%, rgba(180,205,225,0.65) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 48px;
  box-shadow: 0 16px 32px rgba(0,0,0,0.2);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 2.5rem;
  background: rgba(227, 240, 255, 0.25);
  border-bottom: 1px solid rgba(86, 112, 193, 0.35);
}
.header-left .logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}
.logo-icon { width: 40px; height: auto; }
.logo-text {
  font-size: 28px;
  font-weight: 800;
  color: #1f3b4c;
  letter-spacing: -0.5px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}
.schedule-btn, .logout-btn {
  transition: all 0.2s ease;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.4);
  cursor: pointer;
}
.schedule-btn {
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  border: 1px solid rgba(119, 155, 222, 0.7);
  border-radius: 30px;
  padding: 10px 18px;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}
.schedule-btn:hover {
  background: linear-gradient(to bottom, #66a3db, #27559b);
  transform: translateY(-1px);
}
.user-avatar {
  width: 47px;
  height: 47px;
  background: linear-gradient(145deg, #63a8dd, #366acb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(241, 246, 255, 0.7);
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.avatar-initials {
  font-weight: bold;
  font-size: 18px;
  color: white;
}
.logout-btn {
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  border: none;
  border-radius: 30px;
  border: 1px solid rgba(119, 155, 222, 0.7);
  padding: 10px 18px;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}
.logout-btn:hover {
  background: linear-gradient(to bottom, #66a3db, #27559b);
  transform: translateY(-1px);
}

.header-section {
  text-align: center;
  margin: 1rem 0 0.5rem;
}
.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f3b4c;
  background: rgba(216, 230, 251, 0.5);
  display: inline-block;
  padding: 0.4rem 1.5rem;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}
.group-label {
  color: #1e3a5f;
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
}

.state-message {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #1e3a5f;
  background: rgba(255,255,255,0.4);
  margin: 20px;
  border-radius: 28px;
}
.state-message.error { color: #b13b3b; }

.subjects-list {
  padding: 0 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.subject-card {
  background: rgba(168, 199, 231, 0.85);
  backdrop-filter: blur(4px);
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.6);
}

.subject-header {
  padding: 16px 24px;
  background: rgba(163, 193, 232, 0.25);
  border-bottom: 1px solid rgba(86,112,193,0.2);
}
.subject-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1a4c6e;
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
}
.grades-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.grades-table th {
  padding: 14px 12px;
  background: rgba(200, 220, 240, 0.5);
  color: #17365f;
  font-weight: 600;
  border-bottom: 1px solid rgba(102,139,190,0.3);
}
.grades-table td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid rgba(116,149,197,0.3);
  background: rgba(255,255,255,0.6);
  color: #1a2c44;
}
.grade-chip, .attendance-chip {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 40px;
  font-weight: 600;
  font-size: 14px;
  min-width: 60px;
}
.chip-good, .chip-plus {
  background: #8bc9a5;
  color: #1d4d2d;
}
.chip-bad, .chip-minus {
  background: #e8b0b0;
  color: #a14242;
}
.chip-empty {
  background: #c6d3df;
  color: #4a6f8c;
}
.chip-present {
  background: #8bc9a5;
  color: #1d4d2d;
  font-size: 18px;
  padding: 4px 16px;
}
.chip-absent {
  background: #e8b0b0;
  color: #a14242;
  font-size: 18px;
  padding: 4px 16px;
}

.card-footer {
  padding: 14px 24px;
  font-size: 14px;
  color: #1f4a6e;
  background: rgba(227, 240, 255, 0.4);
  border-top: 1px solid rgba(86,112,193,0.3);
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 20px;
}
.sep {
  opacity: 0.5;
}

/* ========== Мобильная адаптация ========== */
.screen.is-mobile {
  background: url('@/assets/phone2.PNG');
  background-color: #8fa0d4;
  position: relative;
  overflow: hidden;
}

.screen.is-mobile::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.1) 100%);
  pointer-events: none;
  z-index: 0;
}

.screen.is-mobile > * {
  position: relative;
  z-index: 1;
}

.screen.is-mobile .grades-card {
  height: calc(100vh - 1rem);
  overflow-y: auto;
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  border: none;
  box-shadow: none;
}

.screen.is-mobile .card-header {
  flex-direction: row !important;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  flex-wrap: nowrap;
  gap: 6px;
  border-bottom: none;
}

.screen.is-mobile .header-right {
  gap: 6px;
  flex-wrap: nowrap;
}

.screen.is-mobile .user-avatar {
  display: none;
}

.screen.is-mobile .schedule-btn,
.screen.is-mobile .logout-btn {
  padding: 5px 12px;
  font-size: 12px;
  border-radius: 20px;
}

.screen.is-mobile .header-section {
  margin: 0.5rem 0;
}

.screen.is-mobile .page-title {
  font-size: 22px;
}

.screen.is-mobile .subjects-list {
  padding: 0 1rem 1rem;
  gap: 1rem;
}

.screen.is-mobile .grades-table th,
.screen.is-mobile .grades-table td {
  padding: 8px 6px;
  font-size: 12px;
}

.screen.is-mobile .grade-chip,
.screen.is-mobile .attendance-chip {
  padding: 3px 12px;
  font-size: 12px;
  min-width: 50px;
}

.screen.is-mobile .chip-present,
.screen.is-mobile .chip-absent {
  font-size: 14px;
}

.screen.is-mobile .card-footer {
  font-size: 12px;
  gap: 12px;
}

@media (max-width: 768px) {
  .screen { padding: 0.5rem; }
  .card-header { padding: 1rem 1.5rem; flex-direction: column; align-items: stretch; }
  .header-right { justify-content: center; }
  .grades-table th, .grades-table td { padding: 8px 6px; font-size: 12px; }
  .grade-chip, .attendance-chip { padding: 3px 12px; font-size: 12px; min-width: 50px; }
  .chip-present, .chip-absent { font-size: 14px; }
  .card-footer { font-size: 12px; gap: 12px; }
}
@media (max-width: 560px) {
  .subjects-list { padding: 0 1rem 1rem; }
  .page-title { font-size: 22px; }
}
</style>