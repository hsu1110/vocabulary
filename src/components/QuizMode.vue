<template>
  <div class="quiz-container">
    <!-- Config Panel (Before Quiz Starts) -->
    <div v-if="quizState === 'setup'" class="setup-panel">
      <!-- 左側表單區塊，右側讓背景圖呼吸 -->
      <div class="setup-inner">
        <h3 class="setup-title">
          <el-icon><Postcard /></el-icon> 小考測驗設定
        </h3>
        
        <el-form label-position="top">
          <!-- 1. Select Range Type -->
          <el-form-item label="1. 選擇測驗範圍">
            <el-radio-group v-model="rangeType" class="quiz-radio-group">
              <el-radio-button value="all">全書範圍</el-radio-button>
              <el-radio-button value="chapter">指定 Part / 章節</el-radio-button>
              <el-radio-button value="wrong" :disabled="!hasWrongWords">
                僅錯字本 (目前共 {{ wrongWordsCount }} 字)
              </el-radio-button>
            </el-radio-group>
          </el-form-item>

          <!-- 2. Show Range selectors if Chapter range is selected -->
          <el-form-item v-if="rangeType === 'chapter'" label="請選擇章節">
            <div class="quiz-range-selects">
              <el-select
                v-model="selectedPartId"
                placeholder="請選擇 Part"
                style="flex: 1;"
                @change="handlePartSelectChange"
              >
                <el-option
                  v-for="p in vocabularyData"
                  :key="p.part_id"
                  :value="p.part_id"
                  :label="p.part_name"
                />
              </el-select>

              <el-select
                v-model="selectedChapterName"
                :disabled="!selectedPartId"
                placeholder="請選擇章節"
                style="flex: 1;"
                @change="handleChapterSelectChange"
              >
                <el-option
                  v-for="ch in availableChapters"
                  :key="ch"
                  :value="ch"
                  :label="ch"
                />
              </el-select>
            </div>
          </el-form-item>

          <!-- 3. Question Count -->
          <el-form-item label="2. 選擇測驗題數">
            <el-input-number
              v-model="questionCount"
              :min="availableWordsList.length > 0 ? 1 : 0"
              :max="maxAvailableQuestions"
              :disabled="availableWordsList.length === 0"
              :step="availableWordsList.length >= 5 ? 5 : 1"
              controls-position="right"
              style="width: 150px;"
            />
            <span class="max-hint text-muted">
              (此範圍最多可測驗 {{ maxAvailableQuestions }} 題)
            </span>
          </el-form-item>

          <!-- 4. Start Button -->
          <el-form-item style="margin-top: 32px;">
            <el-button
              class="btn-primary-neon"
              size="large"
              style="width: 100%; font-size: 18px; height: 50px;"
              :disabled="!isSetupValid"
              @click="startQuiz"
            >
              開始測驗
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- Active Quiz Page -->
    <div v-else-if="quizState === 'active'" class="active-quiz">
      <!-- Header / Progress -->
      <div class="quiz-header-bar glass-container">
        <div class="progress-info">
          <span class="progress-text">題數: {{ currentQuestionIdx + 1 }} / {{ questions.length }}</span>
          <span class="score-text">答對: {{ score }}</span>
        </div>
        <el-progress
          :percentage="Math.round(((currentQuestionIdx) / questions.length) * 100)"
          :stroke-width="8"
          :color="customColors"
          style="width: 100%; margin-top: 10px;"
        />
      </div>

      <!-- Question Box -->
      <div class="question-box glow-card">
        <span class="question-hint">請問以下單字的意思是？</span>
        <div class="question-word">{{ currentQuestion.word }}</div>
        <div v-if="hasAnswered" class="question-phonetic">
          {{ currentQuestion.phonetic }}
          <el-button
            circle
            class="btn-accent-glass"
            size="small"
            :icon="Headset"
            style="margin-left: 8px;"
            @click.stop="speakText(currentQuestion.word)"
          />
        </div>
      </div>

      <!-- Options -->
      <div class="options-container">
        <button
          v-for="opt in currentOptions"
          :key="opt.id"
          class="option-btn"
          :class="getOptionClass(opt.id)"
          :disabled="hasAnswered"
          @click="selectOption(opt.id)"
        >
          <span class="option-label">{{ opt.label }}</span>
          <span class="option-text">{{ opt.definition }}</span>
        </button>
      </div>

      <!-- Footer / Next Button -->
      <div class="quiz-footer">
        <el-button
          v-if="hasAnswered"
          size="large"
          class="btn-primary-neon next-btn"
          @click="nextQuestion"
        >
          {{ currentQuestionIdx === questions.length - 1 ? '查看測驗結果' : '下一題' }}
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Results Page -->
    <div v-else-if="quizState === 'result'" class="result-page">
      <div class="result-header">
        <div class="result-score-circle">
          <span class="score-number">{{ Math.round((score / questions.length) * 100) }}%</span>
          <span class="score-label">分數</span>
        </div>
        <h3 class="result-title">測驗結束！</h3>
        <p class="result-desc">您答對了 {{ score }} 題，共 {{ questions.length }} 題。</p>
      </div>

      <!-- Wrong Words Summary -->
      <div v-if="wrongAnswers.length" class="wrong-summary">
        <h4 class="summary-title text-danger">答錯單字清單 (已自動記入錯字本)：</h4>
        
        <!-- 電腦版：使用 Table 表格 -->
        <el-table :data="wrongAnswers" class="desktop-only" style="width: 100%; border-radius: 8px;">
          <el-table-column prop="word" label="單字" width="150">
            <template #default="scope">
              <span class="wrong-word-link" @click="speakText(scope.row.word)">
                {{ scope.row.word }} <el-icon><Headset /></el-icon>
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="definition" label="中文解釋" />
          <el-table-column label="您的回答">
            <template #default="scope">
              <span class="text-danger">{{ scope.row.yourAnswer }}</span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 手機版：使用精緻的清單字卡，防止排版溢出且更易閱讀 -->
        <div class="mobile-only wrong-cards-list" style="display: flex; flex-direction: column; gap: 12px; width: 100%;">
          <div
            v-for="(w, idx) in wrongAnswers"
            :key="idx"
            class="wrong-word-card glass-container"
            style="padding: 16px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.25); background: rgba(239, 68, 68, 0.04); display: flex; flex-direction: column; gap: 8px; text-align: left;"
          >
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="wrong-word-link" style="font-size: 16px; font-weight: 700; color: var(--text-primary);" @click="speakText(w.word)">
                {{ w.word }} <el-icon style="font-size: 14px; margin-left: 4px;"><Headset /></el-icon>
              </span>
              <el-tag type="danger" size="small" effect="dark" style="border-radius: 6px;">答錯</el-tag>
            </div>
            <div style="font-size: 13.5px; color: var(--text-primary); line-height: 1.4;">
              <span style="color: var(--text-muted); font-weight: 600;">正確釋義：</span>{{ w.definition }}
            </div>
            <div style="font-size: 13.5px; color: #fca5a5; line-height: 1.4;">
              <span style="color: var(--text-muted); font-weight: 600;">您的回答：</span>{{ w.yourAnswer }}
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="perfect-score text-success">
        <el-icon size="40"><Trophy /></el-icon>
        <h4>太棒了！全部答對！</h4>
      </div>

      <!-- Actions -->
      <div class="result-actions">
        <el-button class="btn-primary-neon" size="large" @click="restartSetup">
          重新設定測驗
        </el-button>
        <el-button class="btn-secondary-glass" size="large" @click="$emit('switch-tab', 'study')">
          回到背單字模式
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Postcard, Headset, ArrowRight, Trophy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useTTS } from '../composables/useTTS.js'

