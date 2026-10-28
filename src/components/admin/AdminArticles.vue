<template>
  <section class="admin-articles">
    <header class="section-heading">
      <div><h2>文章与文档</h2><p class="hint">在这里写文章、上传文档，统一查看和管理网站的阅读内容。</p></div>
      <button class="btn btn-primary" :disabled="saving || removing" @click="newArticle">新建文章</button>
    </header>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>

    <section class="document-upload" aria-label="上传文档" :aria-busy="uploadingDocuments">
      <input ref="documentInput" class="hidden-input" type="file" multiple :accept="documentAccept" @change="selectDocuments" />
      <button type="button" class="document-drop" :class="{ dragging: draggingDocuments }" :disabled="saving || removing || uploadingDocuments || coverUploading || !documentsReady"
        @click="documentInput?.click()" @dragover.prevent="draggingDocuments = true" @dragleave.prevent="draggingDocuments = false" @drop.prevent="dropDocuments">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 16V3m-5 5 5-5 5 5M4 14v6a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-6" /></svg>
        <strong>{{ uploadingDocuments ? '正在上传文档…' : '点击或拖入文档上传，支持一次选择多个文件' }}</strong>
        <span>{{ documentsReady ? `${documentExtensions.join('、').toUpperCase()} · 每批最多 20 个，合计不超过 ${rules.total_limit_mb}MB` : '正在读取文档上传规则…' }}</span>
      </button>
      <p class="hint">上传文档会立即公开；需要先写草稿，请使用“新建文章”。Markdown 和 TXT 文档支持在线编辑。</p>
      <div v-if="uploadingDocuments" class="upload-progress" role="status"><progress :value="documentProgress" max="100" aria-label="文档上传进度"></progress><span>{{ documentProgress ? `已上传 ${documentProgress}%` : '正在上传并校验文件…' }}</span><button type="button" class="btn btn-ghost" @click="cancelDocumentUpload">取消上传</button></div>
      <div v-if="uploadResults.length" class="upload-results" role="status"><p v-for="(result, index) in uploadResults" :key="index" :class="result.success ? 'notice' : 'error'">{{ result.message }}</p></div>
    </section>

    <form v-if="editorKind === 'article'" class="editor" :aria-busy="saving || coverUploading" @submit.prevent="saveArticle">
      <div class="editor-heading"><h3>{{ form.id ? '编辑文章' : '新建文章' }}</h3><span class="status-label">{{ form.is_published ? '发布内容' : '草稿内容' }}</span></div>
      <fieldset class="form-section" :disabled="saving">
        <legend>基本信息</legend>
        <div class="fields">
          <label class="field field-full" for="article-title">标题<input id="article-title" v-model="form.title" required maxlength="200" /></label>
          <label class="field field-full" for="article-summary">摘要<textarea id="article-summary" v-model="form.summary" rows="3" maxlength="5000"></textarea></label>
          <label class="field field-full" for="article-category">分类<select id="article-category" v-model="form.category_id"><option :value="null">未分类</option><option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option></select></label>
          <ArticleCoverUpload :key="editorGeneration" ref="coverUploader" class="field-full" v-model="form.cover_image" :rules="rules" :disabled="saving || uploadingDocuments" @busy-change="coverUploading = $event" />
        </div>
      </fieldset>
      <fieldset class="form-section" :disabled="saving">
        <legend>文章正文</legend>
        <label class="field" for="article-content">Markdown 正文<textarea id="article-content" v-model="form.content" rows="16" class="markdown" placeholder="# 文章标题"></textarea></label>
      </fieldset>
      <fieldset class="form-section publication-section" :disabled="saving">
        <legend>发布设置</legend>
        <label class="checkbox" for="article-published"><input id="article-published" type="checkbox" v-model="form.is_published" /><span>发布文章（取消勾选则保存为草稿）</span></label>
      </fieldset>
      <div class="editor-actions actions"><button class="btn btn-primary" :disabled="saving || removing || coverUploading || uploadingDocuments">{{ saving ? '保存中…' : coverUploading ? '请等待封面上传完成' : form.is_published ? '保存并发布' : '保存草稿' }}</button><button type="button" class="btn btn-ghost" :disabled="saving || removing" @click="closeEditor">关闭编辑</button><router-link v-if="form.id && savedPublished" :to="`/article/db-${form.id}`" target="_blank" rel="noopener" class="btn btn-ghost">查看文章</router-link></div>
    </form>

    <form v-else-if="editorKind === 'document'" class="editor" :aria-busy="saving" @submit.prevent="saveDocument">
      <div class="editor-heading"><h3>编辑文档</h3><span class="status-label status-published">公开文档</span></div>
      <p class="document-filename">{{ documentForm.filename }}</p>
      <p class="hint">直接修改原文档内容，保存后立即更新前台文章。</p>
      <label class="field" for="document-content">{{ documentForm.filename.toLowerCase().endsWith('.md') ? 'Markdown 正文' : 'TXT 正文' }}<textarea id="document-content" v-model="documentForm.content" rows="16" class="markdown" :disabled="saving"></textarea></label>
      <div class="actions"><button class="btn btn-primary" :disabled="saving || removing || uploadingDocuments">{{ saving ? '保存中…' : '保存文档' }}</button><button type="button" class="btn btn-ghost" :disabled="saving || removing" @click="closeEditor">关闭编辑</button><router-link :to="`/article/${encodeURIComponent(documentForm.filename)}`" target="_blank" rel="noopener" class="btn btn-ghost">查看文档</router-link></div>
    </form>
    <p v-if="loadingEditor" class="hint" role="status">正在打开编辑内容…</p>

    <section class="article-list" aria-labelledby="article-list-title">
      <div class="list-heading"><h3 id="article-list-title">全部内容 <span class="list-count">{{ entries.length }} 篇</span></h3><button type="button" class="btn btn-ghost" :disabled="loadingList || mutationBusy" @click="loadContent">刷新列表</button></div>
      <form class="list-filters" @submit.prevent="applySearch">
        <div class="search"><label class="search-label" for="article-search">搜索文章或文档</label><input id="article-search" v-model="query" placeholder="搜索标题或文档文件名" maxlength="200" /><button class="btn btn-ghost">搜索</button></div>
        <label class="filter-field" for="content-source">来源<select id="content-source" v-model="sourceFilter"><option value="all">全部来源</option><option value="article">在线文章</option><option value="document">上传文档</option></select></label>
        <label class="filter-field" for="content-status">状态<select id="content-status" v-model="statusFilter"><option value="all">全部状态</option><option value="published">已公开</option><option value="draft">草稿</option></select></label>
      </form>
      <p class="hint">在线文章 {{ articleCount }} 篇 · 上传文档 {{ documentCount }} 篇<span v-if="hasFilters"> · 筛选结果 {{ filteredEntries.length }} 篇</span></p>
      <div class="article-list-body" :aria-busy="loadingList || mutationBusy">
        <p v-if="loadingList" class="hint" role="status">正在加载文章与文档…</p>
        <article v-for="item in visibleEntries" :key="item.key" class="article-row">
          <div class="article-information"><strong class="article-title">{{ item.title }}</strong><p v-if="item.kind === 'document'" class="document-filename">{{ item.filename }}</p><div class="article-meta"><span class="status-label">{{ item.kind === 'article' ? '在线文章' : item.file_type.toUpperCase() + ' 文档' }}</span><span class="status-label" :class="item.is_published ? 'status-published' : 'status-draft'">{{ item.is_published ? '已公开' : '草稿' }}</span><span v-if="item.kind === 'article'">{{ item.category?.name || '未分类' }}</span><time v-if="item.updated_at">{{ item.updated_at }}</time></div></div>
          <div class="actions row-actions"><router-link v-if="item.is_published" :to="item.detailUrl" target="_blank" rel="noopener" class="btn btn-ghost">查看</router-link><button v-if="item.editable" class="btn btn-ghost" :disabled="mutationBusy" @click="openEditor(item)">编辑</button><button class="btn btn-ghost danger" :disabled="mutationBusy" @click="removeContent(item)">删除</button></div>
        </article>
        <p v-if="!loadingList && !visibleEntries.length" class="empty-state">{{ hasFilters ? '没有符合条件的内容，请调整搜索或筛选。' : '还没有内容，可以新建文章或上传文档。' }}</p>
      </div>
      <nav class="pagination" aria-label="文章与文档列表分页"><button class="btn btn-ghost" :disabled="page <= 1 || loadingList" @click="page -= 1">上一页</button><span>第 {{ page }} / {{ totalPages }} 页 · 共 {{ filteredEntries.length }} 篇</span><button class="btn btn-ghost" :disabled="page >= totalPages || loadingList" @click="page += 1">下一页</button></nav>
    </section>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import request from '@/utils/request'
