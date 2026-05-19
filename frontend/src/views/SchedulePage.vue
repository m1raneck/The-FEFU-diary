<template>
  <div class="schedule-container">
    <div class="background-layer"></div>
    <div class="top-header"></div>
    <div class="top-right">
      <div class="avatar-circle"></div>
      <div class="avatar-text">ГС</div>
      <a-button class="logout-btn" @click="logout" type="link">
        <span class="logout-icon">→</span> Выйти
      </a-button>
    </div>

    <div class="header-section">
      <div class="date-range">{{ currentDateRange }}</div>
    </div>

    <div class="week-nav">
      <a-button class="nav-arrow" @click="prevWeek" shape="circle">←</a-button>
      <span class="week-status">{{ weekStatus }}</span>
      <a-button class="nav-arrow" @click="nextWeek" shape="circle">→</a-button>
    </div>

    <div class="schedule-table-wrapper">
      <table class="schedule-table">
        <thead>
          <tr class="table-header">
            <th class="time-col">
              <span class="time-label">Время</span>
            </th>
            <th
              v-for="day in weekDays"
              :key="day.date"
              class="day-col"
              :class="{ 'today-col': isToday(day.date) }"
            >
              <div class="day-content">
                <span class="day-name">{{ day.name }}</span>
                <span class="day-date">{{ day.dateStr }}</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="time in timeSlots"
            :key="time"
            :class="{ 'current-time-row': isCurrentTimeSlot(time) }"
          >
            <td class="time-cell">
              <span class="time-badge">{{ time }}</span>
              <span v-if="isCurrentTimeSlot(time)" class="now-dot"></span>
            </td>
            <td
              v-for="day in weekDays"
              :key="day.date"
              class="lesson-cell"
              @click="openMarksModal(getLesson(day.date, time))"
            >
              <div v-if="getLesson(day.date, time)" class="lesson-block">
                <div class="lesson-title">{{ getLesson(day.date, time).name }}</div>
                <div class="lesson-group">{{ getLesson(day.date, time).group }}</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модалка для редактирования / добавления пары (оставлена для полноты) -->
    <a-modal
      v-model:open="modalVisible"
      :title="editingLesson ? 'Редактировать пару' : 'Добавить пару'"
      @ok="handleSaveLesson"
      @cancel="closeModal"
    >
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

    <!-- Красивое полупрозрачное всплывающее окно журнала оценок -->
    <Teleport to="body">
      <Transition name="marks-modal">
        <div v-if="marksModalVisible" class="marks-overlay" @click.self="marksModalVisible = false">
          <div class="marks-modal-glass">
            <MarksPage :subjectName="currentSubject" @close="marksModalVisible = false" />
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

