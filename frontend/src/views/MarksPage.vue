<template>
  <div class="screen-marks" :class="{ 'is-mobile': isMobile }">
    <div class="marks-card">
      <div class="card-header" v-if="showHeader && !isMobile">
        <div class="header-left">
          <div class="logo-mini">UniDiary</div>
        </div>
        <div class="header-right">
          <div class="subject-badge">{{ subjectName }}</div>
          <div class="group-badge">{{ groupName || 'Группа' }}</div>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>
      </div>
      <div class="card-header card-header-mobile" v-if="showHeader && isMobile">
        <div class="header-top">
          <div class="header-left">
            <div class="logo-mini">UniDiary</div>
          </div>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>
        <div class="header-bottom">
          <div class="subject-badge">{{ subjectName }}</div>
          <div class="group-badge">{{ groupName || 'Группа' }}</div>
        </div>
      </div>

      <div class="import-panel">
        <div v-if="!isMobile" class="import-controls">
          <button class="sample-btn" @click="downloadSampleXlsx">Пример XLSX</button>
          <div class="export-dropdown" ref="exportDropdownRef">
            <button type="button" class="sample-btn export-trigger" @click.stop="toggleExportMenu">📥 Экспорт</button>
            <div v-if="exportMenuOpen" class="export-menu" @click.stop>
              <button type="button" class="export-menu-item" @click="pickExportFormat('csv')">CSV (.csv)</button>
              <button type="button" class="export-menu-item" @click="pickExportFormat('excel')">Excel (.xls)</button>
            </div>
          </div>
          <label class="import-file-btn">
  Загрузить XLSX
  <input type="file" accept=".csv,.xlsx,.xls" @change="handleFileUpload" style="display: none" ref="fileInput" />
</label>
          <button class="scale-settings-btn" @click.stop="openScalePopup($event)">⚙ Шкала и веса</button>
          <button v-if="!importModeActive" class="switch-mode-btn" @click="activateImportMode">➕ Импорт нескольких тестов</button>
          <button v-else class="switch-mode-btn" @click="cancelMultiImport">✕ Отменить импорт</button>
        </div>

        <div v-if="isMobile" class="import-controls import-controls-mobile">
          <div class="mobile-import-row">
            <button class="import-btn scale-settings-btn" @click.stop="openScalePopup($event)">⚙ Шкала и веса</button>
            <div class="export-dropdown" ref="exportDropdownRef">
              <button type="button" class="import-btn export-trigger" @click.stop="toggleExportMenu">📥 Экспорт</button>
              <div v-if="exportMenuOpen" class="export-menu" @click.stop>
                <button type="button" class="export-menu-item" @click="pickExportFormat('csv')">CSV (.csv)</button>
                <button type="button" class="export-menu-item" @click="pickExportFormat('excel')">Excel (.xls)</button>
              </div>
            </div>
          </div>
          <div class="mobile-import-row">
            <label class="import-file-btn">
  Загрузить XLSX
  <input type="file" accept=".csv,.xlsx,.xls" @change="handleFileUpload" style="display: none" ref="fileInput" />
