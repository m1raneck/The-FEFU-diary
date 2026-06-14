<template>
  <div class="screen">
    <div class="schedule-card">
      <div class="card-header">
        <div class="header-left">
          <router-link to="/" class="logo-link">
            <img src="@/assets/icon.png" alt="Logo" class="logo-icon" />
            <span class="logo-text">UniDiary</span>
          </router-link>
        </div>
        <div class="header-right">
          <button class="grades-btn" @click="goToAllGrades" v-if="isStudent">Мои оценки</button>
          <button class="grades-btn" @click="goToAllGrades" v-else>Все оценки</button>
          <button class="logout-btn" @click="logout">Выйти</button>
          <div class="user-avatar">
            <span class="avatar-initials">{{ initials }}</span>
          </div>
        </div>
      </div>


      <div class="schedule-content">
        <div class="week-header">
          <div class="date-range">{{ currentDateRange }}</div>
        </div>
        <div class="week-nav">
          <button class="nav-arrow" @click="prevWeek">←</button>
          <span class="week-status">{{ weekStatus }}</span>
          <button class="nav-arrow" @click="nextWeek">→</button>
        </div>

        <div class="schedule-table-wrapper">
          <table class="schedule-table">
            <thead>
              <tr>
                <th class="time-col">Время</th>
                <th v-for="day in weekDays" :key="day.date" class="day-col" :class="{ 'today-col': isToday(day.date) }">
                  <div class="day-content">
                    <span class="day-name">{{ day.name }}</span>
                    <span class="day-date">{{ day.dateStr }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="time in timeSlots" :key="time" :class="{ 'current-time-row': isCurrentTimeSlot(time) }">
                <td class="time-cell">
                  <div class="time-card">
                    <span class="time-hour">{{ time }}</span>
                    <span v-if="isCurrentTimeSlot(time)" class="now-badge">•</span>
                  </div>
                </td>
                <td v-for="day in weekDays" :key="day.date" class="lesson-cell" @click="onLessonClick(getLesson(day.date, time))">
                  <div v-if="getLesson(day.date, time)" class="lesson-card">
                    <div class="lesson-name">{{ getLesson(day.date, time).name }}</div>
                    <div class="lesson-details">
                      {{ isStudent ? lessonSubtitle(getLesson(day.date, time)) : getLesson(day.date, time).group }}
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <a-modal v-model:open="modalVisible" :title="editingLesson ? 'Редактировать пару' : 'Добавить пару'" @ok="handleSaveLesson" @cancel="closeModal">
      <a-form layout="vertical">
        <a-form-item label="Название предмета" required>
          <a-input v-model:value="formData.name" placeholder="Например: БД" />
        </a-form-item>
        <a-form-item label="Группа">
          <a-input v-model:value="formData.group" placeholder="Б9124-09.03.03ру" />
        </a-form-item>
        <a-form-item label="Аудитория">
          <a-input v-model:value="formData.room" placeholder="408" />
        </a-form-item>
        <a-form-item label="Дата" required>
          <a-date-picker v-model:value="formData.date" format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Время" required>
          <a-select v-model:value="formData.time" placeholder="Выберите время">
            <a-select-option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <Teleport to="body">
      <Transition name="marks-modal">
        <div v-if="marksModalVisible" class="marks-overlay" @click.self="marksModalVisible = false">
          <div class="marks-modal-glass">
            <MarksPage 
              :subjectName="currentSubject" 
              :groupId="currentGroupId"
              :groupName="currentGroupName"
              :scheduleId="currentScheduleId"
              @close="marksModalVisible = false" 
            />
          </div>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="marks-modal">
        <div v-if="studentMarksVisible" class="marks-overlay" @click.self="studentMarksVisible = false">
          <div class="marks-modal-glass student-modal">
            <StudentMarksPage
              :subjectName="currentSubject"
              :scheduleId="currentScheduleId"
              @close="studentMarksVisible = false"
            />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script>
import { getSchedule } from '@/services/schedule'
import { timeSlots } from '../data/scheduleData.js'
import { message } from 'ant-design-vue'
import MarksPage from '@/views/MarksPage.vue'
import StudentMarksPage from '@/views/StudentMarksPage.vue'
import { getStoredUser, fetchAndStoreProfile, logout as authLogout, isStudent } from '@/services/auth'

export default {
  name: 'SchedulePage',
  components: { MarksPage, StudentMarksPage },
  async mounted() {
    try {
      if (!this.user) this.user = await fetchAndStoreProfile()
      const data = await getSchedule()
      this.lessons = this.transformSchedule(data)
    } catch (e) {
      console.error('Ошибка загрузки расписания:', e)
    }
  },
  data() {
    return {
      user: getStoredUser(),
      weekOffset: 0,
      timeSlots,
      lessons: [],
      marksModalVisible: false,
      studentMarksVisible: false,
      currentSubject: '',
      currentGroupId: null,
      currentGroupName: '',
      currentScheduleId: null,
      modalVisible: false,
      editingLesson: null,
      formData: { name: '', group: '', date: undefined, time: undefined, room: '' }
    }
  },
  computed: {
    isStudent() { return isStudent(this.user) },
    initials() {
      const name = this.user?.full_name || ''
      return name.split(' ').filter(Boolean).map(w => w[0]).slice(0,2).join('').toUpperCase() || 'ГС'
    },
    weekDays() {
      const now = new Date()
      const today = now.getDay()
      const diffToMonday = today === 0 ? -6 : 1 - today
      const monday = new Date(now)
      monday.setDate(now.getDate() + diffToMonday + this.weekOffset * 7)
      const days = []
      const names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
      for (let i = 0; i < names.length; i++) {
        const day = new Date(monday)
        day.setDate(monday.getDate() + i)
        const year = day.getFullYear()
        const month = (day.getMonth() + 1).toString().padStart(2, '0')
        const dateNum = day.getDate().toString().padStart(2, '0')
        days.push({
          name: names[i],
          date: `${year}-${month}-${dateNum}`,
          dateStr: `${dateNum}.${month}`
        })
      }
      return days
    },
    currentDateRange() {
      if (!this.weekDays.length) return ''
      const start = this.weekDays[0].dateStr
      const end = this.weekDays[this.weekDays.length-1].dateStr
      const startMonth = parseInt(start.split('.')[1])
      const endMonth = parseInt(end.split('.')[1])
      if (startMonth === endMonth) {
        return `${this.getMonthName(startMonth)} ${start.split('.')[0]} — ${end.split('.')[0]}`
      }
      return `${this.getMonthName(startMonth)} ${start.split('.')[0]} — ${this.getMonthName(endMonth)} ${end.split('.')[0]}`
    },
    weekStatus() {
      if (this.weekOffset === 0) return 'Текущая неделя'
      if (this.weekOffset === -1) return 'Предыдущая неделя'
      if (this.weekOffset === 1) return 'Следующая неделя'
      if (this.weekOffset < 0) return `${Math.abs(this.weekOffset)} недели назад`
      return `${this.weekOffset + 1} неделя`
    }
  },
  methods: {
    getMonthName(monthNum) {
      const months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
      return months[monthNum - 1]
    },
    transformSchedule(scheduleFromDB) {
      const lessons = []
      const weekDays = this.weekDays
      for (const item of scheduleFromDB) {
        const dayIndex = item.weekday - 1
        if (dayIndex < 0 || dayIndex >= weekDays.length) continue
        const dateObj = weekDays[dayIndex]
        if (!dateObj) continue
        const time = this.timeSlots[item.lesson_number - 1]
        if (!time) continue
        lessons.push({
          id: item.id,
          date: dateObj.date,
          time: time,
          name: item.subject?.name || `Предмет ${item.subject_id}`,
          group: item.group?.name || `Группа ${item.group_id}`,
          group_id: item.group_id,
          room: item.room?.number || ''
        })
      }
      return lessons
    },
    getLesson(date, time) { return this.lessons.find(l => l.date === date && l.time === time) },
    isToday(dateStr) {
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0')
      const day = today.getDate().toString().padStart(2, '0')
      return dateStr === `${year}-${month}-${day}`
    },
    isCurrentTimeSlot(time) {
      const now = new Date()
      const [hours, minutes] = time.split(':')
      const slotStart = new Date()
      slotStart.setHours(parseInt(hours), parseInt(minutes), 0)
      const slotEnd = new Date(slotStart)
      slotEnd.setMinutes(slotStart.getMinutes() + 90)
      return now >= slotStart && now <= slotEnd
    },
    prevWeek() { this.weekOffset-- },
    nextWeek() { this.weekOffset++ },
    logout() { authLogout(); this.$router.push('/') },
    lessonSubtitle(lesson) {
      const parts = []
      if (lesson.room) parts.push(`ауд. ${lesson.room}`)
      return parts.join(' · ') || 'Пара'
    },
    onLessonClick(lesson) {
      if (!lesson) return
      this.currentSubject = lesson.name
      this.currentScheduleId = lesson.id || null
      if (this.isStudent) this.studentMarksVisible = true
      else this.openMarksModal(lesson)
    },
    openMarksModal(lesson) {
      this.currentSubject = lesson.name
      this.currentGroupId = lesson.group_id || 1
      this.currentGroupName = lesson.group || 'Группа'
      this.currentScheduleId = lesson.id || null
      this.marksModalVisible = true
    },
    goToAllGrades() {
      if (this.isStudent) this.$router.push('/my-grades')
      else this.$router.push('/all-grades')
    },
    openAddModal() {
      this.editingLesson = null
      this.formData = { name: '', group: '', date: undefined, time: undefined, room: '' }
      this.modalVisible = true
    },
    openEditModal(lesson) {
      this.editingLesson = lesson
      this.formData = {
        name: lesson.name,
        group: lesson.group || '',
        date: lesson.date,
        time: lesson.time,
        room: lesson.room || ''
      }
      this.modalVisible = true
    },
    closeModal() { this.modalVisible = false; this.editingLesson = null },
    handleSaveLesson() {
      if (!this.formData.name || !this.formData.date || !this.formData.time) {
        message.warning('Заполните название, дату и время')
        return
      }
      const dateStr = typeof this.formData.date === 'string' ? this.formData.date : this.formData.date.format('YYYY-MM-DD')
      const newLesson = {
        id: this.editingLesson ? this.editingLesson.id : Date.now(),
        date: dateStr,
        time: this.formData.time,
        name: this.formData.name,
        group: this.formData.group || '',
        room: this.formData.room || ''
      }
      if (this.editingLesson) {
        const index = this.lessons.findIndex(l => l.id === this.editingLesson.id)
        if (index !== -1) this.lessons[index] = newLesson
        message.success('Пара обновлена')
      } else {
        if (this.lessons.some(l => l.date === dateStr && l.time === this.formData.time)) {
          message.error('На это время уже есть пара')
          return
        }
        this.lessons.push(newLesson)
        message.success('Пара добавлена')
      }
      this.closeModal()
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

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

.schedule-card {
  width: 100%;
  max-width: 1400px;
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
.header-right { display: flex; align-items: center; gap: 1.2rem; }

.grades-btn, .logout-btn, .nav-arrow {
  transition: all 0.2s ease;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.4);
  cursor: pointer;
}
.grades-btn:active, .logout-btn:active, .nav-arrow:active {
  transform: translateY(2px);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.grades-btn {
  background: linear-gradient(to bottom, #8fbee6, #537ac2);
  border: 1px solid rgba(79, 107, 200, 0.7);
  border-radius: 25px;
  padding: 10px 20px;
  color: white;
  font-weight: 600;
  font-size: 14px;
}
.grades-btn:hover {
  background: linear-gradient(to bottom, #85b5de, #385ca0);
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
.avatar-initials { font-weight: bold; font-size: 18px; color: white; }
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

.page-nav {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 20px 0 10px;
}
.nav-link {
  padding: 8px 28px;
  border-radius: 40px;
  background: rgba(238,245,255,0.7);
  color: #1f4a6e;
  text-decoration: none;
  font-weight: 600;
  border: 1px solid #6c9ebf;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.nav-link.active, .nav-link:hover {
  background: #6c9ebf;
  color: white;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.schedule-content { padding: 0 2rem 2rem; }
.week-header { text-align: center; margin: 1.5rem 0 0.5rem; }
.date-range {
  font-size: 28px;
  font-weight: 700;
  color: #1f3b4c;
  background: rgba(192, 222, 255, 0.2);
  display: inline-block;
  padding: 0.2rem 1.5rem;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}
.week-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin: 0.8rem 0 1.5rem;
}
.nav-arrow {
  width: 44px;
  height: 44px;
  background: linear-gradient(to bottom, #eef5ff, #bcdeff);
  border: 1px solid rgba(60,100,130,0.5);
  border-radius: 50%;
  font-size: 22px;
  font-weight: bold;
  color: #1f4a6e;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-arrow:hover {
  background: linear-gradient(to bottom, #f1f9ff, #d3e5f8);
  transform: scale(1.02);
}
.week-status {
  background: #283347;
  backdrop-filter: blur(4px);
  padding: 8px 28px;
  border-radius: 20px;
  font-weight: 500;
  color: #f0f8ff;
  border: 1px solid rgba(66, 108, 193, 0.4);
  font-size: 15px;
  box-shadow: inset 0 1px 1px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.1);
}

.schedule-table-wrapper {
  overflow-x: auto;
  border-radius: 28px;
  background: rgba(80,110,140,0.3);
  border: 1px solid rgba(255,255,255,0.5);
}
.schedule-table {
  width: 100%;
  min-width: 950px;
  border-collapse: collapse;
  background: rgba(255,255,255,0.1);
  table-layout: fixed;
}

.schedule-table .time-col,
.schedule-table .time-cell {
  width: 110px;
}
.schedule-table .day-col,
.schedule-table .lesson-cell {
  width: calc((100% - 110px) / 6);
}

.schedule-table th,
.schedule-table td {
  padding: 12px 6px;
  border: 1px solid rgba(215, 232, 255, 0.3);
  vertical-align: middle;
  height: 90px; 
  max-height: 90px;
  min-height: 90px;
}
.schedule-table tbody tr {
  height: 90px;
}
.schedule-table tbody td {
  height: 120px;
}

.day-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  white-space: normal;
}

.time-col,
.day-col {
  background: rgba(65, 100, 140, 0.4);
  color: white;
  font-weight: 600;
}
.time-col {
  background: rgba(93, 124, 167, 0.5);
}
.day-name {
  font-weight: 700;
  font-size: 20px;
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
  white-space: nowrap;
}
.day-date {
  font-size: 14px;
  font-weight: 600;
  color: #eef5ff;
  background: rgba(193, 217, 237, 0.3);
  padding: 4px 10px;
  border-radius: 40px;
  backdrop-filter: blur(2px);
  white-space: nowrap;
}

.today-col {
  background: rgba(90, 135, 175, 0.7);
  border-bottom: 3px solid #ffda88;
}
.today-col .day-name {
  text-shadow: 0 0 6px rgba(0,0,0,0.3);
}
.today-col .day-date {
  background: rgba(158, 186, 223, 0.6);
  color: #fff;
}

.time-cell {
  background: rgba(93, 124, 167, 0.5);
}
.time-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.time-hour {
  font-weight: 700;
  font-size: 18px;
  color: white;
  background: rgba(24, 48, 67, 0.2);
  padding: 4px 12px;
  border-radius: 30px;
  white-space: nowrap;
}

.current-time-row {
  background: rgba(39, 72, 105, 0.2);
}
.current-time-row .time-cell {
  background: rgba(88, 132, 165, 0.8);
}
.current-time-row .time-hour {
  background: #ffffffcc;
  color: #1f4a6e;
  font-weight: 800;
}
.current-time-row .lesson-cell {
  background: rgba(100, 140, 170, 0.3);
}
.current-time-row .now-badge {
  font-size: 24px;
  line-height: 1;
  margin-left: 6px;
  color: #f4ecb4;
  text-shadow: 0 0 4px #8ab3d1;
  animation: softBlink 1.5s infinite;
}

.lesson-cell {
  background: rgba(95,125,150,0.2);
  cursor: pointer;
  transition: background 0.2s;
  padding: 8px;
  text-align: left;
  white-space: normal;
  vertical-align: top;
}
.lesson-cell:hover {
  background: rgba(110, 145, 175, 0.4);
}
.lesson-card {
  background: rgba(255, 255, 255, 0.94);
  border-radius: 24px;
  padding: 12px 14px;
  text-align: left;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
  white-space: normal;
  height: calc(100% - 16px); 
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.lesson-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0,0,0,0.15);
  background: rgb(248, 252, 255);
}
.lesson-name {
  font-weight: 700;
  font-size: 17px;
  color: #1a4c6e;
  margin-bottom: 6px;
  line-height: 1.3;
}
.lesson-details {
  font-size: 13px;
  font-weight: 500;
  color: #2c627e;
  line-height: 1.4;
}

@media (max-width: 1024px) {
  .screen { padding: 1rem; }
  .card-header { padding: 1rem 1.5rem; }
  .logo-text { font-size: 24px; }
  .date-range { font-size: 24px; }
  .day-name { font-size: 18px; }
  .schedule-table th, .schedule-table td {
    height: 120px;
  }
}
@media (max-width: 768px) {
  .card-header { flex-direction: column; gap: 12px; align-items: stretch; }
  .header-right { justify-content: center; }
  .day-name { font-size: 16px; }
  .day-date { font-size: 12px; }
  .schedule-table th, .schedule-table td {
    height: 100px;
    padding: 6px 3px;
  }
  .lesson-card { padding: 8px 10px; }
  .lesson-name { font-size: 15px; }
}
@media (max-width: 560px) {
  .schedule-content { padding: 0 1rem 1rem; }
  .time-hour { font-size: 14px; }
  .schedule-table th, .schedule-table td {
    height: 90px;
    padding: 4px 2px;
  }
  .lesson-card { padding: 6px 8px; }
}
@keyframes softBlink {
  0% { opacity: 0.5; text-shadow: 0 0 0 #5a9ac0; }
  50% { opacity: 1; text-shadow: 0 0 6px #5a9ac0; }
  100% { opacity: 0.5; text-shadow: 0 0 0 #5a9ac0; }
}
</style>

<style>
.marks-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5,15,35,0.55);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.marks-modal-glass {
  width: 100%;
  max-width: 1100px;
  max-height: 88vh;
  background: rgba(12,28,65,0.55);
  backdrop-filter: blur(40px);
  border: 1px solid rgba(140,190,255,0.18);
  border-radius: 28px;
  overflow: hidden;
}
.marks-modal-enter-active, .marks-modal-leave-active { transition: all 0.3s ease; }
.marks-modal-enter-from { opacity: 0; transform: scale(0.95); }
.marks-modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>