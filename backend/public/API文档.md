# 📘 沛心的个人博客 - API 接口文档

> 基于 **Flask + SQLAlchemy + SQLite** 的 RESTful API 服务

---

## 📌 基本信息

| 项目 | 说明 |
|------|------|
| **基础路径** | `http://localhost:5000` (开发环境) |
| **API 前缀** | `/api` |
| **数据格式** | JSON |
| **字符编码** | UTF-8 (支持中文) |
| **跨域支持** | 已启用 CORS |

---

##  接口列表

### 1. 获取统计数据
获取博客的整体运营数据，用于首页展示。

- **接口**: `GET /api/stats`
- **描述**: 获取文章总数、总浏览量、评论总数、分类总数、运行天数
- **认证**: 无需认证

**请求示例**:
```bash
curl http://localhost:5000/api/stats
```

**响应示例**:
```json
{
  "total_articles": 42,
  "total_views": 3568,
  "total_comments": 128,
  "total_categories": 4,
  "days_running": 156
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `total_articles` | integer | 已发布的文章总数 |
| `total_views` | integer | 所有文章浏览量总和 |
| `total_comments` | integer | 评论总数（含回复） |
| `total_categories` | integer | 分类总数 |
| `days_running` | integer | 从第一篇文章创建至今的天数 |

**调用位置**: [App.vue](src/App.vue) `onMounted()` 初始化时调用

---

### 2. 获取文章列表
分页获取已发布的文章列表，支持按分类筛选。

- **接口**: `GET /api/articles`
- **描述**: 分页查询文章列表
- **认证**: 无需认证

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `per_page` | integer | 否 | 12 | 每页数量 |
| `category_id` | integer | 否 | - | 分类ID筛选 |

**请求示例**:
```bash
curl "http://localhost:5000/api/articles?page=1&per_page=12"
```

**响应示例**:
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Vue 3 Composition API 最佳实践",
      "summary": "深入探讨 Vue 3 组合式 API 的使用技巧和设计模式",
      "cover_image": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800",
      "category": {
        "id": 1,
        "name": "前端开发",
        "description": "Vue, React, CSS 等前端技术",
        "article_count": 15
      },
      "views": 128,
      "likes": 45,
      "created_at": "2026-03-15 14:30:00",
      "updated_at": "2026-03-20 10:15:00"
    }
  ],
  "total": 42,
  "pages": 4,
  "current_page": 1
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `articles` | array | 文章列表数组 |
| `articles[].id` | integer | 文章ID |
| `articles[].title` | string | 文章标题 |
| `articles[].summary` | string | 文章摘要 |
| `articles[].cover_image` | string | 封面图片URL |
| `articles[].category` | object | 分类信息 |
| `articles[].views` | integer | 浏览量 |
| `articles[].likes` | integer | 点赞数 |
| `articles[].created_at` | string | 创建时间 (YYYY-MM-DD HH:MM:SS) |
| `articles[].updated_at` | string | 更新时间 |
| `total` | integer | 文章总数 |
| `pages` | integer | 总页数 |
| `current_page` | integer | 当前页码 |

**调用位置**: [Articles.vue](src/views/Articles.vue) `fetchArticles()`

---

### 3. 获取文章详情
获取单篇文章的完整内容、评论列表，并自动增加浏览量。

- **接口**: `GET /api/articles/:article_id`
- **描述**: 获取文章详情和评论
- **认证**: 无需认证

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `article_id` | integer | 是 | 文章ID |

**请求示例**:
```bash
curl http://localhost:5000/api/articles/1
```

**响应示例**:
```json
{
  "article": {
    "id": 1,
    "title": "Vue 3 Composition API 最佳实践",
    "summary": "深入探讨 Vue 3 组合式 API 的使用技巧和设计模式",
    "cover_image": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800",
    "category": {
      "id": 1,
      "name": "前端开发",
      "description": "Vue, React, CSS 等前端技术",
      "article_count": 15
    },
    "views": 129,
    "likes": 45,
    "created_at": "2026-03-15 14:30:00",
    "updated_at": "2026-03-20 10:15:00"
  },
  "content": "# Vue 3 Composition API 最佳实践\n\n这里是文章内容...",
  "comments": [
    {
      "id": 1,
      "author_name": "张三",
      "content": "写得非常好，受益匪浅！",
      "created_at": "2026-03-16 09:20:00",
      "replies": [
        {
          "id": 2,
          "author_name": "沛心",
          "content": "感谢支持！有问题随时交流。",
          "created_at": "2026-03-16 10:05:00",
          "replies": []
        }
      ]
    }
  ]
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `article` | object | 文章基本信息 |
| `content` | string | 文章正文 (Markdown 格式) |
| `comments` | array | 顶级评论列表（不含回复） |
| `comments[].replies` | array | 回复列表（嵌套结构） |

**副作用**: 每次请求自动将 `views` 字段 +1

**调用位置**: [ArticleDetail.vue](src/views/ArticleDetail.vue) `fetchArticle()`

---

### 4. 获取分类列表
获取所有文章分类及其文章数量。

- **接口**: `GET /api/categories`
- **描述**: 获取分类列表
- **认证**: 无需认证

**请求示例**:
```bash
curl http://localhost:5000/api/categories
```

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "前端开发",
    "description": "Vue, React, CSS 等前端技术",
    "article_count": 15
  },
  {
    "id": 2,
    "name": "后端开发",
    "description": "Python, Flask, 数据库等",
    "article_count": 12
  },
  {
    "id": 3,
    "name": "生活随笔",
    "description": "日常思考与生活记录",
    "article_count": 8
  },
  {
    "id": 4,
    "name": "项目实战",
    "description": "完整项目开发经验",
    "article_count": 7
  }
]
```

**调用位置**: 暂无前端调用（预留接口）

---

### 5. 创建评论
为指定文章添加评论或回复。

- **接口**: `POST /api/comments`
- **描述**: 创建新评论或回复
- **认证**: 无需认证

**请求体**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `article_id` | integer | 是 | 文章ID |
| `author_name` | string | 是 | 评论者昵称 |
| `author_email` | string | 是 | 评论者邮箱 |
| `content` | string | 是 | 评论内容 |
| `parent_id` | integer | 否 | 父评论ID（回复时使用） |

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/comments \
  -H "Content-Type: application/json" \
  -d '{
    "article_id": 1,
    "author_name": "李四",
    "author_email": "lisi@example.com",
    "content": "这篇文章太棒了！",
    "parent_id": null
  }'
```