</label>
            <button v-if="!importModeActive" class="import-btn switch-mode-btn" @click="activateImportMode">➕ Импорт нескольких тестов</button>
            <button v-else class="import-btn switch-mode-btn" @click="cancelMultiImport">✕ Отменить импорт</button>
          </div>
        </div>

        <div class="filter-row">
          <div class="attendance-filter">
            <span class="filter-label">Мин. посещений:</span>
            <input type="number" class="filter-input" v-model.number="minAttendanceFilter" min="0" :max="dates.length" placeholder="0" />
            <button v-if="minAttendanceFilter > 0" type="button" class="filter-reset" @click="minAttendanceFilter = 0">×</button>
          </div>
          <div class="student-search">
            <span class="filter-label">Поиск:</span>
            <input type="search" class="search-input" v-model="studentSearchQuery" placeholder="ФИО студента" />
            <button v-if="studentSearchQuery" type="button" class="filter-reset" @click="studentSearchQuery = ''">×</button>
          </div>
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
            <button @click="applyMultiImport" :disabled="!hasEnabledMappings" class="apply-import-btn">📥 Выставить оценки</button>
            <button @click="cancelMultiImport" class="cancel-import-btn">Отмена</button>
          </div>
          <div v-if="multiPreview.length" class="import-preview">
            <div class="preview-header">Предпросмотр (первые 5 студентов)</div>
            <div class="preview-list">
              <div v-for="preview in multiPreview.slice(0, 5)" :key="preview.studentName" class="preview-item">
                <span class="preview-name">{{ preview.studentName }}</span>
                <span v-for="map in preview.mappings" :key="map.csvHeader" class="preview-mapping">{{ map.csvHeader }} → {{ map.finalGrade }}</span>
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
              <th class="col-stat">Итоговая оценка</th>
              <th class="col-stat">П.</th>
              <th v-for="(date, dIdx) in dates" :key="date" class="date-col">
                <div class="date-text">{{ date }}</div>
                <div class="type-selector" @click.stop="openTypePopup($event, dIdx)">{{ getTypeLabel(columnSettings[dIdx].type) }}</div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="visibleStudentEntries.length === 0" class="empty-row">
              <td :colspan="4 + dates.length" class="empty-cell">Студенты не найдены</td>
            </tr>
            <tr v-for="({ student, sIdx }, idx) in visibleStudentEntries" :key="student.id" class="student-row">
              <td class="col-num">{{ idx + 1 }}</td>
              <td class="col-name">{{ student.name }}</td>
              <td class="col-stat"><span class="avg-badge" :class="getAvgClass(student.avg)">{{ student.avg }}</span></td>
              <td class="col-stat" :class="{ 'warn-att': student.attendance < 60 }">{{ student.attendance }}%</td>
              <td v-for="(rec, dIdx) in student.records" :key="dIdx" class="combo-cell">
                <div class="combo-inner">
                  <div class="combo-grade" @click.stop="editGrade(sIdx, dIdx)">
                    <template v-for="disp in [gradeDisplayParts(rec.grade, dIdx)]" :key="dIdx + '-g'">
                      <span class="grade-val" :class="getGradeClass(rec.grade, dIdx)">
                        <template v-if="rec.grade === ''">—</template>
                        <template v-else-if="rec.grade === '+' || rec.grade === '-'">{{ rec.grade }}</template>
                        <template v-else-if="disp.showPercent">
                          <span class="grade-raw">{{ disp.raw }}</span>
                          <span class="grade-arrow">→</span>
                          <span class="grade-pct">{{ disp.pct }}%</span>
                        </template>
                        <template v-else>{{ disp.raw ?? rec.grade }}</template>
                      </span>
                    </template>
                  </div>
                  <div
                    class="combo-presence"
                    :class="rec.present ? 'pres-yes' : 'pres-no'"
                    @click.stop="togglePresence(sIdx, dIdx)"
                    :title="rec.present ? 'Отметить отсутствие' : 'Отметить присутствие'"
                  >
                    <span class="presence-icon">{{ rec.present ? '✓' : '✗' }}</span>
                  </div>
                  <div
                    class="combo-comment"
                    :class="{ 'has-comment': rec.comment }"
                    @click.stop="editComment(sIdx, dIdx)"
                    :title="rec.comment || 'Добавить комментарий'"
                  >💬</div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="legend-row">
        <span class="legend-item"><span class="leg-dot pres-dot"></span>Присутствовал</span>
        <span class="legend-item"><span class="leg-dot abs-dot"></span>Отсутствовал</span>
        <span class="legend-item">| Оценка · посещение · 💬 Комментарий</span>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="popup-fade">
        <div v-if="popup.visible" class="type-popup" :style="{ top: popup.y + 'px', left: popup.x + 'px' }">
          <div class="popup-label">Тип работы</div>
          <div class="popup-grid">
            <button class="popup-btn kr" @click="setType('КР')">КР</button>
            <button class="popup-btn dop" @click="setType('ДОП')">ДОП</button>
            <button class="popup-btn dz" @click="setType('ДЗ')">ДЗ</button>
            <button class="popup-btn dash" @click="setType('±')">+ / -</button>
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
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.from2 = Math.max(0, gradeScale.from2 - 1)">−</button><input type="number" v-model.number="gradeScale.from2" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.from2 = Math.min(gradeScale.to2 - 1, gradeScale.from2 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.to2 = Math.max(gradeScale.from2 + 1, gradeScale.to2 - 1)">−</button><input type="number" v-model.number="gradeScale.to2" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.to2 = Math.min(gradeScale.from3 - 1, gradeScale.to2 + 1)">+</button></div>
            </div>
            <div class="scale-row"><span class="grade-label">Оценка 3:</span>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.from3 = Math.max(gradeScale.to2 + 1, gradeScale.from3 - 1)">−</button><input type="number" v-model.number="gradeScale.from3" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.from3 = Math.min(gradeScale.to3 - 1, gradeScale.from3 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.to3 = Math.max(gradeScale.from3 + 1, gradeScale.to3 - 1)">−</button><input type="number" v-model.number="gradeScale.to3" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.to3 = Math.min(gradeScale.from4 - 1, gradeScale.to3 + 1)">+</button></div>
            </div>
            <div class="scale-row"><span class="grade-label">Оценка 4:</span>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.from4 = Math.max(gradeScale.to3 + 1, gradeScale.from4 - 1)">−</button><input type="number" v-model.number="gradeScale.from4" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.from4 = Math.min(gradeScale.to4 - 1, gradeScale.from4 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.to4 = Math.max(gradeScale.from4 + 1, gradeScale.to4 - 1)">−</button><input type="number" v-model.number="gradeScale.to4" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.to4 = Math.min(gradeScale.from5 - 1, gradeScale.to4 + 1)">+</button></div>
            </div>
            <div class="scale-row"><span class="grade-label">Оценка 5:</span>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.from5 = Math.max(gradeScale.to4 + 1, gradeScale.from5 - 1)">−</button><input type="number" v-model.number="gradeScale.from5" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.from5 = Math.min(gradeScale.to5 - 1, gradeScale.from5 + 1)">+</button></div>
              <div class="custom-number"><button class="num-btn dec" @click="gradeScale.to5 = Math.max(gradeScale.from5 + 1, gradeScale.to5 - 1)">−</button><input type="number" v-model.number="gradeScale.to5" step="1" class="scale-input"><button class="num-btn inc" @click="gradeScale.to5 = Math.min(100, gradeScale.to5 + 1)">+</button></div>
            </div>
            <div class="scale-section-title">Весовые коэффициенты</div>
            <div v-for="cat in categoryWeights" :key="cat.code" class="scale-row">
              <span class="grade-label">{{ cat.name }}:</span>
              <div class="custom-number">
                <span class="hint">вес</span>
                <input type="number" v-model.number="cat.weight" step="0.1" min="0.01" class="scale-input" />
              </div>
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
            <div class="grade-popup-sub">{{ gradeInput.typeName }}</div>
            <input ref="gradeInputRef" v-model="gradeInput.value" class="grade-field" type="number" min="0"
              placeholder="Баллы" @keyup.enter="confirmGrade" @keyup.esc="gradeInput.visible = false">
            <div class="grade-actions"><button class="btn-cancel" @click="gradeInput.visible = false">Отмена</button><button class="btn-ok" @click="confirmGrade">Сохранить</button></div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="fade-scale">
        <div v-if="commentInput.visible" class="grade-overlay" @click.self="commentInput.visible = false">
          <div class="grade-popup comment-popup">
            <div class="grade-popup-name">{{ commentInput.studentName }}</div>
            <div class="grade-popup-sub">{{ commentInput.dateLabel }}</div>
            <textarea
              ref="commentInputRef"
              v-model="commentInput.value"
              class="comment-field"
              rows="4"
              placeholder="Комментарий к паре..."
              @keyup.esc="commentInput.visible = false"
            />
            <div class="grade-actions">
              <button class="btn-cancel" @click="commentInput.visible = false">Отмена</button>
              <button class="btn-ok" @click="confirmComment">Сохранить</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import {
  getStudents, getGrades, getAttendance, getLessonComments,
  saveGrade, saveAttendance, saveLessonComment, bulkSaveGrades,
  getGradeScale, saveGradeScale, getGradeCategories, saveGradeCategories,
  getGradeColumns, saveGradeColumns, normalizeDate
} from '@/services/marks'
import * as XLSX from 'xlsx'

const props = defineProps({ 
  subjectName: { type: String, default: 'Базы данных' },
  groupId: { type: Number, default: 1 },
  groupName: { type: String, default: '' },
  scheduleId: { type: Number, default: null },
  showHeader: { type: Boolean, default: true }
})
const emit = defineEmits(['close'])

