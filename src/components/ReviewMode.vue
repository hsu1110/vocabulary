<template>
  <div class="review-container">
    <!-- Empty State -->
    <div v-if="!wrongWordsDetails.length" class="empty-state glass-container">
      <el-empty description="錯字本空空如也！繼續保持！">
        <el-button type="primary" @click="$emit('switch-tab', 'study')">
          前往背單字
        </el-button>
      </el-empty>
    </div>

    <!-- Review Content -->
    <div v-else class="review-content">
      <!-- Toolbar -->
      <div class="unified-bar glass-container">
        <div class="toolbar-info">
          <el-icon><Warning /></el-icon>
          <span>目前共有 <strong>{{ wrongWordsDetails.length }}</strong> 個答錯的單字</span>
        </div>
        <div class="toolbar-actions">
          <el-radio-group v-model="viewMode" size="default">
            <el-radio-button value="list">清單列表</el-radio-button>
            <el-radio-button value="cards">卡片複習</el-radio-button>
          </el-radio-group>
          <el-button type="danger" plain size="default" @click="clearAllWrong">
            清空錯字本
          </el-button>
        </div>
      </div>

      <!-- 1. List View Mode (電腦版) -->
      <div v-if="viewMode === 'list'" class="list-view glow-card desktop-only" style="padding: 16px; border-radius: 20px;">
        <el-table :data="wrongWordsDetails" style="width: 100%; background: transparent;">
          <el-table-column prop="word" label="單字" width="160">
            <template #default="scope">
              <span class="word-text" @click="speakText(scope.row.word)">
                {{ scope.row.word }} <el-icon><Headset /></el-icon>
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="phonetic" label="音標" width="160" />
          <el-table-column prop="definition" label="中文解釋" />
          <el-table-column prop="box" label="學習掌握度" width="180" align="center">
            <template #default="scope">
              <div class="mastery-progress-wrapper">
                <div class="progress-track">
                  <div 
                    class="progress-bar-fill" 
                    :class="scope.row.box === 2 ? 'warning' : (scope.row.box >= 3 ? 'success' : 'danger')" 
                    :style="{ width: scope.row.box === 2 ? '66%' : (scope.row.box >= 3 ? '100%' : '33%') }"
                  ></div>
                </div>
                <span 
                  class="progress-text-label" 
                  :class="scope.row.box === 2 ? 'text-warning' : (scope.row.box >= 3 ? 'text-success' : 'text-danger')"
                >
                  {{ scope.row.box === 2 ? '已熟練 (Box 2)' : (scope.row.box >= 3 ? '已精通 (Box 3)' : '初學 (Box 1)') }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="錯誤次數" width="120" align="center">
            <template #default="scope">
              <span class="error-badge-pill" :class="{ 'high-error': scope.row.count >= 3 }">
                <el-icon style="margin-right: 4px; vertical-align: middle;"><Warning /></el-icon>
                {{ scope.row.count }} 次
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="scope">
              <el-button
                class="btn-success-glass"
                size="small"
                style="padding: 4px 12px; font-size: 12px; height: auto; border-radius: 8px;"
                @click="removeWrongWord(scope.row.id)"
              >
                直接移出
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 1. List View Mode (手機版卡片列表) -->
      <div v-if="viewMode === 'list'" class="mobile-list-view mobile-only">
        <div 
          v-for="item in wrongWordsDetails" 
          :key="item.id" 
          class="mobile-word-card glow-card"
        >
          <div class="mobile-word-title">
            <span @click="speakText(item.word)" style="cursor: pointer;">
              {{ item.word }} <el-icon style="margin-left: 4px; vertical-align: middle;"><Headset /></el-icon>
            </span>
            <el-button
              class="btn-success-glass"
              size="small"
              style="padding: 4px 10px; font-size: 12px; height: auto; border-radius: 8px;"
              @click="removeWrongWord(item.id)"
            >
              直接移出
            </el-button>
          </div>
          <div class="card-word-phonetic" style="font-size: 14px; margin: 4px 0;">{{ item.phonetic }}</div>
          <div class="mobile-word-def">{{ item.definition }}</div>
          
          <div class="mobile-word-meta">
            <div class="mastery-indicator-new">
              <span class="meta-label">掌握度</span>
              <div class="mastery-progress-wrapper" style="width: 110px;">
                <div class="progress-track" style="height: 6px;">
                  <div 
                    class="progress-bar-fill" 
                    :class="item.box === 2 ? 'warning' : (item.box >= 3 ? 'success' : 'danger')" 
                    :style="{ width: item.box === 2 ? '66%' : (item.box >= 3 ? '100%' : '33%') }"
                  ></div>
                </div>
                <span 
                  class="progress-text-label" 
                  :class="item.box === 2 ? 'text-warning' : (item.box >= 3 ? 'text-success' : 'text-danger')"
                  style="font-size: 11px; margin-top: 2px;"
                >
                  {{ item.box === 2 ? '已熟練 (Box 2)' : (item.box >= 3 ? '已精通 (Box 3)' : '初學 (Box 1)') }}
                </span>
              </div>
            </div>
            
            <div class="error-indicator-new">
              <span class="meta-label">錯誤次數</span>
              <span class="error-badge-pill" :class="{ 'high-error': item.count >= 3 }" style="font-size: 11px; padding: 4px 8px;">
                <el-icon style="margin-right: 3px; vertical-align: middle;"><Warning /></el-icon>
                {{ item.count }} 次
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. Flashcard View Mode -->
      <div v-else-if="viewMode === 'cards'" class="cards-view">
        <div class="content-wrapper-layout" style="width: 100%; display: flex; flex-direction: column; gap: 20px;">
          <!-- Word Card (Unified, no flip) -->
          <div 
            class="word-info-card glow-card"
            @touchstart="handleTouchStart"
            @touchend="handleTouchEnd"
          >
            <!-- Header row (Unified style with StudyMode) -->
            <div class="card-header-row">
              <div class="card-word-title">
                {{ currentWord.word }}
              </div>
              <div class="card-word-phonetic">{{ currentWord.phonetic }}</div>
              <div v-if="currentWord.structure" class="card-word-structure">
                {{ currentWord.structure }}
              </div>
              <div class="card-meta-tags" style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
                <el-tag
                  :type="currentWord.box === 2 ? 'warning' : (currentWord.box >= 3 ? 'success' : 'danger')"
                  effect="dark"
                  class="box-tag"
                  style="border-radius: 12px; padding: 4px 10px; height: auto;"
                >
                  掌握度: {{ currentWord.box === 2 ? '66%' : (currentWord.box >= 3 ? '100%' : '33%') }} (Box {{ currentWord.box || 1 }})
                </el-tag>
                <span class="card-badge" style="position: static; font-size: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); padding: 4px 10px; border-radius: 12px; color: var(--text-muted);">
                  {{ currentWordIndex + 1 }} / {{ wrongWordsDetails.length }}
                </span>
              </div>
            </div>

            <!-- Body -->
            <div class="card-body-section">
              <div class="definition-block">
                <span class="section-label">中文釋義</span>
                <div class="definition-text">{{ currentWord.definition }}</div>
              </div>

              <div v-if="currentWord.literal_meaning" class="literal-block">
                <span class="section-label">字源分析</span>
                <div class="literal-text">{{ currentWord.literal_meaning }}</div>
              </div>
            </div>

            <!-- Footer (Synonyms / Derivatives) -->
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

          <!-- Examples & Audio Pronunciation Panel (Unified style with StudyMode) -->
          <div class="examples-panel glass-container">
            <div class="panel-header">
              <div class="word-header-info">
                <span class="word-name">{{ currentWord.word }}</span>
                <span class="word-index-tag">進度: {{ currentWordIndex + 1 }} / {{ wrongWordsDetails.length }}</span>
              </div>
              <!-- Audio TTS Buttons -->
              <div class="audio-buttons-row">
                <el-button
                  class="btn-accent-glass"
                  :icon="Headset"
                  @click.stop="speakText(currentWord.word)"
                >
                  單字發音
                </el-button>
                <el-button
                  v-if="currentWord.examples && currentWord.examples.length"
                  class="btn-secondary-glass"
                  :icon="VideoPlay"
                  @click.stop="speakText(currentWord.examples.map(ex => ex.en).join(' '))"
                >
                  例句發音
                </el-button>
              </div>
            </div>

            <!-- Examples List -->
            <div v-if="currentWord.examples && currentWord.examples.length" class="examples-list">
              <div v-for="(ex, idx) in currentWord.examples" :key="idx" class="example-item">
                <div class="ex-en" style="display: flex; align-items: flex-start;">
                  <span class="ex-bullet-audio" @click.stop="speakText(ex.en)" title="播放此例句">
                    <el-icon><VideoPlay /></el-icon>
                  </span>
                  <span class="ex-text" @click.stop="speakText(ex.en)" title="播放此例句" style="cursor: pointer; flex: 1;">{{ ex.en }}</span>
                </div>
                <div class="ex-zh">{{ ex.zh }}</div>
              </div>
            </div>
            <div v-else class="no-examples text-muted">
              無提供此單字之課本例句
            </div>
          </div>
        </div>

        <!-- Navigation / Action for Cards (電腦版) -->
        <div class="card-controls-row desktop-only" style="justify-content: center; gap: 24px; margin-top: 16px;">
          <el-button
            :icon="Close"
            class="btn-danger-glass nav-btn-wrong"
            style="min-width: 180px; height: 48px;"
            @click="rateWord(currentWord.id, false)"
          >
            忘記了 (降為 Box 1)
          </el-button>
          
          <el-button
            :icon="Check"
            class="btn-success-glass nav-btn-correct"
            style="min-width: 180px; height: 48px;"
            @click="rateWord(currentWord.id, true)"
          >
            記住了 (+1 箱)
          </el-button>
        </div>

        <!-- Navigation Bar (電腦版 - 與背單字一致) -->
        <div class="navigation-bar desktop-only" style="margin-top: 16px;">
          <el-button
            :disabled="currentWordIndex === 0"
            class="btn-secondary-glass nav-btn-prev"
            @click="prevCard"
          >
            <el-icon><ArrowLeft /></el-icon> 上一個單字
          </el-button>
          
          <el-button
            :disabled="currentWordIndex === wrongWordsDetails.length - 1"
            class="btn-primary-neon nav-btn-next"
            @click="nextCard"
          >
            下一個單字 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>

        <!-- Navigation / Action for Cards (手機版) -->
        <div class="mobile-controls-grid mobile-only" style="display: flex; gap: 8px; width: 100%; margin-top: 16px;">
          <el-button
            :icon="Close"
            class="btn-danger-glass"
            style="flex: 1; height: 48px; font-weight: 600;"
            @click="rateWord(currentWord.id, false)"
          >
            忘記了
          </el-button>
          <el-button
            :icon="Check"
            class="btn-success-glass"
            style="flex: 1; height: 48px; font-weight: 600;"
            @click="rateWord(currentWord.id, true)"
          >
            記住了
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Warning, Headset, ArrowLeft, ArrowRight, Check, Close, VideoPlay } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useTTS } from '../composables/useTTS.js'