const props = defineProps({
  vocabularyData: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['switch-tab', 'update-wrong-count'])

// Quiz states: 'setup', 'active', 'result'
const quizState = ref('setup')

// Setup values
const rangeType = ref('all') // 'all', 'chapter', 'wrong'
const selectedRange = ref([]) // [part_id, chapter_name]
const questionCount = ref(20)

const selectedPartId = ref('')
const selectedChapterName = ref('')

// Initialize and watch selectedRange to sync with selectedPartId and selectedChapterName
watch(selectedRange, (newRange) => {
  if (newRange && newRange.length === 2) {
    selectedPartId.value = newRange[0]
    selectedChapterName.value = newRange[1]
  } else {
    selectedPartId.value = ''
    selectedChapterName.value = ''
  }
}, { immediate: true })

// Chapter options based on selectedPartId
const availableChapters = computed(() => {
  if (!selectedPartId.value) return []
  const part = props.vocabularyData.find(p => p.part_id === selectedPartId.value)
  return part ? part.chapters.map(c => c.chapter_name) : []
})

// Handlers for manual selection change in mobile dropdowns
const handlePartSelectChange = (val) => {
  selectedPartId.value = val
  const part = props.vocabularyData.find(p => p.part_id === val)
  if (part && part.chapters.length > 0) {
    selectedChapterName.value = part.chapters[0].chapter_name
    selectedRange.value = [val, selectedChapterName.value]
  }
}

const handleChapterSelectChange = (val) => {
  selectedChapterName.value = val
  if (selectedPartId.value && val) {
    selectedRange.value = [selectedPartId.value, val]
  }
}

// Quiz Active State
const questions = ref([])
const currentQuestionIdx = ref(0)
const currentOptions = ref([])
const selectedAnswerId = ref(null) // ID of chosen option
const hasAnswered = ref(false)
const score = ref(0)

// Wrong answers tracked in this quiz session for result view
const wrongAnswers = ref([])

// Helper definitions for local storage wrong words
const wrongWordsLocal = ref([])
const hasWrongWords = computed(() => wrongWordsLocal.value.length > 0)
const wrongWordsCount = computed(() => wrongWordsLocal.value.length)

// Compute all flat words under current range (filtering out those with empty definitions)
const availableWordsList = computed(() => {
  if (rangeType.value === 'all') {
    const list = []
    props.vocabularyData.forEach(p => {
      p.chapters.forEach(c => {
        c.words.forEach(w => {
          if (w.definition && w.definition.trim()) {
            list.push(w)
          }
        })
      })
    })
    return list
  } else if (rangeType.value === 'chapter') {
    if (selectedRange.value.length < 2) return []
    const [partId, chapterName] = selectedRange.value
    const part = props.vocabularyData.find(p => p.part_id === partId)
    if (!part) return []
    const chapter = part.chapters.find(c => c.chapter_name === chapterName)
    return chapter ? chapter.words.filter(w => w.definition && w.definition.trim()) : []
  } else if (rangeType.value === 'wrong') {
    const list = []
    const wrongIds = wrongWordsLocal.value.map(item => item.id)
    props.vocabularyData.forEach(p => {
      p.chapters.forEach(c => {
        c.words.forEach(w => {
          if (wrongIds.includes(w.id) && w.definition && w.definition.trim()) {
            list.push(w)
          }
        })
      })
    })
    return list
  }
  return []
})

const maxAvailableQuestions = computed(() => {
  return availableWordsList.value.length
})

watch(availableWordsList, (newList) => {
  if (newList && newList.length > 0) {
    if (questionCount.value > newList.length) {
      questionCount.value = newList.length
    }
    if (questionCount.value < 1) {
      questionCount.value = Math.min(5, newList.length)
    }
  } else {
    questionCount.value = 0
  }
}, { immediate: true })

const isSetupValid = computed(() => {
  if (rangeType.value === 'chapter') {
    return selectedRange.value.length === 2 && availableWordsList.value.length > 0
  }
  if (rangeType.value === 'wrong') {
    return hasWrongWords.value && availableWordsList.value.length > 0
  }
  return availableWordsList.value.length > 0
})

// Current question data
const currentQuestion = computed(() => {
  if (currentQuestionIdx.value >= questions.value.length) return {}
  return questions.value[currentQuestionIdx.value]
})



// Shuffle helper (Fisher-Yates)
const shuffle = (array) => {
  const arr = [...array]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

// Start the Quiz
const startQuiz = () => {
  const pool = availableWordsList.value
  if (pool.length < 1) {
    ElMessage.error('測驗範圍內沒有單字，無法開始小考。')
    return
  }
  
  // Clean last results
  wrongAnswers.value = []
  score.value = 0
  currentQuestionIdx.value = 0
  
  // Pick N random words for questions
  const shuffledPool = shuffle(pool)
  const count = Math.min(questionCount.value, shuffledPool.length)
  questions.value = shuffledPool.slice(0, count)
  
  // Load options for the first question
  setupOptions()
  
  quizState.value = 'active'
}

// Set up 4 options for current question
const setupOptions = () => {
  hasAnswered.value = false
  selectedAnswerId.value = null
  
  const correctWord = currentQuestion.value
  
  // 優先尋找同章節單字作為干擾項
  let chapterCandidates = []
  let partCandidates = []
  const allWords = []
  
  for (const part of props.vocabularyData) {
    let partContainsWord = false
    let partWords = []
    
    for (const chapter of part.chapters) {
      const chapterWords = chapter.words.filter(w => w.definition && w.definition.trim())
      const containsWord = chapterWords.some(w => w.id === correctWord.id)
      
      // 收集該章節中除目前單字外的其他單字
      const otherChapterWords = chapterWords.filter(w => w.id !== correctWord.id)
      if (containsWord) {
        chapterCandidates = otherChapterWords
        partContainsWord = true
      }
      
      partWords.push(...otherChapterWords)
      
      // 同時收集全域所有單字
      allWords.push(...otherChapterWords)
    }
    
    if (partContainsWord) {
      partCandidates = partWords
    }
  }
  
  let distractors = []
  if (chapterCandidates.length >= 3) {
    // 1. 同章節單字足夠，優先使用同章節
    distractors = shuffle(chapterCandidates).slice(0, 3)
  } else if (partCandidates.length >= 3) {
    // 2. 同章節不夠，使用同 Part
    distractors = shuffle(partCandidates).slice(0, 3)
  } else {
    // 3. 都不夠，則使用全書單字
    distractors = shuffle(allWords).slice(0, 3)
  }
  
  // Create option list
  const opts = [
    { id: correctWord.id, label: 'A', definition: correctWord.definition, isCorrect: true },
    { id: distractors[0].id, label: 'B', definition: distractors[0].definition, isCorrect: false },
    { id: distractors[1].id, label: 'C', definition: distractors[1].definition, isCorrect: false },
    { id: distractors[2].id, label: 'D', definition: distractors[2].definition, isCorrect: false }
  ]
  
  // Shuffle options, then assign labels A, B, C, D
  const shuffledOpts = shuffle(opts)
  shuffledOpts.forEach((o, index) => {
    o.label = String.fromCharCode(65 + index) // A, B, C, D
  })
  
  currentOptions.value = shuffledOpts
}

// User selects an option
const selectOption = (optId) => {
  if (hasAnswered.value) return
  selectedAnswerId.value = optId
  hasAnswered.value = true
  
  const isCorrect = (optId === currentQuestion.value.id)
  
  if (isCorrect) {
    score.value++
  } else {
    // Answer is incorrect, log details for end summary
    const chosenOpt = currentOptions.value.find(o => o.id === optId)
    wrongAnswers.value.push({
      word: currentQuestion.value.word,
      definition: currentQuestion.value.definition,
      yourAnswer: chosenOpt ? `(${chosenOpt.label}) ${chosenOpt.definition}` : '無回答'
    })
    
    // Log word ID to LocalStorage wrong pool
    logWrongWord(currentQuestion.value.id)
  }
}

const getOptionClass = (optId) => {
  if (!hasAnswered.value) return ''
  
  const isCorrect = (optId === currentQuestion.value.id)
  const isSelected = (optId === selectedAnswerId.value)
  
  if (isCorrect) return 'correct'
  if (isSelected && !isCorrect) return 'wrong'
  return ''
}

const nextQuestion = () => {
  if (currentQuestionIdx.value < questions.value.length - 1) {
    currentQuestionIdx.value++
    setupOptions()
  } else {
    // End of quiz, show result screen
    quizState.value = 'result'
    // Reload local storage count
    loadWrongWordsLocal()
  }
}

// Log wrong answers to LocalStorage
const logWrongWord = (wordId) => {
  const saved = localStorage.getItem('vocabulary_wrong_words')
  let wrongList = []
  if (saved) {
    try {
      wrongList = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to parse wrong words pool', e)
    }
  }
  
  const existing = wrongList.find(item => item.id === wordId)
  if (existing) {
    existing.count = (existing.count || 1) + 1
    existing.box = 1 // Reset to Box 1 on wrong answer in quiz
    existing.timestamp = Date.now()
  } else {
    wrongList.push({ id: wordId, count: 1, box: 1, timestamp: Date.now() })
  }
  localStorage.setItem('vocabulary_wrong_words', JSON.stringify(wrongList))
  emit('update-wrong-count')
}

const restartSetup = () => {
  quizState.value = 'setup'
}

// 使用共用 TTS composable
const { speakText } = useTTS()

const loadWrongWordsLocal = () => {
  const saved = localStorage.getItem('vocabulary_wrong_words')
  if (saved) {
    try {
      wrongWordsLocal.value = JSON.parse(saved)
    } catch(e) {}
  }
}

const customColors = [
  { color: '#ef4444', percentage: 20 },
  { color: '#f59e0b', percentage: 40 },
  { color: '#eab308', percentage: 60 },
  { color: '#3b82f6', percentage: 80 },
  { color: '#10b981', percentage: 100 }
]

// 答題後按 Enter 或空白鍵可快鍵前進下一題
const handleKeyDown = (e) => {
  if (quizState.value === 'active' && hasAnswered.value) {
    const activeEl = document.activeElement
    if (activeEl && (
      activeEl.tagName === 'INPUT' || 
      activeEl.tagName === 'TEXTAREA' || 
      activeEl.isContentEditable
    )) {
      return
    }
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      nextQuestion()
    }
  }
}

onMounted(() => {
  loadWrongWordsLocal()
  if ('speechSynthesis' in window) {
    window.speechSynthesis.getVoices()
  }
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
})

watch(() => currentQuestionIdx.value, () => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
})
</script>