const dates = ['21/04', '28/04', '5/05', '12/05', '19/05']
const columnSettings = ref(dates.map(() => ({ type: null, categoryCode: null })))
const students = ref([])
const studentsMap = ref(new Map())
const minAttendanceFilter = ref(0)
const studentSearchQuery = ref('')
const isMobile = ref(false)

const visibleStudentEntries = computed(() => {
  const q = studentSearchQuery.value.trim().toLowerCase()
  return students.value
    .map((student, sIdx) => ({ student, sIdx }))
    .filter(({ student }) => {
      if (q && !student.name.toLowerCase().includes(q)) return false
      return true
    })
})

const gradeScale = ref({
  from2: 0, to2: 40,
  from3: 41, to3: 60,
  from4: 61, to4: 80,
  from5: 81, to5: 100
})

const categoryWeights = ref([
  { code: 'DZ', name: 'ДЗ', weight: 0.3 },
  { code: 'KR', name: 'КР', weight: 0.5 },
  { code: 'DOP', name: 'ДОП', weight: 0.2 },
])

function categoriesToPayload() {
  return categoryWeights.value.map(c => ({
    code: c.code,
    name: c.name,
    weight: Number(c.weight),
  }))
}

const TYPE_TO_CATEGORY = { 'ДЗ': 'DZ', 'КР': 'KR', 'ДОП': 'DOP' }
const CATEGORY_TO_TYPE = { DZ: 'ДЗ', KR: 'КР', DOP: 'ДОП' }

function getCategoryWeight(categoryCode) {
  if (!categoryCode) return 1
  const cat = categoryWeights.value.find(c => c.code === categoryCode)
  return cat ? Number(cat.weight) : 1
}

function rulesToLocalScale(rules) {
  const scale = { from2: 0, to2: 40, from3: 41, to3: 60, from4: 61, to4: 80, from5: 81, to5: 100 }
  for (const r of rules) {
    if (r.final_grade === 2) { scale.from2 = r.min_points; scale.to2 = r.max_points }
    if (r.final_grade === 3) { scale.from3 = r.min_points; scale.to3 = r.max_points }
    if (r.final_grade === 4) { scale.from4 = r.min_points; scale.to4 = r.max_points }
    if (r.final_grade === 5) { scale.from5 = r.min_points; scale.to5 = r.max_points }
  }
  return scale
}

function localScaleToRules() {
  return [
    { min_points: gradeScale.value.from2, max_points: gradeScale.value.to2, final_grade: 2 },
    { min_points: gradeScale.value.from3, max_points: gradeScale.value.to3, final_grade: 3 },
    { min_points: gradeScale.value.from4, max_points: gradeScale.value.to4, final_grade: 4 },
    { min_points: gradeScale.value.from5, max_points: gradeScale.value.to5, final_grade: 5 },
  ]
}

async function loadScaleAndCategories() {
  if (!props.scheduleId) return
  try {
    const [rules, categories] = await Promise.all([
      getGradeScale(props.scheduleId),
      getGradeCategories(props.scheduleId),
    ])
    if (rules?.length) gradeScale.value = rulesToLocalScale(rules)
    if (categories?.length) {
      categoryWeights.value = categories.map(c => ({
        id: c.id,
        code: c.code,
        name: c.name,
        weight: Number(c.weight),
      }))
    }
  } catch (err) {
    console.warn('Шкала/веса не загружены', err)
  }
}

function convertScoreToGrade(score) {
  const s = Number(score)
  if (isNaN(s)) return null
  if (s >= gradeScale.value.from2 && s <= gradeScale.value.to2) return 2
  if (s >= gradeScale.value.from3 && s <= gradeScale.value.to3) return 3
  if (s >= gradeScale.value.from4 && s <= gradeScale.value.to4) return 4
  if (s >= gradeScale.value.from5 && s <= gradeScale.value.to5) return 5
  return null
}

function parseCellScore(value) {
  if (value === '' || value === '+' || value === '-') return null
  const raw = String(value).split('→')[0].trim()
  const n = parseFloat(raw)
  return isNaN(n) ? null : n
}

function scoreToPercent(raw, categoryCode) {
  return raw * getCategoryWeight(categoryCode)
}

function formatPct(pct) {
  return Number.isInteger(pct) ? pct : Math.round(pct * 10) / 10
}

function gradeDisplayParts(value, dIdx) {
  const cfg = columnSettings.value[dIdx]
  const n = parseCellScore(value)
  if (n == null || !cfg?.categoryCode || cfg.type === '±') {
    return { showPercent: false, raw: n, pct: null }
  }
  return { showPercent: true, raw: n, pct: formatPct(scoreToPercent(n, cfg.categoryCode)) }
}

function recalcStudentStats() {
  students.value.forEach(student => {
    let totalPercent = 0
    let hasGrades = false
    let presentCount = 0

    student.records.forEach((rec, idx) => {
      const cfg = columnSettings.value[idx]
      const g = parseCellScore(rec.grade)
      if (cfg?.type === '±') {
        if (rec.grade === '+') {
          totalPercent += 1
          hasGrades = true
        }
      } else if (g != null && cfg?.type) {
        totalPercent += scoreToPercent(g, cfg.categoryCode)
        hasGrades = true
      }
      if (rec.present) presentCount++
    })

    student.attendanceCount = presentCount
    student.attendancePoints = presentCount
    student.attendance = Math.round((presentCount / dates.length) * 100)

    if (hasGrades) {
      const totalPct = Math.min(totalPercent, 100)
      const grade = convertScoreToGrade(totalPct)
      student.avg = grade ?? '—'
    } else {
      student.avg = '—'
    }
  })
}

