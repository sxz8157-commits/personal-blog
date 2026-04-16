<template>
  <div class="tagcloud-canvas-wrap">
    <canvas ref="canvasEl" class="tagcloud-canvas" @click="handleClick" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  // [{ name?, label?, value?, count }]
  // - label: displayed text
  // - value: emitted on select (falls back to name/label)
  tags: { type: Array, default: () => [] },
  width: { type: Number, default: 560 },
  height: { type: Number, default: 260 },
  // rotation speed (radians / frame-ish)
  speed: { type: Number, default: 0.0028 },
  // font size range
  minFont: { type: Number, default: 12 },
  maxFont: { type: Number, default: 26 },
  // sphere radius factor based on container min side
  radiusScale: { type: Number, default: 0.62 }
})

const emit = defineEmits(['select'])

const canvasEl = ref(null)
const rafId = ref(0)
const hoveredName = ref('')
const pointer = ref({ x: -1, y: -1 })

function clamp01(x) {
  return Math.max(0, Math.min(1, x))
}
function lerp(a, b, t) {
  return a + (b - a) * t
}

const normalizedTags = computed(() => {
  const list = (props.tags || [])
    .map(t => ({
      label: String((t?.label ?? t?.name ?? '')).trim(),
      value: String((t?.value ?? t?.name ?? t?.label ?? '')).trim(),
      count: Number(t?.count ?? 1)
    }))
    .filter(t => t.label)

  if (!list.length) return []
  const max = Math.max(...list.map(t => t.count))
  const min = Math.min(...list.map(t => t.count))
  const denom = Math.max(1, max - min)

  return list.map((t) => {
    const p = clamp01((t.count - min) / denom)
    return {
      ...t,
      weight: p,
      fontSize: Math.round(lerp(props.minFont, props.maxFont, p))
    }
  })
})

let state = null

function createPoints(n) {
  if (n <= 1) return [{ x: 0, y: 0, z: 1 }]
  if (n === 2) return [{ x: -0.38, y: 0, z: 0.92 }, { x: 0.38, y: 0, z: 0.92 }]
  if (n === 3) {
    return [
      { x: 0, y: -0.34, z: 0.94 },
      { x: -0.35, y: 0.3, z: 0.88 },
      { x: 0.35, y: 0.3, z: 0.88 }
    ]
  }
  // Fibonacci sphere distribution
  const points = []
  const golden = Math.PI * (3 - Math.sqrt(5))
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2
    const radius = Math.sqrt(1 - y * y)
    const theta = golden * i
    const x = Math.cos(theta) * radius
    const z = Math.sin(theta) * radius
    points.push({ x, y, z })
  }
  return points
}

function resizeCanvas() {
  if (!canvasEl.value) return
  const dpr = window.devicePixelRatio || 1
  canvasEl.value.width = Math.floor(props.width * dpr)
  canvasEl.value.height = Math.floor(props.height * dpr)
  canvasEl.value.style.width = `${props.width}px`
  canvasEl.value.style.height = `${props.height}px`
  const ctx = canvasEl.value.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  return ctx
}

function init() {
  const ctx = resizeCanvas()
  const tags = normalizedTags.value
  const n = tags.length
  const points = createPoints(n)
  const items = tags.map((t, i) => ({
    ...t,
    p: points[i % points.length],
    // runtime
    sx: 0,
    sy: 0,
    alpha: 1,
    scale: 1,
    bounds: null
  }))

  state = {
    ctx,
    items,
    rotX: 0.45,
    rotY: 0,
    // radius in pixels
    radius: Math.min(props.width, props.height) * Math.max(0.35, Math.min(0.9, props.radiusScale)),
    centerX: props.width / 2,
    centerY: props.height / 2
  }
}

function rotatePoint(p, ax, ay) {
  // rotate around X
  let { x, y, z } = p
  const cosx = Math.cos(ax)
  const sinx = Math.sin(ax)
  const y1 = y * cosx - z * sinx
  const z1 = y * sinx + z * cosx
  y = y1
  z = z1

  // rotate around Y
  const cosy = Math.cos(ay)
  const siny = Math.sin(ay)
  const x2 = x * cosy + z * siny
  const z2 = -x * siny + z * cosy
  x = x2
  z = z2
  return { x, y, z }
}

