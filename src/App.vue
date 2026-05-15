<template>
  <div id="app">
    <!-- 全屏随机背景 -->
    <div class="global-bg" aria-hidden="true">
      <!-- 图片背景 -->
      <div 
        v-if="bgType === 'image'" 
        class="bg-image" 
        :class="{ loaded: bgLoaded }" 
        :style="{ backgroundImage: currentBg ? `url(${currentBg})` : 'none' }"
      ></div>
      <!-- 视频背景 -->
      <video 
        v-if="bgType === 'video'" 
        class="bg-video" 
        :class="{ loaded: bgLoaded }"
        autoplay 
        loop 
        muted 
        playsinline
        :src="currentBg"
      ></video>
      <div class="bg-fallback"></div>
    </div>

    <!-- Loading Screen -->
    <transition name="loading-fade">
      <div v-if="appStore.isLoading" class="loading-screen">
        <div class="loading-spinner"></div>
        <p class="loading-text">加载中...</p>
      </div>
    </transition>

    <!-- 主内容区域 -->
    <div v-show="!appStore.isLoading" class="app-content">
      <Navbar />
      <main class="page-container">
        <router-view v-slot="{ Component }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </transition>
        </router-view>
      </main>
      <BackToTop />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import request from '@/utils/request'
import Navbar from '@/components/Navbar.vue'
import BackToTop from '@/components/BackToTop.vue'

const appStore = useAppStore()
const currentBg = ref('')
const bgLoaded = ref(false)
const bgType = ref('image') // 'image' 或 'video'
const bgImages = ref([])
const bgVideos = ref([])
const LAST_BG_KEY = 'peixin-last-bg-url'

function buildPublicAssetPath(relativePath) {
  // 去掉开头多余的 /
  const normalized = String(relativePath || '').replace(/^\/+/, '')
  // 基础路径用 / ，和vite.config.js的base保持一致
  const base = import.meta.env.BASE_URL || '/'
  // 最终生成：https://peixin.uno/toux/img.png 这种格式
  return new URL(normalized, window.location.origin + base).toString()
}

function chooseDifferentRandom(list, previousUrl) {
  if (!Array.isArray(list) || list.length === 0) return null
  if (list.length === 1) return list[0]

  const candidates = list.filter(item => item.url !== previousUrl)
  const pool = candidates.length ? candidates : list
  return pool[Math.floor(Math.random() * pool.length)]
}

async function loadBackgroundMedia() {
  try {
    const data = await request.get('/api/background-media')
    bgImages.value = Array.isArray(data?.images) ? data.images : []
    bgVideos.value = Array.isArray(data?.videos) ? data.videos : []
    } catch (err) {
    console.error('加载背景资源失败，使用默认背景:', err)
    // 修正路径，用 / 开头的根路径
    bgImages.value = [{ filename: 'img.png', url: '/api/files/toux/img.png' }]
    bgVideos.value = []
  }
}

// 每次刷新尽量换一个新的背景
function pickRandomBg() {
  const prev = sessionStorage.getItem(LAST_BG_KEY) || ''

  // 优先视频；没有视频再选图片
  const pickVideo = bgVideos.value.length > 0
  if (pickVideo) {
    const chosen = chooseDifferentRandom(bgVideos.value, prev)
    if (chosen) {
      bgType.value = 'video'
      currentBg.value = buildPublicAssetPath(chosen.url)
      bgLoaded.value = true
      sessionStorage.setItem(LAST_BG_KEY, chosen.url)
      return
    }
  }

  if (bgImages.value.length > 0) {
    const chosen = chooseDifferentRandom(bgImages.value, prev)
    if (chosen) {
      bgType.value = 'image'
      const imagePath = buildPublicAssetPath(chosen.url)
      const img = new Image()
      img.onload = () => {
        currentBg.value = imagePath
        bgLoaded.value = true
      }
      img.onerror = () => {
        currentBg.value = ''
        bgLoaded.value = true
      }
      img.src = imagePath
      sessionStorage.setItem(LAST_BG_KEY, chosen.url)
      return
    }
  }

  bgLoaded.value = true
}

onMounted(async () => {
  await loadBackgroundMedia()
  pickRandomBg()
  try {
    await appStore.fetchStats()
  } catch (error) {
    console.error('应用初始化失败:', error)
  } finally {
    appStore.isLoading = false
  }
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
  transition: opacity 1.5s ease;
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
  transition: opacity 1.5s ease;
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
  .hollow-window {
    margin: 16px auto;
    border-radius: 16px;
  }
}

// ==================== Loading Screen ====================
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #071026;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 3px solid rgba(168, 85, 247, 0.2);
  border-top-color: #a855f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 20px;
  color: #e2e8f0;
  font-size: 16px;
  letter-spacing: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
  transition: opacity 0.5s ease;
}

.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
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