<style scoped>
/* 容器：與 StudyMode / ReviewMode 一致，無特殊背景 */
.quiz-container {
  width: 100%;
  margin: 0 auto;
}

/* 設定面板：左側表單 + 右側背景圖呼吸空間 */
.setup-panel {
  position: relative;
  overflow: hidden;
  min-height: 360px;
  padding: 0;
  /* 左深右透漸層，讓右半邊的 exam.jpg 清晰露出 */
  background:
    linear-gradient(
      to right,
      rgba(11, 15, 25, 0.92) 0%,
      rgba(11, 15, 25, 0.85) 10%,
      rgba(11, 15, 25, 0.45) 20%,
      rgba(11, 15, 25, 0.05) 100%
    ),
    url('/exam.jpg') center top / cover no-repeat;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  box-shadow: var(--shadow-main), 0 0 25px rgba(99, 102, 241, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 頂部霓虹線條裝飾 */
.setup-panel::before,
.result-page::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1.5px;
  background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.45), transparent);
  z-index: 2;
}

.setup-panel:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-main), var(--shadow-glow);
}

/* 表單內容限制在左側約 45% 寬 */
.setup-inner {
  padding: 32px;
  max-width: 460px;
  width: 100%;
  position: relative;
  z-index: 1;
}

@media (max-width: 767px) {
  .setup-inner {
    max-width: 100%;
    padding: 20px 16px;
  }
}