function dateToIso(dateStr) {
  const [day, month] = dateStr.split('/')
  return `2026-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}

function isoToDateIdx(isoDate) {
  const dateOnly = String(isoDate).slice(0, 10)
  const parts = dateOnly.split('-')
  const formatted = `${parseInt(parts[2], 10)}/${parts[1]}`
  return dates.indexOf(formatted)
}

async function loadStudents() {
  const token = localStorage.getItem('token')
  if (!token) return
  
  try {
    const data = await getStudents()
    const filtered = data.filter(s => s.group_id === props.groupId)
    
    students.value = filtered.map(s => ({
      id: s.id,
      name: s.full_name,
      avg: 0,
      attendance: 0,
      attendanceCount: 0,
      attendancePoints: 0,
      records: dates.map(() => ({ grade: '', present: true, comment: '' }))
    }))
    
    students.value.sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    
    filtered.forEach(s => {
      studentsMap.value.set(s.full_name, s.id)
    })
    
    await loadScaleAndCategories()
    await loadColumnSettings()
    await loadMarksFromDb()
    recalcStudentStats()
  } catch (err) {
    console.error('Ошибка загрузки студентов', err)
  }
}
async function loadColumnSettings() {
  if (!props.scheduleId) return
  try {
    const cols = await getGradeColumns(props.scheduleId)
    for (const col of cols) {
      const dIdx = isoToDateIdx(col.grade_date)
      if (dIdx !== -1) {
        columnSettings.value[dIdx] = {
          type: col.column_type,
          categoryCode: TYPE_TO_CATEGORY[col.column_type] || null,
        }
      }
    }
  } catch (err) {
    console.warn('Типы колонок не загружены', err)
  }
}

function inferColumnsFromGrades(grades) {
  let inferred = false
  const byDate = {}
  for (const g of grades) {
    if (!g.category_id || byDate[g.grade_date]) continue
    const cat = categoryWeights.value.find(c => c.id === g.category_id)
    if (cat) byDate[g.grade_date] = cat.code
  }
  for (const [isoDate, code] of Object.entries(byDate)) {
    const dIdx = isoToDateIdx(isoDate)
    if (dIdx === -1 || columnSettings.value[dIdx].type) continue
    const type = CATEGORY_TO_TYPE[code]
    if (type) {
      columnSettings.value[dIdx] = { type, categoryCode: code }
      inferred = true
    }
  }
  return inferred
}

async function persistColumnSettings() {
  if (!props.scheduleId) return
  const columns = columnSettings.value
    .map((cfg, idx) => (cfg.type ? { grade_date: dateToIso(dates[idx]), column_type: cfg.type } : null))
    .filter(Boolean)
  try {
    await saveGradeColumns(props.scheduleId, columns)
  } catch (err) {
    console.error('Ошибка сохранения типов колонок', err)
  }
}

async function loadMarksFromDb() {
  if (!props.scheduleId) return

  try {
    const [grades, attendance, lessonComments] = await Promise.all([
      getGrades(props.scheduleId),
      getAttendance(props.scheduleId),
      getLessonComments(props.scheduleId),
    ])

    if (inferColumnsFromGrades(grades)) {
      await persistColumnSettings()
    }

    for (const g of grades) {
      const sIdx = students.value.findIndex(s => s.id === g.student_id)
      const dIdx = isoToDateIdx(g.grade_date)
      if (sIdx !== -1 && dIdx !== -1) {
        const cfg = columnSettings.value[dIdx]
        let display = g.raw_score != null ? g.raw_score : g.grade
        if (cfg?.type === '±') {
          if (display === 1 || display === '1') display = '+'
          else if (display === 0 || display === '0') display = '-'
        }
        if (display != null) students.value[sIdx].records[dIdx].grade = display
      }
    }

    for (const c of lessonComments) {
      const sIdx = students.value.findIndex(s => s.id === c.student_id)
      const dIdx = isoToDateIdx(normalizeDate(c.lesson_date))
      if (sIdx !== -1 && dIdx !== -1) {
        students.value[sIdx].records[dIdx].comment = c.comment || ''
      }
    }

    for (const a of attendance) {
      const sIdx = students.value.findIndex(s => s.id === a.student_id)
      const dIdx = isoToDateIdx(a.date)
      if (sIdx !== -1 && dIdx !== -1) {
        students.value[sIdx].records[dIdx].present = a.status === 'present' || a.status === 'late'
      }
    }
  } catch (err) {
    console.error('Ошибка загрузки оценок/посещаемости', err)
  }
}

const importModeActive = ref(false)
const csvScoreColumns = ref([])
const rawCsvRows = ref([])
const headers = ref([])
const multiPreview = ref([])
const importMessage = ref('')
const importMessageType = ref('info')
const fileInput = ref(null)
const exportMenuOpen = ref(false)
const exportDropdownRef = ref(null)

const hasEnabledMappings = computed(() => csvScoreColumns.value.some(c => c.targetDateIdx !== undefined))

function activateImportMode() {
  importModeActive.value = true
}

function cancelMultiImport() {
  importModeActive.value = false
  csvScoreColumns.value = []
  rawCsvRows.value = []
  headers.value = []
  multiPreview.value = []
  importMessage.value = ''
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
  const isExcel = /\.xlsx?$/i.test(file.name)

  reader.onload = (e) => {
    try {
      let rows
      if (isExcel) {
        // Читаем Excel-файл
        const workbook = XLSX.read(e.target.result, { type: 'array' })
        const sheet = workbook.Sheets[workbook.SheetNames[0]]
        rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '', raw: false })
      } else {
        // Читаем CSV-файл
        rows = parseCSV(e.target.result)
      }
      if (rows.length < 2) throw new Error('Файл должен содержать заголовки и данные')
      analyzeCSVForMultiImport(rows)
    } catch (err) {
      setImportMsg(err.message, 'error')
    }
  }

  if (isExcel) {
    reader.readAsArrayBuffer(file)
  } else {
    reader.readAsText(file, 'UTF-8')
  }
  event.target.value = ''
}
function analyzeCSVForMultiImport(rows) {
  headers.value = rows[0].map(h => h.trim())
  const dataRows = rows.slice(1)
  if (dataRows.length === 0) throw new Error('Нет строк с данными')

  let nameColIdx = headers.value.findIndex(h => /студент|фио|student|name/i.test(h))
  if (nameColIdx === -1) nameColIdx = 0

  const scoreCols = []
  for (let i = 0; i < headers.value.length; i++) {
    if (i === nameColIdx) continue
    const values = dataRows.map(row => parseFloat(row[i])).filter(v => !isNaN(v))
    if (values.length === 0) continue
    const sampleValues = [...new Set(values.slice(0, 3))]
    const studentScores = dataRows.map(row => {
      const val = parseFloat(row[i])
      return isNaN(val) ? 0 : val
    })
    const rawNames = dataRows.map(row => row[nameColIdx]?.trim() || '')
    scoreCols.push({
      header: headers.value[i],
      sampleValues,
      targetDateIdx: 0,
      useGradeScale: false,
      studentScores,
      rawNames
    })
  }
  if (scoreCols.length === 0) throw new Error('Не найдено числовых колонок с процентами')
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
        const grade = convertScoreToGrade(percent)
        finalGrade = grade !== null ? grade : percent
      } else {
        finalGrade = percent
      }
      mappings.push({
        csvHeader: col.header,
        finalGrade,
        targetDateIdx: col.targetDateIdx
      })
    }
    if (mappings.length) preview.push({ studentName, mappings })
  }
  multiPreview.value = preview
}

async function applyMultiImport() {
  if (!hasEnabledMappings.value) {
    setImportMsg('Настройте привязку колонок к датам', 'error')
    return
  }

  const token = localStorage.getItem('token')
  if (!token) {
    setImportMsg('Нет токена авторизации', 'error')
    return
  }

  const scheduleId = props.scheduleId
  if (!scheduleId) {
    setImportMsg('Не выбрана пара (schedule_id)', 'error')
    return
  }

  console.log('Импорт начат, scheduleId:', scheduleId)
  console.log('Студенты в БД:', students.value.map(s => s.name))

  let totalSaved = 0

  for (const col of csvScoreColumns.value) {
    const targetColIdx = col.targetDateIdx
    const gradeDate = dateToIso(dates[targetColIdx])

    const gradesToSend = []

    for (let rowIdx = 0; rowIdx < rawCsvRows.value.length; rowIdx++) {
      const studentNameRaw = col.rawNames[rowIdx]
      if (!studentNameRaw) continue  // пропускаем пустые строки

      // Ищем студента по имени (с trim и регистронезависимо)
      const student = students.value.find(s => 
        s.name.toLowerCase().trim() === studentNameRaw.toLowerCase().trim()
      )
      if (!student) {
        console.warn(`Студент "${studentNameRaw}" не найден в БД`)
        continue
      }

      let percent = col.studentScores[rowIdx]
      let finalGrade = col.useGradeScale ? convertScoreToGrade(percent) : Math.min(percent, 100)
      if (col.useGradeScale && finalGrade === null) finalGrade = percent

      gradesToSend.push({
        student_id: student.id,   // <-- исправлено
        raw_score: percent,
        auto_convert: col.useGradeScale,
        grade: col.useGradeScale ? convertScoreToGrade(percent) : Math.min(percent, 100),
      })
    }

    if (gradesToSend.length === 0) continue

    try {
      const result = await bulkSaveGrades({
        scheduleId,
        gradeDate,
        grades: gradesToSend
      })
      if (result.status === 'success') {
        totalSaved += gradesToSend.length
        setImportMsg(`✅ ${result.message}`, 'success')
      } else {
        setImportMsg(`❌ Ошибка: ${result.message || 'неизвестная'}`, 'error')
      }
    } catch (err) {
      setImportMsg(`❌ Ошибка сети: ${err.message}`, 'error')
    }
  }

  if (totalSaved > 0) {
    await loadMarksFromDb()
    recalcStudentStats()
  }
  cancelMultiImport()
}

function setImportMsg(msg, type) {
  importMessage.value = msg
  importMessageType.value = type
  if (msg) setTimeout(() => { if (importMessage.value === msg) importMessage.value = '' }, 4000)
}

watch(csvScoreColumns, () => { computeMultiPreview() }, { deep: true })

const scalePopup = ref({ visible: false })
function openScalePopup(event) {
  event?.stopPropagation?.()
  scalePopup.value.visible = true
}
function closeScalePopup() {
  scalePopup.value.visible = false
  computeMultiPreview()
  saveScaleSettings()
}

async function saveScaleSettings() {
  if (!props.scheduleId) return
  try {
    await Promise.all([
      saveGradeScale(props.scheduleId, localScaleToRules()),
      saveGradeCategories(props.scheduleId, categoriesToPayload()),
    ])
    setImportMsg('✅ Шкала и веса сохранены', 'success')
    recalcStudentStats()
    await loadScaleAndCategories()
    recalcStudentStats()
  } catch (err) {
    setImportMsg(`❌ ${err.message}`, 'error')
  }
}

const popup = ref({ visible: false, x: 0, y: 0, dIndex: null })
const gradeInput = ref({ visible: false, sIdx: null, dIdx: null, value: '', typeName: '', studentName: '' })
const gradeInputRef = ref(null)
const commentInput = ref({ visible: false, sIdx: null, dIdx: null, value: '', studentName: '', dateLabel: '' })
const commentInputRef = ref(null)

function getTypeLabel(type) {
  if (type === 'КР') return 'КР'
  if (type === 'ДОП') return 'ДОП'
  if (type === 'ДЗ') return 'ДЗ'
  if (type === '±') return '+/-'
  return 'Оц.'
}

function getAvgClass(avg) {
  if (avg === '—' || avg === '' || avg == null) return ''
  const n = Number(avg)
  if (n >= 4) return 'avg-good'
  if (n >= 3) return 'avg-mid'
  return 'avg-bad'
}

function getGradeClass(grade, dIdx) {
  if (grade === '' || grade === '+' || grade === '-') return 'grade-empty'
  const n = parseCellScore(grade)
  if (n == null) return ''
  const cfg = columnSettings.value[dIdx]
  const pct = cfg?.categoryCode ? scoreToPercent(n, cfg.categoryCode) : n
  const converted = convertScoreToGrade(pct)
  if (converted != null && converted >= 4) return 'g-good'
  if (converted != null && converted <= 2) return 'g-low'
  return ''
}

function openTypePopup(e, dIdx) {
  const rect = e.target.getBoundingClientRect()
  popup.value = {
    visible: true,
    x: Math.min(rect.left + window.scrollX - 80, window.innerWidth - 280),
    y: rect.bottom + window.scrollY + 8,
    dIndex: dIdx
  }
}

function closePopup() { popup.value.visible = false }

function setType(type) {
  const dIdx = popup.value.dIndex
  students.value.forEach(s => { s.records[dIdx].grade = type === '±' ? '+' : '0' })
  columnSettings.value[dIdx] = {
    type,
    categoryCode: TYPE_TO_CATEGORY[type] || null,
  }
  recalcStudentStats()
  closePopup()
  persistColumnSettings()
}

async function editGrade(sIdx, dIdx) {
  const cfg = columnSettings.value[dIdx]
  if (!cfg.type) {
    alert('Сначала выберите тип колонки (кнопка "Оц." вверху)')
    return
  }
  if (cfg.type === '±') {
    const rec = students.value[sIdx].records[dIdx]
    rec.grade = rec.grade === '+' ? '-' : '+'
    recalcStudentStats()
    const rawScore = rec.grade === '+' ? 1 : 0
    await persistGrade(sIdx, dIdx, rawScore)
    return
  }
  gradeInput.value = {
    visible: true,
    sIdx, dIdx,
    value: students.value[sIdx].records[dIdx].grade === '' ? '' : parseCellScore(students.value[sIdx].records[dIdx].grade) ?? '',
    typeName: cfg.type,
    studentName: students.value[sIdx].name
  }
  await nextTick()
  gradeInputRef.value?.focus()
  gradeInputRef.value?.select()
}

function confirmGrade() {
  const { sIdx, dIdx, value } = gradeInput.value
  const num = +value
  if (value === '' || isNaN(num) || num < 0) {
    alert('Введите положительное число')
    return
  }
  students.value[sIdx].records[dIdx].grade = num
  gradeInput.value.visible = false
  recalcStudentStats()
  persistGrade(sIdx, dIdx, num)
}

function gradePayloadForCell(sIdx, dIdx, overrides = {}) {
  const student = students.value[sIdx]
  const cfg = columnSettings.value[dIdx]
  const category = categoryWeights.value.find(c => c.code === cfg.categoryCode)
  const rawScore = parseCellScore(student.records[dIdx].grade)
  return {
    studentId: student.id,
    scheduleId: props.scheduleId,
    rawScore,
    autoConvert: false,
    categoryId: category?.id ?? null,
    gradeDate: dateToIso(dates[dIdx]),
    ...overrides,
  }
}

async function persistGrade(sIdx, dIdx, gradeValue) {
  if (!props.scheduleId) return
  try {
    await saveGrade(gradePayloadForCell(sIdx, dIdx, { rawScore: gradeValue }))
  } catch (err) {
    console.error('Ошибка сохранения оценки', err)
    setImportMsg(`❌ ${err.message}`, 'error')
  }
}

async function editComment(sIdx, dIdx) {
  commentInput.value = {
    visible: true,
    sIdx,
    dIdx,
    value: students.value[sIdx].records[dIdx].comment || '',
    studentName: students.value[sIdx].name,
    dateLabel: dates[dIdx],
  }
  await nextTick()
  commentInputRef.value?.focus()
}

async function confirmComment() {
  const { sIdx, dIdx, value } = commentInput.value
  students.value[sIdx].records[dIdx].comment = value.trim()
  commentInput.value.visible = false
  await persistComment(sIdx, dIdx)
}

async function persistComment(sIdx, dIdx) {
  if (!props.scheduleId) return
  const student = students.value[sIdx]
  const rec = student.records[dIdx]
  try {
    await saveLessonComment({
      studentId: student.id,
      scheduleId: props.scheduleId,
      lessonDate: dateToIso(dates[dIdx]),
      comment: rec.comment || '',
    })
    setImportMsg('✅ Комментарий сохранён', 'success')
  } catch (err) {
    console.error('Ошибка сохранения комментария', err)
    setImportMsg(`❌ ${err.message}`, 'error')
  }
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
  try {
    await saveAttendance({
      studentId: student.id,
      scheduleId: props.scheduleId,
      status: present ? 'present' : 'absent',
      date: dateToIso(dates[dIdx])
    })
  } catch (err) {
    console.error('Ошибка сохранения посещаемости', err)
    setImportMsg(`❌ ${err.message}`, 'error')
  }
}

function handleClickOutside(e) {
  if (!e.target.closest('.type-popup')) closePopup()
  if (scalePopup.value.visible && !e.target.closest('.scale-popup')) scalePopup.value.visible = false
  if (exportMenuOpen.value && !e.target.closest('.export-dropdown')) exportMenuOpen.value = false
}

function toggleExportMenu() {
  exportMenuOpen.value = !exportMenuOpen.value
}

function pickExportFormat(format) {
  exportMenuOpen.value = false
  if (format === 'csv') exportJournalCsv()
  else exportJournalExcel()
}

function downloadSampleXlsx() {
  const sampleRows = [
    ['Студент', 'Тест 1 (%)', 'Тест 2 (%)'],
    ['Ковалёв Леонид', '85', '64'],
    ['Шварц Анжелика', '42', '33'],
    ['Углицкий Евгений', '78', '91'],
    ['Смирнов Григорий', '94', '73']
  ]
  downloadXlsxFile('example_marks.xlsx', sampleRows)
}

function downloadXlsxFile(filename, rows) {
  const ws = XLSX.utils.aoa_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Журнал')
  XLSX.writeFile(wb, filename)
}

function sanitizeFileName(value) {
  return String(value || 'journal')
    .replace(/[<>:"/\\|?*]/g, '_')
    .replace(/\s+/g, '_')
    .slice(0, 60)
}

function escapeCsvCell(value) {
  const s = String(value ?? '')
  if (/[",;\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

function formatGradeForExport(grade, dIdx) {
  if (grade === '' || grade == null) return '—'
  if (grade === '+' || grade === '-') return grade
  const parts = gradeDisplayParts(grade, dIdx)
  if (parts.showPercent) return `${parts.raw} (${parts.pct}%)`
  return String(parts.raw ?? grade)
}

function buildJournalExportRows() {
  const header = ['№', 'ФИО', 'Ср.', 'П.%']
  dates.forEach((date, dIdx) => {
    const type = getTypeLabel(columnSettings.value[dIdx].type)
    header.push(`${date} (${type})`)
    header.push(`${date} посещ.`)
    header.push(`${date} комм.`)
  })

  const rows = students.value.map((student, index) => {
    const row = [
      index + 1,
      student.name,
      student.avg ?? '—',
      `${student.attendance ?? 0}%`,
    ]
    student.records.forEach((rec, dIdx) => {
      row.push(formatGradeForExport(rec.grade, dIdx))
      row.push(rec.present ? '✓' : '✗')
      row.push(rec.comment || '')
    })
    return row
  })

  return [header, ...rows]
}

function escapeHtmlCell(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function cellAlignForExport(colIdx) {
  if (colIdx === 0 || colIdx === 2 || colIdx === 3) return 'right'
  if (colIdx === 1) return 'left'
  const subIdx = (colIdx - 4) % 3
  if (subIdx === 0) return 'right'
  if (subIdx === 1) return 'center'
  return 'left'
}

function buildStyledExcelHtml(rows) {
  const [headerRow, ...bodyRows] = rows
  const isNameFirstSheet =
    headerRow.length >= 2 &&
    (String(headerRow[0]).includes('Студент') || String(headerRow[0]).includes('ФИО'))
  const alignFor = colIdx => {
    if (isNameFirstSheet && headerRow.length <= 4) {
      return colIdx === 0 ? 'left' : 'right'
    }
    return cellAlignForExport(colIdx)
  }
  const baseCell =
    'font-family: Times New Roman, Times, serif; font-size: 11pt; border: 1px solid #b0b0b0; padding: 2px 6px;'
  const thStyle = `${baseCell} background: #d9d9d9; font-weight: bold; text-align: center;`
  const headerHtml =
    '<tr>' +
    headerRow.map(c => `<th style="${thStyle}">${escapeHtmlCell(c)}</th>`).join('') +
    '</tr>'
  const bodyHtml = bodyRows
    .map(row => {
      const cells = row
        .map((c, colIdx) => {
          const align = alignFor(colIdx)
          const tdStyle = `${baseCell} text-align: ${align};`
          return `<td style="${tdStyle}">${escapeHtmlCell(c)}</td>`
        })
        .join('')
      return `<tr>${cells}</tr>`
    })
    .join('')

  return [
    '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">',
    '<head><meta charset="utf-8">',
    '<style>table { border-collapse: collapse; } td, th { font-family: Times New Roman, Times, serif; font-size: 11pt; }</style>',
    '</head><body><table>',
    headerHtml,
    bodyHtml,
    '</table></body></html>',
  ].join('')
}