**响应示例**:
```json
{
  "message": "评论成功",
  "comment": {
    "id": 5,
    "author_name": "李四",
    "content": "这篇文章太棒了！",
    "created_at": "2026-04-08 15:30:00",
    "replies": []
  }
}
```

**状态码**:
- `201 Created`: 评论创建成功
- `400 Bad Request`: 缺少必需字段或字段为空
- `500 Internal Server Error`: 服务器内部错误

---

### 6. 获取 SEO Meta 信息
获取博客的 SEO 元数据。

- **接口**: `GET /api/meta`
- **描述**: 获取博客标题、描述、关键词等 SEO 信息
- **认证**: 无需认证

**请求示例**:
```bash
curl http://localhost:5000/api/meta
```

**响应示例**:
```json
{
  "title": "沛心的个人博客",
  "description": "一个充满赛博朋克风格的个人技术博客，分享编程心得与生活感悟",
  "keywords": "博客, 技术, 编程, Vue, Python, Flask",
  "author": "沛心"
}
```

**调用位置**: 暂无前端调用（预留接口）

---

##  数据模型

### Article (文章)
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | integer | 主键 | 文章ID |
| `title` | string(200) | ✅ | 文章标题 |
| `summary` | text | ❌ | 文章摘要 |
| `content` | text | ✅ | 文章正文 |
| `cover_image` | string(500) | ❌ | 封面图片URL |
| `category_id` | integer | ❌ | 分类ID (外键) |
| `views` | integer | 默认0 | 浏览量 |
| `likes` | integer | 默认0 | 点赞数 |
| `is_published` | boolean | 默认true | 是否发布 |
| `created_at` | datetime | 自动生成 | 创建时间 |
| `updated_at` | datetime | 自动更新 | 更新时间 |

### Category (分类)
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | integer | 主键 | 分类ID |
| `name` | string(50) | ✅ 唯一 | 分类名称 |
| `description` | string(200) | ❌ | 分类描述 |
| `created_at` | datetime | 自动生成 | 创建时间 |

### Comment (评论)
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | integer | 主键 | 评论ID |
| `article_id` | integer | ✅ | 文章ID (外键) |
| `author_name` | string(100) | ✅ | 评论者昵称 |
| `author_email` | string(120) | ✅ | 评论者邮箱 |
| `content` | text | ✅ | 评论内容 |
| `parent_id` | integer | ❌ | 父评论ID (自回复) |
| `created_at` | datetime | 自动生成 | 创建时间 |

---

## 🔧 前端集成

### Vite 代理配置 ([vite.config.js](vite.config.js))
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```
- 开发环境下，所有 `/api` 请求自动转发到 Flask 后端
- 前端无需处理跨域问题

### Axios 封装 ([request.js](src/utils/request.js))
```javascript
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```
- 自动添加 `/api` 前缀
- 15秒超时时间
- 请求/响应拦截器
- 统一错误处理 (400/401/403/404/500 等)
- 开发环境日志输出

---

## 🚀 启动方式

### 后端启动
```bash
cd backend
pip install flask flask-cors flask-sqlalchemy python-dotenv
python app.py
```
后端服务运行在 `http://localhost:5000`

### 前端启动
```bash
npm install
npm run dev
```
前端服务运行在 `http://localhost:3000`

### 数据库初始化
首次运行 `python app.py` 时自动执行 `init_db()`，创建示例数据：
- 4 个文章分类
- 3 篇示例文章

---

## ⚠️ 错误响应格式

**通用错误响应**:
```json
{
  "error": "错误类型",
  "message": "错误描述"
}
```

**HTTP 状态码说明**:
| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**前端错误处理示例** ([request.js](src/utils/request.js)):
```javascript
request.interceptors.response.use(
  response => response.data,
  error => {
    // 400 → "请求参数错误"
    // 401 → "未授权，请重新登录"
    // 404 → "请求的资源不存在"
    // 500 → "服务器内部错误"
    return Promise.reject({ status, message, data })
  }
)
```

---

## 📝 注意事项

1. **时间格式**: 所有时间字段使用 `YYYY-MM-DD HH:MM:SS` 格式
2. **Markdown 支持**: 文章 `content` 字段存储 Markdown 格式文本
3. **评论嵌套**: `parent_id` 为 `null` 表示顶级评论，否则为回复
4. **分页逻辑**: 使用 SQLAlchemy 的 `paginate()` 方法，页码从 1 开始
5. **浏览量统计**: 获取文章详情时自动 +1，列表接口不增加
6. **字符编码**: 已配置 `JSON_AS_ASCII = False` 支持中文

---

##  文档版本

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-04-08 | 初始版本 |

---

> 💡 **提示**: 开发环境可通过 Vite 代理直接访问后端接口，生产环境需配置独立域名或路径。