const props = defineProps({
  vocabularyData: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['switch-tab', 'update-wrong-count'])

// 檢視模式：'list'（列表）或 'cards'（卡片）
const viewMode = ref('list')

// 卡片檢視狀態
const currentWordIndex = ref(0)

// 從 localStorage 載入的錯字本本地複本
const wrongWordsList = ref([])

// 透過比對錯字 ID 與 vocabularyData 載入詳細錯字內容
const wrongWordsDetails = computed(() => {
  const list = []
  const wrongMap = new Map()
  wrongWordsList.value.forEach(item => {
    wrongMap.set(item.id, item)
  })
  
  props.vocabularyData.forEach(p => {
    p.chapters.forEach(c => {
      c.words.forEach(w => {
        if (wrongMap.has(w.id)) {
          const item = wrongMap.get(w.id)
          list.push({
            ...w,
            count: item.count || 1,
            box: item.box || 1,
            timestamp: item.timestamp
          })
        }
      })
    })
  })
  
  return list.sort((a, b) => {
    if (a.box !== b.box) return a.box - b.box // Box 1 優先，再來是 2，最後是 3
    if (b.count !== a.count) return b.count - a.count
    return b.timestamp - a.timestamp
  })
})

const currentWord = computed(() => {
  if (currentWordIndex.value >= wrongWordsDetails.value.length) return {}
  return wrongWordsDetails.value[currentWordIndex.value]
})

// 從 LocalStorage 載入錯字清單
const loadWrongWords = () => {
  const saved = localStorage.getItem('vocabulary_wrong_words')
  if (saved) {
    try {
      wrongWordsList.value = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to parse wrong words pool', e)
    }
  } else {
    wrongWordsList.value = []
  }
}

// Remove a single word from wrong pool
const removeWrongWord = (wordId) => {
  const updated = wrongWordsList.value.filter(item => item.id !== wordId)
  wrongWordsList.value = updated
  localStorage.setItem('vocabulary_wrong_words', JSON.stringify(updated))
  emit('update-wrong-count')
  ElMessage.success('已將該單字移出錯字本。')
  
  if (currentWordIndex.value >= updated.length && currentWordIndex.value > 0) {
    currentWordIndex.value = updated.length - 1
  }
}



const rateWord = (wordId, isCorrect) => {
  let updated = [...wrongWordsList.value]
  const idx = updated.findIndex(item => item.id === wordId)
  if (idx === -1) return

  const item = updated[idx]
  let wordRemoved = false

  if (isCorrect) {
    const currentBox = item.box || 1
    if (currentBox >= 3) {
      // 已精通，畢業移出錯字本
      updated.splice(idx, 1)
      wordRemoved = true
      ElMessage.success(`🎉 恭喜！「${currentWord.value.word}」已熟記並畢業，自動移出錯字本！`)
    } else {
      item.box = currentBox + 1
      item.timestamp = Date.now()
      ElMessage.success(`記住了！「${currentWord.value.word}」已晉升至 Box ${item.box}`)
    }
  } else {
    item.box = 1
    item.count = (item.count || 1) + 1
    item.timestamp = Date.now()
    ElMessage.warning(`忘記了！「${currentWord.value.word}」已退回 Box 1`)
  }

  wrongWordsList.value = updated
  localStorage.setItem('vocabulary_wrong_words', JSON.stringify(updated))
  emit('update-wrong-count')

  // 評分後自動前進到下一張
  if (updated.length === 0) {
    currentWordIndex.value = 0
  } else if (wordRemoved) {
    // 單字移出後，splice 已讓後續單字前移，index 不越界則不需調整
    if (currentWordIndex.value >= updated.length) {
      currentWordIndex.value = updated.length - 1
    }
  } else {
    // 正常評分，跳到下一張；已到最後則回到第一張
    const nextIdx = currentWordIndex.value + 1
    currentWordIndex.value = nextIdx < updated.length ? nextIdx : 0
  }
}

const clearAllWrong = () => {
  ElMessageBox.confirm(
    '確定要清空所有的錯字紀錄嗎？清空後將無法恢復。',
    '提示',
    {
      confirmButtonText: '確定清空',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    wrongWordsList.value = []
    localStorage.removeItem('vocabulary_wrong_words')
    emit('update-wrong-count')
    ElMessage.success('已成功清空錯字本。')
  }).catch(() => {})
}

// 使用共用 TTS composable
const { speakText } = useTTS()

// 卡片切換導覽
const prevCard = () => {
  if (currentWordIndex.value > 0) {
    currentWordIndex.value--
  }
}

const nextCard = () => {
  if (currentWordIndex.value < wrongWordsDetails.value.length - 1) {
    currentWordIndex.value++
  }
}

// Touch swipe gestures for mobile card review
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
  const swipeThreshold = 50
  const diff = touchEndX.value - touchStartX.value
  if (Math.abs(diff) > swipeThreshold) {
    if (diff > 0) {
      prevCard()
    } else {
      nextCard()
    }
  }
}

