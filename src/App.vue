<template>
  <div id="app">
    <BackgroundMedia ref="backgroundPlayer" />

    <!-- 首次进入等待背景和页面准备完成，统计请求不再单独控制退场。 -->
    <transition name="loading-fade">
      <StartupLoading
        v-if="startupLoading"
        :brand="pagesStore.text('site', 'brand', '沛心的博客')"
        :message="startupMessage"
        :ready="startupReady"
      />
    </transition>

    <!-- 主内容区域 -->
    <div v-show="!startupLoading" class="app-content">
      <Navbar :interaction-ready="!startupLoading" :background-busy="backgroundSwitchBusy" :background-feedback="backgroundFeedback" :play-area-visible="playfulVisibility" @next-background="requestNextBackground" />
      <main class="page-container">
        <router-view v-slot="{ Component }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" :key="$route.path" @playful-visibility="playfulVisibility = $event" />
          </transition>
        </router-view>
      </main>
      <BackToTop />
    </div>
  </div>
</template>

<script setup>
import { usePagesStore } from '@/stores/pages';
const pagesStore = usePagesStore();
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import request from '@/utils/request'
import Navbar from '@/components/Navbar.vue'
import BackToTop from '@/components/BackToTop.vue'
import StartupLoading from '@/components/StartupLoading.vue'
import BackgroundMedia from '@/components/BackgroundMedia.vue'
import { normalizeBackgroundMedia, chooseDifferentBackground, createBackgroundRotation } from '@/utils/backgroundMedia'
import startupBackground from './assets/startup-background.webp'

const appStore = useAppStore()
const route = useRoute()
const router = useRouter()
function updateMeta() {
  const routePages = { Home:'home', Articles:'articles', About:'about', More:'more', NotFound:'not_found' }
  const site = pagesStore.text('site','title','沛心的个人博客')
  const title = pagesStore.text(routePages[route.name], 'title', route.meta.title || '')
  document.title = route.name === 'Home' ? site : `${title} - ${site}`
  for (const key of ['description','keywords','author']) {
    let tag = document.querySelector(`meta[name="${key}"]`)
    if (!tag) { tag = document.createElement('meta'); tag.name = key; document.head.appendChild(tag) }
    tag.content = pagesStore.text('site',key,'')
  }
}
watch(() => [route.path, pagesStore.pages], updateMeta, { deep:true, immediate:true })
const backgroundPlayer = ref(null)
const startupLoading = ref(true)
const startupReady = ref(false)
const startupMessage = ref('正在加载背景与页面内容…')
const LAST_BG_KEY = 'peixin-last-bg-url'
const MEDIA_TIMEOUT = 4_000
const STARTUP_TIMEOUT = 6_000
const ROTATION_INTERVAL = 30_000
const FIRST_ROTATION_DELAY = 1_000
const backgroundRequest = new AbortController()
let rotationRequest = null
let startupTimer = null
let completionTimer = null
let rotationTimer = null
let disposed = false
let startupExpired = false
let rotationEpoch = 0
let mediaPool = []
let rotation = null
let indexReady = false
let currentBackgroundUrl = ''
let firstRotation = true
const previousBackground = lastBackground()
const failedMedia = new Set()
const backgroundSwitchBusy = ref(false)
const backgroundFeedback = ref('')
const playfulVisibility = ref(false)
watch(() => route.path, () => { playfulVisibility.value = false })
let rotationFlight = null
let feedbackTimer = null

function buildPublicAssetPath(relativePath) {
  const normalized = String(relativePath || '').replace(/^\/+/, '')
  return new URL(normalized, window.location.origin + (import.meta.env.BASE_URL || '/')).toString()
}

function lastBackground() {
  try { return sessionStorage.getItem(LAST_BG_KEY) || '' }
  catch (error) { console.warn('无法读取上次背景记录，将直接选择:', error); return '' }
}

function rememberBackground(url) {
  try { sessionStorage.setItem(LAST_BG_KEY, url) }
  catch (error) { console.warn('无法保存背景记录，不影响显示:', error) }
}

function displayMedia(media) {
  // 预载图片与首屏使用同一URL，其他图片/视频继续使用实际文件地址。
  const url = media.type === 'image' && media.filename === 'img.png' ? startupBackground : media.url
  return { ...media, url: buildPublicAssetPath(url) }
}