function downloadCsvFile(filename, rows) {
  const sep = ';'
  const body = rows
    .map(row => row.map(cell => escapeCsvCell(cell)).join(sep))
    .join('\r\n')
  const blob = new Blob(['\uFEFF' + body], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}

function downloadStyledExcelFile(filename, rows) {
  const html = buildStyledExcelHtml(rows)
  const blob = new Blob(['\uFEFF' + html], { type: 'application/vnd.ms-excel;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}

function exportJournalCsv() {
  if (!students.value.length) {
    setImportMsg('Нет данных для экспорта', 'error')
    return
  }
  const name = sanitizeFileName(`${props.groupName}_${props.subjectName}`)
  downloadCsvFile(`journal_${name}.csv`, buildJournalExportRows())
  setImportMsg('✅ Журнал экспортирован в CSV', 'success')
}

function exportJournalExcel() {
  if (!students.value.length) {
    setImportMsg('Нет данных для экспорта', 'error')
    return
  }
  const name = sanitizeFileName(`${props.groupName}_${props.subjectName}`)
  downloadStyledExcelFile(`journal_${name}.xls`, buildJournalExportRows())
  setImportMsg('✅ Журнал экспортирован в Excel', 'success')
}

function preventBodyScroll(e) {
  if (e.target.closest('.marks-card')) return
  e.preventDefault()
}

onMounted(() => {
  document.body.addEventListener('touchmove', preventBodyScroll, { passive: false })
  document.body.classList.add('no-scroll')
  loadScaleAndCategories()
  loadStudents()
  checkIfMobile()
  window.addEventListener('resize', checkIfMobile)
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.body.removeEventListener('touchmove', preventBodyScroll)
  document.body.classList.remove('no-scroll')
  window.removeEventListener('resize', checkIfMobile)
  document.removeEventListener('click', handleClickOutside)
})

function checkIfMobile() {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    document.body.classList.add('is-mobile')
  } else {
    document.body.classList.remove('is-mobile')
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.screen-marks {
  height: 100%;
  display: flex;
  padding: 0;
  background: #eef4fa;
  align-items: center;
  justify-content: center;
  border-radius: 28px;
  font-family: 'Inter', system-ui, sans-serif;
}

.marks-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, rgba(225, 239, 255, 0.65) 22%, rgba(165, 186, 202, 0.45) 79%, rgba(130, 164, 192, 0.65));
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
  background: rgba(179, 204, 228, 0.7);
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
.import-controls .switch-mode-btn {
  flex: 0 1 auto;
  white-space: nowrap;
  max-width: 100%;
}
.screen-marks.is-mobile .import-controls .switch-mode-btn {
  flex: 1 1 100%;
  white-space: nowrap;
  text-align: center;
  max-width: 100%;
  padding: 10px 16px;
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

.export-dropdown {
  position: relative;
}

.export-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 50;
  background: #f8fbff;
  border: 0.5px solid rgba(112, 165, 218, 0.5);
  border-radius: 16px;
  padding: 6px;
  min-width: 168px;
  box-shadow: 0 4px 16px rgba(30, 60, 100, 0.15);
}

.export-menu-item {
  display: block;
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #1f4a6e;
  cursor: pointer;
  transition: 0.3s;
}

.export-menu-item:hover {
  background: rgba(82, 156, 209, 0.25);
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
  overflow-y: auto;
  margin: 1rem 1.5rem 1rem;
  border-radius: 28px;
  background: rgba(80, 110, 140, 0.3);
  border: 1px solid rgba(103, 116, 193, 0.526);
  flex: 1;
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

.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.popup-fade-enter-from {
  opacity: 0;
  transform: translateY(-12px) scale(0.92);
}

.popup-fade-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

.fade-scale-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fade-scale-leave-active {
  transition: all 0.2s ease-in;
}

.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.88) translateY(10px);
}

.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.94) translateY(8px);
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
  background: #8fa4c3;
  color: #4b618b;
}

.popup-btn.dop {
  background: #586c91;
  color: #283347;
}

.popup-btn.dz {
  background: #bdcfe9;
  color: #6b83a8;
}

.popup-btn.dash {
  background: #5c7bb4;
  color: #cde1ff;
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

.comment-popup { min-width: 320px; }

.legend-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding: 12px 0 16px;    
  margin: 0 2rem;           
  font-size: 12px;
  color: #4a6080;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 30px;
}

.leg-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.pres-dot { background: #5fba8a; }
.abs-dot { background: #e58e8e; }

.comment-field {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #b8cfdf;
  border-radius: 12px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 4px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  align-items: center;
  padding: 0 4px;
  justify-content: center; 
}

.attendance-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.45);
  border-radius: 20px;
  border: 1px solid rgba(100, 160, 200, 0.45);
}

.student-search {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.45);
  border-radius: 20px;
  border: 1px solid rgba(100, 160, 200, 0.45);
}

