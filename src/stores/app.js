import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAppStore = defineStore('app', () => {
  // 状态
  const isDarkMode = ref(true)
  const stats = ref({
    total_articles: 0,
    total_views: 0,
    total_comments: 0,
    total_categories: 0,
    days_running: 0
  })
  const isLoading = ref(true)
  const error = ref(null)
  const lastFetchTime = ref(null)
  
  // 缓存时间（5分钟）
  const CACHE_DURATION = 5 * 60 * 1000

  // 计算属性
  const themeClass = computed(() => isDarkMode.value ? 'dark-theme' : 'light-theme')
  
  // 检查是否需要重新获取数据（基于缓存时间）
  const shouldRefetchStats = computed(() => {
    if (!lastFetchTime.value) return true
    return Date.now() - lastFetchTime.value > CACHE_DURATION
  })

  // 方法
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
  }

  const fetchStats = async (force = false) => {
    // 如果不是强制刷新且缓存有效，则使用缓存
    if (!force && !shouldRefetchStats.value) {
      return stats.value
    }

    isLoading.value = true
    error.value = null
    
    try {
      const data = await request.get('/api/stats')
      stats.value = data
      lastFetchTime.value = Date.now()
      return data
    } catch (err) {
      error.value = {
        message: err.message || '获取统计数据失败',
        status: err.status,
        timestamp: new Date().toISOString()
      }
      console.error('获取统计数据失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
    }
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 强制刷新数据
  const refreshStats = async () => {
    return await fetchStats(true)
  }

  return {
    // 状态
    isDarkMode,
    stats,
    isLoading,
    error,
    lastFetchTime,
    
    // 计算属性
    themeClass,
    shouldRefetchStats,
    
    // 方法
    toggleTheme,
    fetchStats,
    initTheme,
    clearError,
    refreshStats
  }
})
