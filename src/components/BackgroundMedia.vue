<template>
  <div class="global-bg" aria-hidden="true">
    <template v-for="layer in layers" :key="layer.key">
      <div
        v-if="layer.type === 'image'"
        class="bg-image"
        :class="{ loaded: layer.state !== 'preparing' }"
        :data-background-state="layer.state"
        :style="{ backgroundImage: `url(${JSON.stringify(layer.url)})` }"
      ></div>
      <video
        v-else
        :ref="element => rememberVideo(layer.key, element)"
        class="bg-video"
        :class="{ loaded: layer.state !== 'preparing' }"
        :data-background-state="layer.state"
        :src="layer.url"
        muted
        loop
        playsinline
        preload="auto"
      ></video>
    </template>
    <div class="bg-fallback"></div>
  </div>
</template>

<script setup>
import { shallowRef, nextTick, onBeforeUnmount } from 'vue'

const layers = shallowRef([])
const videos = new Map()
let pending = null
let previousTimer = null
let disposed = false
let paused = false

function rememberVideo(key, element) {
  if (element) videos.set(key, element)
  else videos.delete(key)
}

function warn(media, reason, error) {
  console.warn('背景媒体准备失败，保留当前壁纸:', {
    filename: media?.filename || '', type: media?.type, url: media?.url, reason
  }, error || '')
}

function releaseVideo(key) {
  const video = videos.get(key)
  if (!video) return
  try {
    video.pause()
    video.removeAttribute('src')
    video.load()
  } catch (error) {
    warn({ type: 'video', url: key.slice(6) }, '释放媒体失败', error)
  }
  videos.delete(key)
}

function removeLayers(predicate) {
  for (const layer of layers.value) {
    if (predicate(layer) && layer.type === 'video') releaseVideo(layer.key)
  }
  layers.value = layers.value.filter(layer => !predicate(layer))
}

function cancelPending() {
  pending?.finish(false)
}

function prepareLayer(media) {
  const existing = layers.value.some(layer => layer.key === media.key)
  layers.value = existing
    ? layers.value.map(layer => layer.key === media.key ? { ...media, state: 'preparing' } : layer)
    : [...layers.value, { ...media, state: 'preparing' }]
}

function activate(media) {
  clearTimeout(previousTimer)
  removeLayers(layer => layer.state === 'previous')
  const nextLayers = layers.value.map(layer => ({
    ...layer,
    state: layer.key === media.key ? 'active' : 'previous'
  }))
  if (!nextLayers.some(layer => layer.key === media.key)) {
    nextLayers.push({ ...media, state: 'active' })
  }
  layers.value = nextLayers
  previousTimer = setTimeout(() => {
    removeLayers(layer => layer.state === 'previous')
    previousTimer = null
  }, 220)
}