function drawFrame() {
  if (!state?.ctx || !canvasEl.value) return
  const { ctx } = state
  ctx.clearRect(0, 0, props.width, props.height)
  ctx.save()
  // hard clip so texts never draw outside canvas bounds
  ctx.beginPath()
  ctx.rect(0, 0, props.width, props.height)
  ctx.clip()

  const perspective = 0.9
  const depth = 2.2

  // rotate a bit each frame; slow down when hovering
  const hoverSlow = hoveredName.value ? 0.24 : 1
  state.rotY += props.speed * hoverSlow
  state.rotX += props.speed * 0.45 * hoverSlow

  // project + sort by z for painter's algorithm
  const projected = state.items.map((it) => {
    const r = rotatePoint(it.p, state.rotX, state.rotY)
    const x = r.x * state.radius
    const y = r.y * state.radius
    const z = r.z * state.radius

    const scale = perspective / (perspective + (z / (state.radius * depth) + 1))
    const sx = state.centerX + x * scale
    const sy = state.centerY + y * scale
    const alpha = clamp01(0.15 + 0.85 * scale)

    return { it, sx, sy, z, scale, alpha }
  }).sort((a, b) => a.z - b.z)

  // draw tags
  for (const p of projected) {
    const isHover = hoveredName.value && p.it.value === hoveredName.value
    const fontScale = isHover ? 1.45 : 1
    const fontSize = Math.max(10, Math.round(p.it.fontSize * (0.85 + p.scale * 0.72) * fontScale))
    const fontWeight = isHover ? 900 : 650
    ctx.font = `${fontWeight} ${fontSize}px Inter, system-ui, -apple-system, "Noto Sans SC", "Helvetica Neue", Arial`
    const metrics = ctx.measureText(p.it.label)
    const w = metrics.width
    const h = fontSize
    const x = p.sx - w / 2
    const y = p.sy + h / 2

    // store bounds for click detection
    p.it.sx = p.sx
    p.it.sy = p.sy
    p.it.alpha = p.alpha
    p.it.scale = p.scale
    p.it.bounds = { x, y: y - h, w, h }

    const baseAlpha = p.alpha * (isHover ? 1 : 0.9)
    ctx.shadowBlur = isHover ? 10 : 0
    ctx.shadowColor = isHover ? 'rgba(30, 30, 30, 0.35)' : 'transparent'
    ctx.fillStyle = isHover ? `rgba(18,18,18,${Math.min(1, baseAlpha + 0.15)})` : `rgba(0,0,0,${baseAlpha * 0.72})`
    ctx.fillText(p.it.label, x, y)
  }

  ctx.restore()

  rafId.value = requestAnimationFrame(drawFrame)
}

function pickTagAt(x, y) {
  if (!state?.items?.length) return ''
  // choose closest hit to pointer, then prefer front-most for ties
  const hits = []
  for (const it of state.items) {
    const b = it.bounds
    if (!b) continue
    if (x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) {
      const cx = b.x + b.w / 2
      const cy = b.y + b.h / 2
      const dist2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
      hits.push({ it, dist2 })
    }
  }
  if (!hits.length) return ''
  hits.sort((a, b) => (a.dist2 - b.dist2) || (b.it.scale - a.it.scale) || (b.it.alpha - a.it.alpha))
  const picked = hits[0].it
  return picked.value || picked.label
}

function handleMouseMove(e) {
  if (!canvasEl.value) return
  const rect = canvasEl.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  pointer.value = { x, y }
  const name = pickTagAt(x, y)
  hoveredName.value = name
  canvasEl.value.style.cursor = name ? 'pointer' : 'default'
}

function handleMouseLeave() {
  hoveredName.value = ''
  pointer.value = { x: -1, y: -1 }
  if (canvasEl.value) canvasEl.value.style.cursor = 'default'
}

function handleClick(e) {
  if (!canvasEl.value) return
  const rect = canvasEl.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const name = pickTagAt(x, y)
  if (name) emit('select', name)
}

watch(
  () => [props.width, props.height, props.radiusScale, normalizedTags.value.map(t => `${t.value}:${t.label}:${t.count}`).join('|')].join('::'),
  () => {
    cancelAnimationFrame(rafId.value)
    init()
    rafId.value = requestAnimationFrame(drawFrame)
  }
)

onMounted(() => {
  init()
  rafId.value = requestAnimationFrame(drawFrame)
})

onUnmounted(() => {
  cancelAnimationFrame(rafId.value)
})
</script>

<style scoped lang="scss">
.tagcloud-canvas-wrap {
  width: 100%;
  display: block;
  overflow: hidden;
}

.tagcloud-canvas {
  display: block;
  margin: 0;
  border-radius: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}
</style>