.filter-label {
  font-size: 12px;
  color: #1f4a6e;
  font-weight: 500;
}

.filter-input {
  width: 48px;
  padding: 4px 6px;
  border: 1px solid #b8cfdf;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
}

.filter-reset {
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: #dce8f5;
  color: #1f4a6e;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.search-input {
  width: 140px;
  padding: 4px 8px;
  border: 1px solid #b8cfdf;
  border-radius: 8px;
  font-size: 13px;
}

.search-input::placeholder {
  color: #8aa8c4;
}

.empty-cell {
  text-align: center;
  padding: 24px;
  color: #5c6f8c;
  font-size: 14px;
}

.grade-raw { font-weight: 700; }
.grade-arrow { color: #6b8cae; margin: 0 2px; font-size: 11px; }
.grade-pct { font-size: 11px; color: #2c6e9e; font-weight: 600; }

.combo-comment {
  width: 32px;              
  height: 32px;
  border-radius: 50%;          
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(150, 180, 210, 0.3);
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.combo-comment:hover {
  background: #c1d5ec;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.combo-comment.has-comment {
  background: #c8daf0;
  border-color: #bed8ee;
  box-shadow: 0 0 0 2px rgba(95, 138, 173, 0.2);
}

.scale-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #3d6a8c;
  margin: 12px 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
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

.screen-marks.is-mobile {
  background: url('@/assets/main2.PNG');
  background-size: cover;
  background-position: left center;
  background-repeat: no-repeat;
  background-color: #c2dff5;
  background-blend-mode: lighten;
  height: 100%;
  display: flex;
  padding: 5px;
  background: #a3bfdb;
  position: relative;
  border-radius: 0;
}
.screen-marks.is-mobile::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.1) 100%);
  pointer-events: none;
  z-index: 0;
}
.screen-marks.is-mobile > * { position: relative; z-index: 1; }

