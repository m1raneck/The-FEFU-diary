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
          <button class="schedule-btn" @click="$router.push('/schedule')">Расписание</button>
          <button class="logout-btn" @click="logout">Выйти</button>
          <div class="user-avatar">
            <span class="avatar-initials">{{ initials }}</span>
          </div>
        </div>
      </div>

      <div class="filters">
        <div class="filter-group">
          <label>Группа:</label>
          <select v-model="selectedGroupId" @change="onGroupChange">
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Предмет:</label>
          <select v-model="selectedSubjectId" @change="onSubjectChange">
            <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="filter-group info-group" v-if="selectedSubjectName && selectedGroupName">
          <span class="info-badge">{{ selectedSubjectName }}</span>
          <span class="info-badge">{{ selectedGroupName }}</span>
        </div>
      </div>

      <div v-if="selectedScheduleId" class="marks-container">
        <MarksPage
          :subjectName="selectedSubjectName"
          :groupId="selectedGroupId"
          :groupName="selectedGroupName"
          :scheduleId="selectedScheduleId"
          :showHeader="false"
          @close="onCloseMarks"
        />
      </div>
      <div v-else class="empty-state">
        Выберите группу и предмет для просмотра журнала.
      </div>
    </div>
  </div>
</template>

<script>
import { getSchedule } from '@/services/schedule'
import MarksPage from '@/views/MarksPage.vue'
import { getStoredUser, logout as authLogout } from '@/services/auth'

