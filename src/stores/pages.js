import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'
export const usePagesStore = defineStore('pages', () => {
  const pages = ref({}), error = ref('')
  async function loadPages() {
    try { const data = await request.get('/api/pages'); pages.value = data.pages || {}; error.value = '' }
    catch (err) { error.value = err.message }
  }
  function text(page, key, fallback = '') {
    const value = pages.value[page]?.[key]
    return typeof value === 'string' ? value : fallback
  }
  return { pages, error, loadPages, text }
})
