<template>
  <div class="article-detail-page">
    <!-- 文章头部 -->
    <header class="article-header" v-if="article">
      <div class="article-header-inner">
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
          <span class="meta-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ formatDate(article.created_at) }}
          </span>
          <span class="meta-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <line x1="7" y1="7" x2="7.01" y2="7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ article.category?.name }}
          </span>
        </div>
      </div>
    </header>

    <!-- 封面 -->
    <div class="article-cover-wrapper" v-if="article && article.cover_image">
      <img :src="article.cover_image" :alt="article.title" class="article-cover" />
    </div>

    <!-- 文章内容区域 -->
    <div class="article-layout" :class="{ 'no-toc': !hasTocSidebar }" v-if="article">
      <!-- 左侧大纲 -->
      <div v-if="hasTocSidebar" class="article-toc-sidebar">
        <div class="toc-sticky glass-card">
          <h3 class="toc-title">大纲</h3>
          <div class="toc-list">
            <template v-if="fileType === 'md' && headings.length > 0">
              <div
              v-for="heading in headings" 
              :key="heading.id"
              class="toc-item"
              :class="'toc-level-' + heading.level"
            >
              <a 
                href="#"
                @click.prevent="scrollToHeading(heading.id)"
              >
                {{ heading.text }}
              </a>
              </div>
            </template>
            <template v-else-if="fileType === 'pdf'">
              <div class="toc-item toc-level-1">
                <a href="#" @click.prevent="scrollToTop">文档开头</a>
              </div>
              <div v-if="pdfOutlineLoading" class="toc-empty">正在读取 PDF 大纲...</div>
              <div v-else-if="pdfOutlineError" class="toc-empty">{{ pdfOutlineError }}</div>
              <template v-else>
                <div
                  v-for="item in pdfOutline"
                  :key="item.id"
                  class="toc-item"
                  :class="'toc-level-' + item.level"
                >
                  <a
                    href="#"
                    @click.prevent="jumpToPdfPage(item.page)"
                  >
                    {{ item.title }}
                    <span v-if="item.page"> (P{{ item.page }})</span>
                  </a>
                </div>
              </template>
              <div class="toc-item toc-level-1">
                <a :href="fileUrl" target="_blank" rel="noopener noreferrer">新窗口打开 PDF</a>
              </div>
            </template>
            <template v-else-if="fileType === 'xlsx'">
              <div v-if="xlsxLoading" class="toc-empty">正在读取 XLSX 工作表...</div>
              <div v-else-if="xlsxError" class="toc-empty">{{ xlsxError }}</div>
              <div v-else-if="!xlsxSheets.length" class="toc-empty">该 XLSX 未检测到工作表</div>
              <template v-else>
                <div
                  v-for="sheet in xlsxSheets"
                  :key="sheet"
                  class="toc-item toc-level-1"
                >
                  <a
                    href="#"
                    :class="{ active: xlsxActiveSheet === sheet }"
                    @click.prevent="setXlsxActiveSheet(sheet)"
                  >
                    {{ sheet }}
                  </a>
                </div>
              </template>
            </template>
          </div>
        </div>
      </div>

      <!-- 文章内容 -->
      <article class="article-content-section">
        <div class="article-content glass-card">
          <div v-if="fileType === 'md'" class="content-body" v-html="renderedContent"></div>
          <div v-else-if="fileType === 'xmind'" class="content-body file-content xmind-content">
            <h3 class="file-title">{{ article?.title || 'XMind 预览' }}</h3>
            <p class="file-meta">当前格式：XMIND（站内解析预览）</p>
            <div
              class="xmind-panel"
              @wheel.prevent="onXmindWheel"
              @mousedown="onXmindMouseDown"
              @mousemove="onXmindMouseMove"
              @mouseup="onXmindMouseUp"
              @mouseleave="onXmindMouseUp"
            >
              <p v-if="xmindLoading" class="xmind-state">正在解析 XMIND...</p>
              <p v-else-if="xmindError" class="xmind-state xmind-error">{{ xmindError }}</p>
              <div v-else class="xmind-outline">
                <img
                  v-if="xmindPreviewImage"
                  class="xmind-preview-map"
                  :src="xmindPreviewImage"
                  alt="XMIND 导图预览"
                  :style="{ transform: `translate(${xmindOffsetX}px, ${xmindOffsetY}px) scale(${xmindZoom})` }"
                />
                <p v-if="xmindPreviewImage" class="xmind-map-tip">已按导图视图展示（与 XMind 预览风格一致）</p>
                <div
                  v-if="!xmindPreviewImage"
                  v-for="line in xmindLines"
                  :key="line.id"
                  class="xmind-node"
                  :style="{ paddingLeft: `${line.depth * 18 + 10}px` }"
                >
                  <span class="xmind-dot">{{ line.depth === 0 ? '●' : '•' }}</span>
                  <span class="xmind-text">{{ line.title }}</span>
                </div>
              </div>
            </div>
            <div v-if="xmindPreviewImage" class="xmind-actions">
              <button class="file-open-btn" type="button" @click="resetXmindView">重置视图</button>
            </div>
          </div>
          <div v-else-if="fileType === 'docx'" class="content-body file-content docx-content">
            <h3 class="file-title">{{ article?.title || 'DOCX 预览' }}</h3>
            <p class="file-meta">当前格式：DOCX（站内解析预览）</p>
            <div class="docx-panel">
              <p v-if="docxLoading" class="xmind-state">正在解析 DOCX...</p>
              <p v-else-if="docxError" class="xmind-state xmind-error">{{ docxError }}</p>
              <div v-else class="docx-body" v-html="docxHtml"></div>
            </div>
          </div>
          <div v-else-if="fileType === 'xlsx'" class="content-body file-content xlsx-content">
            <h3 class="file-title">{{ article?.title || 'XLSX 预览' }}</h3>
            <p class="file-meta">当前格式：XLSX（站内解析预览）</p>
            <div class="xlsx-panel">
              <p v-if="xlsxLoading" class="xmind-state">正在解析 XLSX...</p>
              <p v-else-if="xlsxError" class="xmind-state xmind-error">{{ xlsxError }}</p>
              <div v-else class="xlsx-table-wrap">
                <table class="xlsx-table">
                  <tbody>
                    <tr v-for="(row, rIdx) in xlsxTable" :key="`r-${rIdx}`">
                      <th v-if="rIdx === 0" v-for="(cell, cIdx) in row" :key="`h-${cIdx}`">{{ cell }}</th>
                      <td v-else v-for="(cell, cIdx) in row" :key="`d-${rIdx}-${cIdx}`">{{ cell }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div v-else class="content-body file-content">
            <h3 class="file-title">{{ article?.title || '文档预览' }}</h3>
            <p class="file-meta">当前格式：{{ fileType.toUpperCase() }}</p>
            <iframe
              v-if="canInlinePreview"
              class="pdf-preview"
              :src="pdfPreviewUrl"
              title="PDF 预览"
            />
            <p v-else class="file-tip">当前格式暂不支持站内解析预览，请点击下方按钮打开。</p>
            <a class="file-open-btn" :href="fileUrl" target="_blank" rel="noopener noreferrer">打开文档</a>
          </div>
        </div>
      </article>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-dots"><span></span><span></span><span></span></div>
      <p>加载中...</p>
    </div>

    <!-- 未找到 -->
    <div v-if="!loading && !article" class="not-found">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/>
        <path d="M8 15s1.5-2 4-2 4 2 4 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="9" y1="9" x2="9.01" y2="9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="15" y1="9" x2="15.01" y2="9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <p>文章不存在</p>
      <router-link to="/articles" class="btn-back">返回文章列表</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import JSZip from 'jszip'
import * as pdfjsLib from 'pdfjs-dist'
import mammoth from 'mammoth'
import * as XLSX from 'xlsx'

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString()

// ================== 【新增】路径生成函数 START ==================
// 简单的根路径生成函数，确保生成 /wenz/文件名 格式
// ================== 【修改】路径生成函数 START ==================
function buildPublicAssetPath(relativePath) {
  const normalized = String(relativePath || '').replace(/^\/+/, '')

  // 关键修改：如果是 wenz, tupian, assets 开头的路径，必须走后端 API 代理
  if (normalized.startsWith('wenz/') || normalized.startsWith('tupian/') || normalized.startsWith('assets/')) {
    return `/api/files/${normalized}`
  }

  return `/${normalized}`
}
// ================== 【修改】路径生成函数 END ====================


const route = useRoute()
const article = ref(null)
const content = ref('')
const loading = ref(false)
const headings = ref([])
const fileType = ref('md')
const fileUrl = ref('')
const xmindLoading = ref(false)
const xmindError = ref('')
const xmindLines = ref([])
const xmindPreviewImage = ref('')
const xmindZoom = ref(1)
const xmindOffsetX = ref(0)
const xmindOffsetY = ref(0)
const xmindDragging = ref(false)
const xmindDragStartX = ref(0)
const xmindDragStartY = ref(0)
const pdfOutlineLoading = ref(false)
const pdfOutlineError = ref('')
const pdfOutline = ref([])
const pdfCurrentPage = ref(1)
const docxLoading = ref(false)
const docxError = ref('')
const docxHtml = ref('')
const xlsxLoading = ref(false)
const xlsxError = ref('')
const xlsxSheets = ref([])
const xlsxActiveSheet = ref('')
const xlsxTable = ref([])
const xlsxSheetData = ref({})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 从 Markdown 内容中提取标题（支持 # ~ ######）
const processHeadings = (mdContent) => {
  const headingsList = []
  let headingIndex = 0
  let source = String(mdContent || '').replace(/\r\n/g, '\n')
  source = source.replace(/^\s*---\s*\n[\s\S]*?\n---\s*\n?/, '')
  const lines = source.split('\n')
  let inCode = false

  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      inCode = !inCode
      continue
    }
    if (inCode) continue

    const m = line.match(/^(#{1,6})\s+(.+)$/)
    if (!m) continue
    const id = `heading-${headingIndex++}`
    headingsList.push({
      level: m[1].length,
      text: m[2].trim(),
      id
    })
  }

  return headingsList
}

function escapeHtml(raw = '') {
  return String(raw)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function applyInlineMarkdown(text = '') {
  const escaped = escapeHtml(text)
  return escaped
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer noopener">$1</a>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
}

function renderMarkdownContent(md = '') {
  if (!md) return ''

  let source = md.replace(/\r\n/g, '\n')
  // Strip YAML frontmatter to avoid metadata text appearing in content.
  source = source.replace(/^\s*---\s*\n[\s\S]*?\n---\s*\n?/, '')
  const lines = source.split('\n')
  const out = []
  let headingIndex = 0

  let inCode = false
  let codeLang = ''
  let codeLines = []
  let inUl = false
  let inOl = false
  let inBlockquote = false
  let paragraphLines = []

  const flushParagraph = () => {
    if (!paragraphLines.length) return
    out.push(`<p>${applyInlineMarkdown(paragraphLines.join(' '))}</p>`)
    paragraphLines = []
  }

  const closeLists = () => {
    if (inUl) {
      out.push('</ul>')
      inUl = false
    }
    if (inOl) {
      out.push('</ol>')
      inOl = false
    }
  }

  const closeBlockquote = () => {
    if (inBlockquote) {
      out.push('</blockquote>')
      inBlockquote = false
    }
  }

  for (const rawLine of lines) {
    const line = rawLine || ''
    const trimmed = line.trim()

    // fenced code block
    if (trimmed.startsWith('```')) {
      flushParagraph()
      closeLists()
      closeBlockquote()
      if (!inCode) {
        inCode = true
        codeLang = trimmed.replace(/^```/, '').trim()
        codeLines = []
      } else {
        out.push(`<pre><code class="language-${codeLang}">${escapeHtml(codeLines.join('\n'))}</code></pre>`)
        inCode = false
        codeLang = ''
        codeLines = []
      }
      continue
    }

    if (inCode) {
      codeLines.push(line)
      continue
    }

    // blank line closes open blocks that need separation
    if (!trimmed) {
      flushParagraph()
      closeLists()
      closeBlockquote()
      continue
    }

    // horizontal rule
    if (/^---+$/.test(trimmed)) {
      flushParagraph()
      closeLists()
      closeBlockquote()
      out.push('<hr />')
      continue
    }

    // headings
    const h = line.match(/^(#{1,6})\s+(.+)$/)
    if (h) {
      flushParagraph()
      closeLists()
      closeBlockquote()
      const level = Math.max(1, Math.min(6, h[1].length))
      const id = `heading-${headingIndex++}`
      out.push(`<h${level} id="${id}">${applyInlineMarkdown(h[2].trim())}</h${level}>`)
      continue
    }

    // blockquote
    const bq = line.match(/^>\s?(.*)$/)
    if (bq) {
      flushParagraph()
      closeLists()
      if (!inBlockquote) {
        out.push('<blockquote>')
        inBlockquote = true
      }
      out.push(`<p>${applyInlineMarkdown(bq[1])}</p>`)
      continue
    }

    // unordered list
    const ul = line.match(/^\s*[-*]\s+(.+)$/)
    if (ul) {
      flushParagraph()
      closeBlockquote()
      if (!inUl) {
        closeLists()
        out.push('<ul>')
        inUl = true
      }
      out.push(`<li>${applyInlineMarkdown(ul[1].trim())}</li>`)
      continue
    }

    // ordered list
    const ol = line.match(/^\s*\d+\.\s+(.+)$/)
    if (ol) {
      flushParagraph()
      closeBlockquote()
      if (!inOl) {
        closeLists()
        out.push('<ol>')
        inOl = true
      }
      out.push(`<li>${applyInlineMarkdown(ol[1].trim())}</li>`)
      continue
    }

    // default paragraph line
    closeLists()
    closeBlockquote()
    paragraphLines.push(trimmed)
  }

  if (inCode) {
    out.push(`<pre><code class="language-${codeLang}">${escapeHtml(codeLines.join('\n'))}</code></pre>`)
  }
  flushParagraph()
  closeLists()
  closeBlockquote()

  return out.join('\n')
}

const renderedContent = computed(() => {
  if (!content.value) return ''

  headings.value = processHeadings(content.value)
  return renderMarkdownContent(content.value)
})

const canInlinePreview = computed(() => fileType.value === 'pdf' && !!fileUrl.value)
const pdfPreviewUrl = computed(() => {
  if (!canInlinePreview.value) return ''
  const sep = fileUrl.value.includes('#') ? '&' : '#'
  return `${fileUrl.value}${sep}page=${pdfCurrentPage.value}`
})
const hasTocSidebar = computed(() => {
  if (fileType.value === 'md') return headings.value.length > 0
  if (fileType.value === 'pdf') return true
  if (fileType.value === 'xlsx') return true
  return false
})

function resetXmindPreview() {
  xmindLoading.value = false
  xmindError.value = ''
  xmindLines.value = []
  xmindPreviewImage.value = ''
  xmindZoom.value = 1
  xmindOffsetX.value = 0
  xmindOffsetY.value = 0
  xmindDragging.value = false
}

function resetPdfOutline() {
  pdfOutlineLoading.value = false
  pdfOutlineError.value = ''
  pdfOutline.value = []
  pdfCurrentPage.value = 1
}

function resetDocxPreview() {
  docxLoading.value = false
  docxError.value = ''
  docxHtml.value = ''
}

function resetXlsxPreview() {
  xlsxLoading.value = false
  xlsxError.value = ''
  xlsxSheets.value = []
  xlsxActiveSheet.value = ''
  xlsxTable.value = []
  xlsxSheetData.value = {}
}

function flattenXmindTopic(topic, depth = 0, out = [], maxNodes = 1500) {
  if (!topic || out.length >= maxNodes) return out
  const rawTitle = String(topic?.title || '').trim()
  const title = rawTitle || '(未命名主题)'
  out.push({ id: `${out.length}-${depth}`, title, depth })
  if (out.length >= maxNodes) return out

  const children = topic?.children || {}
  const attached = Array.isArray(children.attached) ? children.attached : []
  const detached = Array.isArray(children.detached) ? children.detached : []
  const allChildren = [...attached, ...detached]
  for (const child of allChildren) {
    flattenXmindTopic(child, depth + 1, out, maxNodes)
    if (out.length >= maxNodes) break
  }
  return out
}

async function loadXmindPreview(url) {
  resetXmindPreview()
  if (!url) {
    xmindError.value = '未找到 XMIND 文件地址'
    return
  }

  xmindLoading.value = true
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`文件请求失败（${res.status}）`)
    const buf = await res.arrayBuffer()
    const zip = await JSZip.loadAsync(buf)
    const thumbnailFile = Object.values(zip.files).find((f) => /(?:^|\/)thumbnails\/thumbnail\.(png|jpg|jpeg|webp)$/i.test(f.name))
      || Object.values(zip.files).find((f) => /(?:^|\/)thumbnail\.(png|jpg|jpeg|webp)$/i.test(f.name))
    if (thumbnailFile) {
      const extMatch = thumbnailFile.name.match(/\.(png|jpg|jpeg|webp)$/i)
      const ext = String(extMatch?.[1] || 'png').toLowerCase()
      const mime = ext === 'jpg' ? 'jpeg' : ext
      const base64 = await thumbnailFile.async('base64')
      xmindPreviewImage.value = `data:image/${mime};base64,${base64}`
    }

    const contentJsonFile = zip.file('content.json') || Object.values(zip.files).find((f) => /content\.json$/i.test(f.name))
    if (contentJsonFile) {
      const contentText = await contentJsonFile.async('string')
      const data = JSON.parse(contentText)
      const sheets = Array.isArray(data) ? data : []
      if (!sheets.length) throw new Error('XMIND 内容为空')
      const rootTopic = sheets[0]?.rootTopic
      if (!rootTopic) throw new Error('无法解析 XMIND 根主题')

      xmindLines.value = flattenXmindTopic(rootTopic)
      if (!xmindLines.value.length) throw new Error('没有可展示的主题内容')
      return
    }

    // 兼容旧版 XMIND：content.xml
    const contentXmlFile = zip.file('content.xml') || Object.values(zip.files).find((f) => /content\.xml$/i.test(f.name))
    if (!contentXmlFile) {
      throw new Error('暂不支持该 XMIND 版本（缺少 content.json/content.xml）')
    }
    const xmlText = await contentXmlFile.async('string')
    const xmlDoc = new DOMParser().parseFromString(xmlText, 'text/xml')
    const parserError = xmlDoc.querySelector('parsererror')
    if (parserError) throw new Error('XMIND XML 解析失败')

    const localName = (el) => String(el?.localName || el?.nodeName || '').toLowerCase()
    const getChildrenByLocal = (el, name) => Array.from(el?.children || []).filter((c) => localName(c) === name)

    const parseTopicXml = (topicEl, depth = 0, out = [], maxNodes = 1500) => {
      if (!topicEl || out.length >= maxNodes) return out
      const titleNode = getChildrenByLocal(topicEl, 'title')[0]
      const title = String(titleNode?.textContent || '').trim() || '(未命名主题)'
      out.push({ id: `${out.length}-${depth}`, title, depth })
      if (out.length >= maxNodes) return out

      const childrenNode = getChildrenByLocal(topicEl, 'children')[0]
      if (!childrenNode) return out
      const topicsGroups = getChildrenByLocal(childrenNode, 'topics')
      for (const group of topicsGroups) {
        const childTopics = getChildrenByLocal(group, 'topic')
        for (const child of childTopics) {
          parseTopicXml(child, depth + 1, out, maxNodes)
          if (out.length >= maxNodes) break
        }
        if (out.length >= maxNodes) break
      }
      return out
    }

    const sheetEl = Array.from(xmlDoc.getElementsByTagName('*')).find((el) => localName(el) === 'sheet')
    const rootTopicEl = sheetEl ? getChildrenByLocal(sheetEl, 'topic')[0] : null
    if (!rootTopicEl) throw new Error('无法解析 XMIND 根主题')
    xmindLines.value = parseTopicXml(rootTopicEl)
    if (!xmindLines.value.length) throw new Error('没有可展示的主题内容')
  } catch (err) {
    xmindError.value = err?.message || 'XMIND 解析失败'
  } finally {
    xmindLoading.value = false
  }
}

async function loadDocxPreview(url) {
  resetDocxPreview()
  if (!url) {
    docxError.value = '未找到 DOCX 地址'
    return
  }
  docxLoading.value = true
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`文件请求失败（${res.status}）`)
    const arrayBuffer = await res.arrayBuffer()
    const result = await mammoth.convertToHtml(
      { arrayBuffer },
      {
        styleMap: [
          "p[style-name='Heading 1'] => h1:fresh",
          "p[style-name='Heading 2'] => h2:fresh",
          "p[style-name='Heading 3'] => h3:fresh",
          "p[style-name='Heading 4'] => h4:fresh",
          "p[style-name='Heading 5'] => h5:fresh",
          "p[style-name='Heading 6'] => h6:fresh",
          "p[style-name='标题 1'] => h1:fresh",
          "p[style-name='标题 2'] => h2:fresh",
          "p[style-name='标题 3'] => h3:fresh",
          "p[style-name='标题 4'] => h4:fresh",
          "p[style-name='标题 5'] => h5:fresh",
          "p[style-name='标题 6'] => h6:fresh"
        ]
      }
    )
    const rawHtml = String(result?.value || '').trim()
    if (!rawHtml) {
      docxError.value = 'DOCX 内容为空或暂不支持解析'
      return
    }

    docxHtml.value = rawHtml
  } catch (err) {
    docxError.value = err?.message || 'DOCX 预览解析失败'
  } finally {
    docxLoading.value = false
  }
}

function setXlsxActiveSheet(name) {
  if (!name) return
  xlsxActiveSheet.value = name
  xlsxTable.value = xlsxSheetData.value[name] || []
}

async function loadXlsxPreview(url) {
  resetXlsxPreview()
  if (!url) {
    xlsxError.value = '未找到 XLSX 地址'
    return
  }
  xlsxLoading.value = true
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`文件请求失败（${res.status}）`)
    const arrayBuffer = await res.arrayBuffer()
    const wb = XLSX.read(arrayBuffer, { type: 'array' })
    const names = Array.isArray(wb?.SheetNames) ? wb.SheetNames : []
    if (!names.length) {
      xlsxError.value = 'XLSX 没有可读取工作表'
      return
    }

    const maxRows = 200
    const maxCols = 30
    const sheetDataMap = {}
    for (const name of names) {
      const sheet = wb.Sheets[name]
      const grid = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: false, defval: '' })
      sheetDataMap[name] = grid.slice(0, maxRows).map((row) => (Array.isArray(row) ? row.slice(0, maxCols) : []))
    }
    xlsxSheetData.value = sheetDataMap
    xlsxSheets.value = names
    setXlsxActiveSheet(names[0])
  } catch (err) {
    xlsxError.value = err?.message || 'XLSX 预览解析失败'
  } finally {
    xlsxLoading.value = false
  }
}

async function resolvePdfDestPage(pdfDoc, dest) {
  let target = dest
  if (typeof dest === 'string') {
    target = await pdfDoc.getDestination(dest)
  }
  if (!Array.isArray(target) || !target[0]) return null
  const pageIndex = await pdfDoc.getPageIndex(target[0])
  return pageIndex + 1
}

async function flattenPdfOutline(items, pdfDoc, level = 1, out = [], maxNodes = 1200) {
  if (!Array.isArray(items) || out.length >= maxNodes) return out
  for (const item of items) {
    if (!item || out.length >= maxNodes) break
    let page = null
    try {
      if (item.dest) page = await resolvePdfDestPage(pdfDoc, item.dest)
    } catch {
      page = null
    }
    out.push({
      id: `${out.length}-${level}`,
      title: String(item.title || '').trim() || '(未命名标题)',
      level,
      page
    })
    if (Array.isArray(item.items) && item.items.length) {
      await flattenPdfOutline(item.items, pdfDoc, Math.min(level + 1, 6), out, maxNodes)
    }
  }
  return out
}

async function loadPdfOutline(url) {
  resetPdfOutline()
  if (!url) {
    pdfOutlineError.value = '未找到 PDF 地址'
    return
  }
  pdfOutlineLoading.value = true
  try {
    const task = pdfjsLib.getDocument({ url })
    const pdfDoc = await task.promise
    const outline = await pdfDoc.getOutline()
    if (!outline || !outline.length) {
      pdfOutlineError.value = '该 PDF 未包含大纲书签'
      return
    }
    pdfOutline.value = await flattenPdfOutline(outline, pdfDoc)
    if (!pdfOutline.value.length) {
      pdfOutlineError.value = '该 PDF 未包含可解析的大纲'
    }
  } catch (err) {
    pdfOutlineError.value = err?.message || 'PDF 大纲解析失败'
  } finally {
    pdfOutlineLoading.value = false
  }
}

// 滚动到指定标题
const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    const offset = 100
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    window.scrollTo({
      top: elementPosition - offset,
      behavior: 'smooth'
    })
  }
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const jumpToPdfPage = (page) => {
  if (!page || page < 1) return
  pdfCurrentPage.value = page
}

const onXmindWheel = (e) => {
  if (!xmindPreviewImage.value) return
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.08 : 0.08
  xmindZoom.value = Math.max(0.4, Math.min(3.5, xmindZoom.value + delta))
}

const onXmindMouseDown = (e) => {
  if (!xmindPreviewImage.value) return
  if (e.button !== 0) return
  e.preventDefault()
  xmindDragging.value = true
  xmindDragStartX.value = e.clientX - xmindOffsetX.value
  xmindDragStartY.value = e.clientY - xmindOffsetY.value
}

const onXmindMouseMove = (e) => {
  if (!xmindDragging.value) return
  xmindOffsetX.value = e.clientX - xmindDragStartX.value
  xmindOffsetY.value = e.clientY - xmindDragStartY.value
}

const onXmindMouseUp = () => {
  xmindDragging.value = false
}

const resetXmindView = () => {
  xmindZoom.value = 1
  xmindOffsetX.value = 0
  xmindOffsetY.value = 0
}

const fetchArticle = async () => {
  loading.value = true
  try {
    const articleId = decodeURIComponent(String(route.params.id || ''))

    // 先尝试从 MD 文件获取
    try {
      const mdData = await request.get(`/api/md-articles/${encodeURIComponent(articleId)}`)
      article.value = {
        id: articleId,
        title: mdData.filename ? mdData.filename.replace(/\.[^.]+$/, '') : articleId,
        views: 0,
        likes: 0,
        category: null,
        created_at: ''
      }
      content.value = mdData.content || ''
      fileType.value = mdData.file_type || 'md'

      // ================== 【核心修改】fileUrl 赋值 START ==================
      // 确保生成 /wenz/文件名 的根路径
      if (mdData.filename) {
        fileUrl.value = buildPublicAssetPath(`wenz/${mdData.filename}`)
      } else {
        fileUrl.value = ''
      }
      // ================== 【核心修改】fileUrl 赋值 END ====================

      if (fileType.value === 'xmind') {
        await loadXmindPreview(fileUrl.value)
        resetPdfOutline()
        resetDocxPreview()
        resetXlsxPreview()
      } else if (fileType.value === 'pdf') {
        resetXmindPreview()
        await loadPdfOutline(fileUrl.value)
        resetDocxPreview()
        resetXlsxPreview()
      } else if (fileType.value === 'docx') {
        resetXmindPreview()
        resetPdfOutline()
        await loadDocxPreview(fileUrl.value)
        resetXlsxPreview()
      } else if (fileType.value === 'xlsx') {
        resetXmindPreview()
        resetPdfOutline()
        resetDocxPreview()
        await loadXlsxPreview(fileUrl.value)
      } else {
        resetXmindPreview()
        resetPdfOutline()
        resetDocxPreview()
        resetXlsxPreview()
      }
      return
    } catch {
      // MD 未命中时回退到数据库文章
    }

    // 如果 MD 文件没有，尝试从数据库获取
    try {
      const data = await request.get(`/api/articles/${articleId}`)
      article.value = data.article
      content.value = data.content || ''
      fileType.value = 'md'
      fileUrl.value = ''
      resetXmindPreview()
      resetPdfOutline()
      resetDocxPreview()
      resetXlsxPreview()
    } catch (dbError) {
      console.error('文章不存在:', dbError.message)
    }
  } catch (error) {
    console.error('获取文章详情失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchArticle() })
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.article-detail-page {
  padding-top: 16px;
  padding-bottom: 80px;
  min-height: 100vh;
  width: 100%;
}

.article-header {
  padding: 32px 2rem 24px;
  max-width: 900px;
  margin: 0 auto;
}

.article-header-inner {
  max-width: 800px;
}

.article-title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.3;
  margin-bottom: 16px;
}

.article-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 0.85rem;
}

.article-cover-wrapper {
  padding: 0 2rem;
  max-width: 900px;
  margin: 0 auto 32px;

  .article-cover {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 16px;
  }
}

// 主布局：左侧大纲 + 右侧内容
.article-layout {
  display: grid !important;
  grid-template-columns: 280px 1fr !important;
  gap: 40px !important;
  max-width: 1400px !important;
  margin: 0 auto !important;
  padding: 0 2rem !important;
  width: 100% !important;
}

.article-layout.no-toc {
  grid-template-columns: 1fr !important;
  max-width: 1320px !important;
}

// 左侧大纲
.article-toc-sidebar {
  grid-column: 1 !important;
  grid-row: 1 !important;

  @media (max-width: 1024px) {
    display: none !important;
  }

  .toc-sticky {
    position: sticky !important;
    top: 100px !important;
    max-height: calc(100vh - 120px) !important;
    overflow-y: auto !important;
    padding: 24px !important;
    background: rgba(255, 255, 255, 0.65) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
  }

  .toc-title {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
    margin: 0 0 20px 0 !important;
    padding: 0 0 12px 0 !important;
    border-bottom: 2px solid rgba(168, 85, 247, 0.2) !important;
    text-align: center !important;
  }

  .toc-list {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    width: 100% !important;
  }

  .toc-item {
    width: 100% !important;

    a {
      display: block !important;
      width: 100% !important;
      padding: 6px 12px !important;
      color: rgba(0, 0, 0, 0.65) !important;
      text-decoration: none !important;
      font-size: 0.85rem !important;
      line-height: 1.5 !important;
      border-radius: 6px !important;
      transition: all 0.2s ease !important;
      border-left: 3px solid transparent !important;
      word-break: break-word !important;
      white-space: normal !important;
      text-align: left !important;

      &:hover {
        background: rgba(168, 85, 247, 0.08) !important;
        color: #7c3aed !important;
      }

      &.active {
        background: rgba(168, 85, 247, 0.12) !important;
        color: #7c3aed !important;
        font-weight: 600 !important;
        border-left-color: #a855f7 !important;
      }
    }
  }

  // 层级缩进
  .toc-level-1 a {
    padding-left: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: rgba(0, 0, 0, 0.8) !important;
  }

  .toc-level-2 a {
    padding-left: 24px !important;
    font-size: 0.85rem !important;
  }

  .toc-level-3 a {
    padding-left: 36px !important;
    font-size: 0.8rem !important;
    color: rgba(0, 0, 0, 0.55) !important;
  }

  .toc-level-4 a,
  .toc-level-5 a,
  .toc-level-6 a {
    padding-left: 44px !important;
    font-size: 0.78rem !important;
    color: rgba(0, 0, 0, 0.5) !important;
  }

  .toc-empty {
    color: rgba(0, 0, 0, 0.4) !important;
    font-size: 0.9rem !important;
    text-align: center !important;
    padding: 40px 0 !important;
  }
}

// 文章内容
.article-content-section {
  grid-column: 2 !important;
  grid-row: 1 !important;
  min-width: 0 !important;
}

.article-layout.no-toc .article-content-section {
  grid-column: 1 !important;
}

.article-content {
  padding: 32px;
}

.content-body {
  max-width: 760px;
  margin: 0 auto;
  color: rgba(0, 0, 0, 0.75);
  line-height: 1.9;
  font-size: 1.02rem;

  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    color: #1a1a1a;
    margin: 34px 0 14px;
    line-height: 1.35;
    font-weight: 800;
  }
  :deep(h1) { font-size: 2rem; }
  :deep(h2) { font-size: 1.62rem; border-bottom: 1px solid rgba(0, 0, 0, 0.14); padding-bottom: 10px; }
  :deep(h3) { font-size: 1.26rem; font-weight: 700; }
  :deep(h4) { font-size: 1.14rem; font-weight: 700; }
  :deep(h5) { font-size: 1.06rem; font-weight: 700; }
  :deep(h6) { font-size: 1rem; font-weight: 700; color: rgba(0, 0, 0, 0.82); }
  :deep(p) { margin: 0 0 16px 0; }
  :deep(strong) { color: #1a1a1a; font-weight: 600; }
  :deep(em) { color: #7c3aed; font-style: italic; }
  :deep(br) { display: block; content: ''; margin: 6px 0; }

  :deep(code) {
    background: rgba(168, 85, 247, 0.1);
    color: #7c3aed;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
    font-family: 'Consolas', 'Monaco', monospace;
  }

  :deep(pre) {
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    padding: 16px 18px;
    margin: 20px 0;
    overflow-x: auto;

    code {
      background: none;
      padding: 0;
      color: rgba(0, 0, 0, 0.8);
    }
  }

  :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 16px 0;
  }

  :deep(a) {
    color: #a855f7;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }

  :deep(blockquote) {
    border-left: 3px solid rgba(0, 0, 0, 0.22);
    padding: 4px 16px;
    margin: 18px 0;
    background: rgba(0, 0, 0, 0.03);
    border-radius: 0 8px 8px 0;
    color: rgba(0, 0, 0, 0.7);
  }

  :deep(ul), :deep(ol) {
    margin: 12px 0 18px;
    padding-left: 1.4rem;
  }

  :deep(li) {
    margin-bottom: 8px;
    line-height: 1.9;
  }

  :deep(hr) {
    border: none;
    height: 1px;
    background: rgba(0, 0, 0, 0.1);
    margin: 28px 0;
  }
}

.file-content {
  text-align: center;
  padding: 20px 0 8px;
  max-width: 100%;
}

.file-title {
  margin-bottom: 8px;
}

.file-meta {
  margin-bottom: 14px;
  color: rgba(0, 0, 0, 0.55);
}

.pdf-preview {
  width: 100%;
  min-height: 82vh;
  height: calc(100vh - 220px);
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.45);
}

.file-tip {
  margin-bottom: 14px;
  color: rgba(0, 0, 0, 0.62);
}

.file-open-btn {
  display: inline-block;
  margin-top: 4px;
  padding: 10px 16px;
  border-radius: 9999px;
  border: 1px solid rgba(168, 85, 247, 0.35);
  background: rgba(168, 85, 247, 0.12);
  color: #7c3aed;
  font-weight: 700;
  text-decoration: none;
}

.xmind-content {
  text-align: left;
}

.xmind-panel {
  margin-top: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  max-height: calc(100vh - 260px);
  overflow: auto;
  cursor: grab;
  user-select: none;
}

.xmind-panel:active {
  cursor: grabbing;
}

.xmind-outline {
  padding: 10px 0;
}

.xmind-preview-map {
  display: block;
  width: 100%;
  max-height: calc(100vh - 280px);
  object-fit: contain;
  background: #f6f7fb;
  border-radius: 10px;
  transform-origin: center center;
  transition: transform 0.04s linear;
  user-select: none;
  -webkit-user-drag: none;
}

.xmind-map-tip {
  margin: 10px 6px 4px;
  font-size: 0.88rem;
  color: rgba(0, 0, 0, 0.55);
}

.xmind-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.docx-content {
  text-align: left;
}

.docx-panel {
  margin-top: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  max-height: calc(100vh - 260px);
  overflow: auto;
  padding: 20px 24px;
}

.docx-body {
  color: rgba(0, 0, 0, 0.78);
  line-height: 1.8;
}

.docx-body :deep(p) {
  margin: 0 0 14px;
}

.docx-body :deep(h1),
.docx-body :deep(h2),
.docx-body :deep(h3),
.docx-body :deep(h4) {
  margin: 20px 0 12px;
  color: #1a1a1a;
}

.xlsx-content {
  text-align: left;
}

.xlsx-panel {
  margin-top: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  max-height: calc(100vh - 260px);
  overflow: auto;
  padding: 12px;
}

.xlsx-table-wrap {
  overflow: auto;
}

.xlsx-table {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
}

.xlsx-table th,
.xlsx-table td {
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 8px 10px;
  color: rgba(0, 0, 0, 0.78);
  white-space: nowrap;
  font-size: 0.92rem;
}

.xlsx-table th {
  background: rgba(124, 58, 237, 0.08);
  font-weight: 700;
}

.xmind-node {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding-top: 6px;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.06);
}

.xmind-dot {
  color: rgba(124, 58, 237, 0.9);
  line-height: 1.6;
  flex-shrink: 0;
}

.xmind-text {
  color: rgba(0, 0, 0, 0.78);
  line-height: 1.65;
  word-break: break-word;
}

.xmind-state {
  padding: 18px 16px;
  color: rgba(0, 0, 0, 0.62);
}

.xmind-error {
  color: #b91c1c;
}

.loading-state,
.not-found {
  text-align: center;
  padding: 80px 0;
  color: rgba(0, 0, 0, 0.45);

  svg { opacity: 0.3; }
  p { margin-top: 16px; font-size: 1rem; }
}

.loading-dots {
  display: inline-flex;
  gap: 8px;

  span {
    width: 10px; height: 10px;
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

.btn-back {
  display: inline-block;
  margin-top: 24px;
  padding: 10px 24px;
  border-radius: 9999px;
  background: rgba(168, 85, 247, 0.12);
  border: 1px solid rgba(168, 85, 247, 0.25);
  color: #7c3aed;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.4s $ease-damped;

  &:hover {
    background: rgba(168, 85, 247, 0.2);
    transform: translateY(-2px);
  }
}

@media (max-width: 640px) {
  .article-header { padding: 24px 1rem 16px; }
  .article-cover-wrapper { padding: 0 1rem; }
  .article-layout { padding: 0 1rem; }
  .article-content-section { padding: 0; }
  .article-content { padding: 20px; }
}
</style>