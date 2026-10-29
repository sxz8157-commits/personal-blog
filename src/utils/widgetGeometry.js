/** 互动元素的边界与相对位置，独立于 DOM，方便验证窄屏和旋转场景。 */
export function dragBounds(width, height, itemWidth, itemHeight, topInset = 12, margin = 12) {
  const maxX = Math.max(0, width - itemWidth - margin)
  const maxY = Math.max(0, height - itemHeight - margin)
  return { left: Math.min(margin, maxX), right: maxX, top: Math.min(topInset, maxY), bottom: maxY }
}
export function clampPoint(point, bounds) {
  return {
    x: Math.min(bounds.right, Math.max(bounds.left, Number.isFinite(point?.x) ? point.x : bounds.left)),
    y: Math.min(bounds.bottom, Math.max(bounds.top, Number.isFinite(point?.y) ? point.y : bounds.top))
  }
}
export function relativePoint(point, bounds) {
  const safe = clampPoint(point, bounds)
  return { x: (safe.x - bounds.left) / (bounds.right - bounds.left || 1), y: (safe.y - bounds.top) / (bounds.bottom - bounds.top || 1) }
}
export function restorePoint(relative, bounds) {
  if (!Number.isFinite(relative?.x) || !Number.isFinite(relative?.y)) return null
  return clampPoint({ x: bounds.left + relative.x * (bounds.right - bounds.left), y: bounds.top + relative.y * (bounds.bottom - bounds.top) }, bounds)
}
export function snapPoint(point, bounds, mode) {
  const safe = clampPoint(point, bounds)
  if (mode === 'edge') safe.x = safe.x - bounds.left < bounds.right - safe.x ? bounds.left : bounds.right
  if (mode === 'grid') { safe.x = Math.round(safe.x / 12) * 12; safe.y = Math.round(safe.y / 12) * 12 }
  return clampPoint(safe, bounds)
}