import ArticleCoverUpload from './ArticleCoverUpload.vue'

const entries = ref([]), categories = ref([]), rules = ref({}), page = ref(1)
const query = ref(''), appliedQuery = ref(''), sourceFilter = ref('all'), statusFilter = ref('all')
const loadingList = ref(false), loadingEditor = ref(false), saving = ref(false), removing = ref(false)
const error = ref(''), notice = ref(''), editorKind = ref(''), editorGeneration = ref(0), savedPublished = ref(false)
const documentInput = ref(null), uploadingDocuments = ref(false), draggingDocuments = ref(false), documentProgress = ref(0), uploadResults = ref([])
const coverUploader = ref(null), coverUploading = ref(false)
const blank = () => ({ id: null, title: '', summary: '', content: '', cover_image: '', category_id: null, is_published: false })
const form = ref(blank()), documentForm = ref({ filename: '', content: '' })
let savedForm = JSON.stringify(form.value), savedDocument = '', listGeneration = 0, documentUploadGeneration = 0
let listController = null, editorController = null, documentUploadController = null, alive = true
const mutationBusy = computed(() => saving.value || removing.value || uploadingDocuments.value || coverUploading.value)
const documentExtensions = computed(() => rules.value.extensions?.wenz || [])
const documentsReady = computed(() => documentExtensions.value.length > 0 && Number(rules.value.total_limit_mb) > 0)
const documentAccept = computed(() => documentExtensions.value.join(','))
const articleCount = computed(() => entries.value.filter(item => item.kind === 'article').length)
const documentCount = computed(() => entries.value.filter(item => item.kind === 'document').length)
const hasFilters = computed(() => appliedQuery.value || sourceFilter.value !== 'all' || statusFilter.value !== 'all')
const filteredEntries = computed(() => {
  const term = appliedQuery.value.trim().toLocaleLowerCase()
  return entries.value.filter(item => (sourceFilter.value === 'all' || item.kind === sourceFilter.value)
    && (statusFilter.value === 'all' || item.is_published === (statusFilter.value === 'published'))
    && (!term || `${item.title} ${item.filename || ''}`.toLocaleLowerCase().includes(term)))
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredEntries.value.length / 12)))
const visibleEntries = computed(() => filteredEntries.value.slice((page.value - 1) * 12, page.value * 12))
watch([sourceFilter, statusFilter], () => { page.value = 1 })
watch(totalPages, value => { page.value = Math.min(page.value, value) })
function applySearch() { appliedQuery.value = query.value; page.value = 1 }
// 旧发布包中的文档可能没有保留文件时间，零时间不作为内容日期显示。
function documentDate(value) { return typeof value === 'string' && !value.startsWith('1970-01-01') ? value : '' }
function articleForm(article) { const result = blank(); for (const key of Object.keys(result)) if (article[key] !== undefined && article[key] !== null) result[key] = article[key]; return result }
function hasUnsavedChanges() { return editorKind.value === 'article' ? JSON.stringify(form.value) !== savedForm : editorKind.value === 'document' && documentForm.value.content !== savedDocument }
function cancelEditorRequest() { editorGeneration.value += 1; editorController?.abort(); editorController = null; loadingEditor.value = false }
function cancelDocumentUpload() {
  documentUploadGeneration += 1
  documentUploadController?.abort()
  documentUploadController = null
  uploadingDocuments.value = false
  documentProgress.value = 0
  notice.value = '已取消上传。服务器可能已接收部分文件，可刷新列表确认。'
}
function discardChanges() {
  if (saving.value || removing.value) { error.value = '正在保存或删除内容，请等待操作完成后再切换。'; return false }
  const pendingUpload = uploadingDocuments.value || coverUploading.value
  if ((pendingUpload || hasUnsavedChanges()) && !window.confirm(pendingUpload ? '当前有上传或未保存的编辑，是否取消上传并放弃更改？服务器已接收的文件会保留。' : '当前编辑尚未保存，是否放弃更改？')) return false
  cancelEditorRequest()
  if (uploadingDocuments.value) cancelDocumentUpload()
  if (coverUploading.value) coverUploader.value?.cancelUpload()
  coverUploading.value = false
  return true
}
function newArticle() {
  if (!discardChanges()) return
  form.value = blank(); savedForm = JSON.stringify(form.value); savedPublished.value = false
  editorKind.value = 'article'; error.value = ''; notice.value = ''
}
function closeEditor() { if (discardChanges()) editorKind.value = '' }

