<template>
  <div class="study-container">
    <!-- Chapter Selector & Fuzzy Search -->
    <div class="unified-bar glass-container">
      <div class="selector-group">
        <div class="selector-label">
          <el-icon><Notebook /></el-icon>
          <span>學習範圍：</span>
        </div>
        <!-- 學習範圍選擇：雙下拉選單（電腦版並排、手機版自動換行/垂直堆疊） -->
        <div class="study-range-selects">
          <el-select
            v-model="selectedPartId"
            placeholder="選擇 Part"
            style="width: 320px;"
            @change="handlePartSelectChange"
          >
            <template #prefix>
              <el-icon><Compass /></el-icon>
            </template>
            <el-option
              v-for="p in props.vocabularyData"
              :key="p.part_id"
              :label="p.part_name"
              :value="p.part_id"
            />
          </el-select>
          <el-select
            v-model="selectedChapterName"
            placeholder="選擇章節"
            :disabled="!selectedPartId"
            style="width: 380px;"
            @change="handleChapterSelectChange"
          >
            <template #prefix>
              <el-icon><Collection /></el-icon>
            </template>
            <el-option
              v-for="ch in availableChapters"
              :key="ch"
              :label="ch"
              :value="ch"
            />
          </el-select>
        </div>
      </div>

      <div class="search-group">
        <el-autocomplete
          v-model="searchQuery"
          :fetch-suggestions="querySearch"
          placeholder="🔍 搜尋單字或中文釋義..."
          clearable
          value-key="word"
          @select="handleSearchSelect"
        >
          <template #default="{ item }">
            <div class="search-opt-row" style="display: flex; justify-content: space-between;">
              <span class="search-opt-word">{{ item.word }}</span>
              <span class="search-opt-def">{{ item.definition }}</span>
            </div>
          </template>
        </el-autocomplete>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!currentWords.length" class="empty-state glass-container">
      <el-empty description="此章節沒有單字或請先選擇範圍" />
    </div>

    <!-- Study Cards Interface -->
    <div v-else class="cards-layout">
      <!-- Wrap the main card content and examples panel in transition -->
      <transition name="fade-slide" mode="out-in">
        <!-- 1. Skeleton Screen when loading -->
        <div v-if="isLoading" class="skeleton-layout" style="width: 100%; display: flex; flex-direction: column; gap: 20px;">
          <!-- Skeleton Card -->
          <div class="word-info-card glow-card" style="padding: 32px; min-height: 320px; display: flex; flex-direction: column; gap: 24px;">
            <div class="card-header-row" style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
              <div class="skeleton-pulse skeleton-title" style="margin-bottom: 0; height: 32px; width: 140px;"></div>
              <div class="skeleton-pulse skeleton-phonetic" style="margin-bottom: 0; width: 100px; height: 24px;"></div>
            </div>
            <div class="card-body-section" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
              <div>
                <div class="skeleton-pulse" style="width: 60px; height: 12px; margin-bottom: 12px;"></div>
                <div class="skeleton-pulse" style="height: 60px; width: 100%;"></div>
              </div>
              <div>
                <div class="skeleton-pulse" style="width: 60px; height: 12px; margin-bottom: 12px;"></div>
                <div class="skeleton-pulse" style="height: 60px; width: 100%;"></div>
              </div>
            </div>
          </div>

          <!-- Skeleton Examples Panel -->
          <div class="examples-panel glass-container" style="padding: 24px; min-height: 180px; display: flex; flex-direction: column; gap: 16px;">
            <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 16px;">
              <div class="skeleton-pulse" style="width: 120px; height: 24px; margin: 0;"></div>
              <div style="display: flex; gap: 8px;">
                <div class="skeleton-pulse" style="width: 90px; height: 32px; border-radius: 8px;"></div>
                <div class="skeleton-pulse" style="width: 90px; height: 32px; border-radius: 8px;"></div>
              </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 8px;">
              <div class="skeleton-pulse" style="height: 20px; width: 90%;"></div>
              <div class="skeleton-pulse" style="height: 16px; width: 60%;"></div>
            </div>
          </div>
        </div>

        <!-- 2. Actual Content when loaded -->
        <div v-else class="content-wrapper-layout" style="width: 100%; display: flex; flex-direction: column; gap: 20px;">
          <!-- Word Card (Unified, no flip) -->
          <div 
            class="word-info-card glow-card swipe-transition"
            @touchstart="handleTouchStart"
            @touchend="handleTouchEnd"
          >
            <!-- Header row (Word, Phonetic, Structure) -->
            <div class="card-header-row">
              <div class="card-word-title">{{ currentWord.word }}</div>
              <div class="card-word-phonetic">{{ currentWord.phonetic }}</div>
              <div v-if="currentWord.structure" class="card-word-structure">
                {{ currentWord.structure }}
              </div>
              <!-- 單字發音按鈕移入上半卡片 -->
              <el-button
                class="btn-accent-glass card-speak-btn"
                :icon="Headset"
                @click.stop="speakText(currentWord.word)"
              >
                單字發音
              </el-button>
            </div>

            <div class="card-body-section">
              <!-- Main definition -->
              <div class="definition-block">
                <span class="section-label">中文釋義</span>
                <div class="definition-text">{{ currentWord.definition }}</div>
              </div>

              <!-- Literal meaning / Root Analysis -->
              <div v-if="currentWord.literal_meaning" class="literal-block">
                <span class="section-label">字源分析</span>
                <div class="literal-text">{{ currentWord.literal_meaning }}</div>
              </div>
            </div>

            <!-- Synonyms & Derivatives Row -->
            <div 
              v-if="(currentWord.derivatives && currentWord.derivatives.length) || (currentWord.synonyms && currentWord.synonyms.length)" 
              class="card-footer-section"
            >
              <!-- Derivatives -->
              <div v-if="currentWord.derivatives && currentWord.derivatives.length" class="derivatives-col">
                <span class="section-label">衍生詞</span>
                <div class="deriv-tags-row">
                  <el-tag
                    v-for="d in currentWord.derivatives"
                    :key="d.word"
                    type="info"
                    effect="dark"
                    class="custom-deriv-tag"
                  >
                    <strong>{{ d.word }}</strong> ({{ d.meaning }})
                  </el-tag>
                </div>
              </div>

              <!-- Synonyms -->
              <div v-if="currentWord.synonyms && currentWord.synonyms.length" class="synonyms-col">
                <span class="section-label">同義詞</span>
                <div class="syn-tags-row">
                  <el-tag 
                    v-for="s in currentWord.synonyms" 
                    :key="s" 
                    type="success" 
                    effect="plain"
                    class="custom-syn-tag"
                  >
                    {{ s }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- TTS Speak and Example Area -->
          <div class="examples-panel glass-container">
            <div class="panel-header">
              <div class="word-header-info">
                <span class="word-name">{{ currentWord.word }}</span>
                <span class="word-index-tag">進度: {{ currentWordIndex + 1 }} / {{ currentWords.length }}</span>
              </div>
              <!-- 例句發音按鈕 -->
              <div class="audio-buttons-row">
                <el-button
                  v-if="currentWord.examples && currentWord.examples.length"
                  class="btn-secondary-glass"
                  :icon="VideoPlay"
                  @click.stop="speakText(currentWord.examples.map(ex => ex.en).join('. '))"
                >
                  例句發音
                </el-button>
              </div>
            </div>

            <!-- Examples List -->
            <div v-if="currentWord.examples && currentWord.examples.length" class="examples-list">
              <div v-for="(ex, idx) in currentWord.examples" :key="idx" class="example-item">
                <div class="ex-en">{{ ex.en }}</div>
                <div class="ex-zh">{{ ex.zh }}</div>
              </div>
            </div>
            <div v-else class="no-examples text-muted">
              無提供此單字之課本例句
            </div>
          </div>
        </div>
      </transition>

      <!-- Navigation Bar -->
      <div class="navigation-bar">
        <el-button
          :disabled="currentWordIndex === 0"
          class="btn-secondary-glass nav-btn-prev"
          @click="prevWord"
        >
          <el-icon><ArrowLeft /></el-icon> 上一個單字
        </el-button>
        
        <el-button
          :disabled="currentWordIndex === currentWords.length - 1"
          class="btn-primary-neon nav-btn-next"
          @click="nextWord"
        >
          下一個單字 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Headset, VideoPlay, Notebook, ArrowLeft, ArrowRight, Compass, Collection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useTTS } from '../composables/useTTS.js'

