<template>
  <section class="cover-field" aria-labelledby="article-cover-label" :aria-busy="uploading">
    <span id="article-cover-label" class="cover-label">文章封面</span>
    <input ref="fileInput" class="hidden-input" type="file" :accept="accept" @change="selectCover" />
    <button type="button" class="cover-drop" :class="{ dragging }" :disabled="disabled || uploading || !ready"
      @click="fileInput?.click()" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="dropCover">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 16V3m-5 5 5-5 5 5M4 14v6a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-6" /></svg>
      <strong>{{ uploading ? '正在上传封面…' : modelValue ? '点击或拖入图片更换封面' : '点击或拖入图片上传封面' }}</strong>
      <span>{{ ready ? `${extensions.join('、').toUpperCase()} · 单张不超过 ${rules.image_limit_mb}MB` : '正在读取图片上传规则…' }}</span>
    </button>
    <div v-if="previewUrl" class="cover-preview">
      <img v-if="!imageFailed" :key="previewUrl" :src="previewUrl" alt="文章封面预览" @error="imageFailed = true" />
      <p v-else class="cover-message" role="status">当前封面无法预览，可以重新上传图片。</p>
      <button class="btn btn-ghost" type="button" :disabled="disabled || uploading" @click="removeCover">移除封面</button>
    </div>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <div v-if="uploading" class="cover-progress" role="status"><span>{{ progress ? `已上传 ${progress}%` : '正在上传并校验图片…' }}</span><button type="button" class="btn btn-ghost" @click="cancelUpload">取消上传</button></div>
    <p class="cover-message">上传后自动保存图片地址。移除封面只取消文章引用，上传的图片仍保留。</p>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import request from '@/utils/request'

const props = defineProps({ modelValue: { type: String, default: '' }, rules: { type: Object, default: () => ({}) }, disabled: Boolean })
const emit = defineEmits(['update:modelValue', 'busy-change'])
const fileInput = ref(null), uploading = ref(false), dragging = ref(false), error = ref(''), progress = ref(0), imageFailed = ref(false)
const extensions = computed(() => props.rules.extensions?.covers || [])
const ready = computed(() => extensions.value.length > 0 && Number(props.rules.image_limit_mb) > 0)
const accept = computed(() => extensions.value.join(','))
const previewUrl = computed(() => {
  if (!props.modelValue) return ''
  try {
    const url = new URL(props.modelValue, window.location.origin)
    return ['http:', 'https:'].includes(url.protocol) ? url.href : ''
  } catch { return '' }
})
let controller = null, generation = 0
watch(() => props.modelValue, () => { imageFailed.value = false })
function setUploading(value) { uploading.value = value; emit('busy-change', value) }
function cancelUpload() {
  generation += 1
  controller?.abort()
  controller = null
  setUploading(false)
  progress.value = 0
  error.value = '已取消上传。若服务器已完成接收，图片会保留在封面目录中。'
}
function removeCover() { error.value = ''; emit('update:modelValue', '') }
function selectCover(event) { const files = Array.from(event.target.files || []); event.target.value = ''; uploadCover(files) }
function dropCover(event) { dragging.value = false; uploadCover(Array.from(event.dataTransfer?.files || [])) }
async function uploadCover(files) {
  if (props.disabled || uploading.value || !ready.value || !files.length) return
  error.value = ''
  if (files.length !== 1) { error.value = '每篇文章请选择一张封面图片。'; return }
  const file = files[0], extension = '.' + file.name.split('.').pop().toLowerCase()
  if (!extensions.value.includes(extension)) { error.value = '不支持这种封面图片格式，请按上传区域的格式选择图片。'; return }
  if (!file.size || file.size > Number(props.rules.image_limit_mb) * 1024 * 1024) { error.value = `封面不能为空且不能超过 ${props.rules.image_limit_mb}MB。`; return }
  const currentGeneration = ++generation
  controller = new AbortController()
  const data = new FormData()
  data.append('subdir', 'covers')
  data.append('files', file)
  progress.value = 0
  setUploading(true)
  try {
    const result = await request.post('/api/admin/upload', data, { timeout: 120000, signal: controller.signal,
      onUploadProgress: event => { if (currentGeneration === generation && event.total) progress.value = Math.min(100, Math.round(event.loaded / event.total * 100)) } })
    if (currentGeneration !== generation) return
    const returnedFile = result.files?.[0]
    const uploadedName = result.uploaded?.[0]
    const returnedUrl = returnedFile?.url || (uploadedName ? `/api/files/covers/${encodeURIComponent(uploadedName)}` : '')
    if (!returnedUrl) throw new Error(result.rejected?.map(item => item.reason).join('；') || '封面没有上传成功，请重试。')
    const url = new URL(returnedUrl, window.location.origin)
    if (url.origin !== window.location.origin || !url.pathname.startsWith('/api/files/covers/')) throw new Error('服务器返回的封面地址无效，请重试。')
    emit('update:modelValue', url.pathname + url.search)
  } catch (err) {
    if (currentGeneration === generation) error.value = err.data?.rejected?.map(item => item.reason).join('；') || err.message || '封面上传失败，请重试。'
  } finally {
    if (currentGeneration === generation) { controller = null; setUploading(false) }
  }
}
defineExpose({ cancelUpload })
onBeforeUnmount(() => { generation += 1; controller?.abort() })
</script>

<style scoped>
.cover-field { display: grid; gap: 10px; min-width: 0; }
.cover-label { color: #344054; font-weight: 500; }
.hidden-input { display: none; }
.cover-drop { display: flex; flex-direction: column; align-items: center; gap: 8px; width: 100%; min-height: 132px; padding: 18px; border: 2px dashed #d9d0eb; border-radius: 10px; color: #5b21b6; background: #fcfaff; font: inherit; text-align: center; cursor: pointer; }
.cover-drop.dragging, .cover-drop:hover:not(:disabled) { background: #f3edff; border-color: #8b5bd2; }
.cover-drop span, .cover-message, .cover-progress { margin: 0; color: #667085; font-size: 12px; overflow-wrap: anywhere; }
.cover-preview { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; }
.cover-preview img { display: block; width: min(220px, 100%); max-height: 140px; object-fit: contain; border: 1px solid #e2e6ed; border-radius: 8px; background: #f8f9fc; }
.cover-progress { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.error { margin: 0; font-size: 13px; }
</style>