async function loadBackgroundIndex(signal) {
  try {
    const data = await request.get('/api/background-media', { timeout: 3000, signal })
    if (disposed || signal?.aborted) return false
    mediaPool = normalizeBackgroundMedia(data)
    rotation = createBackgroundRotation(mediaPool, { previousUrl: currentBackgroundUrl })
    failedMedia.clear()
    indexReady = true
    return true
  } catch (error) {
    if (!disposed && !signal?.aborted) console.warn('背景列表暂时不可用，将保留当前壁纸并重试:', error.message)
    indexReady = false
    return false
  }
}

async function initializeBackground() {
  await loadBackgroundIndex(backgroundRequest.signal)
  if (disposed || startupExpired) return
  const image = chooseDifferentBackground(mediaPool.filter(item => item.type === 'image'), previousBackground)
  const initial = image || { type: 'image', filename: 'img.png', url: startupBackground }
  startupMessage.value = '正在准备背景…'
  await nextTick()
  const ready = await backgroundPlayer.value?.show(displayMedia(initial), { timeout: MEDIA_TIMEOUT, signal: backgroundRequest.signal })
  if (ready && !disposed && !startupExpired) {
    currentBackgroundUrl = image?.url || ''
    if (image) rememberBackground(image.url)
  }
}

function scheduleRotation(delay = ROTATION_INTERVAL) {
  clearTimeout(rotationTimer)
  rotationTimer = null
  if (disposed || startupLoading.value || document.hidden) return
  rotationTimer = setTimeout(() => { rotationTimer = null; rotateBackground() }, delay)
}

// 手动按钮和自动轮播共用唯一切换任务，避免取消彼此的加载或重复下载。
function rotateBackground() {
  if (disposed || startupLoading.value || document.hidden) return Promise.resolve(false)
  if (rotationFlight) return rotationFlight
  clearTimeout(rotationTimer)
  rotationTimer = null
  backgroundSwitchBusy.value = true
  const epoch = rotationEpoch
  rotationFlight = performBackgroundRotation(epoch).finally(() => {
    backgroundSwitchBusy.value = false
    rotationFlight = null
  })
  return rotationFlight
}

async function performBackgroundRotation(epoch) {
  try {
    if (!indexReady || !mediaPool.length || failedMedia.size >= mediaPool.length) {
      rotationRequest = new AbortController()
      await loadBackgroundIndex(rotationRequest.signal)
      rotationRequest = null
    }
    if (disposed || document.hidden || epoch !== rotationEpoch) return false
    const attempts = mediaPool.length
    for (let attempt = 0; attempt < attempts; attempt++) {
      const excluded = [...failedMedia, currentBackgroundUrl]
      let next = rotation?.next(firstRotation ? [...excluded, previousBackground] : excluded)
      if (!next && firstRotation) next = rotation?.next(excluded)
      if (!next) { indexReady = false; break }
      const ready = await backgroundPlayer.value?.show(displayMedia(next), { timeout: 12_000 })
      if (disposed || document.hidden || epoch !== rotationEpoch) return false
      if (ready) {
        currentBackgroundUrl = next.url
        rememberBackground(next.url)
        firstRotation = false
        scheduleRotation()
        return true
      }
      failedMedia.add(next.url)
    }
    scheduleRotation()
    return false
  } catch (error) {
    if (!disposed && epoch === rotationEpoch) {
      console.warn('壁纸切换失败，保留当前背景:', error)
      scheduleRotation()
    }
    return false
  }
}

async function requestNextBackground() {
  if (backgroundSwitchBusy.value || disposed || document.hidden) return
  clearTimeout(feedbackTimer)
  backgroundFeedback.value = '正在准备下一张壁纸…'
  const changed = await rotateBackground()
  if (disposed) return
  backgroundFeedback.value = changed ? '壁纸已切换' : document.hidden ? '切换已暂停，当前壁纸保留' : mediaPool.length < 2 && indexReady ? '当前没有其他可切换的壁纸' : '暂时无法切换，已保留当前壁纸'
  feedbackTimer = setTimeout(() => { backgroundFeedback.value = '' }, 4500)
}

function handleBackgroundVisibility() {
  if (startupLoading.value) return
  rotationEpoch += 1
  clearTimeout(rotationTimer)
  rotationTimer = null
  rotationRequest?.abort()
  rotationRequest = null
  backgroundPlayer.value?.setPaused(document.hidden)
  if (!document.hidden) scheduleRotation(FIRST_ROTATION_DELAY)
}

