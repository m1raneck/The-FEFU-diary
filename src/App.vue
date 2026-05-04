<template>
  <div class="main-container">
    <div class="glass-panel">
      <!-- Шапка -->
      <div class="header">
        <div class="group-info">
          <span class="label-text">Группа:</span>
          <span class="group-name">Б9124-09.03.03ру</span>
        </div>
        <div class="subject-name">Базы данных</div>
      </div>

      <!-- Таблица -->
      <div class="table-wrapper">
        <div class="table-container">
          <table class="journal-table">
            <thead>
              <tr>
                <th class="col-num">№</th>
                <th class="text-left col-fio">ФИО</th>
                <th class="col-stat">Ср.</th>
                <th class="col-stat">П.</th>
                <th v-for="(date, dIndex) in dates" :key="date" colspan="2" 
                    class="date-header" :class="{ 'active-col': headerPopup.dIndex === dIndex }">
                  <div class="date-text">{{ date }}</div>
                  <div class="sub-headers">
                    <span 
                      class="clickable-header type-label" 
                      @click.stop="openHeaderPopup($event, dIndex)"
                    >
                      {{ columnSettings[dIndex].type || 'Оц.' }}
                    </span>
                    <span>П</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(student, index) in students" :key="index" class="student-row">
                <td class="col-num">{{ index + 1 }}</td>
                <td class="text-left sticky-col">{{ student.name }}</td>
                <td class="col-stat">{{ student.avg }}</td>
                <td class="col-stat" :class="{ 'text-red': student.attendance < 60 }">{{ student.attendance }}</td>
                
                <template v-for="(record, dIndex) in student.records" :key="dIndex">
                  <!-- Ячейка оценки/посещаемости -->
                  <td class="grade-cell" @click.stop="handleGradeClick(index, dIndex)">
                    <span class="grade-val">
                      {{ record.grade }}
                    </span>
                  </td>
                  <!-- Посещаемость (прямоугольник) -->
                  <td class="presence-cell" @click="togglePresence(index, dIndex)">
                    <div class="presence-rect" :class="record.present ? 'present' : 'absent'"></div>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Попап настроек -->
      <Teleport to="body">
        <div 
          class="popup-menu" 
          v-if="headerPopup.visible" 
          :style="{ top: headerPopup.y + 'px', left: headerPopup.x + 'px' }"
          @click.stop
        >
          <div class="popup-arrow"></div>
          <div class="popup-grid">
            <button class="btn btn-purple" @click="setColumnType('КР', 5)">КР</button>
            <button class="btn btn-teal" @click="setColumnType('ДОП', null)">ДОП</button>
            <button class="btn btn-lilac" @click="setColumnType('ДЗ', 100)">ДЗ</button>
            <button class="btn btn-blue" @click="setColumnType('-', 0)">-</button>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const dates = ['21/04', '28/04', '5/05', '12/05', '19/05'];

// Храним настройки для каждой колонки
const columnSettings = ref(dates.map(() => ({ type: null, max: 5 })));

const students = ref([
  { name: 'Беляев А.А.', avg: 65, attendance: 100, records: dates.map(() => ({ grade: '', present: true })) },
  { name: 'Васильев А.Г.', avg: 30, attendance: 98, records: dates.map(() => ({ grade: '', present: true })) },
  { name: 'Геннадьева В. Д.', avg: 63, attendance: 50, records: dates.map(() => ({ grade: '', present: false })) },
  { name: 'Кирова Л. Д.', avg: 58, attendance: 77, records: dates.map(() => ({ grade: '', present: true })) },
  { name: 'Макарова Н. В.', avg: 52, attendance: 98, records: dates.map(() => ({ grade: '', present: true })) },
  { name: 'Лаврова Л. Д.', avg: 70, attendance: 77, records: dates.map(() => ({ grade: '', present: true })) },
  { name: 'Никитина В. Н.', avg: 21, attendance: 100, records: dates.map(() => ({ grade: '', present: true })) },
  { name: 'Орлова А. А.', avg: 0, attendance: 0, records: dates.map(() => ({ grade: '', present: false })) },
  { name: 'Павлова В. Н.', avg: 36, attendance: 50, records: dates.map(() => ({ grade: '', present: true })) },
]);

const headerPopup = ref({ visible: false, x: 0, y: 0, dIndex: null });