async function loadContent() {
  const currentGeneration = ++listGeneration
  listController?.abort()
  const controller = new AbortController(); listController = controller
  loadingList.value = true; error.value = ''
  try {
    const documentsPromise = request.get('/api/md-articles', { signal: controller.signal })
    // 个人博客统一聚合现有两种来源，不新增数据表或复制文档内容。
    const articlesPromise = (async () => {
      const first = await request.get('/api/admin/articles', { params: { page: 1, per_page: 100 }, signal: controller.signal })
      const articles = [...(first.articles || [])]
      for (let number = 2; number <= first.pages; number += 1) {
        const result = await request.get('/api/admin/articles', { params: { page: number, per_page: 100 }, signal: controller.signal })
        articles.push(...(result.articles || []))
      }
      return articles
    })()
    const [articles, documents] = await Promise.all([articlesPromise, documentsPromise])
    if (!alive || currentGeneration !== listGeneration) return
    entries.value = [
      ...articles.map(item => ({ ...item, key: `article-${item.id}`, kind: 'article', editable: true, updated_at: item.updated_at || item.created_at || '', detailUrl: `/article/db-${item.id}` })),
      ...(documents.articles || []).map(item => ({ ...item, key: `document-${item.filename}`, kind: 'document', is_published: true, editable: ['md', 'txt'].includes(item.file_type), updated_at: documentDate(item.created_at), detailUrl: `/article/${encodeURIComponent(item.filename)}` }))
    ].sort((left, right) => right.updated_at.localeCompare(left.updated_at) || left.key.localeCompare(right.key))
    page.value = Math.min(page.value, totalPages.value)
  } catch (err) {
    if (alive && currentGeneration === listGeneration) error.value = '加载内容失败：' + err.message
  } finally {
    if (currentGeneration === listGeneration) { loadingList.value = false; listController = null }
  }
}