/* 進行中測驗：各子區塊獨立，不再用大面板包覆 */
.active-quiz {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setup-title {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
  color: var(--text-primary);
}

.quiz-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: fit-content;
  min-width: 280px;
}

/* 讓 El Plus radio button 在垂直排列時撐滿群組寬度 */
.quiz-radio-group :deep(.el-radio-button) {
  width: 100%;
}

/* 暗色玻璃風格（與手機版一致） */
.quiz-radio-group :deep(.el-radio-button__inner) {
  width: 100%;
  display: block;
  border-radius: 10px !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  background: rgba(30, 41, 59, 0.4) !important;
  color: var(--text-muted) !important;
  padding: 12px 16px !important;
  text-align: center;
  box-shadow: none !important;
  transition: all 0.2s ease !important;
}

.quiz-radio-group :deep(.el-radio-button__inner:hover) {
  background: rgba(99, 102, 241, 0.1) !important;
  border-color: rgba(99, 102, 241, 0.3) !important;
  color: var(--text-primary) !important;
}

/* 選中狀態 */
.quiz-radio-group :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: rgba(99, 102, 241, 0.15) !important;
  border-color: var(--primary-color) !important;
  color: var(--text-primary) !important;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.3) !important;
}

/* disabled 狀態 */
.quiz-radio-group :deep(.el-radio-button.is-disabled .el-radio-button__inner) {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}

