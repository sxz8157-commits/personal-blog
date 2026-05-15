# 沛心的个人博客 - 本地运行指南

## 最近更新（2026-04）

- 文章页改为词云导航：点击词云标题可直接进入文章详情。
- 修复 Markdown 详情页层级问题：支持 `#` 到 `######` 标题识别与目录同步。
- 修复音乐播放器“无法切歌”：播放列表扩展为多首，支持顺序循环切换。
- 清理前端页面中的无用样式和调试日志，提升可维护性。

## 项目结构

```
博客/
├── backend/              # 后端 Flask 应用
│   ├── app.py           # Flask 核心应用和 API 路由
│   └── blog.db          # SQLite 数据库 (自动生成)
├── src/                 # 前端 Vue 3 应用
│   ├── components/      # 可复用组件
│   │   ├── ArticleCard.vue    # 文章卡片
│   │   ├── BackToTop.vue      # 返回顶部按钮
│   │   ├── Hero.vue           # 首页 Hero 区域
│   │   ├── Navbar.vue         # 导航栏
│   │   ├── StatsCard.vue      # 统计卡片
│   │   └── Timeline.vue       # 时间线
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态管理
│   ├── styles/          # 全局样式
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML 模板
├── package.json         # 前端依赖
├── requirements.txt     # 后端依赖
└── vite.config.js       # Vite 配置

```

## 环境要求

- **Node.js**: >= 16.0.0
- **Python**: >= 3.8
- **npm/pnpm/yarn**: 任意包管理器

## 快速启动

### 1. 后端启动

```bash
# 进入项目根目录
cd C:\Work\xiangmu\boke

# 创建并激活虚拟环境 (推荐)
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# 或者 Windows CMD
.\venv\Scripts\activate.bat

# 安装后端依赖
pip install -r requirements.txt

# 启动后端服务 (运行在 http://localhost:5000)
python backend/app.py
```

后端服务启动后会:
- ✅ 自动创建 SQLite 数据库 (`backend/blog.db`)
- ✅ 自动初始化示例数据 (3 个分类、3 篇文章)
- ✅ 提供 RESTful API 接口
- ✅ 已配置 CORS 跨域支持

### 2. 前端启动

```bash
# 在另一个终端窗口，进入项目根目录
cd C:\Work\xiangmu\boke

# 安装前端依赖
npm install
# 或使用 pnpm
pnpm install
# 或使用 yarn
yarn install

# 启动前端开发服务器 (运行在 http://localhost:3000)
npm run dev
```

前端开发服务器特性:
- ✅ Vite 热更新 (HMR)
- ✅ 自动代理 `/api` 请求到后端 `http://localhost:5000`
- ✅ SCSS 预处理器支持
- ✅ 路径别名 `@/` 指向 `src/`

### 3. 访问应用

打开浏览器访问: **http://localhost:3000**

## API 接口文档

后端提供以下 RESTful API:

| 方法 | 路径 | 说明 | 示例 |
|------|------|------|------|
| GET | `/api/stats` | 获取统计数据 | 文章数、浏览量、运行时长 |
| GET | `/api/articles` | 获取文章列表 (分页) | `?page=1&per_page=12` |
| GET | `/api/articles/:id` | 获取单篇文章详情 | `/api/articles/1` |
| GET | `/api/categories` | 获取分类列表 | 所有文章分类 |
| POST | `/api/comments` | 创建评论 | 提交评论数据 |
| GET | `/api/meta` | 获取 SEO 信息 | 网站标题、描述等 |
| GET | `/api/md-articles` | 获取 Markdown 文章列表 | 文章词云数据来源 |
| GET | `/api/md-articles/:id` | 获取 Markdown 文章详情 | `/api/md-articles/vue3入门` |

### 示例请求

```bash
# 获取统计数据
curl http://localhost:5000/api/stats

# 获取文章列表
curl http://localhost:5000/api/articles?page=1&per_page=6

# 获取分类列表
curl http://localhost:5000/api/categories
```

## 核心特性

### 前端技术栈
- ✅ **Vue 3 Composition API** (`<script setup>` 语法糖)
- ✅ **Vite** 极速构建工具
- ✅ **Element Plus** UI 组件库
- ✅ **Pinia** 状态管理
- ✅ **Vue Router** 路由管理
- ✅ **SCSS** 样式预处理器
- ✅ **GSAP** 专业动画库

### 视觉设计
- ✅ **全息毛玻璃拟态** (Glassmorphism)
- ✅ **赛博朋克二次元微光风格**
- ✅ **霓虹紫 + 赛博粉 + 全息蓝** 配色体系
- ✅ **极致响应式** 设计 (手机/平板/桌面)
- ✅ **高质量二次元壁纸** 全屏背景

### 动画交互
- ✅ **打字机效果** Hero 标题动画
- ✅ **交错瀑布流** 卡片淡入上浮
- ✅ **丝滑贝塞尔曲线** 过渡动画
- ✅ **硬件加速** 优化 (防止掉帧)
- ✅ **微交互反馈** (Hover/Click/Scroll)
- ✅ **动态导航栏** (滚动变窄、模糊加深)

### 后端架构
- ✅ **Flask** 轻量级 Web 框架
- ✅ **SQLAlchemy** ORM 数据库操作
- ✅ **SQLite** 零配置数据库
- ✅ **Flask-CORS** 跨域解决方案
- ✅ **RESTful API** 设计规范
- ✅ **自动数据初始化** (首次运行)

## 自定义配置

### 修改背景壁纸

编辑 `src/styles/main.scss` 中的 `body::before`:

```scss
body {
  &::before {
    background: url('你的壁纸URL') center/cover no-repeat fixed;
  }
}
```

### 修改主题色

编辑 `src/styles/variables.scss`:

```scss
:root {
  --primary-color: #a855f7;      // 主色调
  --secondary-pink: #ec4899;     // 赛博粉
  --secondary-blue: #3b82f6;     // 全息蓝
}
```

### 修改打字机文字

编辑 `src/components/Hero.vue`:

```javascript
const titleText = '欢迎来到沛心的博客'
const subtitle = '探索技术之美，记录生活点滴 ✨'
```

## 构建部署

### 前端生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录，可部署到:
- Vercel
- Netlify
- GitHub Pages
- 任意静态托管服务

### 后端生产部署

```bash
# 安装生产级 WSGI 服务器
pip install gunicorn

# 启动生产服务
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

或使用 Docker 容器化部署。

## 常见问题

### Q: 后端启动失败，提示端口被占用
A: 修改 `backend/app.py` 中的端口号:
```python
app.run(debug=True, port=5001)  # 改为其他端口
```

### Q: 前端无法访问后端 API
A: 检查 Vite 代理配置 `vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // 确保端口正确
      changeOrigin: true
    }
  }
}
```

### Q: 数据库初始化失败
A: 删除 `backend/blog.db` 后重新启动后端，会自动重新创建。

### Q: 图片加载缓慢
A: 项目已实现渐进式图片懒加载和骨架屏占位，首次加载会显示 loading 动画。

## 技术支持

- Vue 3 官方文档: https://vuejs.org/
- Element Plus 文档: https://element-plus.org/
- Flask 官方文档: https://flask.palletsprojects.com/
- Vite 官方文档: https://vitejs.dev/

---

**Enjoy Coding! ✨**
