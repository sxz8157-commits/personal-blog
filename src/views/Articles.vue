<template>
  <div class="articles-page">
    <div class="hollow-window">
      <!-- Page Header -->
      <header class="page-header">
        <h1 class="page-title">文章词云</h1>
        <p class="page-subtitle text-readable">点击词云中的文档标题，直接进入详情（支持 MD / PDF / XMind 等）</p>
        
        <!-- 来源切换按钮已删除，现在直接使用 MD 文章 -->
      </header>

      <section class="articles-section">
        <!-- Word Cloud: 点击即跳转文章 -->
        <div ref="tagcloudCardEl" class="tagcloud-panel">
          <template v-if="!loading && cloudItems.length">
            <TagCloudCanvas
              :tags="cloudItems"
              :width="canvasW"
              :height="canvasH"
              :speed="0.0024"
              :radius-scale="cloudRadiusScale"
              :min-font="15"
              :max-font="40"
              @select="goToArticle"
            />
          </template>

          <div v-else class="tagcloud-empty text-readable">
            暂无文章可展示。请在 `public/wenz` 下添加 Markdown 文章后刷新页面。
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-dots">
            <span></span><span></span><span></span>
          </div>
          <p class="text-readable">加载中...</p>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && articles.length === 0" class="empty-state">
          <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <line x1="7" y1="8" x2="17" y2="8"/>
            <line x1="7" y1="12" x2="17" y2="12"/>
            <line x1="7" y1="16" x2="12" y2="16"/>
          </svg>
          <p class="text-readable">暂无文章，敬请期待</p>
        </div>

        <!-- 分页已删除 -->
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import TagCloudCanvas from '@/components/TagCloudCanvas.vue'

const router = useRouter()
const articles = ref([])
const loading = ref(false)

// canvas 尺寸直接用窗口比例，不再监听 DOM
const canvasW = computed(() => {
  const w = window.innerWidth
  if (w < 640) return Math.floor(w * 0.88)
  if (w < 1024) return Math.floor(w * 0.62)
  return Math.floor(w * 0.44)
})

const canvasH = computed(() => Math.min(Math.floor(canvasW.value * 0.62), 600))

const fetchArticles = async () => {
  loading.value = true
  try {
    const data = await request.get('/api/md-articles')
    articles.value = data.articles || []
  } catch (error) {
    console.error('获取文章列表失败:', error)
  } finally {
    loading.value = false
  }
}

const cloudItems = computed(() => {
  const list = articles.value || []
  const valid = list
    .filter(a => a && a.id && a.title)
  return valid.map((a) => {
    const title = String(a.title).trim()
    const fileType = String(a.file_type || '').toUpperCase()
    const rawFilename = String(a.filename || a.id || '').trim()
    const baseName = rawFilename ? rawFilename.replace(/\.[^.]+$/, '') : title
    // 词云统一按“真实文件名”展示，避免文档内部标题与文件名不一致导致误解
    // 如 ES6.md 的标题可能是“转码结果输出到标准输出”
    const coreLabel = baseName || title
    const label = fileType ? `${coreLabel} (${fileType})` : coreLabel
    return {
      label,
      value: String(a.id),
      count: Math.max(1, Number(a.views || 0) + Number(a.likes || 0) + 1)
    }
  })
})

const cloudRadiusScale = computed(() => {
  const n = cloudItems.value.length
  // 文档越多球体越大；但限制在卡片可点击范围内
  const scale = 0.5 + Math.sqrt(Math.max(1, n)) * 0.06
  return Math.max(0.52, Math.min(0.82, scale))
})

function goToArticle(articleId) {
  if (!articleId) return
  router.push(`/article/${encodeURIComponent(articleId)}`)
}

onMounted(() => {
  fetchArticles()
})

watch(loading, async (v) => {
  if (!v) {
    await nextTick()
  }
})

watch(cloudItems, async () => {
  await nextTick()
})

onUnmounted(() => {
})
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.articles-page {
  padding-top: 16px;
  min-height: calc(100vh - 68px);
  overflow: hidden;
}

// ===== 页面标题 =====
.page-header {
  text-align: center;
  padding: 48px 2rem 40px;
}

.page-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  background: linear-gradient(135deg, #e879f9 0%, #ec4899 50%, #a855f7 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: 0 0 30px rgba(168, 85, 247, 0.4) !important;
  margin-bottom: 12px;
}

.page-subtitle {
  color: rgba(0, 0, 0, 0.6);
  font-size: 1.05rem;
}

// ===== 文章列表 =====
.articles-section {
  display: flex;
  justify-content: center;
  max-height: calc(100vh - 220px);
  overflow: hidden;
}

.tagcloud-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.tagcloud-empty {
  margin-top: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px dashed rgba(0, 0, 0, 0.15);
  background: rgba(0, 0, 0, 0.03);
  color: rgba(0, 0, 0, 0.55);
  font-weight: 700;
  line-height: 1.65;
}

// ===== 状态 =====
.loading-state,
.empty-state {
  text-align: center;
  padding: 80px 0;
  color: rgba(0, 0, 0, 0.45);

  svg {
    opacity: 0.3;
  }

  p {
    margin-top: 16px;
    font-size: 1rem;
  }
}

.loading-dots {
  display: inline-flex;
  gap: 8px;

  span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #a855f7;
    animation: bounce 1.4s infinite ease-in-out both;
  }

  span:nth-child(1) { animation-delay: -0.32s; }
  span:nth-child(2) { animation-delay: -0.16s; }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@media (max-width: 640px) {
  .articles-section { padding: 0 1rem; }
  .page-header { padding: 32px 1rem 40px; }
}
</style>