.max-hint {
  margin-left: 12px;
  font-size: 13px;
}

.quiz-header-bar {
  padding: 16px 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-muted);
}

.question-box {
  padding: 32px 24px;
  text-align: center;
}

.question-hint {
  font-size: 14px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.question-word {
  font-family: 'Outfit', sans-serif;
  font-size: 38px;
  font-weight: 800;
  color: var(--text-primary);
  margin-top: 10px;
  margin-bottom: 10px;
}

.question-phonetic {
  font-size: 16px;
  color: var(--text-highlight);
  font-style: italic;
  display: inline-flex;
  align-items: center;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50% !important;
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  color: var(--text-muted) !important;
  font-weight: 700;
  margin-right: 14px;
  flex-shrink: 0;
  line-height: 1 !important;
}

.option-text {
  font-size: 16px;
}

.quiz-footer {
  display: flex;
  justify-content: flex-end;
}

.next-btn {
  height: 48px !important;
  font-size: 16px !important;
  padding: 0 28px !important;
}

/* 結果頁面：不使用背景圖以求畫面乾淨與一致 */
.result-page {
  position: relative;
  overflow: hidden;
  padding: 40px 32px;
  text-align: center;
  background: linear-gradient(135deg, rgba(22, 28, 45, 0.75) 0%, rgba(15, 23, 42, 0.9) 100%);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  box-shadow: var(--shadow-main), 0 0 25px rgba(99, 102, 241, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.result-page:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-main), var(--shadow-glow);
}

.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.result-score-circle {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  border: 4px solid var(--primary-color);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  background: rgba(99, 102, 241, 0.05);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
}

.score-number {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
}

.score-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.result-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
}

