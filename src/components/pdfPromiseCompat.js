// PDF.js 6 的 legacy 包仍直接调用该 API，旧移动 WebView 需要先补齐。
// 保留原生实现；主线程和 PDF 专用 worker 共用同一标准 Promise 能力构造。
export function installPdfPromiseCompat() {
  if (typeof Promise.withResolvers === 'function') return
  Object.defineProperty(Promise, 'withResolvers', {
    configurable: true,
    writable: true,
    value: function withResolvers() {
      let resolve
      let reject
      const promise = new this((resolvePromise, rejectPromise) => {
        resolve = resolvePromise
        reject = rejectPromise
      })
      if (typeof resolve !== 'function' || typeof reject !== 'function') {
        throw new TypeError('Promise 构造函数没有提供有效的 resolve/reject')
      }
      return { promise, resolve, reject }
    }
  })
}