async function openEditor(item) {
  if (!discardChanges()) return
  editorKind.value = ''; error.value = ''; notice.value = ''
  const currentGeneration = editorGeneration.value, controller = new AbortController()
  editorController = controller; loadingEditor.value = true
  try {
    const result = await request.get(item.kind === 'article' ? `/api/admin/articles/${item.id}` : `/api/admin/documents/${encodeURIComponent(item.filename)}`, { signal: controller.signal })
    if (!alive || currentGeneration !== editorGeneration.value) return
    if (item.kind === 'article') { form.value = articleForm(result.article); savedForm = JSON.stringify(form.value); savedPublished.value = form.value.is_published }
    else { documentForm.value = { filename: result.filename, content: result.content }; savedDocument = result.content }
    editorKind.value = item.kind
  } catch (err) { if (alive && currentGeneration === editorGeneration.value) error.value = err.message }
  finally { if (currentGeneration === editorGeneration.value) { loadingEditor.value = false; editorController = null } }
}

async function saveArticle() {
  if (mutationBusy.value || editorKind.value !== 'article') return
  saving.value = true; error.value = ''; notice.value = ''
  const payload = { ...form.value }
  try {
    const result = payload.id ? await request.put(`/api/admin/articles/${payload.id}`, payload) : await request.post('/api/admin/articles', payload)
    if (!alive) return
    form.value = articleForm(result.article); savedForm = JSON.stringify(form.value); savedPublished.value = form.value.is_published
    notice.value = form.value.is_published ? '文章已发布，访客现在可以阅读。' : '草稿已保存，仅在后台可见。'
    page.value = 1; await loadContent()
  } catch (err) { if (alive) error.value = err.message }
  finally { saving.value = false }
}
async function saveDocument() {
  if (mutationBusy.value || editorKind.value !== 'document') return
  if (new TextEncoder().encode(documentForm.value.content).length > Number(rules.value.text_limit_mb || 1) * 1024 * 1024) { error.value = `文档内容不能超过 ${rules.value.text_limit_mb || 1}MB。`; return }
  saving.value = true; error.value = ''; notice.value = ''
  const payload = { ...documentForm.value }
  try {
    await request.put(`/api/admin/documents/${encodeURIComponent(payload.filename)}`, { content: payload.content })
    if (!alive) return
    savedDocument = payload.content; notice.value = '文档已保存，前台内容已更新。'; await loadContent()
  } catch (err) { if (alive) error.value = err.message }
  finally { saving.value = false }
}
async function removeContent(item) {
  if (mutationBusy.value) return
  const editingTarget = (editorKind.value === 'article' && item.kind === 'article' && form.value.id === item.id) || (editorKind.value === 'document' && item.kind === 'document' && documentForm.value.filename === item.filename)
  if (editingTarget && !discardChanges()) return
  const question = item.kind === 'article' ? `确定删除文章“${item.title}”及其评论？此操作无法撤销。` : `确定删除文档“${item.filename}”？前台将无法再阅读此文档，此操作无法撤销。`
  if (!window.confirm(question)) return
  cancelEditorRequest()
  removing.value = true; error.value = ''; notice.value = ''
  try {
    await request.delete(item.kind === 'article' ? `/api/admin/articles/${item.id}` : `/api/admin/file/wenz/${encodeURIComponent(item.filename)}`)
    if (!alive) return
    if (editingTarget) editorKind.value = ''
    notice.value = item.kind === 'article' ? '文章已删除。' : '文档已删除。'
    await loadContent()
  } catch (err) { if (alive) error.value = err.message }
  finally { removing.value = false }
}

