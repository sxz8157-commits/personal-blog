import axios from 'axios'

// 判断是否为开发环境
const isDevelopment =
  import.meta.env.DEV ||
  (typeof process !== 'undefined' && process?.env?.NODE_ENV === 'development')

// 创建axios实例
const request = axios.create({
  // 同域名部署，baseURL留空即可，会自动请求当前域名的/api
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 开发环境记录请求日志
    if (isDevelopment) {
      console.log(`📤 [${config.method?.toUpperCase()}] ${config.url}`, {
        params: config.params,
        data: config.data
      })
    }

    // 可以在这里添加认证token等
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }

    return config
  },
  error => {
    // 请求配置错误
    if (isDevelopment) {
      console.error('❌ 请求配置错误:', error)
    }
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 开发环境记录响应日志
    if (isDevelopment) {
      console.log(`📥 [${response.status}] ${response.config.url}`, response.data)
    }
    
    // 直接返回数据
    return response.data
  },
  error => {
    // 统一错误处理
    if (axios.isCancel(error)) {
      // 请求被取消
      console.warn('⚠️ 请求被取消:', error.message)
      return Promise.reject(new Error('请求已取消'))
    }

    if (!error.response) {
      // 网络错误或超时
      console.error('🌐 网络错误:', error.message)
      return Promise.reject(new Error('网络连接失败，请检查网络设置'))
    }

    const { status, data } = error.response
    
    // 开发环境记录错误详情
    if (isDevelopment) {
      console.error(`❌ [${status}] ${error.config?.url}:`, {
        message: error.message,
        response: data
      })
    }

    // 根据状态码处理错误
    let errorMessage = '请求失败'
    
    switch (status) {
      case 400:
        errorMessage = data?.message || '请求参数错误'
        break
      case 401:
        errorMessage = '未授权，请重新登录'
        // 可以在这里触发登出逻辑
        // localStorage.removeItem('token')
        // window.location.href = '/login'
        break
      case 403:
        errorMessage = '拒绝访问'
        break
      case 404:
        errorMessage = '请求的资源不存在'
        break
      case 408:
        errorMessage = '请求超时'
        break
      case 500:
        errorMessage = '服务器内部错误'
        break
      case 502:
        errorMessage = '网关错误'
        break
      case 503:
        errorMessage = '服务不可用'
        break
      case 504:
        errorMessage = '网关超时'
        break
      default:
        errorMessage = data?.message || `请求失败 (${status})`
    }

    // 返回统一的错误格式
    return Promise.reject({
      status,
      message: errorMessage,
      data: data,
      originalError: error
    })
  }
)

// 添加取消请求的方法
const cancelTokenSource = axios.CancelToken.source()
request.cancelTokenSource = cancelTokenSource

// 添加取消所有请求的方法
request.cancelAllRequests = (message = '用户取消请求') => {
  cancelTokenSource.cancel(message)
}

export default request