export default {
  name: 'SchedulePage',
  components: {
    MarksPage
  },
  async mounted() {
  try {
    const data = await getSchedule()
    this.lessons = this.transformSchedule(data)
  } catch (error) {
    console.warn('Не удалось загрузить расписание из БД, загружаю демо-пары', error)
    this.generateDemoLessons()
  }
},
  data() {
    return {
      weekOffset: 0,
      timeSlots,
      lessons: [],
      // для модалки журнала
      marksModalVisible: false,
      currentSubject: '',
      // для модалки редактирования
      modalVisible: false,
      editingLesson: null,
      formData: {
        name: '',
        group: '',
        date: undefined,
        time: undefined,
        room: ''
      }
    }
  },
  computed: {
    weekDays() {
      const now = new Date()
      const today = now.getDay()
      const diffToMonday = today === 0 ? -6 : 1 - today
      const monday = new Date(now)
      monday.setDate(now.getDate() + diffToMonday + this.weekOffset * 7)

      const weekDaysArray = []
      const daysNames = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
      for (let i = 0; i < 7; i++) {
        const day = new Date(monday)
        day.setDate(monday.getDate() + i)
        const year = day.getFullYear()
        const month = (day.getMonth() + 1).toString().padStart(2, '0')
        const dateNum = day.getDate().toString().padStart(2, '0')
        weekDaysArray.push({
          name: daysNames[i],
          date: `${year}-${month}-${dateNum}`,
          dateStr: `${dateNum}.${month}`
        })
      }
      return weekDaysArray
    },
    currentDateRange() {
      if (this.weekDays.length === 0) return ''
      const start = this.weekDays[0].dateStr
      const end = this.weekDays[6].dateStr
      const startMonth = this.weekDays[0].dateStr.split('.')[1]
      const endMonth = this.weekDays[6].dateStr.split('.')[1]
      if (startMonth === endMonth) {
        return `${this.getMonthName(parseInt(startMonth))} ${start.split('.')[0]} — ${end.split('.')[0]}`
      }
      return `${this.getMonthName(parseInt(startMonth))} ${start.split('.')[0]} — ${this.getMonthName(parseInt(endMonth))} ${end.split('.')[0]}`
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
        // Преобразуем массив из БД в формат, понятный компоненту
        const lessons = []
        const weekDays = this.weekDays   // массив { date: '2025-05-19', name: 'ПН', dateStr: '19.05' }
        
        for (const item of scheduleFromDB) {
          // weekday: 1=ПН, 2=ВТ, ..., 7=ВС
          const dayIndex = item.weekday - 1
          if (dayIndex < 0 || dayIndex >= weekDays.length) continue
          
          const dateObj = weekDays[dayIndex]
          if (!dateObj) continue
          
          // lesson_number: 1 -> timeSlots[0] = '08:30'
          const time = this.timeSlots[item.lesson_number - 1]
          if (!time) continue
          
          // Название предмета – если пришло вложенным (subject.name), иначе оставляем subject_id
          const subjectName = item.subject?.name || `Предмет ${item.subject_id}`
          const groupName = item.group?.name || `Группа ${item.group_id}`
          const roomNumber = item.room?.number || (item.room_id ? `Ауд. ${item.room_id}` : '')
          
          lessons.push({
            id: item.id,
            date: dateObj.date,
            time: time,
            name: subjectName,
            group: groupName,
            room: roomNumber
          })
        }
        return lessons
      },
    generateDemoLessons() {
      const demo = []
      const week = this.weekDays
      const monday = week.find(d => d.name === 'ПН')
      if (monday) {
        demo.push({ id: Date.now() + 1, date: monday.date, time: '08:30', name: 'БД', group: 'Б9124-09.03.03ру', room: '408' })
        demo.push({ id: Date.now() + 2, date: monday.date, time: '10:10', name: 'Английский', group: 'Б9124-09.03.03ру', room: '301' })
      }
      const tuesday = week.find(d => d.name === 'ВТ')
      if (monday) {
        demo.push({ id: Date.now() + 1, date: tuesday.date, time: '11:50', name: 'Дизайн', group: 'Б9124-09.03.03ру', room: '408' })
        demo.push({ id: Date.now() + 2, date: tuesday.date, time: '10:10', name: 'ОЦГ', group: 'Б9124-09.03.03ру', room: '301' })
      }
      const friday = week.find(d => d.name === 'ПТ')
      if (monday) {
        demo.push({ id: Date.now() + 1, date: friday.date, time: '13:30', name: 'БД', group: 'Б9124-09.03.03ру', room: '408' })
        demo.push({ id: Date.now() + 2, date: friday.date, time: '08:30', name: 'Методы', group: 'Б9124-09.03.03ру', room: '301' })
      }
      const wednesday = week.find(d => d.name === 'СР')
      if (wednesday) {
        demo.push({ id: Date.now() + 3, date: wednesday.date, time: '11:50', name: 'Философия', group: 'Б9124-09.03.03ру', room: '215' })
      }
      this.lessons = demo
    },
    getLesson(date, time) {
      return this.lessons.find(l => l.date === date && l.time === time)
    },
    isToday(dateStr) {
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0')
      const day = today.getDate().toString().padStart(2, '0')
      const localToday = `${year}-${month}-${day}`
      return dateStr === localToday
    },
    isCurrentTimeSlot(time) {
      const now = new Date()
      const [hours, minutes] = time.split(':')
      const slotStart = new Date()
      slotStart.setHours(parseInt(hours), parseInt(minutes), 0)
      const slotEnd = new Date(slotStart)
      slotEnd.setMinutes(slotEnd.getMinutes() + 90)
      return now >= slotStart && now <= slotEnd
    },
    prevWeek() {
      this.weekOffset--
    },
    nextWeek() {
      this.weekOffset++
    },
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/')
    },
    // Метод открытия журнала (клик по паре)
    openMarksModal(lesson) {
      if (!lesson) return
      this.currentSubject = lesson.name
      this.marksModalVisible = true
    },
    // Методы для модалки редактирования
    openAddModal() {
      this.editingLesson = null
      this.formData = {
        name: '',
        group: '',
        date: undefined,
        time: undefined,
        room: ''
      }
      this.modalVisible = true
    },
    openEditModal(lesson) {
      if (!lesson) return
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
    closeModal() {
      this.modalVisible = false
      this.editingLesson = null
    },
    handleSaveLesson() {
      if (!this.formData.name || !this.formData.date || !this.formData.time) {
        message.warning('Заполните название, дату и время')
        return
      }
      const dateStr = typeof this.formData.date === 'string' 
        ? this.formData.date 
        : this.formData.date.format('YYYY-MM-DD')
      
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
        const exists = this.lessons.some(l => l.date === dateStr && l.time === this.formData.time)
        if (exists) {
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

.schedule-container {
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow-x: auto;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(145deg, #b9d0e8 7.14%, #c8dff7);
  z-index: 0;
}

.top-header {
  position: relative;
  height: 80px;
  background: rgba(41, 77, 103, 0.75);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(156, 192, 221, 0.3);
  z-index: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
  transition: 0.2s;
}

.avatar-text {
  font-family: 'Krona One', 'Inter', system-ui, sans-serif;
  font-size: 20px;
  font-weight: bold;
  color: #eef5ff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.logout-btn {
  background: rgba(200, 220, 240, 0.15);
  backdrop-filter: blur(4px);
  color: #eef5ff;
  border: 1px solid rgba(100, 160, 200, 0.5);
  border-radius: 28px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.logout-btn:hover {
  background: rgba(100, 160, 200, 0.35);
  border-color: #5a9ac0;
}

.header-section {
  position: relative;
  text-align: center;
  padding: 25px 0 8px;
  z-index: 1;
}

.date-range {
  font-size: 28px;
  font-weight: 600;
  color: #eef5ff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
  letter-spacing: -0.3px;
}

.week-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 8px 0 20px;
  z-index: 1;
  position: relative;
}

.nav-arrow {
  width: 40px;
  height: 40px;
  background: rgba(90, 154, 192, 0.35);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(90, 154, 192, 0.6);
  border-radius: 50%;
  cursor: pointer;
  color: #eef5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}
.nav-arrow:hover {
  background: #5a9ac0;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.week-status {
  font-size: 15px;
  font-weight: 500;
  color: #1e3a5f;
  background: rgba(238, 245, 255, 0.85);
  backdrop-filter: blur(4px);
  padding: 6px 24px;
  border-radius: 40px;
  border: 1px solid #5a9ac0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.schedule-table-wrapper {
  position: relative;
  margin: 0 20px 30px 20px;
  overflow-x: auto;
  z-index: 1;
  background: #647a96;
  border-radius: 28px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
}

.schedule-table {
  width: 100%;
  min-width: 950px;
  border-collapse: collapse;
  border-radius: 28px;
  overflow: hidden;
}

.table-header {
  background: linear-gradient(105deg, #617e94, #1f4e6e);
}

.time-col {
  width: 100px;
  padding: 16px 12px;
  text-align: center;
  border-right: 1px solid rgba(255, 255, 255, 0.15);
}

.time-label {
  font-weight: 600;
  font-size: 13px;
  color: #bdd4e8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.day-col {
  padding: 14px 10px;
  text-align: center;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.day-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.day-name {
  font-weight: 700;
  font-size: 18px;
  color: white;
}

.day-date {
  font-size: 13px;
  color: #bdd4e8;
}

.time-cell {
  background: #99abbf;
  text-align: center;
  padding: 20px 12px;
  border-bottom: 1px solid #647a96;
  border-right: 1px solid #647a96;
  vertical-align: middle;
}

.time-badge {
  display: inline-block;
  font-weight: 600;
  font-size: 15px;
  color: #1f4e6e;
  background: white;
  padding: 6px 14px;
  border-radius: 30px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  font-family: monospace;
}

.lesson-cell {
  background: #8da0b5;
  border-bottom: 1px solid #647a96;
  border-right: 1px solid #647a96;
  padding: 14px 12px;
  vertical-align: top;
  min-width: 150px;
  height: 110px;
  transition: background 0.2s;
}

.lesson-cell:hover {
  background: #8da0b5;
}

.lesson-block {
  background: linear-gradient(125deg, #ebf5ff, #e0edf8);
  border-radius: 20px;
  padding: 18px 14px;
  transition: all 0.25s;
  cursor: pointer;
  height: 100%;
  min-height: 86px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-left: 5px solid #3e8eb0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.lesson-block:hover {
  transform: translateY(-2px);
  background: linear-gradient(125deg, #f0f8ff, #e6f2fc);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.1);
}

.lesson-title {
  font-weight: 800;
  font-size: 18px;
  color: #1a4c6e;
  margin-bottom: 8px;
}

.lesson-group {
  font-size: 12px;
  font-weight: 500;
  color: #4a6f8c;
  line-height: 1.4;
}

.today-col {
  background: rgba(90, 154, 192, 0.2);
  position: relative;
}
.today-col::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 10%;
  width: 80%;
  height: 2px;
  background: rgba(178, 192, 209, 0.83);
  border-radius: 2px;
}

.current-time-row .time-cell {
  background: #b9c9da;
}

.current-time-row .time-badge {
  background: #ffffff;
  box-shadow: none;
  color: #204e6e;
}
.now-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #204e6e;
  border-radius: 50%;
  margin-left: 6px;
  vertical-align: middle;
  animation: pulse 1.2s infinite;
}
@keyframes pulse {
  0% { opacity: 0.4; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1.2); }
}
.current-time-row .lesson-cell {
  background: rgba(178, 192, 209, 0.83);
}

/* Адаптивность */
@media (max-width: 1024px) {
  .date-range { font-size: 24px; }
  .day-name { font-size: 16px; }
  .lesson-title { font-size: 16px; }
  .lesson-block { padding: 14px 10px; min-height: 78px; }
  .lesson-cell { min-width: 130px; height: 100px; }
  .time-cell { padding: 18px 8px; }
}
@media (max-width: 768px) {
  .top-right { right: 15px; gap: 10px; }
  .avatar-circle { width: 38px; height: 38px; }
  .avatar-text { font-size: 16px; }
  .logout-btn { padding: 5px 14px; font-size: 12px; }
  .date-range { font-size: 20px; }
  .day-name { font-size: 14px; }
  .day-date { font-size: 11px; }
  .week-status { font-size: 12px; padding: 4px 16px; }
  .lesson-title { font-size: 14px; }
  .lesson-group { font-size: 10px; }
  .lesson-block { padding: 12px 8px; min-height: 72px; }
  .lesson-cell { min-width: 115px; height: 92px; padding: 10px 8px; }
  .time-badge { font-size: 12px; padding: 4px 10px; }
}
@media (max-width: 600px) {
  .lesson-title { font-size: 13px; }
  .lesson-group { font-size: 9px; }
  .day-name { font-size: 12px; }
}
</style>
<style>
/* Оверлей журнала оценок */
.marks-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 15, 35, 0.55);
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
  background: rgba(12, 28, 65, 0.55);
  backdrop-filter: blur(40px) saturate(1.6) brightness(1.1);
  border: 1px solid rgba(140, 190, 255, 0.18);
  border-radius: 28px;
  box-shadow:
    0 40px 80px rgba(0, 0, 0, 0.45),
    0 0 80px rgba(50, 100, 200, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    inset 0 0 0 1px rgba(120, 170, 240, 0.06);
  overflow: hidden;
}

/* Анимация появления */
.marks-modal-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.3, 0.64, 1);
}
.marks-modal-leave-active {
  transition: all 0.2s ease;
}
.marks-modal-enter-from {
  opacity: 0;
  transform: scale(0.92) translateY(20px);
}
.marks-modal-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
.marks-modal-enter-from .marks-modal-glass,
.marks-modal-leave-to .marks-modal-glass {
  transform: scale(0.96);
}
</style>