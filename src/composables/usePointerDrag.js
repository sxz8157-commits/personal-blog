import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { clampPoint, dragBounds, relativePoint, restorePoint, snapPoint } from '@/utils/widgetGeometry'

/** 只在具体小元素上接管手势；超过阈值后才捕获指针，保留原生按钮点击。 */
export function usePointerDrag(target, { area, initial, snap = '', returnHome = false, storageKey = '' } = {}) {
  const point = ref({ x: 0, y: 0 })
  const ready = ref(false)
  const dragging = ref(false)
  const settling = ref(false)
  let gesture = null, lastBounds = null, frame = 0, settleTimer = null, observer = null, blockClickUntil = 0
  const style = computed(() => ({ transform: `translate3d(${point.value.x}px, ${point.value.y}px, 0)`, visibility: ready.value ? 'visible' : 'hidden' }))
  function bounds() {
    const element = target.value
    if (!element || !element.offsetWidth) return null
    const box = area?.value
    if (area && !box) return null
    const width = box ? box.clientWidth : document.documentElement.clientWidth
    const height = box ? box.clientHeight : window.innerHeight
    const top = box ? 12 : (document.querySelector('.navbar')?.getBoundingClientRect().bottom || 56) + 12
    const result = dragBounds(width, height, element.offsetWidth, element.offsetHeight, top, box ? 12 : 20)
    // 给右下角原有返回顶部和手机安全区留出停靠空间。
    if (!box) result.bottom = Math.max(result.top, result.bottom - 80)
    return result
  }
  function home(b) { return clampPoint(initial?.(b) || { x: b.left, y: b.bottom }, b) }
  function save() {
    if (!storageKey || !lastBounds) return
    try { localStorage.setItem(storageKey, JSON.stringify(relativePoint(point.value, lastBounds))) }
    catch (error) { console.warn('互动位置无法保存，仍可正常拖动:', error.name) }
  }
  function reflow() {
    const b = bounds()
    if (!b) return
    if (gesture) finish(true)
    let next = ready.value && lastBounds ? restorePoint(relativePoint(point.value, lastBounds), b) : null
    if (!ready.value && storageKey) {
      try { next = restorePoint(JSON.parse(localStorage.getItem(storageKey) || 'null'), b) }
      catch (error) { console.warn('互动位置记录不可用，将使用默认位置:', error.name) }
    }
    point.value = snapPoint(returnHome ? home(b) : next || home(b), b, snap)
    lastBounds = b
    ready.value = true
  }
  function reset() {
    if (gesture) finish(true)
    const b = bounds()
    if (!b) return
    point.value = snapPoint(home(b), b, snap)
    lastBounds = b
    settling.value = true
    clearTimeout(settleTimer)
    settleTimer = setTimeout(() => { settling.value = false }, 380)
    save()
  }
  function begin(event) {
    if (event.button !== 0 || event.isPrimary === false || gesture || event.target.closest('[data-no-drag]')) return
    const b = bounds()
    if (!b) return
    clearTimeout(settleTimer)
    settling.value = false
    lastBounds = b
    gesture = { id: event.pointerId, startX: event.clientX, startY: event.clientY, origin: { ...point.value }, next: { ...point.value } }
    window.addEventListener('pointermove', move, { passive: false })
    window.addEventListener('pointerup', end)
    window.addEventListener('pointercancel', cancel)
    window.addEventListener('blur', cancel)
  }
  function move(event) {
    if (!gesture || gesture.id !== event.pointerId) return
    const dx = event.clientX - gesture.startX, dy = event.clientY - gesture.startY
    if (!dragging.value && Math.hypot(dx, dy) < 7) return
    if (!dragging.value) {
      dragging.value = true
      try { target.value?.setPointerCapture(gesture.id) }
      catch (error) { console.warn('指针捕获不可用，将继续跟踪拖动:', error.name) }
    }
    event.preventDefault()
    gesture.next = clampPoint({ x: gesture.origin.x + dx, y: gesture.origin.y + dy }, lastBounds)
    if (!frame) frame = requestAnimationFrame(() => { frame = 0; if (gesture) point.value = gesture.next })
  }
  function finish(cancelled = false) {
    const current = gesture
    if (!current) return
    cancelAnimationFrame(frame)
    frame = 0
    const moved = dragging.value
    gesture = null
    dragging.value = false
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', end)
    window.removeEventListener('pointercancel', cancel)
    window.removeEventListener('blur', cancel)
    if (target.value?.hasPointerCapture(current.id)) target.value.releasePointerCapture(current.id)
    if (moved) {
      blockClickUntil = performance.now() + 350
      point.value = cancelled ? current.origin : returnHome ? home(lastBounds) : snapPoint(current.next, lastBounds, snap)
      settling.value = true
      clearTimeout(settleTimer)
      settleTimer = setTimeout(() => { settling.value = false }, 380)
      if (!cancelled) save()
    }
  }
  function end(event) { if (gesture?.id === event.pointerId) finish() }
  function cancel() { finish(true) }
  function guardClick(event) {
    if (event.detail && performance.now() < blockClickUntil) { event.preventDefault(); event.stopImmediatePropagation() }
  }
  function keydown(event) {
    if (event.target.closest('[data-no-drag]')) return
    if (event.key === 'Home') { event.preventDefault(); reset(); return }
    const directions = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }
    const direction = directions[event.key]
    if (!direction) return
    event.preventDefault()
    const b = bounds()
    if (!b) return
    const step = event.shiftKey ? 24 : 10
    point.value = clampPoint({ x: point.value.x + direction[0] * step, y: point.value.y + direction[1] * step }, b)
    lastBounds = b
    save()
  }
  onMounted(() => {
    reflow()
    observer = new ResizeObserver(reflow)
    if (target.value) observer.observe(target.value)
    if (area?.value) observer.observe(area.value)
    window.addEventListener('resize', reflow)
  })
  watch(() => area?.value, (next, previous) => {
    if (previous) observer?.unobserve(previous)
    if (next) observer?.observe(next)
    reflow()
  }, { flush: 'post' })
  onUnmounted(() => {
    finish(true)
    observer?.disconnect()
    window.removeEventListener('resize', reflow)
    cancelAnimationFrame(frame)
    clearTimeout(settleTimer)
  })
  return { point, style, ready, dragging, settling, begin, guardClick, keydown, reset }
}