const props = defineProps({
  vocabularyData: {
    type: Array,
    required: true
  }
})

// Ranges and indexing
const selectedRange = ref([]) // [part_id, chapter_name]
const currentWordIndex = ref(0)

// Two separate selects helper for mobile
const selectedPartId = ref('')
const selectedChapterName = ref('')
const isLoading = ref(false)

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

// Handlers for manual selection change
const handlePartSelectChange = (val) => {
  selectedPartId.value = val
  const part = props.vocabularyData.find(p => p.part_id === val)
  if (part && part.chapters.length > 0) {
    selectedChapterName.value = part.chapters[0].chapter_name
    selectedRange.value = [val, selectedChapterName.value]
    handleRangeChange()
  }
}

const handleChapterSelectChange = (val) => {
  selectedChapterName.value = val
  if (selectedPartId.value && val) {
    selectedRange.value = [selectedPartId.value, val]
    handleRangeChange()
  }
}

// Autocomplete search
const searchQuery = ref('')
const querySearch = (queryString, cb) => {
  const results = queryString
    ? allWordsFlat.value.filter(item => {
        return (
          item.word.toLowerCase().includes(queryString.toLowerCase()) ||
          item.definition.toLowerCase().includes(queryString.toLowerCase())
        )
      })
    : []
  cb(results.slice(0, 20))
}
const handleSearchSelect = (item) => {
  handleSearchChange(item)
  searchQuery.value = ''
}

