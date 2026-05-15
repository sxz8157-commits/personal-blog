/**
 * 日期格式化工具函数
 */

/**
 * 格式化日期为相对时间（如：今天、昨天、3天前等）
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 相对时间字符串
 */
export function formatRelativeDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 14) return '1周前'
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 60) return '1个月前'
  if (days < 365) return `${Math.floor(days / 30)}个月前`
  if (days < 730) return '1年前'
  return `${Math.floor(days / 365)}年前`
}

/**
 * 格式化日期为中文日期字符串（如：2024年1月15日）
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @param {Object} options - 格式化选项
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(dateString, options = {}) {
  const date = new Date(dateString)
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  }
  
  return date.toLocaleDateString('zh-CN', defaultOptions)
}

/**
 * 格式化日期时间为完整的中文日期时间字符串
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的日期时间字符串
 */
export function formatDateTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 检查日期是否为今天
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {boolean} 是否为今天
 */
export function isToday(dateString) {
  const date = new Date(dateString)
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

/**
 * 检查日期是否为昨天
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {boolean} 是否为昨天
 */
export function isYesterday(dateString) {
  const date = new Date(dateString)
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  
  return date.getDate() === yesterday.getDate() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getFullYear() === yesterday.getFullYear()
}
