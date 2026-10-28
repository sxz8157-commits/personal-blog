// 只接受可由浏览器正常请求的图片/视频地址，保留查询参数中的文件版本。
function mediaUrlKey(value) {
  if (typeof value !== 'string') return ''
  const url = value.trim()
  if (!url || /^[?#]/.test(url) || /[\u0000-\u001f\u007f\\]/.test(url)) return ''
  try {
    const parsed = new URL(url, 'https://background.invalid/')
    if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') return ''
    parsed.hash = ''
    return parsed.href
  } catch {
    return ''
  }
}

function uniqueCandidates(candidates) {
  if (!Array.isArray(candidates)) return []
  const seen = new Set()
  return candidates.filter(item => {
    if (!item || (item.type !== 'image' && item.type !== 'video')) return false
    const key = mediaUrlKey(item.url)
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function exclusionKeys(urls) {
  const values = Array.isArray(urls) ? urls : [urls]
  return new Set(values.map(value => mediaUrlKey(value)).filter(Boolean))
}

function randomIndex(length, random) {
  const value = random()
  // 注入的随机函数也做边界保护，避免生成越界下标。
  const fraction = Number.isFinite(value) ? Math.min(Math.max(value, 0), 1 - Number.EPSILON) : 0
  return Math.floor(fraction * length)
}

/** 合并后端图片和视频列表；不信任响应中的 type 字段，按来源赋予类型。 */
export function normalizeBackgroundMedia(data) {
  const candidates = []
  for (const [field, type] of [['images', 'image'], ['videos', 'video']]) {
    if (!Array.isArray(data?.[field])) continue
    for (const item of data[field]) {
      if (!item || typeof item !== 'object' || !mediaUrlKey(item.url)) continue
      candidates.push({
        type,
        filename: typeof item.filename === 'string' ? item.filename.trim() : '',
        url: item.url.trim()
      })
    }
  }
  return uniqueCandidates(candidates)
}

/** 多个背景时避开当前/上次背景；只有一个时继续使用它，空列表返回 null。 */
export function chooseDifferentBackground(candidates, previousUrl = '', random = Math.random) {
  const media = uniqueCandidates(candidates)
  if (!media.length) return null
  if (media.length === 1) return media[0]
  const excluded = exclusionKeys(previousUrl)
  const pool = media.filter(item => !excluded.has(mediaUrlKey(item.url)))
  return pool.length ? pool[randomIndex(pool.length, random)] : null
}

/**
 * 每轮消费一次全部可用背景，支持洗牌或顺序轮播。
 * next 可排除已加载失败的地址；全部不可用时返回 null，不无限重试。
 */
export function createBackgroundRotation(candidates, {
  mode = 'shuffle',
  previousUrl = '',
  random = Math.random
} = {}) {
  const media = uniqueCandidates(candidates)
  let queue = []
  let lastUrl = mediaUrlKey(previousUrl)

  function refill(excluded) {
    queue = media.filter(item => !excluded.has(mediaUrlKey(item.url)))
    if (mode === 'shuffle') {
      for (let index = queue.length - 1; index > 0; index -= 1) {
        const swap = randomIndex(index + 1, random)
        ;[queue[index], queue[swap]] = [queue[swap], queue[index]]
      }
    }
    // 洗牌后调整第一项，确保上一轮最后一项不会马上出现第二次。
    if (queue.length > 1 && mediaUrlKey(queue[0].url) === lastUrl) {
      const alternative = queue.findIndex(item => mediaUrlKey(item.url) !== lastUrl)
      ;[queue[0], queue[alternative]] = [queue[alternative], queue[0]]
    }
  }

  return {
    next(excludedUrls = []) {
      const excluded = exclusionKeys(excludedUrls)
      if (!media.some(item => !excluded.has(mediaUrlKey(item.url)))) return null
      // 删除本轮失败项后直接补充下一轮；无需在失效资源间重复重试。
      queue = queue.filter(item => !excluded.has(mediaUrlKey(item.url)))
      if (!queue.length) refill(excluded)
      const next = queue.shift()
      lastUrl = mediaUrlKey(next.url)
      return next
    }
  }
}
