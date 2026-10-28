<template>
  <div class="articles-page">
    <section class="cloud-intro article-glass" aria-labelledby="cloud-title">
      <header class="cloud-header">
        <p class="section-eyebrow"><span aria-hidden="true"></span> 随意探索，慢慢阅读</p>
        <h1 id="cloud-title">{{ pagesStore.text('articles', 'title', '文章词云') }}</h1>
        <p class="cloud-description">{{ pagesStore.text('articles', 'subtitle', '点击词云中的文章或文档标题，直接进入详情') }}</p>
      </header>

      <div ref="cloudPanel" class="cloud-stage" :aria-busy="loading">
        <div v-if="loading" class="panel-state" role="status"><span class="loading-orbit" aria-hidden="true"></span><p>正在整理文章…</p></div>
        <div v-else-if="loadError" class="panel-state" role="alert"><p>{{ loadError }}</p><button type="button" class="quiet-button" @click="fetchArticles">重新加载</button></div>
        <template v-else-if="articles.length">
          <TagCloudCanvas :tags="cloudItems" :width="canvasW" :height="canvasH" :speed="0.0024" :radius-scale="cloudRadiusScale" :font-size="18" :active="cloudVisible && !reducedMotion" @select="goToArticle" />
          <p v-if="openingArticle" class="article-opening" role="status">正在打开文章…</p>
        </template>
        <p v-else class="panel-state">{{ pagesStore.text('articles', 'empty', '暂无文章，敬请期待') }}</p>
      </div>

      <a class="browse-cue" href="#article-library" @click.prevent="scrollToLibrary">
        <span>{{ articles.length ? `${articles.length} 篇文章与文档` : '文章与笔记' }}</span>
        <span class="browse-cue-action">向下浏览文章 <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg></span>
      </a>
    </section>

    <section id="article-library" ref="library" class="article-library article-glass" aria-labelledby="library-title" tabindex="-1">
      <header class="library-header">
        <div><p class="section-eyebrow">把灵感整理成篇</p><h2 id="library-title">文章与笔记<span class="total-count">{{ articles.length }}</span></h2></div>
        <p class="library-caption">从一个关键词，找到想读的内容。</p>
      </header>

      <form class="search-bar" role="search" @submit.prevent="searchSubmitted">
        <label for="article-search" class="visually-hidden">搜索文章</label>
        <svg viewBox="0 0 24 24" width="21" height="21" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4.5 4.5" /></svg>
        <input id="article-search" v-model="searchQuery" type="search" placeholder="搜索标题、关键词或文档格式…" autocomplete="off" enterkeyhint="search" @keydown.esc="searchQuery = ''" />
        <button v-if="searchQuery" type="button" class="clear-search" aria-label="清空搜索" @click="searchQuery = ''">×</button>
        <span class="search-hint" aria-hidden="true">搜索</span>
      </form>

      <div class="library-tools">
        <div class="format-filters" role="group" aria-label="按文档格式筛选">
          <button type="button" :aria-pressed="!activeFormat" @click="activeFormat = ''">全部</button>
          <button v-for="format in formats" :key="format" type="button" :aria-pressed="activeFormat === format" @click="activeFormat = format">{{ format }}</button>
        </div>
        <p class="result-count" role="status" aria-live="polite">{{ loading ? '正在加载…' : `共 ${filteredArticles.length} 篇` }}</p>
      </div>

      <div v-if="loading" class="list-skeleton" aria-label="正在加载文章" aria-busy="true"><div v-for="i in 3" :key="i"><span></span><span></span></div></div>
      <div v-else-if="loadError" class="list-empty" role="alert"><h3>文章暂时没有加载成功</h3><p>{{ loadError }}</p><button type="button" class="quiet-button" @click="fetchArticles">重新加载</button></div>
      <template v-else-if="filteredArticles.length">
        <div class="article-list">
          <article v-for="article in pagedArticles" :key="article.id" class="article-row">
            <RouterLink :to="article.href" class="article-link">
              <span class="article-format" aria-hidden="true">{{ article.format }}</span>
              <div class="article-copy">
                <div class="article-meta"><span>{{ article.format === '文章' ? '原创文章' : article.format + ' 文档' }}</span><template v-if="article.date"><span aria-hidden="true">·</span><time :datetime="article.date">{{ article.date }}</time></template></div>
                <h3>{{ article.title }}</h3><p class="article-summary">{{ article.description }}</p>
                <div v-if="article.tags.length" class="article-tags"><span v-for="tag in article.tags.slice(0, 3)" :key="tag"># {{ tag }}</span></div>
              </div>
              <span class="read-link" aria-hidden="true"><span>阅读</span><svg viewBox="0 0 24 24" width="20" height="20"><path d="M5 12h14m-5-5 5 5-5 5" /></svg></span>
            </RouterLink>
          </article>
        </div>
        <nav v-if="pageCount > 1" class="pagination" aria-label="文章列表分页">
          <button type="button" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">上一页</button>
          <span aria-live="polite">第 <strong>{{ currentPage }}</strong> / {{ pageCount }} 页</span>
          <button type="button" :disabled="currentPage === pageCount" @click="changePage(currentPage + 1)">下一页</button>
        </nav>
      </template>
      <div v-else class="list-empty"><span class="empty-symbol" aria-hidden="true">⌕</span><h3>{{ articles.length ? '没有找到相关内容' : '新的文章，还在路上' }}</h3><p>{{ articles.length ? '试试更短的关键词，或切换文档格式。' : '等下一次灵感，慢慢写给你。' }}</p><button v-if="searchQuery || activeFormat" type="button" class="quiet-button" @click="resetSearch">查看全部文章</button></div>
      <p class="library-footer">每一次记录，都是一点新的发现。</p>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePagesStore } from '@/stores/pages'