const openHeaderPopup = (event, dIndex) => {
  const rect = event.currentTarget.getBoundingClientRect();
  headerPopup.value = {
    visible: true,
    x: rect.left - 60,
    y: rect.bottom + window.scrollY + 10,
    dIndex
  };
};

const setColumnType = (type, max) => {
  const dIndex = headerPopup.value.dIndex;
  
  if (type === 'ДОП') {
    const customMax = prompt('Введите максимально возможный балл (систему) для ДОП:');
    if (!customMax || isNaN(customMax) || customMax <= 0) {
      alert('Ошибка: введите число больше 0');
      return;
    }
    max = parseInt(customMax);
  }
  
  // При смене типа на "-" очищаем баллы в этой колонке для корректности
  if (type === '-') {
    students.value.forEach(s => s.records[dIndex].grade = '+');
  } else {
    students.value.forEach(s => s.records[dIndex].grade = '0');
  }

  columnSettings.value[dIndex] = { type, max };
  headerPopup.value.visible = false;
};

const handleGradeClick = (sIdx, dIndex) => {
  const config = columnSettings.value[dIndex];
  const record = students.value[sIdx].records[dIndex];

  if (!config.type) {
    alert('Сначала выберите тип (КР, ДЗ, ДОП или -) нажав на "Оц."');
    return;
  }

  // Если выбрано "-", переключаем + / -
  if (config.type === '-') {
    record.grade = record.grade === '+' ? '-' : '+';
    return;
  }

  // Логика баллов для КР, ДЗ, ДОП
  const res = prompt(`Введите балл для ${config.type} (0-${config.max}):`);
  if (res !== null && res !== '') {
    const val = parseInt(res);
    if (!isNaN(val) && val >= 0 && val <= config.max) {
      record.grade = val.toString();
    } else {
      alert(`Ошибка: введите число от 0 до ${config.max}`);
    }
  }
};

const togglePresence = (sIdx, rIdx) => { 
  students.value[sIdx].records[rIdx].present = !students.value[sIdx].records[rIdx].present; 
};

onMounted(() => {
  document.addEventListener('click', () => headerPopup.value.visible = false);
});
</script>

<style scoped>
/* Стили без изменений */
.main-container {
  min-height: 100dvh;
  width: 100%;
  background-color: #7d8ea3;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  width: 100%;
  max-width: 900px;
  padding: 30px 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 0 10px;
}
.group-info { color: #333; font-size: 14px; }
.group-name { font-weight: bold; }
.subject-name { color: #5a6a7d; font-weight: bold; font-size: 16px; }

.table-wrapper {
  background: #d9e1e8;
  border-radius: 12px;
  padding: 10px;
}

.table-container {
  overflow-x: auto;
}

.journal-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  color: #333;
}

.journal-table th {
  padding: 8px 4px;
  font-weight: 600;
  vertical-align: bottom;
}

.date-header {
  min-width: 60px;
  border-radius: 8px 8px 0 0;
}

.date-header.active-col {
  background: rgba(255, 255, 255, 0.3);
}

.sub-headers {
  display: flex;
  justify-content: space-around;
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.clickable-header { 
  cursor: pointer; 
  padding: 2px 4px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
}

.student-row:nth-child(even) td {
  background: rgba(255, 255, 255, 0.15);
}

.journal-table td {
  padding: 6px 4px;
  text-align: center;
}

.sticky-col {
  text-align: left !important;
  font-weight: 500;
  min-width: 140px;
}

.text-red { color: #d9534f; font-weight: bold; }

.grade-cell {
  width: 25px;
  cursor: pointer;
}

.presence-cell {
  width: 35px;
  cursor: pointer;
}

.presence-rect {
  width: 35px;
  height: 18px;
  border-radius: 4px;
  margin: 0 auto;
}

.present { background-color: #e2f7e2; }
.absent { background-color: #ffdce0; }

.popup-menu {
  position: absolute;
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  width: 180px;
  z-index: 1000;
}

.popup-arrow {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid white;
}

.popup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.btn {
  border: none;
  padding: 12px 5px;
  border-radius: 6px;
  color: black;
  font-weight: bold;
  cursor: pointer;
  font-size: 12px;
}

.btn-purple { background: #a29bfe; }
.btn-teal { background: #81ecec; }
.btn-lilac { background: #d6a2e8; }
.btn-blue { background: #adcfff; }

@media (max-width: 768px) {
  .glass-panel { padding: 10px; border-radius: 0; }
}
</style>