export default {
  name: 'AllGradesPage',
  components: { MarksPage },
  data() {
    return {
      user: getStoredUser(),
      allSchedules: [],
      groups: [],
      selectedGroupId: null,
      selectedSubjectId: null,
      selectedScheduleId: null,
      selectedGroupName: '',
      selectedSubjectName: '',
      isMobile: false
    }
  },
  computed: {
    initials() {
      const name = this.user?.full_name || ''
      return name
        .split(' ')
        .filter(Boolean)
        .map(w => w[0])
        .slice(0, 2)
        .join('')
        .toUpperCase() || 'ГС'
    },
    subjects() {
      if (!this.selectedGroupId) return []
      const group = this.groups.find(g => g.id === this.selectedGroupId)
      return group ? group.subjects : []
    },
  },
  async mounted() {
  this.checkIfMobile()
  window.addEventListener('resize', this.checkIfMobile)
  await this.loadData()
  if (this.groups.length) {
    this.selectedGroupId = this.groups[0].id
    await this.onGroupChange()
  }
},
  beforeDestroy() {
    window.removeEventListener('resize', this.checkIfMobile)
  },
  methods: {
    checkIfMobile() {
      this.isMobile = window.innerWidth < 768
    },
    async loadData() {
      try {
        const schedules = await getSchedule()
        this.allSchedules = schedules

        const groupMap = new Map()
        schedules.forEach(item => {
          const group = item.group
          const subject = item.subject
          if (!group || !subject) return

          if (!groupMap.has(group.id)) {
            groupMap.set(group.id, {
              id: group.id,
              name: group.name,
              subjects: [],
            })
          }
          const groupData = groupMap.get(group.id)
          if (!groupData.subjects.some(s => s.id === subject.id)) {
            groupData.subjects.push({ id: subject.id, name: subject.name })
          }
        })
        this.groups = Array.from(groupMap.values())
      } catch (e) {
        console.error('Ошибка загрузки расписания:', e)
        this.groups = [
          {
            id: 1,
            name: 'Б9124-09.03.03ру',
            subjects: [{ id: 101, name: 'Базы данных' }],
          },
        ]
      }
    },

    async onGroupChange() {
      this.selectedSubjectId = null
      this.selectedScheduleId = null
      if (this.selectedGroupId && this.subjects.length) {
        this.selectedSubjectId = this.subjects[0].id
        await this.onSubjectChange()
      }
      const group = this.groups.find(g => g.id === this.selectedGroupId)
      this.selectedGroupName = group ? group.name : ''
    },

    async onSubjectChange() {
      if (!this.selectedGroupId || !this.selectedSubjectId) {
        this.selectedScheduleId = null
        return
      }
      const schedule = this.allSchedules.find(
        item =>
          item.group?.id === this.selectedGroupId &&
          item.subject?.id === this.selectedSubjectId
      )
      if (schedule) {
        this.selectedScheduleId = schedule.id
        this.selectedSubjectName = schedule.subject.name
      } else {
        this.selectedScheduleId = null
      }
    },

    onCloseMarks() {
    },

    logout() {
      authLogout()
      this.$router.push('/')
    },
  },
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

.grades-card {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.schedule-btn,
.logout-btn {
  background: linear-gradient(to bottom, #75b5f0, #2d5ca4);
  border: 1px solid rgba(119, 155, 222, 0.7);
  border-radius: 30px;
  padding: 8px 18px;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.schedule-btn:hover,
.logout-btn:hover {
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

.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(4px);
  border-bottom: 1px solid rgba(255,255,255,0.3);
  flex-shrink: 0;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #1f3b4c;
  font-size: 15px;
}

.filter-group select {
  padding: 8px 16px;
  border-radius: 30px;
  border: 1px solid rgba(86, 112, 193, 0.5);
  background: rgba(255,255,255,0.7);
  font-weight: 500;
  color: #1f3b4c;
  outline: none;
  cursor: pointer;
  font-size: 14px;
}

.filter-group select:hover {
  background: rgba(255,255,255,0.9);
}

.info-group {
  margin-left: auto;
  display: flex;
  gap: 0.8rem;
}

.info-badge {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(4px);
  padding: 6px 16px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  color: #1f4a6e;
  border: 1px solid rgba(100, 160, 200, 0.5);
}

.marks-container {
  flex: 1;
  overflow: hidden;
  padding: 0.5rem 1rem 1rem;
}

.filter-group select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%234a6a8a' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 12px;
  padding: 10px 44px 10px 20px;
  font-family: 'Inter', system-ui, sans-serif;
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(86, 112, 193, 0.4);
  border-radius: 30px;
  font-size: 14px;
  font-weight: 500;
  color: #1f3b4c;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  min-width: 160px;
  max-width: 260px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.filter-group select:hover {
  background-color: rgba(255, 255, 255, 0.95);
  border-color: #6b8fc4;
  box-shadow: 0 4px 12px rgba(0, 20, 40, 0.12);
  transform: translateY(-1px);
}

.filter-group select:focus {
  outline: none;
  border-color: #4f7db3;
  box-shadow: 0 0 0 3px rgba(79, 125, 179, 0.25);
}

.filter-group select option {
  background: white;
  color: #1f3b4c;
  padding: 8px 16px;
  font-weight: 400;
  font-size: 14px;
}

.filter-group select option:hover,
.filter-group select option:checked {
  background: #e8f0fe;
  color: #1a3b54;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #1f3b4c;
  opacity: 0.7;
}

.screen.is-mobile {
  background: url('@/assets/phone2.PNG') left center / cover no-repeat;
  background-color: #6b8cae;
  position: relative;
  padding: 0.5rem;
  height: 100vh;
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
  min-height: auto;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  border-radius: 32px;
  margin: 0;
  box-shadow: none;
  border: none;
}

.screen.is-mobile .card-header {
  border-bottom: none;
  padding: 0.8rem 1rem;
  flex-wrap: wrap;
  gap: 6px;
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

.screen.is-mobile .filters {
  border-bottom: none;
  background: transparent;
  flex-direction: column;
  align-items: stretch;
  padding: 0.8rem 1rem;
  gap: 0.6rem;
}

.screen.is-mobile .filter-group {
  width: 100%;
}

.screen.is-mobile .filter-group select {
  width: 100%;
  min-width: auto;
  max-width: 100%;
}

.screen.is-mobile .info-group {
  margin-left: 0;
  justify-content: center;
}

.screen.is-mobile .marks-container {
  padding: 0 !important;
  margin: 0 !important;
  background: none !important;
  overflow: visible;
}

@media (max-width: 768px) {
  .screen { padding: 0.5rem; }
  .filters { flex-direction: column; align-items: stretch; }
  .info-group { margin-left: 0; justify-content: center; }
}
</style>