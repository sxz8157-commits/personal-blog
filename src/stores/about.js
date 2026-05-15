import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useAboutStore = defineStore('about', () => {
  const aboutData = ref(null)
  const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存
  const lastFetchTime = ref(null)
  const error = ref(null)

  const loadAboutData = async (force = false) => {
    // 如果缓存有效，直接返回缓存数据
    if (!force && aboutData.value && lastFetchTime.value &&
        Date.now() - lastFetchTime.value < CACHE_DURATION) {
      return aboutData.value
    }

    try {
      const data = await request.get('/api/about')
      aboutData.value = data
      lastFetchTime.value = Date.now()
      error.value = null
      return data
    } catch (err) {
      console.error('加载关于页面数据失败:', err)
      error.value = err.message || '加载失败'
      // 如果有缓存数据，即使过期也继续使用
      if (aboutData.value) {
        return aboutData.value
      }
      return null
    }
  }

  return { aboutData, loadAboutData, error }
})