function show(media, { timeout = 12_000, signal } = {}) {
  cancelPending()
  if (disposed || paused || signal?.aborted) return Promise.resolve(false)
  if (!['image', 'video'].includes(media?.type) || typeof media?.url !== 'string' || !media.url.trim()) {
    warn(media, '无效的媒体类型或地址')
    return Promise.resolve(false)
  }
  const selected = { type: media.type, filename: media.filename || '', url: media.url.trim() }
  selected.key = `${selected.type}:${selected.url}`
  const active = layers.value.find(layer => layer.state === 'active')
  const activeVideo = videos.get(selected.key)
  if (active?.key === selected.key && (selected.type === 'image' || (activeVideo?.readyState >= 2 && !activeVideo.paused))) {
    return Promise.resolve(true)
  }

  return new Promise(resolve => {
    let settled = false
    let image = null
    let video = null
    let frameA = null
    let frameB = null
    let playReady = false
    const wait = Number.isFinite(timeout) && timeout > 0 ? timeout : 12_000
    const timer = setTimeout(() => finish(false, '等待就绪超时'), wait)
    const abort = () => finish(false)
    const checkVideo = () => {
      if (playReady && video?.readyState >= 2 && !video.paused) finish(true)
    }
    const videoError = () => finish(false, '视频读取失败', video?.error)
    function finish(ready, reason, error) {
      if (settled) return
      settled = true
      clearTimeout(timer)
      if (frameA !== null) cancelAnimationFrame(frameA)
      if (frameB !== null) cancelAnimationFrame(frameB)
      signal?.removeEventListener('abort', abort)
      if (image) {
        image.onload = image.onerror = null
        if (!ready) image.removeAttribute('src')
      }
      if (video) {
        for (const event of ['loadeddata', 'canplay', 'playing']) video.removeEventListener(event, checkVideo)
        video.removeEventListener('error', videoError)
      }
      const success = ready && !disposed && !paused && !signal?.aborted && pending?.finish === finish
      if (success) activate(selected)
      else removeLayers(layer => layer.key === selected.key && layer.state === 'preparing')
      if (pending?.finish === finish) pending = null
      if (!success && reason) warn(selected, reason, error)
      resolve(success)
    }
    pending = { finish }
    signal?.addEventListener('abort', abort, { once: true })
    // 信号可能在监听注册之前已经取消。
    if (signal?.aborted) { finish(false); return }

    if (selected.type === 'image') {
      image = new Image()
      image.onload = async () => {
        try {
          if (typeof image.decode === 'function') await image.decode()
          if (settled) return
          // 解码完成后才挂载 CSS 背景，复用同一 URL 的预载缓存。
          prepareLayer(selected)
          await nextTick()
          if (settled) return
          frameA = requestAnimationFrame(() => {
            frameB = requestAnimationFrame(() => finish(true))
          })
        } catch (error) {
          finish(false, '图片解码失败', error)
        }
      }
      image.onerror = error => finish(false, '图片读取失败', error)
      image.src = selected.url
      return
    }

    // 相同 URL 的视频就绪后仍复用原 DOM，避免切换时再次下载。
    if (active?.key !== selected.key) {
      prepareLayer(selected)
    }
    nextTick(async () => {
      if (settled) return
      video = videos.get(selected.key)
      if (!video) { finish(false, '视频元素未能挂载'); return }
      video.muted = true
      video.defaultMuted = true
      video.playsInline = true
      for (const event of ['loadeddata', 'canplay', 'playing']) video.addEventListener(event, checkVideo)
      video.addEventListener('error', videoError)
      try {
        await video.play()
        if (settled) return
        playReady = true
        checkVideo()
      } catch (error) {
        finish(false, '视频无法自动播放', error)
      }
    })
  })
}

function setPaused(value) {
  paused = Boolean(value)
  if (paused) {
    cancelPending()
    for (const video of videos.values()) video.pause()
    return Promise.resolve(true)
  }
  const active = layers.value.find(layer => layer.state === 'active' && layer.type === 'video')
  const video = active && videos.get(active.key)
  if (!video || disposed) return Promise.resolve(true)
  try {
    return Promise.resolve(video.play()).then(() => {
      if (paused || disposed || layers.value.find(layer => layer.state === 'active')?.key !== active.key) {
        video.pause()
        return false
      }
      return !video.paused && video.readyState >= 2
    }).catch(error => {
      if (!disposed) warn(active, '恢复视频播放失败', error)
      return false
    })
  } catch (error) {
    warn(active, '恢复视频播放失败', error)
    return Promise.resolve(false)
  }
}

onBeforeUnmount(() => {
  disposed = true
  cancelPending()
  clearTimeout(previousTimer)
  removeLayers(() => true)
})

defineExpose({ show, cancelPending, setPaused })
</script>

<style scoped>
.global-bg { position: fixed; inset: 0; z-index: -1; overflow: hidden; }
.bg-image, .bg-video { position: absolute; inset: 0; opacity: 0; transition: opacity 0.2s ease; }
.bg-image { background-size: cover; background-position: center; background-repeat: no-repeat; }
.bg-video { width: 100%; height: 100%; object-fit: cover; }
.loaded { opacity: 1; }
[data-background-state='preparing'] { z-index: 1; }
[data-background-state='previous'] { z-index: 2; }
[data-background-state='active'] { z-index: 3; }
.bg-fallback { position: absolute; inset: 0; z-index: 0; background: linear-gradient(135deg, #071026 0%, #0b1220 50%, #0f172a 100%); }
@media (prefers-reduced-motion: reduce) { .bg-image, .bg-video { transition: none; } }
</style>
