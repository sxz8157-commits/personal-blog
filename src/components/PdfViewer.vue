<template>
  <section class="pdf-viewer" :aria-busy="loading || rendering">
    <div class="pdf-toolbar" role="toolbar" aria-label="PDF 页码导航">
      <button type="button" :disabled="!pageCount || page <= 1" @click="goToPage(page - 1)">上一页</button>
      <label class="pdf-page-control">
        <span>第</span>
        <input v-model="pageInput" type="number" inputmode="numeric" min="1" :max="pageCount || 1" :disabled="!pageCount" aria-label="PDF 页码" @change="submitPage" @keydown.enter.prevent="submitPage" />
        <span>/ {{ pageCount || '—' }} 页</span>
      </label>
      <button type="button" :disabled="!pageCount || page >= pageCount" @click="goToPage(page + 1)">下一页</button>
    </div>
    <p v-if="loading" class="pdf-state" role="status">正在加载 PDF…</p>
    <p v-else-if="error" class="pdf-state pdf-error" role="alert">{{ error }}</p>
    <p v-else-if="rendering" class="pdf-state" role="status">正在显示第 {{ page }} 页…</p>
    <div ref="pageHost" class="pdf-page-host">
      <div ref="pageSurface" class="pdf-page" :class="{ 'page-ready': renderedPage > 0 }" :data-page="renderedPage">
        <canvas ref="canvasEl" class="pdf-canvas" :aria-label="`PDF 第 ${page} 页`" />
        <div ref="textLayerEl" class="textLayer" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { installPdfPromiseCompat } from './pdfPromiseCompat'

const props = defineProps({
  src: { type: String, required: true },
  page: { type: Number, default: 1 }
})
const emit = defineEmits(['update:page', 'outline-change', 'page-change', 'rendered'])
const pageHost = ref(null)
const pageSurface = ref(null)
const canvasEl = ref(null)
const textLayerEl = ref(null)
const pageCount = ref(0)
const pageInput = ref(String(props.page))
const renderedPage = ref(0)
const loading = ref(true)
const rendering = ref(false)
const error = ref('')
const MAX_CANVAS_PIXELS = 4_000_000
let pdfjs = null
let documentTask = null
let pdfDocument = null
let workerPort = null
let pdfWorker = null
let cancelWorkerReady = null
let renderTask = null
let textTask = null
let resizeObserver = null
let resizeTimer = null
let lastWidth = 0
let documentVersion = 0
let renderVersion = 0
let renderQueue = Promise.resolve()
let disposed = false

function goToPage(value) {
  if (!pageCount.value) return
  const next = Math.max(1, Math.min(pageCount.value, Math.trunc(Number(value) || 1)))
  pageInput.value = String(next)
  emit('update:page', next)
}

function submitPage() {
  goToPage(pageInput.value)
}

function cancelRendering() {
  renderTask?.cancel()
  textTask?.cancel()
}

async function destroyDocument() {
  renderVersion++
  cancelRendering()
  const oldTask = documentTask
  const oldWorker = pdfWorker
  const oldPort = workerPort
  documentTask = null
  pdfDocument = null
  pdfWorker = null
  workerPort = null
  cancelWorkerReady?.()
  cancelWorkerReady = null
  if (oldTask) {
    try {
      await oldTask.destroy()
    } catch (destroyError) {
      console.warn('清理 PDF 文档失败:', destroyError.message)
    }
  }
  oldWorker?.destroy()
  oldPort?.terminate()
}

function waitForWorker(port) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => finish(new Error('PDF 渲染服务加载超时，请刷新后重试')), 20000)
    function finish(error) {
      clearTimeout(timeout)
      port.removeEventListener('message', onMessage)
      port.removeEventListener('error', onError)
      cancelWorkerReady = null
      if (error) reject(error)
      else resolve()
    }
    function onMessage(event) {
      if (event.data?.type === 'blog-pdf-worker-ready') finish()
      else if (event.data?.type === 'blog-pdf-worker-error') finish(new Error(event.data.message))
    }
    function onError(event) { finish(new Error(event.message || '当前浏览器无法启动 PDF 渲染服务')) }
    cancelWorkerReady = () => finish(new DOMException('PDF 加载已取消', 'AbortError'))
    port.addEventListener('message', onMessage)
    port.addEventListener('error', onError)
  })
}

