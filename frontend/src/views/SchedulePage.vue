<template>
  <div class="screen" :class="{ 'is-mobile': isMobile }">
    <div class="schedule-card" :class="{ 'is-mobile': isMobile }">
      <div class="card-header">
        <div class="header-left">
          <router-link to="/" class="logo-link">
            <img src="@/assets/icon.png" alt="Logo" class="logo-icon" />
            <span class="logo-text">UniDiary</span>
          </router-link>
        </div>
        <div class="week-header">
          <div class="date-range">{{ currentDateRange }}</div>
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
        <div v-if="isMobile" class="mobile-date-range">{{ currentDateRange }}</div>
        <div class="week-nav">
          <button class="nav-arrow" @click="prevWeek">←</button>
          <span class="week-status">{{ weekStatus }}</span>
          <button class="nav-arrow" @click="nextWeek">→</button>
        </div>

        <div v-if="isMobile" class="mobile-day-view">
          <div class="mobile-days-row">
            <button
              v-for="(day, index) in weekDays"
              :key="day.date"
              class="mobile-day-btn"
              :class="{ 'active': index === selectedDayIndex }"
              @click="selectedDayIndex = index"
            >
              {{ day.name }}
            </button>
          </div>

          <div class="mobile-lessons-list">
            <div
              v-for="time in timeSlots"
              :key="time"
              class="mobile-lesson-item"
              :class="{ 'current-mobile-slot': isToday(selectedDay.date) && isCurrentTimeSlot(time) }"
            >
              <div class="mobile-time-header">
                <span class="mobile-time-text">{{ time }}</span>
                <div class="mobile-time-line"></div>
              </div>

              <div
                v-if="getLesson(selectedDay.date, time)"
                class="mobile-lesson-card"
                @click="onLessonClick(getLesson(selectedDay.date, time))"
              >
                <div class="mobile-lesson-name">{{ getLesson(selectedDay.date, time).name }}</div>
                <div class="mobile-lesson-meta">
                  <span
                    v-if="!isStudent && getLesson(selectedDay.date, time).group"
                    class="group-badge-small"
                  >
                    {{ getLesson(selectedDay.date, time).group }}
                  </span>
                  <span
                    v-if="getLesson(selectedDay.date, time)?.room"
                    class="room-badge room-badge-right"
                  >
                    {{ getLesson(selectedDay.date, time).room }}
                  </span>
                </div>
              </div>
              <div v-else class="mobile-empty-slot">
                <span class="empty-text">Нет пары</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="schedule-table-wrapper" ref="tableWrapper">
          <table class="schedule-table" ref="scheduleTable">
            <thead ref="tableHead" style="flex-shrink: 0;">
              <tr>
                <th class="time-col">Время</th>
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
            <tbody ref="tableBody">
              <tr
                v-for="time in timeSlots"
                :key="time"
                :class="{ 'current-time-row': isCurrentTimeSlot(time) }"
                class="schedule-row"
              >
                <td class="time-cell">
                  <div class="time-card">
                    <span class="time-hour">{{ time }}</span>
                    <span v-if="isCurrentTimeSlot(time)" class="now-badge">•</span>
                  </div>
                </td>
                <td
                  v-for="day in weekDays"
                  :key="day.date"
                  class="lesson-cell"
                  @click="onLessonClick(getLesson(day.date, time))"
                >
                  <div v-if="getLesson(day.date, time)" class="lesson-card">
                    <div class="lesson-name" :title="getLesson(day.date, time).name">
                      {{ getLesson(day.date, time).name }}
                    </div>
                    <div class="lesson-details" :class="{ 'student-details': isStudent }">
                      <template v-if="!isStudent">
                        <span class="group-badge-small">{{ getLesson(day.date, time).group }}</span>
                        <span v-if="getLesson(day.date, time)?.room" class="room-badge">{{ getLesson(day.date, time).room }}</span>
                      </template>
                      <template v-else>
                        <span v-if="getLesson(day.date, time)?.room" class="room-badge">{{ getLesson(day.date, time).room }}</span>
                      </template>
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
      this.$nextTick(() => {
        this.resizeRows()
        this.adjustFontSizes()
      })
      this.checkIfMobile()
      window.addEventListener('resize', this.onWindowResize)
    } catch (e) {
      console.error('Ошибка загрузки расписания:', e)
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onWindowResize)
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
      formData: { name: '', group: '', date: undefined, time: undefined, room: '' },
      isMobile: false,
      selectedDayIndex: 0
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
    },
    selectedDay() {
      if (this.weekDays.length > 0) {
        return this.weekDays[this.selectedDayIndex] || this.weekDays[0]
      }
      return { name: '', date: '', dateStr: '' }
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
    },
    resizeRows() {
      const wrapper = this.$refs.tableWrapper
      const head = this.$refs.tableHead
      const body = this.$refs.tableBody
      if (!wrapper || !head || !body) return

      const wrapperHeight = wrapper.clientHeight
      const headHeight = head.clientHeight
      const availableHeight = wrapperHeight - headHeight - 4

      const rows = body.querySelectorAll('tr')
      if (rows.length === 0) return

      const rowHeight = Math.floor(availableHeight / rows.length)
      const minRowHeight = 40
      const maxRowHeight = 120
      const finalHeight = Math.min(Math.max(rowHeight, minRowHeight), maxRowHeight)

      rows.forEach(row => {
        row.style.height = finalHeight + 'px'
        row.style.maxHeight = finalHeight + 'px'
        row.style.minHeight = finalHeight + 'px'
        row.querySelectorAll('td').forEach(cell => {
          cell.style.height = finalHeight + 'px'
          cell.style.maxHeight = finalHeight + 'px'
          cell.style.minHeight = finalHeight + 'px'
        })
      })

      this.$nextTick(() => this.adjustFontSizes())
    },
    adjustFontSizes() {
      const cards = this.$el.querySelectorAll('.lesson-card')
      cards.forEach(card => {
        const nameEl = card.querySelector('.lesson-name')
        const detailsEl = card.querySelector('.lesson-details')
        if (!nameEl || !detailsEl) return

        const text = nameEl.textContent
        if (!text) return

        nameEl.style.fontSize = ''
        detailsEl.style.fontSize = ''

        const parentWidth = nameEl.parentElement.clientWidth - 20
        if (parentWidth <= 0) return
        const isShort = text.length <= 11
        const nameBaseSize = isShort ? 17 : 15
        const detailsBaseSize = isShort ? 14 : 14

        nameEl.style.fontSize = nameBaseSize + 'px'
        let overflow = nameEl.scrollWidth > parentWidth
        let newNameSize = nameBaseSize
        while (overflow && newNameSize > 9) {
          newNameSize -= 0.5
          nameEl.style.fontSize = newNameSize + 'px'
          overflow = nameEl.scrollWidth > parentWidth
        }
        if (overflow) {
          nameEl.style.wordBreak = 'break-word'
          nameEl.style.overflowWrap = 'break-word'
        } else {
          nameEl.style.wordBreak = 'normal'
          nameEl.style.overflowWrap = 'normal'
        }

        detailsEl.style.fontSize = detailsBaseSize + 'px'
      })
    },
    checkIfMobile() {
      this.isMobile = window.innerWidth < 768
    },
    onWindowResize() {
      this.checkIfMobile()
      if (!this.isMobile) {
        this.resizeRows()
      }
    }
  },
  watch: {
    weekOffset() {
      this.$nextTick(() => {
        if (!this.isMobile) {
          this.resizeRows()
          this.adjustFontSizes()
        }
      })
    },
    lessons() {
      this.$nextTick(() => {
        if (!this.isMobile) {
          this.resizeRows()
          this.adjustFontSizes()
        }
      })
    },
    weekDays: {
      handler(newDays) {
        const todayIndex = newDays.findIndex(d => this.isToday(d.date))
        this.selectedDayIndex = todayIndex !== -1 ? todayIndex : 0
      },
      immediate: true
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
  padding: 2.5rem;
  font-family: 'Inter', system-ui, sans-serif;
}

.screen.is-mobile {
  background: url('@/assets/phone2.PNG');
  background-color: #8fa0d4;
  position: relative;
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

.screen.is-mobile .week-header {
  display: none;
}

.schedule-card {
  width: 98%;
  max-width: 1600px;
  height: 92vh;
  background: linear-gradient(145deg, rgba(245,250,255,0.65) 22%, rgba(210,230,245,0.45) 79%, rgba(180,205,225,0.65) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 48px;
  box-shadow: 0 16px 32px rgba(0,0,0,0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.schedule-card.is-mobile {
  height: auto;
  min-height: 92vh;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  border-radius: 32px;
}

.screen.is-mobile .card-header {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 2rem;
  background: rgba(227, 240, 255, 0.25);
  border-bottom: 1px solid rgba(86, 112, 193, 0.35);
  flex-shrink: 0;
}
.header-left .logo-link {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
}
.logo-icon { width: 40px; height: auto; }
.logo-text {
  font-size: 26px;
  font-weight: 800;
  color: #1f3b4c;
  letter-spacing: -0.5px;
}

.header-right { display: flex; align-items: center; gap: 1rem; }

.screen.is-mobile .header-right {
  gap: 6px;
  flex-wrap: nowrap;
}
.screen.is-mobile .grades-btn,
.screen.is-mobile .logout-btn {
  padding: 5px 12px;
  font-size: 12px;
  border-radius: 20px;
}
.screen.is-mobile .logout-btn {
  padding: 5px 14px;
}

.screen.is-mobile .user-avatar {
  display: none;
}

.screen.is-mobile .logo-link {
  gap: 6px;
}

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
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  border: 1px solid rgba(119, 155, 222, 0.7);
  border-radius: 30px;
  padding: 8px 18px;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}
.grades-btn:hover {
  background: linear-gradient(to bottom, #66a3db, #27559b);
  transform: translateY(-1px);
}
.user-avatar {
  width: 44px;
  height: 44px;
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
  padding: 8px 18px;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}
.logout-btn:hover {
  background: linear-gradient(to bottom, #66a3db, #27559b);
  transform: translateY(-1px);
}

.schedule-content {
  padding: 0 2rem 1.2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.mobile-date-range {
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  color: #1f3b4c;
  background: rgba(244, 249, 255, 0.3);
  display: inline-block;
  align-self: center;
  padding: 0.1rem 1.5rem;
  border-radius: 24px;
  backdrop-filter: blur(4px);
  margin-top: 0.8rem;
  margin-bottom: 0.4rem;
}

.week-header {
  text-align: center;
  margin: 0.5rem 0 0.1rem;
  flex-shrink: 0;
}
.date-range {
  font-size: 24px;
  font-weight: 700;
  color: #1f3b4c;
  background: rgba(244, 249, 255, 0.2);
  display: inline-block;
  padding: 0.1rem 1.5rem;
  border-radius: 24px;
  backdrop-filter: blur(4px);
  margin-left: 120px;
}

.week-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin: 0.8rem 0 0.8rem;  
  flex-shrink: 0;
}
.nav-arrow {
  width: 38px;
  height: 38px;
  background: linear-gradient(to bottom, #eef5ff, #bcdeff);
  border: 1px solid rgba(60,100,130,0.5);
  border-radius: 50%;
  font-size: 20px;
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
.nav-arrow:disabled {
  opacity: 0.5;
  transform: none;
  box-shadow: none;
  cursor: default;
}
.week-status {
  background: #283347;
  backdrop-filter: blur(4px);
  padding: 4px 22px;
  border-radius: 24px;
  font-weight: 500;
  color: #f0f8ff;
  border: 1px solid rgba(66, 108, 193, 0.4);
  font-size: 15px;
  box-shadow: inset 0 1px 1px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.1);
}

.schedule-table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  border-radius: 24px;
  background: rgba(80,110,140,0.3);
  border: 1px solid rgba(255,255,255,0.5);
  flex: 1;
  min-height: 0;
  margin-bottom: 0.3rem;
}
.schedule-table {
  width: 100%;
  min-width: 850px;
  border-collapse: collapse;
  background: rgba(255,255,255,0.1);
  table-layout: fixed;
  height: 100%;
}
.schedule-table tbody {
  height: 100%;
}

.schedule-table .time-col,
.schedule-table .time-cell {
  width: 90px;
}
.schedule-table .day-col,
.schedule-table .lesson-cell {
  width: calc((100% - 90px) / 6);
}

.schedule-table thead {
  flex-shrink: 0;
}
.schedule-table th {
  padding: 4px 5px;
  border: 1px solid rgba(215, 232, 255, 0.3);
  vertical-align: middle;
  min-height: 72px;
  height: 72px;
  overflow: visible;
}
.schedule-table td {
  padding: 4px 5px;
  border: 1px solid rgba(215, 232, 255, 0.3);
  vertical-align: middle;
}

.day-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 2px 0;
  white-space: normal;
  width: 100%;
  word-break: break-word;
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
  font-size: 16px;
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
  white-space: nowrap;
}
.day-date {
  font-size: 12px;
  font-weight: 600;
  color: #eef5ff;
  background: rgba(193, 217, 237, 0.3);
  padding: 2px 10px;
  border-radius: 40px;
  backdrop-filter: blur(2px);
  display: inline-block;
  white-space: nowrap;
  word-break: break-word;
  max-width: 100%;
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
  gap: 2px;
}
.time-hour {
  font-weight: 700;
  font-size: 15px;
  color: white;
  background: rgba(24, 48, 67, 0.2);
  padding: 3px 12px;
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
  font-size: 20px;
  line-height: 1;
  margin-left: 4px;
  color: #f4ecb4;
  text-shadow: 0 0 4px #8ab3d1;
  animation: softBlink 1.5s infinite;
}

.lesson-cell {
  background: rgba(95,125,150,0.2);
  cursor: pointer;
  transition: background 0.2s;
  padding: 4px;
  text-align: left;
  white-space: normal;
  vertical-align: top;
}
.lesson-cell:hover {
  background: rgba(110, 145, 175, 0.4);
}

.lesson-card {
  background: rgba(255, 255, 255, 0.94);
  border-radius: 18px;
  padding: 8px 14px;
  text-align: left;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
  white-space: normal;
  height: calc(100% - 8px);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
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
  line-height: 1.2;
  margin-bottom: 1px;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

.lesson-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #2c627e;
  line-height: 1.3;
  margin-top: 8px;
  width: 100%;
}

.lesson-details.student-details {
  justify-content: flex-end;
  align-items: flex-end;
  margin-top: auto;
}

.group-badge-small {
  font-size: 12px;
  color: #5580ab;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  flex-shrink: 1;
  margin-right: 8px;
}

.room-badge {
  display: inline-block;
  background: rgba(186, 207, 239, 0.7);
  border-radius: 16px;
  padding: 2px 12px;
  margin-bottom: 4px;
  margin-top: 1px;
  font-weight: 600;
  color: #1a4c6e;
  font-size: inherit;
  line-height: 1.4;
  letter-spacing: 0.3px;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255,255,255,0.3);
  flex-shrink: 0;
}

.mobile-day-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  margin-top: 0.4rem;
}

.mobile-days-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.mobile-day-btn {
  background: none;
  border: none;
  font-weight: 600;
  font-size: 16px;
  color: #3a5a78;
  padding: 0.2rem 0.3rem;
  cursor: pointer;
  transition: color 0.2s, border-bottom 0.2s;
  border-bottom: 2px solid transparent;
  outline: none;
}
.mobile-day-btn.active {
  color: #2d6fb4;
  border-bottom-color: #2d6fb4;
}

.mobile-lessons-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 0 0.5rem 1rem;
}

.mobile-lesson-item {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.mobile-time-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.mobile-time-text {
  font-weight: 600;
  font-size: 14px;
  color: #5b7d99;
  white-space: nowrap;
}

.mobile-time-line {
  flex: 1;
  height: 1px;
  background: rgba(70, 130, 200, 0.2);
}

.mobile-lesson-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 16px;
  padding: 0.6rem 0.9rem;
  box-shadow: 0 4px 10px rgba(80, 140, 210, 0.12);
  display: flex;
  flex-direction: column;
  justify-content: center;
  cursor: pointer;
  transition: 0.2s;
  border: 1px solid rgba(70, 130, 200, 0.08);
}
.mobile-lesson-card:active {
  transform: scale(0.98);
  background: #e6f0fa;
}

.mobile-lesson-name {
  font-weight: 700;
  font-size: 15px;
  color: #1a4460;
  margin-bottom: 4px;
  line-height: 1.3;
}

.mobile-lesson-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #3b6582;
}

.mobile-lesson-meta .room-badge-right {
  margin-left: auto;
  background: rgba(88, 150, 210, 0.15);
  border-radius: 12px;
  padding: 2px 10px;
  font-weight: 600;
  color: #245b80;
  backdrop-filter: blur(2px);
}

.mobile-empty-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(206, 219, 249, 0.25);
  backdrop-filter: blur(4px);
  border-radius: 16px;
  color: #9aafc4;
  font-size: 14px;
  font-weight: 500;
  padding: 0.7rem;
}