function selectDocuments(event) { const files = Array.from(event.target.files || []); event.target.value = ''; uploadDocuments(files) }
function dropDocuments(event) { draggingDocuments.value = false; uploadDocuments(Array.from(event.dataTransfer?.files || [])) }
function rejectionMessages(result) { return (result.rejected || []).map(item => ({ success: false, message: `${item.filename}：${item.reason}` })) }
async function uploadDocuments(files) {
  if (!files.length || !documentsReady.value || mutationBusy.value) return
  error.value = ''; notice.value = ''; uploadResults.value = []
  if (files.length > 20) { error.value = '每批最多上传 20 个文档，请分批上传。'; return }
  const accepted = [], rejected = []
  for (const file of files) {
    const extension = '.' + file.name.split('.').pop().toLowerCase(), limit = ['.md', '.txt'].includes(extension) ? rules.value.text_limit_mb : rules.value.document_limit_mb
    if (!documentExtensions.value.includes(extension)) rejected.push({ success: false, message: `${file.name}：不支持这种文档格式。` })
    else if (!file.size || file.size > Number(limit) * 1024 * 1024) rejected.push({ success: false, message: `${file.name}：文件为空或超过 ${limit}MB。` })
    else accepted.push(file)
  }
  uploadResults.value = rejected
  if (!accepted.length) return
  if (accepted.reduce((sum, file) => sum + file.size, 0) > Number(rules.value.total_limit_mb) * 1024 * 1024) { error.value = `本次上传合计不能超过 ${rules.value.total_limit_mb}MB。`; return }
  const currentGeneration = ++documentUploadGeneration, controller = new AbortController(), data = new FormData()
  documentUploadController = controller; uploadingDocuments.value = true; documentProgress.value = 0
  accepted.forEach(file => data.append('files', file)); data.append('subdir', 'wenz')
  try {
    const result = await request.post('/api/admin/upload', data, { timeout: 120000, signal: controller.signal,
      onUploadProgress: event => { if (currentGeneration === documentUploadGeneration && event.total) documentProgress.value = Math.min(100, Math.round(event.loaded / event.total * 100)) } })
    if (!alive || currentGeneration !== documentUploadGeneration) return
    uploadResults.value = [...rejected, ...(result.uploaded || []).map(filename => ({ success: true, message: `${filename}：上传成功，已公开。` })), ...rejectionMessages(result)]
    notice.value = `成功上传 ${result.count || 0} 个文档。`; page.value = 1; await loadContent()
  } catch (err) {
    if (alive && currentGeneration === documentUploadGeneration) { error.value = '文档上传失败：' + err.message; uploadResults.value = [...rejected, ...rejectionMessages(err.data || {})] }
  } finally {
    if (currentGeneration === documentUploadGeneration) { documentUploadController = null; uploadingDocuments.value = false }
  }
}