.result-desc {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0;
}

.wrong-summary {
  text-align: left;
  margin-bottom: 32px;
}

.summary-title {
  font-size: 16px;
  margin-bottom: 12px;
}

.wrong-word-link {
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.wrong-word-link:hover {
  color: var(--primary-color);
}

.perfect-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.perfect-score h4 {
  font-size: 20px;
  margin: 0;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.quiz-range-selects {
  display: flex;
  gap: 12px;
  width: 100%;
}

@media (max-width: 767px) {
  .quiz-range-selects {
    flex-direction: column !important;
    gap: 10px !important;
  }

  .setup-panel {
    padding: 20px 16px !important;
    border-radius: 16px !important;
    background:
      linear-gradient(rgba(22, 28, 45, 0.55), rgba(22, 28, 45, 0.55)),
      url('/exam.jpg') 20% 35% / 240% 100% no-repeat fixed !important;
  }
  
  .setup-title {
    font-size: 18px !important;
    margin-bottom: 16px !important;
  }
  
  .result-page {
    padding: 24px 16px !important;
    border-radius: 16px !important;
  }
  
  .result-score-circle {
    width: 100px !important;
    height: 100px !important;
  }
  
  .score-number {
    font-size: 28px !important;
  }
  
  .result-actions {
    flex-direction: column !important;
    gap: 12px !important;
    width: 100% !important;
  }
  
  .result-actions .el-button {
    width: 100% !important;
    margin-left: 0 !important;
  }

  .quiz-footer {
    width: 100% !important;
  }

  .quiz-footer .next-btn {
    width: 100% !important;
  }
}
</style>

