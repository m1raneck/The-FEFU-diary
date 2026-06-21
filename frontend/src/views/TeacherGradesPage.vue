<template>
  <div class="screen">
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
        <h1 class="page-title">Оценки (Преподаватель)</h1>
        <p class="page-subtitle">Сводка по студентам и предметам</p>
      </div>

      <div v-if="groups.length > 1" class="group-tabs">
        <button
          v-for="group in groups"
          :key="group.id"
          type="button"
          class="group-tab"
          :class="{ active: selectedGroupId === group.id }"
          @click="selectGroup(group.id)"
        >
          {{ group.name }}
        </button>
      </div>

      <div v-if="loading" class="state-message">Загрузка...</div>
      <div v-else-if="error" class="state-message error">{{ error }}</div>
      <div v-else-if="!selectedGroupId" class="state-message">Нет групп в расписании</div>
      <div v-else-if="subjects.length === 0" class="state-message">Нет предметов для выбранной группы</div>

      <div v-else class="subjects-list">
        <div v-for="subj in subjects" :key="subj.scheduleId" class="subject-card">
          <div class="subject-header">
            <div class="subject-title-wrap">
              <h2>{{ subj.name }}</h2>
              <span class="group-badge">{{ subj.groupName }}</span>
              <span v-if="subj.room" class="room-badge">Ауд. {{ subj.room }}</span>
            </div>
            <button type="button" class="journal-btn" @click="openJournal(subj)">Открыть журнал</button>
          </div>

          <div class="table-wrapper">
            <table class="grades-table">
              <thead>
                <tr>
                  <th class="col-num">№</th>
                  <th class="col-name">ФИО</th>
                  <th>Ср.</th>
                  <th>Посещ.</th>
                  <th class="col-action"></th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(student, idx) in subj.students" :key="student.id">
                  <tr
                    class="student-row"
                    :class="{ expanded: isExpanded(subj.scheduleId, student.id), 'row-warn': isAttendanceWarning(student) }"
                  >
                    <td class="col-num">{{ idx + 1 }}</td>
                    <td class="col-name" :class="{ 'warn-text': isAttendanceWarning(student) }">{{ student.name }}</td>
                    <td>
                      <span class="grade-chip" :class="gradeChipClass(student.avg)">
                        {{ student.avg ?? '—' }}
                      </span>
                    </td>
                    <td :class="{ 'warn-text': isAttendanceWarning(student) }">
                      <b>{{ student.attendancePct }}%</b>
                    </td>
                    <td class="col-action">
                      <button
                        type="button"
                        class="details-btn"
                        @click="toggleDetails(subj.scheduleId, student.id)"
                      >
                        {{ isExpanded(subj.scheduleId, student.id) ? 'Скрыть' : 'Подробнее' }}
                      </button>
                    </td>
                  </tr>
                  <tr
                    v-if="isExpanded(subj.scheduleId, student.id)"
                    :key="`${student.id}-details`"
                    class="details-row"
                  >
                    <td colspan="5">
                      <div class="details-panel">
                        <table class="details-table">
                          <thead>
                            <tr><th>Дата</th><th>Оценка</th><th>Посещение</th><th>Комментарий</th></tr>
                          </thead>
                          <tbody>
                            <tr v-if="student.rows.length === 0">
                              <td colspan="4" class="empty-details">Нет записей</td>
                            </tr>
                            <tr v-for="row in student.rows" :key="row.date">
                              <td>{{ row.dateLabel }}</td>
                              <td>
                                <span class="grade-chip" :class="gradeChipClass(row.grade)">
                                  {{ formatGrade(row.grade) }}
                                </span>
                              </td>
                              <td>
                                <span class="attendance-chip" :class="attendanceChipClass(row.present)">
                                  {{ attendanceText(row.present) }}
                                </span>
                              </td>
                              <td class="comment-cell">{{ row.comment || '—' }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>

          <div class="card-footer">
            <span>Студентов: <b>{{ subj.students.length }}</b></span>
            <span class="sep">|</span>
            <span>Средняя посещаемость: <b>{{ subj.groupAttendancePct }}%</b></span>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="marks-modal">
        <div v-if="marksModalVisible" class="marks-overlay" @click.self="marksModalVisible = false">
          <div class="marks-modal-glass">
            <MarksPage
              :subjectName="journalSubject"
              :groupId="journalGroupId"
              :groupName="journalGroupName"
              :scheduleId="journalScheduleId"
              @close="onJournalClose"
            />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script>
import { getSchedule } from '@/services/schedule'
import { getStudents, getGrades, getAttendance, getLessonComments, normalizeDate } from '@/services/marks'
import { getStoredUser, fetchAndStoreProfile, logout as authLogout, isStudent, isTeacher } from '@/services/auth'
import MarksPage from '@/views/MarksPage.vue'

const MIN_ATTENDANCE_STORAGE_KEY = 'journalMinAttendanceFilters'

export default {
  name: 'TeacherGradesPage',
  components: { MarksPage },
  data() {
    return {
      user: getStoredUser(),
      loading: true,
      error: '',
      scheduleRaw: [],
      allStudents: [],
      groups: [],
      selectedGroupId: null,
      subjects: [],
      expandedKeys: {},
      marksModalVisible: false,
      journalSubject: '',
      journalGroupId: null,
      journalGroupName: '',
      journalScheduleId: null,
    }
  },
  computed: {
    initials() {
      const name = this.user?.full_name || ''
      return name.split(' ').filter(Boolean).map(w => w[0]).slice(0, 2).join('').toUpperCase() || 'ПР'
    },
  },
  async mounted() {
    if (isStudent(this.user)) {
      this.$router.replace('/my-grades')
      return
    }
    if (!isTeacher(this.user)) {
      this.$router.replace('/schedule')
      return
    }
    try {
      if (!this.user) this.user = await fetchAndStoreProfile()
      await this.loadData()
    } catch (e) {
      this.error = e.message || 'Ошибка загрузки'
    } finally {
      this.loading = false
    }
  },
  methods: {
    expandKey(scheduleId, studentId) {
      return `${scheduleId}:${studentId}`
    },
    isExpanded(scheduleId, studentId) {
      return !!this.expandedKeys[this.expandKey(scheduleId, studentId)]
    },
    toggleDetails(scheduleId, studentId) {
      const key = this.expandKey(scheduleId, studentId)
      this.expandedKeys[key] = !this.expandedKeys[key]
    },
    getMinAttendanceForSchedule(scheduleId) {
      try {
        const stored = JSON.parse(localStorage.getItem(MIN_ATTENDANCE_STORAGE_KEY) || '{}')
        return Number(stored[scheduleId] ?? 0)
      } catch {
        return 0
      }
    },
    isAttendanceWarning(student) {
      const min = this.getMinAttendanceForSchedule(student.scheduleId)
      if (min > 0) {
        return (student.attendanceCount ?? 0) < min
      }
      return student.attendancePct < 60
    },
    gradeChipClass(grade) {
      if (grade === '+') return 'chip-plus'
      if (grade === '-') return 'chip-minus'
      const num = parseFloat(grade)
      if (!isNaN(num)) {
        if (num >= 4) return 'chip-good'
        if (num >= 3) return 'chip-mid'
        return 'chip-bad'
      }
      return 'chip-empty'
    },
    formatGrade(grade) {
      if (grade === '+') return '+'
      if (grade === '-') return '−'
      if (grade == null || grade === '') return '—'
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
    dedupeSchedule(items) {
      const map = new Map()
      for (const item of items) {
        const subjectId = item.subject?.id ?? item.subject_id
        const key = `${item.group_id}-${subjectId}`
        if (!map.has(key)) map.set(key, item)
      }
      return [...map.values()]
    },
    buildGroups(schedule) {
      const map = new Map()
      for (const item of schedule) {
        if (!item.group_id) continue
        if (!map.has(item.group_id)) {
          map.set(item.group_id, {
            id: item.group_id,
            name: item.group?.name || `Группа ${item.group_id}`,
          })
        }
      }
      return [...map.values()].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    },
    buildStudentRows(studentId, grades, attendance, comments) {
      const dateSet = new Set()
      grades.filter(g => g.student_id === studentId).forEach(g => dateSet.add(normalizeDate(g.grade_date)))
      attendance.filter(a => a.student_id === studentId).forEach(a => dateSet.add(normalizeDate(a.date)))
      comments.filter(c => c.student_id === studentId).forEach(c => dateSet.add(normalizeDate(c.lesson_date)))

      const dates = [...dateSet].filter(Boolean).sort()
      return dates.map(iso => {
        const g = grades.find(x => x.student_id === studentId && normalizeDate(x.grade_date) === iso)
        const a = attendance.find(x => x.student_id === studentId && normalizeDate(x.date) === iso)
        const c = comments.find(x => x.student_id === studentId && normalizeDate(x.lesson_date) === iso)
        let grade = g?.grade ?? null
        if (g?.raw_score != null && grade == null) grade = g.raw_score
        return {
          date: iso,
          dateLabel: this.formatDate(iso),
          grade,
          comment: c?.comment || '',
          present: a ? (a.status === 'present' || a.status === 'late') : null,
        }
      })
    },
    summarizeStudent(student, scheduleId, grades, attendance, comments) {
      const rows = this.buildStudentRows(student.id, grades, attendance, comments)
      const gradeNums = rows.map(r => r.grade).filter(v => v != null && v !== '+' && v !== '-').map(Number).filter(v => !isNaN(v))
      const avg = gradeNums.length
        ? Math.round(gradeNums.reduce((a, b) => a + b, 0) / gradeNums.length)
        : null
      const known = rows.filter(r => r.present !== null)
      const attendanceCount = known.filter(r => r.present).length
      const attendancePct = known.length ? Math.round((attendanceCount / known.length) * 100) : 0

      return {
        id: student.id,
        name: student.full_name,
        scheduleId,
        rows,
        avg,
        attendanceCount,
        attendancePct,
      }
    },
    async buildSubjectCard(scheduleItem, groupStudents) {
      const [grades, attendance, comments] = await Promise.all([
        getGrades(scheduleItem.id),
        getAttendance(scheduleItem.id),
        getLessonComments(scheduleItem.id),
      ])

      const students = groupStudents
        .map(s => this.summarizeStudent(s, scheduleItem.id, grades, attendance, comments))
        .sort((a, b) => a.name.localeCompare(b.name, 'ru'))

      const knownStudents = students.filter(s => s.rows.some(r => r.present !== null))
      const groupAttendancePct = knownStudents.length
        ? Math.round(knownStudents.reduce((sum, s) => sum + s.attendancePct, 0) / knownStudents.length)
        : 0

      return {
        scheduleId: scheduleItem.id,
        name: scheduleItem.subject?.name || `Предмет #${scheduleItem.id}`,
        groupId: scheduleItem.group_id,
        groupName: scheduleItem.group?.name || `Группа ${scheduleItem.group_id}`,
        room: scheduleItem.room?.number || '',
        students,
        groupAttendancePct,
      }
    },
    async loadSubjectsForGroup(groupId) {
      const groupSchedule = this.dedupeSchedule(
        this.scheduleRaw.filter(item => item.group_id === groupId)
      )
      const groupStudents = this.allStudents
        .filter(s => s.group_id === groupId)
        .sort((a, b) => a.full_name.localeCompare(b.full_name, 'ru'))

      const subjects = await Promise.all(
        groupSchedule.map(item => this.buildSubjectCard(item, groupStudents))
      )
      this.subjects = subjects.sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    },
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        const [schedule, students] = await Promise.all([getSchedule(), getStudents()])
        this.scheduleRaw = schedule
        this.allStudents = students
        this.groups = this.buildGroups(schedule)

        if (!this.groups.length) {
          this.selectedGroupId = null
          this.subjects = []
          return
        }

        if (!this.selectedGroupId || !this.groups.some(g => g.id === this.selectedGroupId)) {
          this.selectedGroupId = this.groups[0].id
        }

        await this.loadSubjectsForGroup(this.selectedGroupId)
      } catch (e) {
        this.error = e.message || 'Ошибка загрузки'
        this.subjects = []
      } finally {
        this.loading = false
      }
    },
    async selectGroup(groupId) {
      if (this.selectedGroupId === groupId) return
      this.selectedGroupId = groupId
      this.expandedKeys = {}
      this.loading = true
      try {
        await this.loadSubjectsForGroup(groupId)
      } catch (e) {
        this.error = e.message || 'Ошибка загрузки'
      } finally {
        this.loading = false
      }
    },
    openJournal(subj) {
      this.journalSubject = subj.name
      this.journalGroupId = subj.groupId
      this.journalGroupName = subj.groupName
      this.journalScheduleId = subj.scheduleId
      this.marksModalVisible = true
    },
    async onJournalClose() {
      this.marksModalVisible = false
      if (this.selectedGroupId) {
        await this.loadSubjectsForGroup(this.selectedGroupId)
      }
    },
    goToSchedule() {
      this.$router.push('/schedule')
    },
    logout() {
      authLogout()
      this.$router.push('/')
    },
  },
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
  align-items: flex-start;
  justify-content: center;
  padding: 2rem;
  font-family: 'Inter', system-ui, sans-serif;
}