// Flatten words for fuzzy search lookup
const allWordsFlat = computed(() => {
  const list = []
  props.vocabularyData.forEach(part => {
    part.chapters.forEach(ch => {
      ch.words.forEach(w => {
        list.push({
          id: w.id,
          word: w.word,
          definition: w.definition,
          partId: part.part_id,
          chapterName: ch.chapter_name
        })
      })
    })
  })
  return list
})

const handleSearchChange = (item) => {
  if (!item) return
  selectedRange.value = [item.partId, item.chapterName]
  setTimeout(() => {
    const idx = currentWords.value.findIndex(w => w.id === item.id)
    if (idx !== -1) {
      currentWordIndex.value = idx
      saveProgress()
    }
  }, 50)
}



// Get current words list in selected chapter
const currentWords = computed(() => {
  if (selectedRange.value.length < 2) return []
  const [partId, chapterName] = selectedRange.value
  const part = props.vocabularyData.find(p => p.part_id === partId)
  if (!part) return []
  const chapter = part.chapters.find(c => c.chapter_name === chapterName)
  return chapter ? chapter.words : []
})

// Current active word object
const currentWord = computed(() => {
  if (currentWordIndex.value >= currentWords.value.length) return {}
  return currentWords.value[currentWordIndex.value]
})

// Watch currentWord changes to trigger automatic loading animation
watch(() => currentWord.value, (newWord) => {
  if (newWord && newWord.word) {
    isLoading.value = true
    setTimeout(() => {
      isLoading.value = false
    }, 200)
  }
})

// Reset word index
const handleRangeChange = () => {
  currentWordIndex.value = 0
  saveProgress()
}

const prevWord = () => {
  if (currentWordIndex.value > 0) {
    currentWordIndex.value--
    saveProgress()
  }
}

const nextWord = () => {
  if (currentWordIndex.value < currentWords.value.length - 1) {
    currentWordIndex.value++
    saveProgress()
  }
}

// 使用共用 TTS composable
const { speakText } = useTTS()

// Progress memory functions
const saveProgress = () => {
  if (selectedRange.value.length === 2) {
    const [partId, chapterName] = selectedRange.value
    const progress = {
      partId,
      chapterName,
      wordIndex: currentWordIndex.value
    }
    localStorage.setItem('vocabulary_study_progress', JSON.stringify(progress))
  }
}

const loadProgress = () => {
  const saved = localStorage.getItem('vocabulary_study_progress')
  if (saved) {
    try {
      const { partId, chapterName, wordIndex } = JSON.parse(saved)
      const part = props.vocabularyData.find(p => p.part_id === partId)
      if (part) {
        const chapter = part.chapters.find(c => c.chapter_name === chapterName)
        if (chapter && chapter.words.length > wordIndex) {
          selectedRange.value = [partId, chapterName]
          currentWordIndex.value = wordIndex
          ElMessage.success('已自動恢復您上次的學習進度。')
          return
        }
      }
    } catch (e) {
      console.error('Failed to parse study progress', e)
    }
  }
  
  if (props.vocabularyData.length > 0 && props.vocabularyData[0].chapters.length > 0) {
    const firstPartId = props.vocabularyData[0].part_id
    const firstChapterName = props.vocabularyData[0].chapters[0].chapter_name
    selectedRange.value = [firstPartId, firstChapterName]
    currentWordIndex.value = 0
  }
}

