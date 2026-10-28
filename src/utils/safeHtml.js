import DOMPurify from 'dompurify'
export function safeUrl(value, image = false) {
  const url = String(value || '').trim()
  if (/[\u0000-\u0020\\]/.test(url)) return ''
  if (/^https?:\/\//i.test(url) || /^\/(?!\/)/.test(url) || url.startsWith('#')) return url
  if (!image && /^mailto:[^\s]+$/i.test(url)) return url
  if (image && /^data:image\/(png|jpeg|gif|webp|bmp);base64,/i.test(url)) return url
  if (url && !/^[a-z][a-z\d+.-]*:/i.test(url) && !url.startsWith('//')) return url
  return ''
}
DOMPurify.addHook('afterSanitizeAttributes', node => {
  for (const attribute of ['href', 'src']) {
    if (node.hasAttribute(attribute) && !safeUrl(node.getAttribute(attribute), attribute === 'src')) node.removeAttribute(attribute)
  }
  if (node.tagName === 'A') node.setAttribute('rel', 'noopener noreferrer')
})
export function sanitizeHtml(html) {
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true }, FORBID_TAGS: ['style','iframe','form','input','button'], FORBID_ATTR: ['style'] })
}