const handleKeyDown = (e) => {
  if (viewMode.value === 'cards') {
    if (e.key === 'ArrowLeft') {
      prevCard()
    } else if (e.key === 'ArrowRight') {
      nextCard()
    }
  }
}

onMounted(() => {
  loadWrongWords()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.review-container {
  width: 100%;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.review-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.toolbar-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
}

.toolbar-info strong {
  color: var(--primary-color);
  font-size: 18px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.list-view {
  padding: 12px;
}

.word-text {
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.word-text:hover {
  color: var(--primary-color);
}

/* Cards Review Mode styling */
.cards-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* Unified Card (matching StudyMode) */
.word-info-card {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  border-radius: 20px;
  width: 100%;
  box-sizing: border-box;
}

.card-header-row {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 16px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
  position: relative;
}

.card-badge {
  position: absolute;
  top: 0px;
  right: 0px;
  font-size: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 4px 10px;
  border-radius: 12px;
  color: var(--danger);
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

/* Card Controls */
.card-controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 12px;
}

.nav-btn-prev {
  flex: 1;
}

.nav-btn-wrong {
  flex: 1.5;
}

.nav-btn-correct {
  flex: 1.5;
}

.nav-btn-next {
  flex: 1.2;
}

.card-badge-group {
  position: absolute;
  top: -8px;
  right: 0px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.card-badge {
  position: static !important;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  padding: 4px 10px;
  border-radius: 12px;
  color: var(--text-muted);
}

.box-tag {
  font-size: 12px;
  border-radius: 12px;
  padding: 4px 10px;
}

.speak-inline-btn {
  margin-left: 12px;
  vertical-align: middle;
}

/* Mobile card list styling */
.mobile-word-card {
  padding: 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-main);
  transition: all 0.25s ease;
}

.mobile-word-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: 'Outfit', sans-serif;
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  padding-bottom: 8px;
}

.mobile-word-def {
  font-size: 16px;
  font-weight: 600;
  color: var(--accent-color);
  margin-top: 4px;
}

.mobile-word-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.mastery-indicator {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pill-group {
  display: flex;
  gap: 4px;
}

.indicator-pill {
  width: 20px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  transition: all 0.3s ease;
}

.indicator-pill.active.danger {
  background: var(--danger);
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}

.indicator-pill.active.warning {
  background: var(--warning);
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.5);
}

.indicator-pill.active.success {
  background: var(--success);
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

.error-indicator {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.error-count-tag {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  color: var(--warning);
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
}

.error-count-tag.high {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--danger);
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    padding: 16px;
  }
  .toolbar-actions {
    justify-content: space-between;
  }
  .card-controls-row {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  .nav-btn-prev, .nav-btn-speak, .nav-btn-learned, .nav-btn-next {
    width: 100%;
    margin-left: 0 !important;
  }
}

/* Custom Mastery Progress Bar */
.mastery-progress-wrapper {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
  padding: 4px 0;
}

.progress-track {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  height: 8px;
  overflow: hidden;
  position: relative;
  width: 100%;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-bar-fill.danger {
  background: linear-gradient(90deg, #ef4444, #f87171);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.45);
}

.progress-bar-fill.warning {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.45);
}

.progress-bar-fill.success {
  background: linear-gradient(90deg, #10b981, #34d399);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.45);
}

.progress-text-label {
  font-size: 11px;
  font-weight: 700;
  margin-top: 4px;
  display: block;
  text-align: left;
}

.progress-text-label.text-danger {
  color: #fca5a5 !important;
}

.progress-text-label.text-warning {
  color: #fde047 !important;
}

.progress-text-label.text-success {
  color: #a7f3d0 !important;
}

/* Custom Error Badge Pill */
.error-badge-pill {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(245, 158, 11, 0.12) !important;
  border: 1px solid rgba(245, 158, 11, 0.3) !important;
  color: #fde047 !important;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.15);
  transition: all 0.2s ease;
}

.error-badge-pill.high-error {
  background: rgba(239, 68, 68, 0.12) !important;
  border: 1px solid rgba(239, 68, 68, 0.3) !important;
  color: #fca5a5 !important;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.15);
}

.mastery-indicator-new, .error-indicator-new {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.error-indicator-new {
  align-items: flex-end;
}

/* Navigation Bar (Desktop Card Mode) */
.navigation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  gap: 16px;
  width: 100%;
}

.navigation-bar .nav-btn-prev,
.navigation-bar .nav-btn-next {
  flex: 1;
  height: 48px;
  font-weight: 600;
}
/* Examples Panel styling (Unified with StudyMode) */
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

.audio-buttons-row {
  display: flex;
  gap: 10px;
}
</style>