const touchStartX = ref(0)
const touchEndX = ref(0)

const handleTouchStart = (e) => {
  touchStartX.value = e.touches[0].clientX
}

const handleTouchEnd = (e) => {
  touchEndX.value = e.changedTouches[0].clientX
  handleSwipe()
}

const handleSwipe = () => {
  const diffX = touchEndX.value - touchStartX.value
  const threshold = 60
  if (Math.abs(diffX) > threshold) {
    if (diffX > 0) {
      prevWord()
    } else {
      nextWord()
    }
  }
}

const handleKeyboard = (event) => {
  if (currentWords.value.length === 0) return
  if (event.key === 'ArrowLeft') {
    prevWord()
  } else if (event.key === 'ArrowRight') {
    nextWord()
  }
}

onMounted(() => {
  loadProgress()
  // 預先載入語音清單（非同步，讓 TTS fallback 更快找到英語語音）
  if ('speechSynthesis' in window) {
    window.speechSynthesis.getVoices()
  }
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
})

watch(() => currentWordIndex.value, () => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
})
</script>

<style scoped>
.study-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.selector-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.selector-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.cards-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* Unified Info Card Styling */
.word-info-card {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  border-radius: 20px;
}

.card-header-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

/* 發音按鈕靠右貼齊卡片邊緣 */
.card-speak-btn {
  margin-left: auto;
}

.card-word-title {
  font-family: 'Outfit', sans-serif;
  font-size: 40px;
  font-weight: 800;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}

.card-word-phonetic {
  font-size: 20px;
  color: var(--text-highlight);
  font-style: italic;
}

.card-word-structure {
  font-family: var(--font-sans);
  font-size: 14px;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  letter-spacing: 0.5px;
}

.card-body-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .card-body-section {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.section-label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.definition-text {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-color);
}

.literal-text {
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary);
}

.card-footer-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

@media (max-width: 768px) {
  .card-footer-section {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.deriv-tags-row, .syn-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.custom-deriv-tag {
  border-color: rgba(255, 255, 255, 0.1) !important;
  background-color: rgba(255, 255, 255, 0.04) !important;
  color: var(--text-primary) !important;
}

.custom-syn-tag {
  background-color: rgba(16, 185, 129, 0.1) !important;
  border-color: rgba(16, 185, 129, 0.2) !important;
  color: #a7f3d0 !important;
}

/* Examples Panel styling */
.examples-panel {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

.word-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.word-name {
  font-family: 'Outfit', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.word-index-tag {
  font-size: 13px;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 8px;
  border-radius: 6px;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.example-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
}

.ex-bullet-audio {
  color: var(--accent-color);
  margin-right: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(6, 182, 212, 0.1);
  transition: all 0.2s ease;
  vertical-align: middle;
}

.ex-bullet-audio:hover {
  background: var(--accent-color);
  color: #ffffff;
  transform: scale(1.15);
}

.ex-en {
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary);
}

.ex-zh {
  font-size: 14px;
  color: var(--text-muted);
  padding-left: 34px;
}

/* Navigation control bar */
.navigation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  gap: 16px;
}

.nav-btn-prev {
  flex: 1;
}

.nav-btn-next {
  flex: 1;
}

.audio-buttons-row {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .selector-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  .selector-group, .search-group {
    width: 100%;
  }
  .el-cascader, .el-select {
    width: 100% !important;
  }
  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  .study-range-selects {
    flex-direction: column !important;
    gap: 8px !important;
    width: 100% !important;
  }
  .study-range-selects .el-select {
    width: 100% !important;
  }
}

.study-range-selects {
  display: flex;
  gap: 10px;
  align-items: center;
}

.selector-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-group {
  display: flex;
  align-items: center;
}

.search-opt-word {
  float: left;
  font-weight: 600;
  color: var(--text-primary);
}

.search-opt-def {
  float: right;
  color: var(--text-muted);
  font-size: 13px;
  margin-left: 8px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