onMounted(async () => {
  document.body.classList.add('site-starting')
  document.addEventListener('visibilitychange', handleBackgroundVisibility)
  const deadline = new Promise(resolve => {
    startupTimer = setTimeout(() => {
      startupExpired = true
      backgroundRequest.abort()
      backgroundPlayer.value?.cancelPending()
      console.warn('页面准备等待超时，将继续进入')
      resolve()
    }, STARTUP_TIMEOUT)
  })
  try {
    appStore.fetchStats().catch(error => console.warn('统计暂时不可用:', error.message))
    const results = await Promise.race([
      Promise.allSettled([initializeBackground(), pagesStore.loadPages(), router.isReady()]),
      deadline
    ])
    if (results?.[0]?.status === 'rejected') console.error('背景初始化失败，将在进入后重试:', results[0].reason)
    if (results?.[2]?.status === 'rejected') console.error('初始页面加载失败:', results[2].reason)
  } catch (error) {
    console.error('应用初始化失败:', error)
  } finally {
    clearTimeout(startupTimer)
    if (!disposed) {
      startupMessage.value = '准备就绪，正在进入…'
      startupReady.value = true
      completionTimer = setTimeout(() => {
        startupLoading.value = false
        document.body.classList.remove('site-starting')
        backgroundPlayer.value?.setPaused(document.hidden)
        // 首屏退场后才加载其他背景；视频不再挡住进入网站。
        scheduleRotation(FIRST_ROTATION_DELAY)
      }, 220)
    }
  }
})

onUnmounted(() => {
  disposed = true
  rotationEpoch += 1
  backgroundRequest.abort()
  rotationRequest?.abort()
  backgroundPlayer.value?.cancelPending()
  clearTimeout(startupTimer)
  clearTimeout(completionTimer)
  clearTimeout(feedbackTimer)
  clearTimeout(rotationTimer)
  document.removeEventListener('visibilitychange', handleBackgroundVisibility)
  document.body.classList.remove('site-starting')
})

</script>

<style lang="scss">
// ==================== 全局重置 ====================
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  font-size: 16px;
}

body {
  font-family: 'Inter', 'Noto Sans SC', system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
  color: #1a1a1a;
  line-height: 1.6;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  position: relative;
}

// ==================== 全局背景系统 ====================
.global-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
}

.bg-image {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  background-repeat: no-repeat;
  opacity: 0;
  transition: opacity 0.2s ease;
  will-change: opacity;

  &.loaded {
    opacity: 1;
  }
}

.bg-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.2s ease;
  will-change: opacity;

  &.loaded {
    opacity: 1;
  }
}

.bg-fallback {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #071026 0%, #0b1220 50%, #0f172a 100%);
  z-index: -1;
}

// ==================== 页面容器 ====================
.app-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

// ==================== 页面镂空区域 ====================
.page-container {
  padding-top: 68px;
  min-height: 100vh;
  overflow: hidden;
}

// 内页镂空容器
.hollow-window {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px) saturate(160%);
  -webkit-backdrop-filter: blur(12px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  margin: 24px auto;
  max-width: 54%;
  width: 100%;
}

@media (max-width: 768px) {
  .page-container { padding-top: 56px; }

  .hollow-window {
    margin: 16px auto;
    max-width: calc(100% - 32px);
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(12px) saturate(160%);
    -webkit-backdrop-filter: blur(12px) saturate(160%);
    border-radius: 16px;
  }

  .app-content .glass-card:hover { transform: none; }
  .app-content .back-to-top-btn {
    right: 16px;
    bottom: calc(16px + env(safe-area-inset-bottom, 0px));
    width: 44px;
    height: 44px;
    color: #6d28d9;
  }
}

// ==================== 路由过渡动画 ====================
.page-slide-enter-active,
.page-slide-leave-active {
  transition: opacity 0.45s cubic-bezier(0.25, 0.8, 0.25, 1),
              transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(24px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateY(-16px);
}

.loading-fade-enter-active,
.loading-fade-leave-active {
  transition: opacity 0.3s ease;
}

.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .loading-fade-enter-active,
  .loading-fade-leave-active,
  .bg-image,
  .bg-video { transition: none; }
}

// ==================== 毛玻璃镂空卡片 ====================
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px) saturate(160%);
  -webkit-backdrop-filter: blur(12px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  will-change: transform, opacity;

  &:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 255, 255, 0.25);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  }
}

// ==================== 隐藏滚动条 ====================
::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: transparent;
}

// ==================== 全局文字可读性 ====================
.text-readable {
  color: #1a1a1a;
  text-shadow: none;
}

// 例外：渐变文字
.gradient-text,
.text-gradient {
  text-shadow: 0 0 30px rgba(168, 85, 247, 0.4) !important;
}

// ==================== 工具类 ====================
.text-gradient {
  background: linear-gradient(135deg, #a855f7, #ec4899, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (max-width: 640px) {
  .container {
    padding: 0 1rem;
  }
}
</style>
