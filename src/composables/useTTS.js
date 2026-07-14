import { ElMessage } from 'element-plus'

/**
 * TTS 文字轉語音 Composable
 * 直接使用瀏覽器原生 SpeechSynthesis API，無需外部 API
 */
export function useTTS() {
  const speakText = (text) => {
    if (!text) return
    if (!('speechSynthesis' in window)) {
      ElMessage.warning('您的裝置不支援語音朗讀功能。')
      return
    }

    // 清除方括號、圓括號等非英文標記，避免 TTS 讀到雜訊
    const cleanText = text.replace(/\[.*?\]/g, '').replace(/\(.*?\)/g, '').trim()

    // 取消目前播放中的語音，避免重疊
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.lang = 'en-US'
    utterance.rate = 0.85

    // 優先選擇英語語音（en-US 優先，其次任何 en- 開頭）
    const voices = window.speechSynthesis.getVoices()
    const engVoice =
      voices.find(v => v.lang === 'en-US') ||
      voices.find(v => v.lang.startsWith('en'))
    if (engVoice) utterance.voice = engVoice

    window.speechSynthesis.speak(utterance)
  }

  return { speakText }
}