import request from '@/utils/request'
import TagCloudCanvas from '@/components/TagCloudCanvas.vue'
import { filterArticles, prepareArticles } from '@/utils/articleIndex'

const pagesStore = usePagesStore()
const router = useRouter()
const articles = ref([])
const loading = ref(true)
const loadError = ref('')
const openingArticle = ref(false)
const searchQuery = ref('')
const activeFormat = ref('')
const currentPage = ref(1)
const PAGE_SIZE = 8
const cloudPanel = ref(null)
const library = ref(null)
const panelWidth = ref(0)
const viewportWidth = ref(window.innerWidth)
const cloudVisible = ref(true)
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
const reducedMotion = ref(motionPreference.matches)
let resizeObserver = null
let intersectionObserver = null
let indexRequest = null
let disposed = false

const formats = computed(() => [...new Set(articles.value.map(article => article.format))])
const filteredArticles = computed(() => filterArticles(articles.value, searchQuery.value, activeFormat.value))
const pageCount = computed(() => Math.max(1, Math.ceil(filteredArticles.value.length / PAGE_SIZE)))
const pagedArticles = computed(() => filteredArticles.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE))
const cloudItems = computed(() => articles.value.map(article => ({ value: article.id, label: `${article.title} (${article.format})`, count: article.count })))
const canvasW = computed(() => Math.max(1, Math.floor(Math.min(700, panelWidth.value || viewportWidth.value - 64))))
const canvasH = computed(() => Math.round(Math.min(canvasW.value * (viewportWidth.value < 640 ? 0.94 : 0.62), 410)))
const cloudRadiusScale = computed(() => Math.max(0.52, Math.min(0.82, 0.5 + Math.sqrt(Math.max(1, articles.value.length)) * 0.06)))
watch([searchQuery, activeFormat], () => { currentPage.value = 1 })

