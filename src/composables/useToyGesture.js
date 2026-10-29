import { onUnmounted, ref } from 'vue'

/** 在原有拖动之上区分点击、长按和划动，只在按下期间监听窗口。 */
export function useToyGesture(drag, onGesture) {
  const pressing = ref(false), charged = ref(false)
  let active = null, holdTimer = null, suppressUntil = 0
  function start(event) {
    if (event.button !== 0 || event.isPrimary === false || active) return
    drag.begin(event)
    active = { id: event.pointerId, x: event.clientX, y: event.clientY, dx: 0, dy: 0, distance: 0, at: performance.now() }
    pressing.value = true
    holdTimer = setTimeout(() => { if (active && active.distance < 9) charged.value = true }, 400)
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', finish)
    window.addEventListener('pointercancel', cancel)
    window.addEventListener('blur', cancel)
  }
  function move(event) {
    if (event.pointerId !== active?.id) return
    active.dx = event.clientX - active.x; active.dy = event.clientY - active.y
    active.distance = Math.max(active.distance, Math.hypot(active.dx, active.dy))
    if (active.distance >= 9) { clearTimeout(holdTimer); charged.value = false }
  }
  function clear() {
    clearTimeout(holdTimer); holdTimer = null; active = null
    pressing.value = false; charged.value = false
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', finish)
    window.removeEventListener('pointercancel', cancel)
    window.removeEventListener('blur', cancel)
  }
  function finish(event) {
    if (event.pointerId !== active?.id) return
    const gesture = { ...active, duration: performance.now() - active.at }
    clear()
    if (gesture.distance >= 9 || gesture.duration >= 400) {
      suppressUntil = performance.now() + 400
      onGesture(gesture.distance >= 9 ? 'swipe' : 'hold', gesture)
    }
  }
  function cancel() { if (active) suppressUntil = performance.now() + 400; clear() }
  function guard(event) {
    drag.guardClick(event)
    if (event.detail && performance.now() < suppressUntil) { event.preventDefault(); event.stopImmediatePropagation() }
  }
  onUnmounted(clear)
  return { pressing, charged, start, guard, cancel }
}
