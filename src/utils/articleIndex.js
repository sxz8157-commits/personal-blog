/** 将公开索引整理为词云和列表共用的数据，不额外下载正文或查询草稿。 */
export function prepareArticles(rows) {
  if (!Array.isArray(rows)) throw new TypeError('文章索引返回格式异常，请稍后重试')
  return rows.filter(row => row && row.id != null && String(row.title || '').trim()).map(row => {
    const id = String(row.id)
    const filename = String(row.filename || (row.source === 'database' ? '' : id))
    const title = row.source === 'database' ? String(row.title).trim() : filename.replace(/\.[^.]+$/, '') || String(row.title).trim()
    const format = row.source === 'database' ? '文章' : String(row.file_type || filename.split('.').pop() || '文档').toUpperCase()
    const tags = Array.isArray(row.tags) ? row.tags.filter(tag => typeof tag === 'string' && tag.trim()).map(tag => tag.trim()) : []
    const summary = String(row.summary || '')
      .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
      .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
      .replace(/<[^>]*>/g, '').replace(/[`#*_>]+/g, '').replace(/\s+/g, ' ').trim()
    const rawDate = String(row.updated_at || row.created_at || '')
    const date = /^\d{4}-\d{2}-\d{2}/.test(rawDate) && Number(rawDate.slice(0, 4)) > 1970 ? rawDate.slice(0, 10) : ''
    const description = summary && !/^文档格式[：:]/.test(summary) ? summary : `${format === '文章' ? '文章' : format + ' 文档'} · 点击打开，慢慢阅读。`
    return {
      id, title, filename, format, tags, description, date,
      href: `/article/${encodeURIComponent(id)}`,
      count: Math.max(1, Number(row.views || 0) + Number(row.likes || 0) + 1),
      searchText: normalizeSearch([title, row.title, filename, summary, format, ...tags].join(' '))
    }
  })
}

export function normalizeSearch(value) {
  return String(value || '').normalize('NFKC').toLocaleLowerCase().trim()
}

export function filterArticles(articles, query, format = '') {
  const words = normalizeSearch(query).split(/\s+/).filter(Boolean)
  return articles.filter(article => (!format || article.format === format) && words.every(word => article.searchText.includes(word)))
}