function updateCanvasSize() {
  viewportWidth.value = window.innerWidth
  const width = cloudPanel.value?.getBoundingClientRect().width || 0
  if (width > 0) panelWidth.value = width
}
function updateMotion(event) { reducedMotion.value = event.matches }
async function fetchArticles() {
  indexRequest?.abort()
  const controller = new AbortController()
  indexRequest = controller
  loading.value = true
  loadError.value = ''
  try {
    const data = await request.get('/api/article-index', { signal: controller.signal })
    if (disposed || controller.signal.aborted) return
    articles.value = prepareArticles(data?.articles)
    currentPage.value = 1
    if (!formats.value.includes(activeFormat.value)) activeFormat.value = ''
  } catch (error) {
    if (!disposed && !controller.signal.aborted) {
      loadError.value = error.message || '文章加载失败，请稍后重试'
      console.error('文章索引加载失败:', loadError.value)
    }
  } finally {
    if (!disposed && indexRequest === controller) { loading.value = false; indexRequest = null }
  }
}
function scrollToLibrary() {
  library.value?.scrollIntoView({ behavior: reducedMotion.value ? 'auto' : 'smooth', block: 'start' })
  library.value?.focus({ preventScroll: true })
}
function resetSearch() { searchQuery.value = ''; activeFormat.value = '' }
function searchSubmitted() { document.getElementById('article-search')?.blur() }
async function changePage(page) {
  currentPage.value = Math.max(1, Math.min(pageCount.value, page))
  await nextTick()
  scrollToLibrary()
}
async function goToArticle(id) {
  if (!id || openingArticle.value) return
  openingArticle.value = true
  try { await router.push(`/article/${encodeURIComponent(id)}`) }
  catch (error) { console.error('文章打开失败:', error); loadError.value = '文章暂时未能打开，请刷新后重试' }
  finally { if (!disposed) openingArticle.value = false }
}
onMounted(() => {
  updateCanvasSize()
  resizeObserver = new ResizeObserver(updateCanvasSize)
  resizeObserver.observe(cloudPanel.value)
  intersectionObserver = new IntersectionObserver(([entry]) => { cloudVisible.value = entry.isIntersecting }, { threshold: 0, rootMargin: '-72px 0px 0px 0px' })
  intersectionObserver.observe(cloudPanel.value)
  window.addEventListener('resize', updateCanvasSize)
  motionPreference.addEventListener('change', updateMotion)
  fetchArticles()
})
onUnmounted(() => {
  disposed = true
  indexRequest?.abort()
  resizeObserver?.disconnect()
  intersectionObserver?.disconnect()
  window.removeEventListener('resize', updateCanvasSize)
  motionPreference.removeEventListener('change', updateMotion)
})
</script>

