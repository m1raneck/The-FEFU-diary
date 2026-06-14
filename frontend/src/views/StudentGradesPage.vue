<template>
  <div class="grades-page">
    <div class="background-layer"></div>
    <div class="top-header"></div>
    <div class="top-right">
      <div class="avatar-circle"></div>
      <div class="avatar-text">{{ initials }}</div>
      <a-button class="logout-btn" @click="logout" type="link">
        <span class="logout-icon">→</span> Выйти
      </a-button>
    </div>

    <div class="page-nav">
      <router-link to="/schedule" class="nav-link">Расписание</router-link>
      <router-link to="/my-grades" class="nav-link active">Мои оценки</router-link>
    </div>

    <div class="header-section">
      <h1 class="page-title">Мои оценки</h1>
      <p v-if="user?.student_info?.group_name" class="group-label">
        Группа: {{ user.student_info.group_name }}
      </p>
    </div>

    <div v-if="loading" class="state-box">Загрузка...</div>
    <div v-else-if="error" class="state-box error">{{ error }}</div>
    <div v-else-if="subjects.length === 0" class="state-box">Оценок пока нет</div>

    <div v-else class="subjects-list">
      <div v-for="subj in subjects" :key="subj.scheduleId" class="subject-card">
        <div class="subject-header">
          <h2>{{ subj.name }}</h2>
          <span v-if="subj.room" class="room-badge">ауд. {{ subj.room }}</span>
        </div>
        <table class="grades-table">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Оценка</th>
              <th>Посещение</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in subj.rows" :key="row.date">
              <td>{{ row.dateLabel }}</td>
              <td><span class="grade" :class="gradeClass(row.grade)">{{ row.grade ?? '—' }}</span></td>
              <td>
                <span :class="row.present === null ? '' : (row.present ? 'pres-yes' : 'pres-no')">
                  {{ row.present === null ? '—' : (row.present ? 'Присутствовал' : 'Отсутствовал') }}
                </span>
              </td>
              <td class="comment-cell">{{ row.comment || '—' }}</td>
            </tr>
          </tbody>
        </table>
        <div class="card-footer">
          Средний: <b>{{ subj.avg ?? '—' }}</b>
          <span class="sep">·</span>
          Посещаемость: <b>{{ subj.attendancePct }}%</b>
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
      subjects: []
    }
  },
  computed: {
    initials() {
      const name = this.user?.full_name || ''
      return name.split(' ').filter(Boolean).map(w => w[0]).slice(0, 2).join('').toUpperCase() || 'СТ'
    }
  },
  async mounted() {
    if (!isStudent(this.user)) {
      this.$router.replace('/schedule')
      return
    }
    try {
      if (!this.user) this.user = await fetchAndStoreProfile()
      await this.loadGrades()
    } catch (e) {
      this.error = e.message || 'Ошибка загрузки'
      this.loading = false
    }
  },
  methods: {
    gradeClass(grade) {
      if (grade == null) return ''
      if (grade >= 80) return 'good'
      if (grade >= 60) return 'mid'
      return 'low'
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
          const attendancePct = known.length
            ? Math.round((known.filter(r => r.present).length / known.length) * 100)
            : 0

          return {
            scheduleId: Number(scheduleId),
            name: sch?.subject?.name || `Предмет #${scheduleId}`,
            room: sch?.room?.number || '',
            rows,
            avg,
            attendancePct
          }
        }).sort((a, b) => a.name.localeCompare(b.name))
      } catch (e) {
        this.error = e.message || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },
    logout() {
      authLogout()
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.grades-page {
  min-height: 100vh;
  position: relative;
  font-family: 'Inter', system-ui, sans-serif;
}
.background-layer {
  position: fixed;
  inset: 0;
  background: linear-gradient(145deg, #b9d0e8 7.14%, #c8dff7);
  z-index: 0;
}
.top-header {
  position: relative;
  height: 80px;
  background: rgba(41, 77, 103, 0.75);
  backdrop-filter: blur(12px);
  z-index: 1;
}
.top-right {
  position: absolute;
  top: 16px;
  right: 40px;
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 2;
}
.avatar-circle {
  width: 48px;
  height: 48px;
  background: linear-gradient(145deg, #5a9ac0, #2e6a8e);
  border-radius: 50%;
  border: 2px solid rgba(200, 220, 240, 0.7);
}
.avatar-text {
  font-size: 20px;
  font-weight: bold;
  color: #eef5ff;
}
.logout-btn {
  background: rgba(200, 220, 240, 0.15);
  color: #eef5ff;
  border: 1px solid rgba(100, 160, 200, 0.5);
  border-radius: 28px;
  padding: 8px 20px;
}
.page-nav {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 16px 0 0;
}
.nav-link {
  padding: 8px 24px;
  border-radius: 40px;
  background: rgba(238, 245, 255, 0.7);
  color: #1e3a5f;
  text-decoration: none;
  font-weight: 500;
  border: 1px solid #5a9ac0;
  transition: 0.2s;
}
.nav-link.active, .nav-link:hover {
  background: #5a9ac0;
  color: #fff;
}
.header-section {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 20px 20px 8px;
}
.page-title {
  font-size: 28px;
  color: #eef5ff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.group-label {
  color: #1e3a5f;
  margin-top: 8px;
  font-size: 14px;
}
.state-box {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 40px;
  color: #1e3a5f;
  font-size: 16px;
}
.state-box.error { color: #b13b3b; }
.subjects-list {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto 40px;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.subject-card {
  background: rgba(255,255,255,0.85);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.subject-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #dae4ed;
}
.subject-header h2 {
  font-size: 18px;
  color: #1a4c6e;
}
.room-badge {
  font-size: 12px;
  color: #4a6f8c;
  background: #eef5ff;
  padding: 4px 12px;
  border-radius: 20px;
}
.grades-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.grades-table th {
  padding: 10px;
  background: #eef3fc;
  color: #17365f;
  font-weight: 600;
}
.grades-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #e0e8f0;
  color: #1a2c44;
}
.grade { font-weight: 700; }
.grade.good { color: #1f6e43; }
.grade.mid { color: #b76e00; }
.grade.low { color: #b13b3b; }
.pres-yes { color: #1f9755; }
.pres-no { color: #cc4d4d; }
.comment-cell { font-size: 13px; color: #4a6f8c; max-width: 240px; }
.card-footer {
  padding: 12px 20px;
  font-size: 13px;
  color: #4a6f8c;
  background: #f6fafe;
}
.sep { margin: 0 8px; }
</style>
