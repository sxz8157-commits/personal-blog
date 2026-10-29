# 页面互动元素

本次按用户“可点、可拖”的要求实现四种互动，保留原壁纸、紫粉色和玻璃风格。

## 使用方式

- **小唱片**：页面左下方的小浮件，点击播放/暂停既有音乐，拖动后贴边；选项中可复位或收起。只有一个音频元素，导航音乐盒与唱片共用播放状态。
- **换壁纸按钮**：与唱片合成同一组可拖浮件；点击准备下一张图/视频，就绪才替换，失败保留当前壁纸。手动与自动轮播共用进行中的任务，连续点击不并发。
- **纸飞机**：更多页底部“随手玩一会儿”中，点击轻弹，拖动松手回弹。
- **互动磁贴**：同一区域内的三枚小磁贴，点击显示现有页面文案，拖动后吸附；“全部归位”恢复位置并收起内容。

手机打开键盘、导航菜单或音乐盒时浮件避让；更多页互动区域进入视口时也暂时隐藏浮件，离开恢复。后台不展示挂件。减少动态效果偏好下保留操作、省略旋转和弹性动画。

拖动只作用于小控件本身，不拦截整页滚动；超过约 7px 才算拖动，避免松手误触点击。键盘方向键可挪动，Home 复位。本地只保存浮件相对位置，不增加阅读记录、稍后读或静读功能，不增加第三方请求或运行依赖。

## 实现与检查

- `src/components/InteractiveDock.vue`：唱片、壁纸按钮、复位/收起与避让。
- `src/components/PlayfulCorner.vue`、`MagneticNote.vue`：纸飞机与磁贴。
- `src/composables/usePointerDrag.js`、`src/utils/widgetGeometry.js`：共用拖动与边界。
- `src/App.vue`、`src/components/Navbar.vue`、`src/views/More.vue`：接入原播放/轮播状态与更多页。
- `node --test tests/widgetGeometry.test.mjs`：几何边界、相对位置、吸附测试。

参考：[Pointer Events](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events)、[指针捕获](https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture)。复用原音乐播放器、背景队列及已验证的前端增量发布器。

## 本地已验证

Vite build、3 项几何单元测试、17 项浏览器场景、原文章页四尺寸回归通过。覆盖真实 WAV 播放/暂停、共享音频、拖动/点击区分、触摸、回弹、吸附、复位、收起、手动/自动切背景互斥、失败保留、存储异常、键盘避让、转屏、减少动态效果及切页清理。无 pageerror、Vue 警告或内容写请求。

手机使用 Edge/CDP 触摸模拟，实体手机/微信未实测。本地原接口数据采用公开只读快照，媒体失败/竞态使用隔离夹具；上线后另做真实 HTTPS 验收。

主 JS gzip 从约 73.53KB 增至约 76.74KB，增加约 3.21KB；更多页按原路由按需加载。未更改后端、数据库、认证或生产配置。