<style scoped lang="scss">
.articles-page {
  --article-ink: #242035;
  --article-muted: #5d566d;
  --article-accent: #7c3aed;
  --article-line: rgba(103, 78, 136, 0.14);
  --article-surface: rgba(255, 255, 255, 0.16);
  width: min(1040px, calc(100% - 64px));
  margin: 20px auto 64px;
  color: var(--article-ink);
}
.article-glass {
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: 24px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.27), rgba(255, 255, 255, 0.12));
  backdrop-filter: blur(16px) saturate(120%);
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  box-shadow: 0 12px 40px rgba(35, 20, 60, 0.08);
}
.cloud-intro { min-height: calc(100svh - 112px); padding: 32px 40px 20px; display: flex; flex-direction: column; }
.cloud-header { text-align: center; }
.section-eyebrow { color: var(--article-muted); font-size: 12px; letter-spacing: 0.12em; margin: 0 0 10px; display: flex; align-items: center; gap: 8px; }
.cloud-header .section-eyebrow { justify-content: center; }
.section-eyebrow > span { width: 6px; height: 6px; border-radius: 50%; background: #b56cde; box-shadow: 0 0 0 4px rgba(181, 108, 222, 0.1); }
.cloud-header h1 { font-size: clamp(28px, 3.8vw, 42px); font-weight: 800; line-height: 1.3; letter-spacing: -0.035em; margin: 0 0 10px; color: var(--article-ink); }
.cloud-description { margin: 0 auto; max-width: 520px; font-size: 14px; line-height: 1.8; color: var(--article-muted); text-wrap: pretty; }
.cloud-stage { position: relative; flex: 1; min-height: 300px; display: flex; justify-content: center; align-items: center; width: 100%; }
.browse-cue { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; padding: 16px 0 0; border-top: 1px solid var(--article-line); font-size: 12px; color: var(--article-muted); text-decoration: none; }
.browse-cue-action { display: flex; gap: 8px; align-items: center; font-size: 13px; color: var(--article-accent); }
svg { fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; flex-shrink: 0; }
.article-library { margin-top: 28px; padding: 36px 40px 20px; scroll-margin-top: 88px; outline: none; }
.library-header { display: flex; justify-content: space-between; gap: 20px; align-items: flex-end; margin-bottom: 25px; }
.library-header h2 { margin: 0; font-size: 26px; letter-spacing: -0.025em; line-height: 1.35; display: flex; align-items: center; gap: 12px; color: var(--article-ink); }
.total-count { font-size: 12px; letter-spacing: 0; font-weight: 500; padding: 3px 9px; border-radius: 8px; color: var(--article-accent); background: rgba(124, 58, 237, 0.08); }
.library-caption { font-size: 12px; margin: 0 0 3px; color: var(--article-muted); }
.search-bar { display: flex; align-items: center; gap: 12px; padding: 0 16px; min-height: 54px; border: 1px solid rgba(111, 83, 148, 0.18); border-radius: 14px; color: var(--article-muted); background: rgba(255, 255, 255, 0.23); transition: border-color 160ms, box-shadow 160ms; }
.search-bar:focus-within { border-color: rgba(124, 58, 237, 0.58); box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.08); }
.search-bar input { min-width: 0; width: 100%; border: 0; outline: 0; background: transparent; color: var(--article-ink); font: inherit; font-size: 14px; line-height: 1.6; padding: 14px 0; }
.search-bar input::placeholder { color: var(--article-muted); opacity: 0.85; }
.search-bar input::-webkit-search-cancel-button { display: none; }
.search-hint { font-size: 11px; white-space: nowrap; padding: 2px 7px; border: 1px solid var(--article-line); border-radius: 5px; }
.clear-search { width: 36px; height: 40px; border: 0; border-radius: 8px; background: transparent; font-size: 24px; color: var(--article-muted); cursor: pointer; flex-shrink: 0; }
.library-tools { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin: 18px 0 16px; }
.format-filters { display: flex; flex-wrap: wrap; gap: 6px; }
.format-filters button { padding: 7px 12px; min-height: 36px; border: 1px solid transparent; border-radius: 9px; background: transparent; color: var(--article-muted); font: inherit; font-size: 12px; cursor: pointer; }
.format-filters button[aria-pressed='true'] { background: rgba(124, 58, 237, 0.11); color: var(--article-accent); border-color: rgba(124, 58, 237, 0.13); font-weight: 600; }
.result-count { margin: 0; white-space: nowrap; font-size: 12px; color: var(--article-muted); }
.article-row { border-top: 1px solid var(--article-line); }
.article-link { display: flex; gap: 20px; align-items: center; padding: 25px 10px; color: inherit; text-decoration: none; border-radius: 12px; transition: background-color 160ms, transform 160ms; }
.article-format { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 54px; height: 62px; font-size: 11px; font-weight: 700; letter-spacing: 0.02em; color: var(--article-accent); border: 1px solid rgba(136, 88, 196, 0.16); border-radius: 11px 11px 16px 11px; background: linear-gradient(150deg, rgba(240, 223, 255, 0.4), rgba(255, 255, 255, 0.13)); }
.article-copy { min-width: 0; flex: 1; }
.article-meta { display: flex; gap: 9px; flex-wrap: wrap; margin-bottom: 7px; font-size: 11px; color: var(--article-muted); }
.article-copy h3 { margin: 0 0 8px; font-size: 19px; line-height: 1.5; font-weight: 650; letter-spacing: -0.02em; overflow-wrap: anywhere; color: var(--article-ink); }
.article-summary { margin: 0; font-size: 13px; line-height: 1.85; color: var(--article-muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; overflow-wrap: anywhere; }
.article-tags { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; color: var(--article-accent); font-size: 11px; }
.read-link { display: flex; gap: 7px; align-items: center; color: var(--article-accent); font-size: 12px; flex-shrink: 0; }
.pagination { display: flex; justify-content: space-between; align-items: center; gap: 12px; border-top: 1px solid var(--article-line); padding-top: 22px; margin-top: 6px; font-size: 12px; color: var(--article-muted); }
.pagination button, .quiet-button { padding: 9px 14px; min-height: 40px; background: var(--article-surface); border: 1px solid var(--article-line); border-radius: 9px; color: var(--article-accent); font: inherit; font-size: 13px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: default; }
.library-footer { margin: 26px 0 0; padding-top: 16px; border-top: 1px solid var(--article-line); text-align: center; color: var(--article-muted); font-size: 11px; letter-spacing: 0.05em; }
.panel-state, .list-empty { padding: 44px 20px; text-align: center; font-size: 14px; color: var(--article-muted); line-height: 1.8; }
.panel-state p, .list-empty p { margin: 0 0 14px; }
.list-empty h3 { font-size: 18px; color: var(--article-ink); font-weight: 600; margin: 6px 0 8px; }
.empty-symbol { font-size: 36px; color: var(--article-accent); }
.article-opening { position: absolute; bottom: 6px; left: 50%; transform: translateX(-50%); white-space: nowrap; padding: 8px 15px; border-radius: 20px; background: rgba(255, 255, 255, 0.7); color: var(--article-accent); font-size: 13px; }
.loading-orbit { display: inline-block; width: 24px; height: 24px; border: 2px solid var(--article-line); border-top-color: var(--article-accent); border-radius: 50%; margin-bottom: 12px; animation: orbit 1s linear infinite; }
.list-skeleton > div { padding: 30px 0; border-top: 1px solid var(--article-line); }
.list-skeleton span { display: block; width: 45%; height: 17px; border-radius: 5px; background: rgba(111, 83, 148, 0.09); margin-bottom: 12px; }
.list-skeleton span + span { width: 80%; height: 12px; margin-bottom: 0; }
.visually-hidden { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
button:focus-visible, a:focus-visible { outline: 2px solid var(--article-accent); outline-offset: 4px; }
@keyframes orbit { to { transform: rotate(360deg); } }
@media (hover: hover) {
  .article-link:hover { background: rgba(255, 255, 255, 0.15); transform: translateX(3px); }
  .article-link:hover h3 { color: var(--article-accent); }
  .format-filters button:hover, .clear-search:hover { background: rgba(124, 58, 237, 0.06); }
}
@media (max-width: 768px) {
  .articles-page { width: calc(100% - 32px); margin: 16px auto 32px; }
  .cloud-intro { min-height: calc(100svh - 88px); padding: 28px 20px 18px; }
  .article-library { margin-top: 20px; padding: 26px 22px 18px; scroll-margin-top: 76px; }
  .library-caption { display: none; }
  .article-glass { border-radius: 20px; }
}
@media (max-width: 480px) {
  .cloud-intro { padding: 26px 12px 16px; }
  .cloud-stage { min-height: 300px; }
  .cloud-description { font-size: 13px; padding: 0 10px; }
  .browse-cue { margin: 0 6px; gap: 8px; font-size: 11px; }
  .browse-cue-action { font-size: 12px; gap: 4px; }
  .section-eyebrow { font-size: 11px; }
  .article-library { padding: 24px 18px 18px; }
  .library-header { margin-bottom: 22px; }
  .library-header h2 { font-size: 23px; }
  .search-bar { padding: 0 12px; gap: 9px; min-height: 50px; }
  .search-bar input { font-size: 16px; }
  .search-hint { display: none; }
  .library-tools { align-items: flex-start; gap: 8px; margin-top: 14px; }
  .result-count { padding-top: 9px; }
  .format-filters { gap: 3px; }
  .format-filters button { padding: 8px 10px; min-height: 40px; }
  .article-link { padding: 22px 0; gap: 12px; align-items: flex-start; }
  .article-format { width: 40px; height: 48px; font-size: 9px; border-radius: 8px 8px 12px 8px; }
  .article-copy h3 { font-size: 17px; }
  .article-meta { font-size: 10px; gap: 5px; margin-bottom: 6px; }
  .article-summary { font-size: 13px; }
  .read-link { margin-top: 26px; }
  .read-link > span { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .loading-orbit { animation: none; }
  .article-link, .search-bar { transition: none; }
  .article-link:hover { transform: none; }
}
</style>
