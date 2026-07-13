<template>
  <div class="app-wrapper">
    <!-- Header / Nav Bar -->
    <header class="header-nav glass-container">
      <div class="brand-title">
        <img src="/gua1.png" class="brand-avatar" alt="gua1" />
        <span>張晨晨考試加油！</span>
        <img src="/gua2.png" class="brand-avatar" alt="gua3" />
      </div>

      <!-- Menu Navigation -->
      <el-menu
        :default-active="activeTab"
        mode="horizontal"
        :ellipsis="false"
        @select="handleTabSelect"
      >
        <el-menu-item index="study">
          <el-icon><Notebook /></el-icon>
          <span>背單字</span>
        </el-menu-item>
        <el-menu-item index="quiz">
          <el-icon><Postcard /></el-icon>
          <span>單字小考</span>
        </el-menu-item>
        <el-menu-item index="review">
          <el-icon><Warning /></el-icon>
          <span>
            錯字複習
            <el-badge
              v-if="wrongCount > 0"
              :value="wrongCount"
              type="danger"
              class="menu-badge"
            />
          </span>
        </el-menu-item>
      </el-menu>
    </header>

    <!-- Main Content Panel -->
    <main class="main-content">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-panel glass-container">
        <el-icon class="is-loading" size="40"><Loading /></el-icon>
        <p>正在載入字彙資料庫 (1.6 MB)...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="hasError" class="error-panel glass-container">
        <el-icon size="40" class="text-danger"><CircleClose /></el-icon>
        <p>資料庫載入失敗，請確認 vocabulary.json 存在於 public 目錄中。</p>
      </div>

      <!-- Active Content Components -->
      <div v-else class="content-fade">
        <StudyMode
          v-if="activeTab === 'study'"
          :vocabulary-data="vocabData"
        />
        <QuizMode
          v-else-if="activeTab === 'quiz'"
          :vocabulary-data="vocabData"
          @switch-tab="handleSwitchTab"
          @update-wrong-count="updateWrongCount"
        />
        <ReviewMode
          v-else-if="activeTab === 'review'"
          :vocabulary-data="vocabData"
          @switch-tab="handleSwitchTab"
          @update-wrong-count="updateWrongCount"
        />
      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>英文字彙學習網頁 © 2026. 靜態單頁離線字彙系統（進度自動儲存於本機）</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Reading, Notebook, Postcard, Warning, Loading, CircleClose } from '@element-plus/icons-vue'
import StudyMode from './components/StudyMode.vue'
import QuizMode from './components/QuizMode.vue'
import ReviewMode from './components/ReviewMode.vue'

const activeTab = ref('study')
const vocabData = ref([])
const isLoading = ref(true)
const hasError = ref(false)
const wrongCount = ref(0)

const handleTabSelect = (tabIndex) => {
  activeTab.value = tabIndex
  // Sync wrong count on tab changes
  updateWrongCount()
}

const handleSwitchTab = (tabIndex) => {
  activeTab.value = tabIndex
  updateWrongCount()
}

// Fetch vocabulary database JSON
const fetchVocabulary = async () => {
  try {
    isLoading.value = true
    // Fetch relative path. Works for both dev and built dist.
    const res = await fetch('./vocabulary.json')
    if (!res.ok) throw new Error('Failed to fetch JSON data')
    vocabData.value = await res.json()
    isLoading.value = false
  } catch (err) {
    console.error('Error fetching vocabulary database:', err)
    hasError.value = true
    isLoading.value = false
  }
}

// Count local storage wrong words
const updateWrongCount = () => {
  const saved = localStorage.getItem('vocabulary_wrong_words')
  if (saved) {
    try {
      const list = JSON.parse(saved)
      wrongCount.value = list.length
    } catch (e) {
      wrongCount.value = 0
    }
  } else {
    wrongCount.value = 0
  }
}

onMounted(() => {
  fetchVocabulary()
  updateWrongCount()
  
  // Set up listener to sync wrong words count across components
  window.addEventListener('storage', (e) => {
    if (e.key === 'vocabulary_wrong_words') {
      updateWrongCount()
    }
  })
})
</script>

<style>
.brand-avatar {
  width: 54px;
  height: 54px;
  object-fit: contain;
  filter: drop-shadow(0 0 6px var(--primary-glow));
}

/* CSS overrides or general app transitions */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.loading-panel, .error-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
  flex-grow: 1;
  text-align: center;
}

.loading-panel p, .error-panel p {
  font-size: 16px;
  color: var(--text-muted);
}

.menu-badge {
  margin-left: 4px;
}

.app-footer {
  text-align: center;
  padding: 32px 0 16px;
  color: var(--text-muted);
  font-size: 13px;
  border-top: 1px solid var(--border-color);
  margin-top: 40px;
}

/* Animations and fades */
.content-fade {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
