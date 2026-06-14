<template>
  <div class="screen-marks">
    <div class="marks-card">
      <div class="card-header">
        <div class="header-left">
          <div class="logo-mini">UniDiary</div>
        </div>
        <div class="header-right">
          <div class="subject-badge">{{ subjectName }}</div>
          <div class="group-badge">{{ groupName || 'Группа' }}</div>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>
      </div>

      <div class="import-panel">
        <div class="import-controls">
          <button class="sample-btn" @click="downloadSampleCSV">Пример CSV</button>
          <label class="import-file-btn">
            Загрузить CSV
            <input type="file" accept=".csv" @change="handleFileUpload" style="display: none" ref="fileInput" />
          </label>
          <button v-if="!importModeActive" class="switch-mode-btn" @click="activateImportMode">➕ Импорт нескольких
            тестов</button>
          <button v-if="importModeActive" class="scale-settings-btn" @click.stop="openScalePopup">⚙ Настроить
            шкалу</button>
        </div>

        <div v-if="importModeActive" class="multi-import-container">
          <div class="mapping-table">
            <div class="mapping-row header">
              <div>CSV колонка</div>
              <div>Целевая дата</div>
              <div>Перевести в оценку (2‑5)</div>
            </div>
            <div v-for="(col, idx) in csvScoreColumns" :key="idx" class="mapping-row">
              <div><strong>{{ col.header }}</strong> ({{ col.sampleValues.join(', ') }}%)</div>
              <div><select v-model="col.targetDateIdx">
                  <option v-for="(date, dIdx) in dates" :value="dIdx">{{ date }}</option>
                </select></div>
              <div><input type="checkbox" v-model="col.useGradeScale"><span class="hint">(по вашей шкале)</span></div>
            </div>
          </div>
          <div class="import-actions">
            <button @click="applyMultiImport" :disabled="!hasEnabledMappings" class="apply-import-btn">📥 Выставить
              оценки</button>
            <button @click="cancelMultiImport" class="cancel-import-btn">Отмена</button>
          </div>
          <div v-if="multiPreview.length" class="import-preview">
            <div class="preview-header">Предпросмотр (первые 5 студентов)</div>
            <div class="preview-list">
              <div v-for="preview in multiPreview.slice(0, 5)" :key="preview.studentName" class="preview-item">
                <span class="preview-name">{{ preview.studentName }}</span>
                <span v-for="map in preview.mappings" :key="map.csvHeader" class="preview-mapping">{{ map.csvHeader }} →
                  {{ map.finalGrade }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="importMessage" class="import-message" :class="importMessageType">{{ importMessage }}</div>
      </div>

      <div class="table-wrapper">
        <table class="marks-table">
          <thead>
            <tr>
              <th class="col-num">№</th>
              <th class="col-name">ФИО</th>
              <th class="col-stat">Ср.</th>
              <th class="col-stat">П.</th>
              <th v-for="(date, dIdx) in dates" :key="date" class="date-col">
                <div class="date-text">{{ date }}</div>
                <div class="type-selector" @click.stop="openTypePopup($event, dIdx)">{{
                  getTypeLabel(columnSettings[dIdx].type) }}</div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, sIdx) in students" :key="sIdx" class="student-row">
              <td class="col-num">{{ sIdx + 1 }}</td>
              <td class="col-name">{{ student.name }}</td>
              <td class="col-stat"><span class="avg-badge" :class="getAvgClass(student.avg)">{{ student.avg }}</span>
              </td>
              <td class="col-stat" :class="{ 'warn-att': student.attendance < 60 }">{{ student.attendance }}%</td>
              <td v-for="(rec, dIdx) in student.records" :key="dIdx" class="combo-cell">
                <div class="combo-inner">
                  <div class="combo-grade" @click.stop="editGrade(sIdx, dIdx)"><span class="grade-val"
                      :class="getGradeClass(rec.grade, dIdx)">{{ rec.grade === '' ? '—' : rec.grade }}</span></div>
                  <div class="combo-presence" :class="rec.present ? 'pres-yes' : 'pres-no'"
                    @click.stop="togglePresence(sIdx, dIdx)"
                    :title="rec.present ? 'Отметить отсутствие' : 'Отметить присутствие'"><span class="presence-icon">{{
                      rec.present ? '✓' : '✗' }}</span></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="popup-fade">
        <div v-if="popup.visible" class="type-popup" :style="{ top: popup.y + 'px', left: popup.x + 'px' }">
          <div class="popup-label">Тип работы</div>
          <div class="popup-grid">
            <button class="popup-btn kr" @click="setType('КР', 5)">KP</button>
            <button class="popup-btn dop" @click="setType('ДОП', null)">ДОП</button>
            <button class="popup-btn dz" @click="setType('ДЗ', 100)">ДЗ</button>
            <button class="popup-btn dash" @click="setType('±', 0)">+ / -</button>
          </div>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="popup-fade">
        <div v-if="scalePopup.visible" class="scale-popup" @click.stop>
          <div class="popup-label scale-title">Настройка шкалы</div>
          <div class="scale-inputs">
            <div class="scale-row"><span class="grade-label">Оценка 2:</span>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.from2 = Math.max(0, gradeScale.from2 - 1)">−</button><input type="number"
                  v-model.number="gradeScale.from2" step="1" class="scale-input"><button class="num-btn inc"
                  @click="gradeScale.from2 = Math.min(gradeScale.to2 - 1, gradeScale.from2 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.to2 = Math.max(gradeScale.from2 + 1, gradeScale.to2 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.to2" step="1" class="scale-input"><button class="num-btn inc"
                  @click="gradeScale.to2 = Math.min(gradeScale.from3 - 1, gradeScale.to2 + 1)">+</button></div>
            </div>
            <div class="scale-row"><span class="grade-label">Оценка 3:</span>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.from3 = Math.max(gradeScale.to2 + 1, gradeScale.from3 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.from3" step="1" class="scale-input"><button
                  class="num-btn inc"
                  @click="gradeScale.from3 = Math.min(gradeScale.to3 - 1, gradeScale.from3 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.to3 = Math.max(gradeScale.from3 + 1, gradeScale.to3 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.to3" step="1" class="scale-input"><button class="num-btn inc"
                  @click="gradeScale.to3 = Math.min(gradeScale.from4 - 1, gradeScale.to3 + 1)">+</button></div>
            </div>
            <div class="scale-row"><span class="grade-label">Оценка 4:</span>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.from4 = Math.max(gradeScale.to3 + 1, gradeScale.from4 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.from4" step="1" class="scale-input"><button
                  class="num-btn inc"
                  @click="gradeScale.from4 = Math.min(gradeScale.to4 - 1, gradeScale.from4 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.to4 = Math.max(gradeScale.from4 + 1, gradeScale.to4 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.to4" step="1" class="scale-input"><button class="num-btn inc"
                  @click="gradeScale.to4 = Math.min(gradeScale.from5 - 1, gradeScale.to4 + 1)">+</button></div>
            </div>
            <div class="scale-row"><span class="grade-label">Оценка 5:</span>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.from5 = Math.max(gradeScale.to4 + 1, gradeScale.from5 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.from5" step="1" class="scale-input"><button
                  class="num-btn inc"
                  @click="gradeScale.from5 = Math.min(gradeScale.to5 - 1, gradeScale.from5 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec"
                  @click="gradeScale.to5 = Math.max(gradeScale.from5 + 1, gradeScale.to5 - 1)">−</button><input
                  type="number" v-model.number="gradeScale.to5" step="1" class="scale-input"><button class="num-btn inc"
                  @click="gradeScale.to5 = Math.min(100, gradeScale.to5 + 1)">+</button></div>
            </div>
          </div>
          <div class="scale-actions"><button class="large-btn" @click="closeScalePopup">Применить</button></div>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="fade-scale">
        <div v-if="gradeInput.visible" class="grade-overlay" @click.self="gradeInput.visible = false">
          <div class="grade-popup">
            <div class="grade-popup-name">{{ gradeInput.studentName }}</div>
            <div class="grade-popup-sub">{{ gradeInput.typeName }} · максимум {{ gradeInput.max }}</div>
            <input ref="gradeInputRef" v-model="gradeInput.value" class="grade-field" type="number" :min="0"
              :max="gradeInput.max" :placeholder="`0–${gradeInput.max}`" @keyup.enter="confirmGrade"
              @keyup.esc="gradeInput.visible = false">
            <div class="grade-actions"><button class="btn-cancel"
                @click="gradeInput.visible = false">Отмена</button><button class="btn-ok"
                @click="confirmGrade">Сохранить</button></div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { getStudents, getGrades, getAttendance, saveGrade, saveAttendance, bulkSaveGrades } from '@/services/marks'

const props = defineProps({
  subjectName: { type: String, default: 'Базы данных' },
  groupId: { type: Number, default: 1 },
  groupName: { type: String, default: 'Б9124-09.03.03ру' },
  scheduleId: { type: Number, default: 1 }
})
const emit = defineEmits(['close'])

const dates = ['21/04', '28/04', '5/05', '12/05', '19/05']
const columnSettings = ref(dates.map(() => ({ type: null, max: 5 })))
const students = ref([])
const studentsMap = ref(new Map())

const gradeScale = ref({ from2: 0, to2: 40, from3: 41, to3: 60, from4: 61, to4: 80, from5: 81, to5: 100 })

function convertPercentToGrade(percent) {
  if (percent >= gradeScale.value.from2 && percent <= gradeScale.value.to2) return 2
  if (percent >= gradeScale.value.from3 && percent <= gradeScale.value.to3) return 3
  if (percent >= gradeScale.value.from4 && percent <= gradeScale.value.to4) return 4
  if (percent >= gradeScale.value.from5 && percent <= gradeScale.value.to5) return 5
  return null
}

function recalcStudentStats() {
  students.value.forEach(student => {
    let totalPercent = 0, graded = 0, presentCount = 0
    student.records.forEach((rec, idx) => {
      const cfg = columnSettings.value[idx]
      if (cfg && cfg.max && rec.grade !== '' && rec.grade !== '+' && rec.grade !== '-') {
        const g = parseFloat(rec.grade)
        if (!isNaN(g)) {
          totalPercent += (g / cfg.max) * 100
          graded++
        }
      }
      if (rec.present) presentCount++
    })
    student.avg = graded ? Math.round(totalPercent / graded) : 0
    student.attendance = Math.round((presentCount / dates.length) * 100)
  })
}

function dateToIso(dateStr) {
  const [day, month] = dateStr.split('/')
  return `2026-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}
function isoToDateIdx(isoDate) {
  const parts = isoDate.split('-')
  const formatted = `${parseInt(parts[2], 10)}/${parts[1]}`
  return dates.indexOf(formatted)
}

async function loadStudents() {
  try {
    const data = await getStudents()
    const filtered = data.filter(s => s.group_id === props.groupId)
    if (filtered.length === 0) {
      setImportMsg('Нет студентов в этой группе', 'error')
      return
    }
    students.value = filtered.map(s => ({
      id: s.id,
      name: s.full_name,
      avg: 0,
      attendance: 0,
      records: dates.map(() => ({ grade: '', present: true }))
    }))
    filtered.forEach(s => studentsMap.value.set(s.full_name, s.id))
    await loadMarksFromDb()
    recalcStudentStats()
  } catch (err) {
    console.error(err)
    setImportMsg(`Ошибка загрузки студентов: ${err.message}`, 'error')
  }
}

async function loadMarksFromDb() {
  if (!props.scheduleId) return
  try {
    const [grades, attendance] = await Promise.all([getGrades(props.scheduleId), getAttendance(props.scheduleId)])
    for (const g of grades) {
      const sIdx = students.value.findIndex(s => s.id === g.student_id)
      const dIdx = isoToDateIdx(g.grade_date)
      if (sIdx !== -1 && dIdx !== -1 && g.grade != null)
        students.value[sIdx].records[dIdx].grade = g.grade
    }
    for (const a of attendance) {
      const sIdx = students.value.findIndex(s => s.id === a.student_id)
      const dIdx = isoToDateIdx(a.date)
      if (sIdx !== -1 && dIdx !== -1)
        students.value[sIdx].records[dIdx].present = a.status === 'present' || a.status === 'late'
    }
  } catch (err) {
    console.error(err)
    setImportMsg(`Ошибка загрузки оценок: ${err.message}`, 'error')
  }
}

const importModeActive = ref(false)
const csvScoreColumns = ref([])
const rawCsvRows = ref([])
const multiPreview = ref([])
const importMessage = ref('')
const importMessageType = ref('info')
const fileInput = ref(null)
const hasEnabledMappings = computed(() => csvScoreColumns.value.some(c => c.targetDateIdx !== undefined))

function activateImportMode() {
  importModeActive.value = true
  if (!csvScoreColumns.value.length) setImportMsg('Загрузите CSV-файл с процентами', 'info')
}
function cancelMultiImport() {
  importModeActive.value = false
  csvScoreColumns.value = []
  rawCsvRows.value = []
  multiPreview.value = []
  setImportMsg('', 'info')
  if (fileInput.value) fileInput.value.value = ''
}
function parseCSV(text) {
  const rows = [], regex = /(?:,|^)(?:"([^"]*(?:""[^"]*)*)"|([^",]*))/g
  const lines = text.split(/\r?\n/)
  for (let line of lines) {
    if (!line.trim()) continue
    const row = []
    let match
    while ((match = regex.exec(line)) !== null) row.push(match[1] !== undefined ? match[1].replace(/""/g, '"') : (match[2] || ''))
    if (row.length) rows.push(row)
    regex.lastIndex = 0
  }
  return rows
}
function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const rows = parseCSV(e.target.result)
      if (rows.length < 2) throw new Error('Файл должен содержать заголовки и данные')
      analyzeCSVForMultiImport(rows)
    } catch (err) { setImportMsg(err.message, 'error') }
  }
  reader.readAsText(file, 'UTF-8')
  event.target.value = ''
}
function analyzeCSVForMultiImport(rows) {
  const headers = rows[0].map(h => h.trim())
  const dataRows = rows.slice(1)
  if (!dataRows.length) throw new Error('Нет строк с данными')
  let nameColIdx = headers.findIndex(h => /студент|фио|student|name/i.test(h))
  if (nameColIdx === -1) nameColIdx = 0
  const scoreCols = []
  for (let i = 0; i < headers.length; i++) {
    if (i === nameColIdx) continue
    const values = dataRows.map(row => parseFloat(row[i])).filter(v => !isNaN(v))
    if (!values.length) continue
    const sampleValues = [...new Set(values.slice(0, 3))]
    const studentScores = dataRows.map(row => { const val = parseFloat(row[i]); return isNaN(val) ? 0 : val })
    const rawNames = dataRows.map(row => row[nameColIdx]?.trim() || '')
    scoreCols.push({ header: headers[i], sampleValues, targetDateIdx: 0, useGradeScale: false, studentScores, rawNames })
  }
  if (!scoreCols.length) throw new Error('Не найдено числовых колонок с процентами')
  csvScoreColumns.value = scoreCols
  rawCsvRows.value = dataRows
  importModeActive.value = true
  computeMultiPreview()
  setImportMsg(`Обнаружено ${scoreCols.length} колонок. Настройте импорт.`, 'success')
}
function computeMultiPreview() {
  const preview = []
  for (const student of students.value) {
    const studentName = student.name
    const mappings = []
    for (const col of csvScoreColumns.value) {
      const rowIdx = col.rawNames.findIndex(n => n.toLowerCase() === studentName.toLowerCase())
      if (rowIdx === -1) continue
      let percent = col.studentScores[rowIdx]
      let finalGrade
      if (col.useGradeScale) {
        const grade = convertPercentToGrade(percent)
        finalGrade = grade !== null ? grade : percent
      } else finalGrade = percent
      mappings.push({ csvHeader: col.header, finalGrade, targetDateIdx: col.targetDateIdx })
    }
    if (mappings.length) preview.push({ studentName, mappings })
  }
  multiPreview.value = preview
}
async function applyMultiImport() {
  if (!hasEnabledMappings.value) { setImportMsg('Настройте привязку колонок к датам', 'error'); return }
  if (!props.scheduleId) { setImportMsg('Не выбрана пара (schedule_id)', 'error'); return }
  let totalSaved = 0
  for (const col of csvScoreColumns.value) {
    const targetColIdx = col.targetDateIdx
    const gradeDate = dateToIso(dates[targetColIdx])
    const gradesToSend = []
    for (let rowIdx = 0; rowIdx < rawCsvRows.value.length; rowIdx++) {
      const studentNameRaw = col.rawNames[rowIdx]
      const student = students.value.find(s => s.name.toLowerCase() === studentNameRaw?.toLowerCase())
      if (!student) continue
      const studentId = studentsMap.value.get(student.name)
      if (!studentId) continue
      let percent = col.studentScores[rowIdx]
      let finalGrade = col.useGradeScale ? convertPercentToGrade(percent) : Math.min(percent, 100)
      if (col.useGradeScale && finalGrade === null) finalGrade = percent
      gradesToSend.push({ student_id: studentId, grade: Math.round(finalGrade), comment: '' })
    }
    if (!gradesToSend.length) continue
    try {
      const result = await bulkSaveGrades({ scheduleId: props.scheduleId, gradeDate, grades: gradesToSend })
      if (result.status === 'success') { totalSaved += gradesToSend.length; setImportMsg(`✅ ${result.message}`, 'success') }
      else setImportMsg(`❌ Ошибка: ${result.message || 'неизвестная'}`, 'error')
    } catch (err) { setImportMsg(`❌ Ошибка сети: ${err.message}`, 'error') }
  }
  if (totalSaved > 0) { await loadMarksFromDb(); recalcStudentStats() }
  cancelMultiImport()
}
function setImportMsg(msg, type) { importMessage.value = msg; importMessageType.value = type; if (msg) setTimeout(() => { if (importMessage.value === msg) importMessage.value = '' }, 4000) }
watch(csvScoreColumns, () => { computeMultiPreview() }, { deep: true })

const scalePopup = ref({ visible: false })
function openScalePopup(event) { event.stopPropagation(); scalePopup.value.visible = true }
function closeScalePopup() { scalePopup.value.visible = false; computeMultiPreview() }

const popup = ref({ visible: false, x: 0, y: 0, dIndex: null })
const gradeInput = ref({ visible: false, sIdx: null, dIdx: null, value: '', max: 5, typeName: '', studentName: '' })
const gradeInputRef = ref(null)

function getTypeLabel(type) {
  if (type === 'КР') return 'KP'
  if (type === 'ДОП') return 'ДОП'
  if (type === 'ДЗ') return 'Д3'
  if (type === '±') return '+/-'
  return 'Оц.'
}
function getAvgClass(avg) { if (avg >= 70) return 'avg-good'; if (avg >= 40) return 'avg-mid'; return 'avg-bad' }
function getGradeClass(grade, dIdx) {
  if (grade === '' || grade === '+' || grade === '-') return 'grade-empty'
  const cfg = columnSettings.value[dIdx]
  if (!cfg.max) return ''
  const ratio = grade / cfg.max
  if (ratio >= 0.8) return 'g-good'
  if (ratio <= 0.5) return 'g-low'
  return ''
}
function openTypePopup(e, dIdx) {
  const rect = e.target.getBoundingClientRect()
  popup.value = { visible: true, x: Math.min(rect.left + window.scrollX - 80, window.innerWidth - 280), y: rect.bottom + window.scrollY + 8, dIndex: dIdx }
}
function closePopup() { popup.value.visible = false }
function setType(type, max) {
  const dIdx = popup.value.dIndex
  if (type === 'ДОП') {
    const c = prompt('Максимальный балл для ДОП:')
    if (!c || isNaN(+c) || +c <= 0) { alert('Нужно положительное число'); return }
    max = +c
  }
  students.value.forEach(s => { s.records[dIdx].grade = type === '±' ? '+' : '0' })
  columnSettings.value[dIdx] = { type, max }
  recalcStudentStats()
  closePopup()
}
async function editGrade(sIdx, dIdx) {
  const cfg = columnSettings.value[dIdx]
  if (!cfg.type) { alert('Сначала выберите тип колонки (кнопка "Оц." вверху)'); return }
  if (cfg.type === '±') {
    const rec = students.value[sIdx].records[dIdx]
    rec.grade = rec.grade === '+' ? '-' : '+'
    recalcStudentStats()
    return
  }
  gradeInput.value = { visible: true, sIdx, dIdx, value: students.value[sIdx].records[dIdx].grade === '' ? '' : students.value[sIdx].records[dIdx].grade, max: cfg.max, typeName: cfg.type, studentName: students.value[sIdx].name }
  await nextTick()
  gradeInputRef.value?.focus()
  gradeInputRef.value?.select()
}
function confirmGrade() {
  const { sIdx, dIdx, value, max } = gradeInput.value
  const num = +value
  if (value === '' || isNaN(num) || num < 0 || num > max) { alert(`Введите число от 0 до ${max}`); return }
  students.value[sIdx].records[dIdx].grade = num
  gradeInput.value.visible = false
  recalcStudentStats()
  persistGrade(sIdx, dIdx, num)
}
async function persistGrade(sIdx, dIdx, gradeValue) {
  if (!props.scheduleId) return
  const student = students.value[sIdx]
  try { await saveGrade({ studentId: student.id, scheduleId: props.scheduleId, grade: Math.round(gradeValue), gradeDate: dateToIso(dates[dIdx]) }) }
  catch (err) { console.error(err); setImportMsg(`❌ ${err.message}`, 'error') }
}
function togglePresence(sIdx, dIdx) {
  students.value[sIdx].records[dIdx].present = !students.value[sIdx].records[dIdx].present
  recalcStudentStats()
  persistAttendance(sIdx, dIdx)
}
async function persistAttendance(sIdx, dIdx) {
  if (!props.scheduleId) return
  const student = students.value[sIdx]
  const present = student.records[dIdx].present
  try { await saveAttendance({ studentId: student.id, scheduleId: props.scheduleId, status: present ? 'present' : 'absent', date: dateToIso(dates[dIdx]) }) }
  catch (err) { console.error(err); setImportMsg(`❌ ${err.message}`, 'error') }
}
function handleClickOutside(e) {
  if (!e.target.closest('.type-popup')) closePopup()
  if (scalePopup.value.visible && !e.target.closest('.scale-popup')) scalePopup.value.visible = false
}
function downloadSampleCSV() {
  const sampleRows = [['Студент', 'Тест 1 (%)', 'Тест 2 (%)'], ['Ковалёв Леонид', '85', '64'], ['Шварц Анжелика', '42', '33'], ['Углицкий Евгений', '78', '91'], ['Смирнов Григорий', '94', '73']]
  const csv = sampleRows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'example_marks.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}

onMounted(() => { loadStudents(); document.addEventListener('click', handleClickOutside) })
onBeforeUnmount(() => { document.removeEventListener('click', handleClickOutside) })
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.screen-marks {
  display: flex;
  padding: 0;
  background: #eef4fa;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', system-ui, sans-serif;
}

.marks-card {
  width: 100%;
  max-width: 1400px;
  max-height: 90vh;
  overflow-y: auto;
  background: linear-gradient(145deg, rgba(208, 218, 229, 0.65) 22%, rgba(165, 186, 202, 0.45) 79%, rgba(130, 164, 192, 0.65) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 28px;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.2);
}

.card-header {
  position: sticky;
  top: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 2.5rem;
  background: rgba(227, 240, 255, 0.25);
  border-bottom: 1px solid rgba(86, 112, 193, 0.35);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.header-left .logo-mini {
  font-size: 28px;
  font-weight: 800;
  color: #1f3b4c;
  letter-spacing: -0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.subject-badge,
.group-badge {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  padding: 8px 18px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 500;
  color: #1f4a6e;
  border: 1px solid rgba(100, 160, 200, 0.6);
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(to bottom, #ebf5ff, #abc7f2);
  border: 0.5px solid rgba(26, 104, 157, 0.6);
  font-size: 20px;
  color: #1f4a6e;
  cursor: pointer;
  transition: 0.2s;
}

.close-btn:hover {
  background: linear-gradient(to bottom, #dceaf9, #a5c3f1);
  transform: scale(1.02);
}

.import-panel {
  margin: 1.5rem 2rem 0;
  background: rgba(235, 245, 255, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 25px;
  border: 0.5px solid rgba(131, 179, 211, 0.6);
  padding: 1rem 1.5rem;
}

.import-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
}

.import-file-btn,
.sample-btn,
.switch-mode-btn,
.scale-settings-btn {
  background: rgba(248, 252, 255, 0.9);
  border: 0.5px solid rgba(112, 165, 218, 0.5);
  padding: 9px 18px;
  border-radius: 25px;
  font-size: 13px;
  font-weight: 500;
  color: #1f4a6e;
  cursor: pointer;
  transition: 0.8s;
}

.import-file-btn:hover,
.sample-btn:hover,
.switch-mode-btn:hover,
.scale-settings-btn:hover {
  background: rgba(82, 156, 209, 0.5);
  color: white;
}

.multi-import-container {
  margin-top: 16px;
  border-top: 1px solid rgba(100, 130, 160, 0.3);
  padding-top: 30px;
}

.mapping-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 30px;
}

.mapping-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1.2fr;
  gap: 12px;
  align-items: center;
  font-size: 13px;
  background: rgba(248, 252, 255, 0.604);
  padding: 10px 12px;
  border-radius: 16px;
}

.mapping-row.header {
  font-weight: 600;
  background: rgba(37, 41, 83, 0.095);
  color: #1e3a5f;
}

.hint {
  font-size: 13px;
  color: #105585;
  margin-left: 4px;
}

.import-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  justify-content: center;
}

.apply-import-btn,
.cancel-import-btn {
  background: linear-gradient(to bottom, #dceaf9, #e8f1ff);
  border: none;
  padding: 6px 20px;
  border-radius: 32px;
  font-weight: 600;
  border: 1px solid #a5c4ec;
  color: #1e3a5f;
  cursor: pointer;
}

.apply-import-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-import-btn {
  background: #283347;
  color: #e1f1ff;
}

.import-preview {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  padding: 12px;
}

.preview-header {
  font-weight: 600;
  margin-bottom: 8px;
  color: #1e3a5f;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-item {
  background: white;
  padding: 4px 12px;
  border-radius: 24px;
  font-size: 12px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.preview-name {
  font-weight: 700;
  color: #1e4a76;
}

.preview-mapping {
  background: #e9f0f8;
  padding: 2px 8px;
  border-radius: 20px;
}

.import-message {
  margin-top: 10px;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 24px;
  text-align: center;
}

.import-message.success {
  background: #c6e0c4;
  color: #1f6e43;
}

.import-message.error {
  background: #f8d7d7;
  color: #b13b3b;
}

.import-message.info {
  background: #e3edf8;
  color: #2c6e9e;
}

.table-wrapper {
  overflow-x: auto;
  margin: 1.5rem 2rem 1rem;
  border-radius: 28px;
  background: rgba(80, 110, 140, 0.3);
  border: 1px solid rgba(103, 116, 193, 0.526);
}

.marks-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 800px;
}

.marks-table thead th {
  position: sticky;
  top: 0;
  background: rgba(206, 225, 255, 0.611);
  padding: 15px 8px;
  font-weight: 700;
  color: #17365f;
  border-bottom: 1px solid rgba(102, 139, 190, 0.3);
}

.marks-table td {
  padding: 18px 8px;
  border-bottom: 1px solid rgba(116, 149, 197, 0.3);
}

.student-row:nth-child(odd) td {
  background: rgba(222, 235, 255, 0.655);
}

.student-row:nth-child(even) td {
  background: rgba(180, 198, 230, 0.849);
}

.student-row:hover td {
  background: rgba(164, 175, 225, 0.554);
}

.col-num {
  width: 44px;
  text-align: center;
  color: #1f3b4c;
}

.col-name {
  text-align: left;
  padding-left: 16px;
  font-weight: 600;
  color: #1a2c44;
}

.col-stat {
  width: 64px;
  text-align: center;
}

.avg-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 30px;
  font-weight: 600;
}

.avg-good {
  background: #efffee85;
  color: #1f6e43;
}

.avg-mid {
  background: #fffdf4bb;
  color: #a67c00;
}

.avg-bad {
  background: #fff0e9b8;
  color: #b3291a;
}

.warn-att {
  color: #b13b3b;
  font-weight: 600;
}

.date-col {
  min-width: 90px;
}

.date-text {
  font-size: 14px;
  font-weight: 600;
  color: #1f4a6e;
  margin-bottom: 8px;
}

.type-selector {
  cursor: pointer;
  background: rgba(60, 106, 153, 0.3);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #1f4a6e;
  display: inline-block;
}

.type-selector:hover {
  background: rgba(100, 150, 200, 0.6);
}

.combo-cell {
  padding: 4px 6px !important;
}

.combo-inner {
  display: flex;
  align-items: stretch;
  height: 36px;
  border-radius: 20px;
  background: rgba(245, 250, 255, 0.544);
  border: 1px solid rgba(52, 96, 141, 0.4);
  overflow: hidden;
}

.combo-grade {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.combo-grade:hover {
  background: rgba(220, 235, 250, 0.487);
}

.grade-val {
  font-weight: 600;
  font-size: 14px;
  color: #1a2c44;
}

.grade-empty {
  color: #36669d;
  font-weight: 700;
}

.g-good {
  color: #1f6e43;
  font-weight: 700;
}

.g-low {
  color: #b13b3b;
  font-weight: 700;
}

.combo-presence {
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.combo-presence .presence-icon {
  font-size: 16px;
  font-weight: bold;
  transition: transform 0.1s;
}

.combo-presence.pres-yes {
  background: #5fba8a;
  color: white;
}

.combo-presence.pres-no {
  background: #e58e8e;
  color: white;
}

.combo-presence:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.combo-presence:active {
  transform: scale(0.97);
}

.type-popup {
  position: absolute;
  background: #F8FBFF;
  border-radius: 20px;
  padding: 12px 16px;
  border: none;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  z-index: 10000;
  width: 180px;
  min-width: 140px;
  backdrop-filter: blur(30px);
}

.popup-label {
  font-size: 14px;
  font-weight: 600;
  color: #1f4a6e;
  text-align: center;
  margin-bottom: 12px;
}

.popup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.popup-btn {
  border: none;
  padding: 22px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  transition: 0.1s;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.popup-btn.kr {
  background: #8FA4C3;
  color: #4B618B;
}

.popup-btn.dop {
  background: #586C91;
  color: #283347;
}

.popup-btn.dz {
  background: #BDCFE9;
  color: #6B83A8;
}

.popup-btn.dash {
  background: #5C7BB4;
  color: #CDE1FF;
}

.popup-btn:hover {
  transform: scale(0.97);
  filter: brightness(0.9);
}

.popup-btn:active {
  transform: scale(0.95);
}

.scale-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #ffffff;
  border-radius: 32px;
  padding: 24px 28px;
  width: 600px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
  z-index: 10001;
}

.scale-inputs {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 28px;
}

.scale-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #d9e5ec;
  padding: 8px 20px;
  border-radius: 48px;
  justify-content: center;
}

.grade-label {
  width: 80px;
  font-weight: 600;
  color: #2c5a7a;
  font-size: 15px;
}

.scale-input {
  width: 80px;
  padding: 8px 12px;
  border-radius: 40px !important;
  border: 1px solid #b8cfdf !important;
  background: #ffffff !important;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: #2c5a7a;
  outline: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  -moz-appearance: textfield !important;
  appearance: none !important;
}

.scale-input:focus {
  border-color: #7faaC4 !important;
  box-shadow: 0 0 0 3px rgba(100, 150, 200, 0.3) !important;
  background: #ffffff !important;
}

.scale-input::-webkit-outer-spin-button,
.scale-input::-webkit-inner-spin-button {
  -webkit-appearance: none !important;
  margin: 0 !important;
}

.large-btn {
  padding: 12px 24px;
  font-size: 16px;
  background: linear-gradient(135deg, #7f9fbf, #5f8aad);
  color: white;
  border: none;
  border-radius: 60px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.large-btn:hover {
  transform: translateY(-2px);
  background: linear-gradient(135deg, #8fafcf, #6f9abf);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
}

.custom-number {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.num-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.num-btn.dec {
  background: #8fb5c5;
  color: white;
}

.num-btn.dec:hover {
  background: #6f9db0;
  transform: scale(1.05);
}

.num-btn.inc {
  background: #b293ba;
  color: white;
}

.num-btn.inc:hover {
  background: #764677ba;
  transform: scale(1.05);
}

.num-btn:active {
  transform: scale(0.95);
}

.scale-actions {
  text-align: center;
}

.scale-popup .popup-label {
  font-size: 18px !important;
  font-weight: 700 !important;
  color: #2c5a7a !important;
  margin-bottom: 20px !important;
}

.grade-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 58, 95, 0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10010;
}

.grade-popup {
  background: white;
  border-radius: 32px;
  padding: 24px;
  width: 280px;
  box-shadow: 0 20px 35px rgba(0, 0, 0, 0.2);
}

.grade-popup-name {
  font-weight: 700;
  font-size: 1rem;
  margin-bottom: 4px;
  text-align: center;
}

.grade-popup-sub {
  font-size: 12px;
  color: #5c6f8c;
  text-align: center;
  margin-bottom: 16px;
}

.grade-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #cfdfed;
  border-radius: 40px;
  font-size: 20px;
  font-weight: 500;
  text-align: center;
}

.grade-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  justify-content: center;
}

.btn-cancel,
.btn-ok {
  flex: 1;
  padding: 8px;
  border-radius: 40px;
  border: none;
  font-weight: 500;
  cursor: pointer;
}

.btn-cancel {
  background: #eef3fc;
  color: #1e3a5f;
}

.btn-ok {
  background: #2c6e9e;
  color: white;
}

.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: all 0.15s ease;
}

.popup-fade-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}

.fade-scale-enter-active {
  transition: all 0.2s cubic-bezier(0.2, 0.9, 0.4, 1.1);
}

.fade-scale-leave-active {
  transition: all 0.1s;
}

.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.96);
}

.mapping-row select {
  background: #ffffff;
  border: 2px solid #b8cfdf;
  border-radius: 40px !important;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #2c5a7a;
  cursor: pointer;
  outline: none;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%232c5a7a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  width: auto;
  min-width: 100px;
}

.mapping-row select:hover {
  border-color: #7faaC4;
  background-color: #fafdff;
}

.mapping-row select:focus {
  border-color: #7faaC4;
  box-shadow: 0 0 0 3px rgba(100, 150, 200, 0.3);
}

.mapping-row input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  background: #ffffff;
  border: 2px solid #b8cfdf;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  vertical-align: middle;
  margin-right: 6px;
}

.mapping-row input[type="checkbox"]:checked {
  background: #7f9fbf;
  border-color: #5f8aad;
  box-shadow: inset 0 0 0 3px white;
}

.mapping-row input[type="checkbox"]:hover {
  border-color: #7faaC4;
  transform: scale(1.02);
}

.mapping-row input[type="checkbox"]:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(100, 150, 200, 0.4);
}

.mapping-row input[type="checkbox"]+span {
  vertical-align: middle;
  margin-left: 4px;
}

.mapping-row div:last-child {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.mapping-row select option {
  background-color: #ffffff;
  color: #2c5a7a;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px;
  padding: 10px;
}

.mapping-row select option:hover {
  background-color: #e9f0f8;
}
</style>