async function readOutline(document, version) {
  const items = []
  try {
    const outline = await document.getOutline()
    async function walk(nodes, level = 1) {
      for (const node of nodes || []) {
        if (disposed || version !== documentVersion || items.length >= 1200) return
        let page = null
        if (node.dest) {
          try {
            const destination = typeof node.dest === 'string' ? await document.getDestination(node.dest) : node.dest
            if (Array.isArray(destination) && destination[0] != null) {
              page = typeof destination[0] === 'number'
                ? destination[0] + 1
                : await document.getPageIndex(destination[0]) + 1
            }
          } catch (destinationError) {
            if (disposed || version !== documentVersion) return
            console.warn('PDF 大纲页码无法读取:', destinationError.message)
          }
        }
        items.push({ id: `${items.length}-${level}`, title: String(node.title || '').trim() || '(未命名标题)', level, page })
        if (node.items?.length) await walk(node.items, Math.min(level + 1, 6))
      }
    }
    await walk(outline)
    if (!disposed && version === documentVersion) {
      emit('outline-change', { loading: false, items, error: items.length ? '' : '该 PDF 未包含大纲书签' })
    }
  } catch (outlineError) {
    if (!disposed && version === documentVersion) {
      emit('outline-change', { loading: false, items: [], error: outlineError.message || 'PDF 大纲读取失败' })
    }
  }
}

async function loadDocument() {
  const version = ++documentVersion
  loading.value = true
  error.value = ''
  pageCount.value = 0
  renderedPage.value = 0
  emit('outline-change', { loading: true, items: [], error: '' })
  await destroyDocument()
  if (disposed || version !== documentVersion) return
  try {
    // 先补齐旧移动浏览器缺少的 API，再加载官方 legacy 包其余兼容实现。
    installPdfPromiseCompat()
    pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs')
    if (disposed || version !== documentVersion) return
    workerPort = new Worker(new URL('./pdfWorkerCompat.js', import.meta.url), { type: 'module' })
    await waitForWorker(workerPort)
    if (disposed || version !== documentVersion) return
    pdfWorker = new pdfjs.PDFWorker({ port: workerPort })
    // 仅保留一页画布，按需请求 PDF 分段，不预取整本文档。
    const task = pdfjs.getDocument({ url: props.src, worker: pdfWorker, isEvalSupported: false, disableAutoFetch: true, disableStream: true })
    documentTask = task
    const document = await task.promise
    if (disposed || version !== documentVersion) return
    pdfDocument = document
    pageCount.value = document.numPages
    goToPage(props.page)
    loading.value = false
    await nextTick()
    requestRender()
    void readOutline(document, version)
  } catch (loadError) {
    if (disposed || version !== documentVersion) return
    loading.value = false
    error.value = loadError.message || 'PDF 加载失败，请稍后重试'
    emit('outline-change', { loading: false, items: [], error: error.value })
  }
}

function requestRender() {
  const version = ++renderVersion
  cancelRendering()
  // 串行渲染，快速翻页时旧任务先取消，避免同一画布并发绘制和内存堆积。
  renderQueue = renderQueue.then(async () => {
    const document = pdfDocument
    const width = pageHost.value?.clientWidth || 0
    if (disposed || version !== renderVersion || !document || width < 1) return
    rendering.value = true
    error.value = ''
    const target = Math.max(1, Math.min(document.numPages, props.page))
    let documentPage = null
    let currentRender = null
    let currentText = null
    try {
      documentPage = await document.getPage(target)
      if (disposed || version !== renderVersion) return
      const original = documentPage.getViewport({ scale: 1 })
      const viewport = documentPage.getViewport({ scale: width / original.width })
      const ratio = Math.min(window.devicePixelRatio || 1, 2, Math.sqrt(MAX_CANVAS_PIXELS / (viewport.width * viewport.height)), 8192 / Math.max(viewport.width, viewport.height))
      const canvas = canvasEl.value
      canvas.width = Math.max(1, Math.floor(viewport.width * ratio))
      canvas.height = Math.max(1, Math.floor(viewport.height * ratio))
      canvas.style.width = `${viewport.width}px`
      canvas.style.height = `${viewport.height}px`
      pageSurface.value.style.width = `${viewport.width}px`
      pageSurface.value.style.height = `${viewport.height}px`
      pageSurface.value.style.setProperty('--total-scale-factor', String(viewport.scale * viewport.userUnit))
      textLayerEl.value.replaceChildren()
      currentRender = documentPage.render({ canvasContext: canvas.getContext('2d'), canvas, viewport, transform: ratio === 1 ? null : [ratio, 0, 0, ratio, 0, 0] })
      renderTask = currentRender
      currentText = new pdfjs.TextLayer({ textContentSource: documentPage.streamTextContent({ includeMarkedContent: true }), container: textLayerEl.value, viewport })
      // 显式尺寸避免旧移动 WebView 不支持 CSS round() 时文字层错位。
      textLayerEl.value.style.width = `${viewport.width}px`
      textLayerEl.value.style.height = `${viewport.height}px`
      textTask = currentText
      await Promise.all([currentRender.promise, currentText.render()])
      if (disposed || version !== renderVersion) return
      renderedPage.value = target
      emit('rendered', { page: target, pages: document.numPages })
    } catch (renderError) {
      if (!disposed && version === renderVersion && !['RenderingCancelledException', 'AbortException'].includes(renderError.name)) {
        error.value = renderError.message || 'PDF 页面显示失败'
      }
    } finally {
      currentRender?.cancel()
      currentText?.cancel()
      if (renderTask === currentRender) renderTask = null
      if (textTask === currentText) textTask = null
      documentPage?.cleanup()
      if (!disposed && version === renderVersion) rendering.value = false
    }
  }).catch(queueError => {
    if (!disposed) {
      rendering.value = false
      error.value = queueError.message || 'PDF 页面显示失败'
      console.warn('PDF 渲染队列失败:', queueError.message)
    }
  })
}

