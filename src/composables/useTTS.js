import { ElMessage } from 'element-plus'

/**
 * TTS 文字轉語音 Composable
 * 優先使用有道語音 API，失敗或超時後自動回退至系統原生 SpeechSynthesis
 */
export function useTTS() {
  const speakText = (text) => {
    if (!text) return
    // 清除方括號、圓括號等非英文標記，避免 TTS 讀到雜訊
    const cleanText = text.replace(/\[.*?\]/g, '').replace(/\(.*?\)/g, '').trim()

    const audioUrl = `https://dict.youdao.com/dictvoice?type=2&audio=${encodeURIComponent(cleanText)}`
    const audio = new Audio(audioUrl)

    let fallbackExecuted = false
    const runFallback = () => {
      if (fallbackExecuted) return
      fallbackExecuted = true
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel()
        const utterance = new SpeechSynthesisUtterance(cleanText)
        utterance.lang = 'en-US'
        utterance.rate = 0.9
        // 優先選擇英語語音
        const voices = window.speechSynthesis.getVoices()
        const engVoice = voices.find(v => v.lang.includes('en') || v.lang.includes('EN'))
        if (engVoice) utterance.voice = engVoice
        window.speechSynthesis.speak(utterance)
      } else {
        ElMessage.warning('您的裝置不支援語音朗讀功能。')
      }
    }

    audio.play().catch(err => {
      console.warn('有道語音播放失敗，改用系統原生語音', err)
      runFallback()
    })

    // 800ms 超時保護：若有道語音未在時限內播放則啟動 fallback
    setTimeout(() => {
      if (audio.paused && !fallbackExecuted) {
        console.warn('有道語音超時，改用系統原生語音')
        runFallback()
      }
    }, 800)
  }

  return { speakText }
}