.screen-marks.is-mobile .marks-card {
   background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  border-radius: 32px;
  margin: 0.5rem;
  overflow-y: auto;
  height: 100%;
  overscroll-behavior: contain;
  -webkit-overscroll-behavior: contain;
  box-shadow: none;
  border: none;  
}
.screen-marks.is-mobile .card-header-mobile {
  display: flex;
  flex-direction: column;
  padding: 0.8rem 1rem;
  gap: 6px;
  width: 100%;
  box-sizing: border-box;
}

.screen-marks.is-mobile .card-header-mobile .header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.screen-marks.is-mobile .card-header-mobile .header-bottom {
  display: flex;
  justify-content: center;
  gap: 8px;
}
.screen-marks.is-mobile .header-right {
  gap: 6px;
  flex-wrap: nowrap;
}
.screen-marks.is-mobile .subject-badge,
.screen-marks.is-mobile .group-badge {
  padding: 4px 12px;
  font-size: 12px;
}
.screen-marks.is-mobile .close-btn {
  width: 30px;
  height: 30px;
  font-size: 18px;
}
.screen-marks.is-mobile .import-panel {
  margin: 0.5rem 1rem;
  padding: 0.8rem;
}
.screen-marks.is-mobile .import-controls {
  gap: 6px;
  justify-content: flex-start;
}
.screen-marks.is-mobile .sample-btn {
  display: none;
}