.current-mobile-slot .mobile-time-text {
  color: #2d6fb4;
  font-weight: 700;
}
.current-mobile-slot .mobile-time-line {
  background: rgba(45, 111, 180, 0.5);
}
.current-mobile-slot .mobile-lesson-card {
  border-left: 3px solid #4a90d9;
  background: #f4f9ff;
}

@media (max-width: 1024px) {
  .screen { padding: 1.5rem; }
  .card-header { padding: 0.6rem 1.5rem; }
  .logo-text { font-size: 22px; }
  .date-range { font-size: 22px; }
  .day-name { font-size: 15px; }
  .lesson-name { font-size: 14px; }
  .lesson-details { font-size: 11px; }
  .time-hour { font-size: 14px; }
}
@media (max-width: 768px) {
  .screen { padding: 1rem; }
  .day-name { font-size: 14px; }
  .day-date { font-size: 11px; }
  .lesson-card { padding: 6px 12px; }
  .lesson-name { font-size: 13px; }
  .lesson-details { font-size: 10px; }
}
@media (max-width: 560px) {
  .screen { padding: 0.5rem; }
  .schedule-content { padding: 0 0.8rem 1rem; }
  .time-hour { font-size: 12px; }
  .lesson-card { padding: 4px 10px; }
  .lesson-name { font-size: 11px; }
  .lesson-details { font-size: 9px; }
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
  height: 88vh;
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