.grades-card {
  width: 100%;
  max-width: 1200px;
  background: linear-gradient(145deg, rgba(245,250,255,0.65) 22%, rgba(210,230,245,0.45) 79%, rgba(180,205,225,0.65) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 48px;
  box-shadow: 0 16px 32px rgba(0,0,0,0.2);
  overflow: hidden;
  margin-bottom: 2rem;
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

.schedule-btn, .logout-btn, .journal-btn, .details-btn, .group-tab {
  transition: all 0.2s ease;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.4);
  cursor: pointer;
}

.schedule-btn, .logout-btn {
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  border: 1px solid rgba(119, 155, 222, 0.7);
  border-radius: 30px;
  padding: 10px 18px;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}

.schedule-btn:hover, .logout-btn:hover, .journal-btn:hover, .group-tab:hover {
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

.header-section {
  text-align: center;
  margin: 1rem 0 0.5rem;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f3b4c;
  background: rgba(192, 222, 255, 0.2);
  display: inline-block;
  padding: 0.4rem 1.5rem;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

.page-subtitle {
  color: #1e3a5f;
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
}

.group-tabs {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  padding: 0 2rem 1rem;
}

.group-tab {
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(112, 165, 218, 0.5);
  border-radius: 30px;
  padding: 8px 18px;
  color: #1f4a6e;
  font-weight: 600;
  font-size: 14px;
}

.group-tab.active {
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  color: #fff;
  border-color: rgba(119, 155, 222, 0.7);
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
  background: rgba(100, 140, 180, 0.1);
  border-bottom: 1px solid rgba(86,112,193,0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.subject-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.subject-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1a4c6e;
  margin: 0;
}

.group-badge, .room-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.55);
  color: #1f4a6e;
  border: 1px solid rgba(112, 165, 218, 0.4);
}

.journal-btn {
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  border: 1px solid rgba(119, 155, 222, 0.7);
  border-radius: 30px;
  padding: 8px 16px;
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
}

.table-wrapper { overflow-x: auto; }

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

.col-num { width: 48px; }
.col-name { text-align: left !important; min-width: 180px; }
.col-action { width: 120px; }

.student-row.expanded td {
  background: rgba(227, 240, 255, 0.75);
}

.row-warn td {
  background: rgba(255, 240, 240, 0.55);
}

.warn-text {
  color: #b13b3b;
  font-weight: 600;
}

.details-btn {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(112, 165, 218, 0.5);
  border-radius: 20px;
  padding: 6px 12px;
  color: #1f4a6e;
  font-size: 12px;
  font-weight: 600;
}

.details-row td {
  padding: 0 !important;
  background: rgba(245, 250, 255, 0.85) !important;
}

.details-panel {
  padding: 12px 16px 16px;
}

.details-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.details-table th,
.details-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(116,149,197,0.25);
  background: rgba(255,255,255,0.75);
}

.empty-details {
  color: #4a6f8c;
  font-style: italic;
}

.grade-chip, .attendance-chip {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 40px;
  font-weight: 600;
  font-size: 14px;
  min-width: 60px;
}

.chip-good, .chip-plus, .chip-present {
  background: #8bc9a5;
  color: #1d4d2d;
}

.chip-mid {
  background: #f0dfa0;
  color: #7a5b00;
}

.chip-bad, .chip-minus, .chip-absent {
  background: #e8b0b0;
  color: #a14242;
}

.chip-empty {
  background: #c6d3df;
  color: #4a6f8c;
}

.chip-present, .chip-absent {
  font-size: 18px;
  padding: 4px 16px;
}

.comment-cell {
  text-align: left !important;
  max-width: 280px;
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
  flex-wrap: wrap;
}

.sep { opacity: 0.5; }

.marks-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 35, 55, 0.45);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.marks-modal-glass {
  width: min(98vw, 1400px);
  max-height: 96vh;
  overflow: auto;
  border-radius: 32px;
}

.marks-modal-enter-active,
.marks-modal-leave-active {
  transition: opacity 0.25s ease;
}

.marks-modal-enter-from,
.marks-modal-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .screen { padding: 1rem; }
  .card-header { padding: 1rem 1.5rem; flex-direction: column; align-items: stretch; }
  .header-right { justify-content: center; }
  .grades-table th, .grades-table td { padding: 8px 6px; font-size: 12px; }
  .grade-chip, .attendance-chip { padding: 3px 12px; font-size: 12px; min-width: 50px; }
  .chip-present, .chip-absent { font-size: 14px; }
  .card-footer { font-size: 12px; gap: 12px; }
  .subject-header { flex-direction: column; align-items: stretch; }
  .journal-btn { width: 100%; }
}

@media (max-width: 560px) {
  .subjects-list { padding: 0 1rem 1rem; }
  .page-title { font-size: 22px; }
}
</style>