.screen-marks.is-mobile .import-file-btn,
.screen-marks.is-mobile .switch-mode-btn,
.screen-marks.is-mobile .scale-settings-btn {
  padding: 6px 12px;
  font-size: 11px;
}

.screen-marks.is-mobile .table-wrapper {
  overflow-x: auto;
  overflow-y: visible;
  margin: 0.5rem;
  border-radius: 20px;
  flex: 1 0 auto;
}
.screen-marks.is-mobile .marks-table {
  min-width: 650px;
  font-size: 11px;
}
.screen-marks.is-mobile .marks-table th,
.screen-marks.is-mobile .marks-table td {
  padding: 8px 4px;
}
.screen-marks.is-mobile .combo-inner {
  height: 28px;
}
.screen-marks.is-mobile .grade-val {
  font-size: 12px;
}

.screen-marks.is-mobile .combo-presence {
  width: 24px;
  height: 24px;
}
.screen-marks.is-mobile .combo-presence .presence-icon {
  font-size: 12px;
}
.screen-marks.is-mobile .combo-comment {
  width: 24px;
  height: 24px;
  font-size: 12px;
}

.screen-marks.is-mobile .import-controls-mobile .mobile-import-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
}

.screen-marks.is-mobile .import-file-btn,
.screen-marks.is-mobile .import-btn {
  background: rgba(248, 252, 255, 0.9);
  border: 0.5px solid rgba(112, 165, 218, 0.5);
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 500;
  color: #1f4a6e;
  cursor: pointer;
  transition: 0.2s;
  white-space: nowrap;
  flex: 1;
  max-width: 190px;
  text-align: center;
}

.screen-marks.is-mobile .import-controls {
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.screen-marks.is-mobile .legend-row {
  margin: 0 0.5rem 16px;
  font-size: 10px;
  gap: 8px;
  justify-content: center;
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

.no-scroll {
  overflow: hidden;
}

body.is-mobile .scale-popup {
  width: 350px !important;
  padding: 12px 16px !important;
  border-radius: 24px !important;
}

body.is-mobile .scale-popup .popup-label {
  font-size: 15px !important;
  margin-bottom: 12px !important;
}

body.is-mobile .scale-row {
  padding: 4px 12px !important;
  gap: 6px !important;
}

body.is-mobile .grade-label {
  width: 60px !important;
  font-size: 12px !important;
}

body.is-mobile .scale-input {
  width: 50px !important;
  padding: 4px 5px !important;
  font-size: 12px !important;
}

body.is-mobile .num-btn {
  width: 24px !important;
  height: 24px !important;
  font-size: 16px !important;
}

body.is-mobile .large-btn {
  padding: 6px 16px !important;
  font-size: 13px !important;
}

body.is-mobile .scale-section-title {
  text-align: center !important;
}
</style>