import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElIcon } from 'element-plus'
import App from './App.vue'
import router from './router'
import './styles/main.scss'

const app = createApp(App)
const pinia = createPinia()

// 页面只使用图标容器；按需注册，避免首屏下载整套组件和所有图标。
app.component('ElIcon', ElIcon)
app.use(pinia)
app.use(router)

app.mount('#app')
// Vue 已显示动态加载页后，移除脚本下载阶段的静态首屏。
document.getElementById('boot-loading')?.remove()
