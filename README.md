# 个人博客与内容管理

Vue 3 + Vite 前端，Flask + SQLite 后端。后台入口为 `/admin`，管理文章、页面文案、个人简介、卡片与媒体文件。

2026-10-03 已部署到 [HTTPS 网站](https://115.159.92.222/) 和[后台](https://115.159.92.222/admin)。实际服务器目录、systemd、证书续期、备份和验证方法见 [.Codex/生产部署.md](.Codex/生产部署.md)。线上使用独立后台凭据，位置记录在该文档中；不使用服务器 SSH 密码登录博客后台。

## 本地启动（Windows / PowerShell）

在项目根目录执行，Python 建议 3.11 以上，Node.js 使用 22.12 以上或 24。

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
# 首次配置或更换管理员密码；密码不会回显。
backend/.venv/Scripts/python.exe backend/manage.py configure-admin
# 只为空表添加示例内容，不覆盖已有数据。
backend/.venv/Scripts/python.exe -m flask --app backend.app init-db
backend/.venv/Scripts/python.exe -m flask --app backend.app run --host 127.0.0.1 --port 8000
```

另一个终端执行：

```powershell
cd src
npm ci
npm run dev -- --host 127.0.0.1
```

打开 `http://127.0.0.1:4000`，后台为 `http://127.0.0.1:4000/admin`。启动脚本 `start-backend.bat` 使用新建的 `backend/.venv`。

本次整改已经生成新的本地管理配置 `.env`。初始密码保存在 `backend/.admin-initial-password.txt`，它与 `.env` 都被 Git 忽略。需要更换时运行上面的 `configure-admin`；旧密码和旧登录会话会失效。不要把这两个文件上传到静态站点。

## 首次进入与刷新

- 每次完整打开或刷新页面，先显示加载界面与动态加载条；应用脚本下载期间也有静态加载页。
- 图片完成加载和解码，或视频首帧可显示，且全局文案、统计请求和初始路由准备完成后，自动进入网站。视频后续内容继续正常缓冲，各页面自己的数据保留原有加载提示。
- 背景列表最多等待 8 秒，单个图片或视频最多等待 12 秒；视频失败尝试图片，均失败使用默认渐变背景。应用初始化总等待上限为 20 秒，避免长时间无法进入。
- 站内切换页面复用当前背景；完整刷新重新加载。手机布局适配，并遵守系统“减少动态效果”设置。

## 后台内容范围

- **文章管理**：新增、编辑、删除、按标题搜索、分类选择、摘要、封面、Markdown 正文、草稿和发布状态。发布后进入文章词云；草稿的公开详情、点赞与评论接口均返回 404。
- **页面文案**：站点名称、作者、SEO 描述与关键词、导航标签；首页标题与按钮；文章页、关于页、更多页与 404 页的标题和提示；开发日志的新增、编辑、删除与排序。
- **关于页面**：姓名、简介、标签、技能与联系方式，通过一次请求在同一事务中保存。
- **网站卡片**：项目介绍、技能卡片和标签的增删改。
- **文档文件**：上传、删除；现有 Markdown/TXT 可在线编辑，保存后直接公开。需要草稿时使用“文章管理”。PDF、DOCX、XLSX、PPTX、XMind 保留文件上传和预览入口。
- **背景/音频**：上传与删除；前后端使用相同的白名单，中文文件名保留。

音乐盒优先使用音频内嵌的歌名和艺术家；缺失标签时按 `歌名 - 作者` 或 `歌名_-_作者` 的文件名回退。原文件与播放 URL 保持不变。标签读取使用 [Mutagen](https://mutagen.readthedocs.io/en/latest/api/base.html)（已加入后端 requirements）；更新此修复时安装后端依赖并重启服务，前端刷新后重新获取列表。

页面文案复用 `about_content` 表的 `page_*` 分区，文章复用 `articles` 表。没有新增表或变更字段。`/api/about` 的原返回结构保留。

## 文件与数据

- 默认数据库：`backend/blog.db`。
- 默认公开文件根目录：`backend/public`；读、写、删除均使用该目录。生产可通过 `PUBLIC_DIR` 指定持久目录。
- 现有文件目录中全部文档是公开资料，请只在其中保存准备公开的文件。草稿正文存放在数据库中。
- 前端构建不复制公开文件、部署文档或后端配置，文档详情直接使用后端返回的 `/api/files/...` URL。
- 每次最多 20 个文件，总文件大小最多 100MB，请求含 multipart 开销最多 105MB。文本 1MB、图片 5MB、音频 50MB、视频和其它文档 100MB。图片校验实际格式，Office/XMind 校验容器结构，文本必须是 UTF-8。

## 生产部署（Linux）

1. 停止写入后备份 SQLite 和公开文件目录。可使用 SQLite backup API 或 `sqlite3 backend/blog.db '.backup /安全路径/blog.db'`；运行中的数据库不要只复制主文件而遗漏 WAL。
2. 使用独立虚拟环境安装 `backend/requirements-prod.txt`，在服务器配置根目录 `.env`。参考 `.env.example`，设置 `APP_ENV=production`、`SITE_URL=https://peixin.uno`、正确的 `PUBLIC_DIR` 与 `DATABASE_URL`。
3. 在服务器运行 `python backend/manage.py configure-admin`，配置独立密码。根目录 `.env` 必须由服务账户读取；部署时不要复制本机初始密码文件。每次手动更换密码同时轮换 `SECRET_KEY`，使旧会话失效。
4. 后端启动前运行 `python -m flask --app backend.app init-db`。已有内容不会被重新填充或覆盖。
5. 从项目根目录运行：

```bash
gunicorn --workers 1 --threads 4 --timeout 120 --bind 127.0.0.1:8000 backend.app:app
```

当前评论、点赞与登录限流存储在进程内，因此使用 **一个 worker**、多个线程；多进程部署前需要共享限流存储。

6. 在 `src` 执行 `npm ci && npm run build`，只把 `src/dist` 部署到 Nginx 静态目录。
7. 对照 `nginx.conf` 调整真实目录和证书路径，执行 `nginx -t` 后再加载配置。Nginx 与 Flask 必须使用同一个公开文件物理目录。80 端口跳转 HTTPS，API 转发到回环地址 8000；`/sitemap.xml` 和 `/feed.xml` 也转发后端。
8. 后端前方只有一层可信 Nginx、且后端不对公网开放时设置 `TRUST_PROXY=true`。生产 Cookie 带 `Secure`，必须通过 HTTPS 登录。

配置修改后重新启动后端。禁止使用 Windows 开发启动脚本作为生产服务。

## 验证

```powershell
backend/.venv/Scripts/python.exe -m unittest discover -s backend/tests -v
cd src
npm run build
npm audit
```

接口测试使用临时数据库与文件目录，不修改博客正式内容。浏览器验证同样使用 `.Codex/qa` 内的副本。

Git 已停止跟踪本机 `.env`、SQLite 和构建产物；旧 Git 历史仍可能含旧口令，当前版本已废弃该口令。远端历史清理涉及协同与强制推送，需要另行处理。

本地数据备份位于 `C:\tools\boke\.Codex-backups\20261003-blog-before-cms`。若需恢复数据，先停服务，再从备份恢复数据库及公开文件，之后使用当前修复版本启动，避免旧启动逻辑覆盖内容。

接口与权限说明见 [docs/API.md](docs/API.md)。

HTML 清理使用 [DOMPurify](https://github.com/cure53/DOMPurify)；SheetJS 使用[官方发布包](https://docs.sheetjs.com/docs/getting-started/installation/nodejs/)，npm 上旧的 `xlsx@0.18.5` 不再使用。
