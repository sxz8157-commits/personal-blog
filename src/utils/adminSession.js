import { reactive } from 'vue'
// 登录凭据由 HttpOnly Cookie 保存，CSRF token 仅保存在内存中。
export const adminSession = reactive({ authenticated: false, csrfToken: '' })
export function updateSession(data) {
  adminSession.authenticated = data?.authenticated === true
  adminSession.csrfToken = data?.csrf_token || ''
}
