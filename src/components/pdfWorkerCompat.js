import { installPdfPromiseCompat } from './pdfPromiseCompat'

installPdfPromiseCompat()

// 动态导入保证兼容补齐先执行，加载结束后才允许主线程发起 PDF 消息。
import('pdfjs-dist/legacy/build/pdf.worker.mjs').then(() => {
  self.postMessage({ type: 'blog-pdf-worker-ready' })
}).catch(error => {
  self.postMessage({ type: 'blog-pdf-worker-error', message: error.message || 'PDF worker 加载失败' })
})
