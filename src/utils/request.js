import axios from 'axios'
import { adminSession, updateSession } from './adminSession'

const request = axios.create({ baseURL: '', timeout: 15000, withCredentials: true })
request.interceptors.request.use(config => {
  const method = String(config.method || 'get').toLowerCase()
  const protectedWrite = /^(\/api\/admin(?:\/|$)|\/api\/cards(?:\/|$)|\/api\/about(?:\/|$))/.test(config.url || '')
  if (protectedWrite && !['get','head','options'].includes(method) && adminSession.csrfToken) config.headers['X-CSRF-Token'] = adminSession.csrfToken
  // 不记录请求体或登录密码；上传 boundary 由浏览器生成。
  return config
})
request.interceptors.response.use(response => response.data, error => {
  const status = error.response?.status || 0
  const data = error.response?.data
  if (status === 401) updateSession(null)
  const messages = { 401:'请先登录后台',403:'会话校验失败，请刷新页面',404:'请求的内容不存在',413:'本次上传总大小超过限制',429:'操作过于频繁，请稍后重试',500:'服务器内部错误',502:'网关连接失败',503:'服务暂不可用' }
  return Promise.reject({ status, message:data?.message || messages[status] || (status ? '请求失败' : '网络连接失败，请检查后端服务'), data:typeof data === 'object' ? data : undefined })
})
export default request