function beforeUnload(event) { if (hasUnsavedChanges() || mutationBusy.value) { event.preventDefault(); event.returnValue = '' } }
defineExpose({ discardChanges })
onMounted(async () => {
  window.addEventListener('beforeunload', beforeUnload)
  const results = await Promise.allSettled([loadContent(), request.get('/api/categories'), request.get('/api/admin/upload-rules')])
  if (!alive) return
  if (results[1].status === 'fulfilled') categories.value = results[1].value
  else error.value = '分类读取失败：' + results[1].reason.message
  if (results[2].status === 'fulfilled') rules.value = results[2].value
  else error.value = '上传规则读取失败：' + results[2].reason.message
})
onBeforeUnmount(() => {
  alive = false; listGeneration += 1; documentUploadGeneration += 1
  cancelEditorRequest(); listController?.abort(); documentUploadController?.abort()
  window.removeEventListener('beforeunload', beforeUnload)
})
</script>

<style scoped>
.admin-articles { display: grid; gap: 24px; min-width: 0; }
.section-heading, .editor-heading, .list-heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.section-heading > div, .article-information { min-width: 0; }
h2, h3, p { margin: 0; }
.hint { margin-top: 8px; }
.hidden-input { display: none; }
.document-upload { display: grid; gap: 10px; }
.document-drop { display: flex; flex-direction: column; align-items: center; gap: 9px; width: 100%; min-height: 144px; padding: 22px; border: 2px dashed #d9d0eb; border-radius: 12px; background: #fcfaff; color: #5b21b6; font: inherit; text-align: center; cursor: pointer; }
.document-drop span { font-size: 12px; color: #667085; }
.document-drop.dragging, .document-drop:hover:not(:disabled) { background: #f3edff; border-color: #8b5bd2; }
.upload-progress { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; color: #667085; font-size: 13px; }
.upload-progress progress { width: min(240px, 100%); accent-color: #6d28d9; }
.upload-results { display: grid; gap: 6px; font-size: 13px; overflow-wrap: anywhere; }
.editor { display: grid; gap: 24px; min-width: 0; padding: 24px; }
.form-section { min-width: 0; margin: 0; padding: 16px 0 0; border: 0; }
.form-section legend { padding: 0; }
.fields { display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; }
.field { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.field-full { grid-column: 1 / -1; }
.field input, .field textarea, .field select { width: 100%; min-width: 0; box-sizing: border-box; }
.markdown { min-height: 320px; resize: vertical; }
.checkbox { display: flex; align-items: flex-start; gap: 10px; }
.checkbox input { flex: 0 0 auto; margin-top: 3px; }
.actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.article-list { display: grid; gap: 16px; min-width: 0; }
.list-heading { align-items: center; flex-wrap: wrap; }
.list-count { margin-left: 8px; }
.list-filters { display: grid; grid-template-columns: minmax(160px, 1fr) 140px 130px; gap: 12px; align-items: end; }
.search { display: flex; align-items: center; gap: 10px; min-width: 0; }
.search-label { position: absolute; width: 1px; height: 1px; padding: 0; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
.search input { flex: 1; min-width: 0; }
.filter-field { display: grid; gap: 4px; min-width: 0; font-size: 12px; }
.article-list-body { display: grid; gap: 12px; min-height: 80px; }
.article-row { display: flex; align-items: center; justify-content: space-between; gap: 20px; min-width: 0; padding: 18px; }
.article-title { display: block; overflow-wrap: anywhere; }
.document-filename { margin-top: 5px; color: #667085; font-size: 12px; overflow-wrap: anywhere; }
.article-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 10px; margin-top: 8px; }
.article-meta time { overflow-wrap: anywhere; }
.status-label { display: inline-flex; align-items: center; flex: 0 0 auto; }
.row-actions { flex: 0 0 auto; }
.empty-state { padding: 32px 16px; text-align: center; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; flex-wrap: wrap; }
@media (max-width: 1150px) {
  .list-filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .search { grid-column: 1 / -1; }
  .article-row { align-items: flex-start; flex-direction: column; gap: 14px; }
}
@media (max-width: 640px) {
  .section-heading { align-items: stretch; flex-direction: column; }
  .section-heading > .btn { align-self: flex-start; }
  .editor { padding: 16px; }
  .document-drop { padding: 18px 14px; }
  .article-row { padding: 16px; }
  .pagination { gap: 10px; font-size: 13px; }
}
</style>