watch(() => props.src, loadDocument, { immediate: true })
watch(() => props.page, value => {
  pageInput.value = String(value)
  emit('page-change')
  requestRender()
})

onMounted(() => {
  resizeObserver = new ResizeObserver(() => {
    const width = pageHost.value?.clientWidth || 0
    if (width < 1 || Math.abs(width - lastWidth) < 1) return
    lastWidth = width
    clearTimeout(resizeTimer)
    resizeTimer = setTimeout(requestRender, 80)
  })
  resizeObserver.observe(pageHost.value)
})

onUnmounted(() => {
  disposed = true
  documentVersion++
  resizeObserver?.disconnect()
  clearTimeout(resizeTimer)
  void destroyDocument().then(() => pdfjs?.TextLayer.cleanup())
  if (canvasEl.value) canvasEl.value.width = canvasEl.value.height = 0
})
</script>

<style scoped lang="scss">
.pdf-viewer { min-width: 0; width: 100%; }
.pdf-toolbar {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 0;
  margin-bottom: 14px;
  border-bottom: 1px solid rgba(124, 58, 237, 0.18);
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(12px);
  border-radius: 10px;
  color: #302834;
}
.pdf-toolbar button {
  min-height: 40px;
  padding: 6px 12px;
  border: 1px solid rgba(124, 58, 237, 0.24);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.45);
  color: #6d28d9;
  cursor: pointer;
  &:disabled { opacity: 0.42; cursor: default; }
}
.pdf-page-control { display: inline-flex; align-items: center; gap: 6px; font-size: 0.9rem; white-space: nowrap; }
.pdf-page-control input { width: 56px; min-height: 38px; padding: 4px; border: 1px solid rgba(124, 58, 237, 0.25); border-radius: 6px; background: rgba(255, 255, 255, 0.75); color: #1a1a1a; text-align: center; }
.pdf-state { margin: 12px 0; color: #333; font-size: 0.95rem; }
.pdf-error { color: #b91c1c; }
.pdf-page-host { width: 100%; min-width: 0; }
.pdf-page { position: relative; max-width: 100%; background: #fff; overflow: hidden; visibility: hidden; --scale-round-x: 1px; --scale-round-y: 1px; }
.pdf-page.page-ready { visibility: visible; }
.pdf-canvas { display: block; max-width: 100%; }
.textLayer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  overflow: clip;
  text-align: initial;
  line-height: 1;
  letter-spacing: normal;
  word-spacing: normal;
  text-size-adjust: none;
  forced-color-adjust: none;
  transform-origin: 0 0;
  --min-font-size: 1;
  --text-scale-factor: calc(var(--total-scale-factor) * var(--min-font-size));
  --min-font-size-inv: calc(1 / var(--min-font-size));
  :deep(span), :deep(br) { color: transparent; position: absolute; white-space: pre; cursor: text; transform-origin: 0 0; user-select: text; }
  :deep(> :not(.markedContent)), :deep(.markedContent span:not(.markedContent)) {
    --font-height: 0;
    --scale-x: 1;
    --rotate: 0deg;
    font-size: calc(var(--text-scale-factor) * var(--font-height));
    transform: rotate(var(--rotate)) scaleX(var(--scale-x)) scale(var(--min-font-size-inv));
  }
  :deep(.markedContent) { display: contents; }
  :deep(span::selection) { background: rgba(124, 58, 237, 0.3); }
}
@media (max-width: 640px) {
  .pdf-toolbar { gap: 6px; }
  .pdf-toolbar button { padding: 6px 9px; font-size: 0.82rem; }
  .pdf-page-control { gap: 4px; font-size: 0.8rem; }
  .pdf-page-control input { width: 44px; }
}
</style>
