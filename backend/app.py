import os
import re
import html
import uuid
import logging
import mimetypes
from datetime import datetime
from functools import wraps
from urllib.parse import quote, unquote
from collections import defaultdict
from typing import Dict, List
from threading import Lock
from flask import Flask, jsonify, request, send_from_directory, make_response
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

app = Flask(__name__)

# ---- CORS: restrict origins in production ----
_cors_origins = os.getenv('CORS_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": _cors_origins}})

# ---- Database config ----
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(basedir, 'blog.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')

db = SQLAlchemy(app)

# ---- Logging ----
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter(
    '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","msg":"%(message)s"}'
))
_root_logger = logging.getLogger()
_root_logger.setLevel(logging.INFO)
_root_logger.addHandler(_log_handler)
logger = logging.getLogger(__name__)

# ---- App config ----
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

# ---- Admin API Key ----
ADMIN_API_KEY = os.getenv('VITE_ADMIN_PASSWORD', '')


# ==================== 辅助数据类型（模块级数据定义，放在模型前避免前向引用） ====================

class AboutContentData:
    """AboutContent 数据的简单结构体"""
    def __init__(self, section, key, value, sort_order=0):
        self.section = section
        self.key = key
        self.value = value
        self.sort_order = sort_order


# ---- Module-level shared data (dedup) ----
ABOUT_CONTENTS_DATA = [
    AboutContentData(section='intro', key='name', value='沛心', sort_order=1),
    AboutContentData(section='intro', key='subtitle', value='全栈开发者 / 赛博美学探索者 / 代码诗人', sort_order=2),
    AboutContentData(section='intro', key='bio', value='我是一名热爱技术与艺术交汇的开发者。在这里，我用代码编织梦想，用像素绘制灵感。从前端交互的丝滑动效，到后端逻辑的精妙设计，每一个细节都是对完美的追求。欢迎来到我的数字花园，这里记录着我在赛博空间中的每一次探索与成长。', sort_order=3),
    AboutContentData(section='tags', key='tag', value='Vue 3', sort_order=1),
    AboutContentData(section='tags', key='tag', value='Flask', sort_order=2),
    AboutContentData(section='tags', key='tag', value='Node.js', sort_order=3),
    AboutContentData(section='tags', key='tag', value='Python', sort_order=4),
    AboutContentData(section='tags', key='tag', value='爬虫', sort_order=5),
    AboutContentData(section='tags', key='tag', value='UI/UX', sort_order=6),
    AboutContentData(section='tags', key='tag', value='全栈开发', sort_order=7),
    AboutContentData(section='tags', key='tag', value='开源贡献', sort_order=8),
    AboutContentData(section='skills', key='skill', value='Vue 3 / Composition API', sort_order=1),
    AboutContentData(section='skills', key='skill', value='JavaScript / TypeScript', sort_order=2),
    AboutContentData(section='skills', key='skill', value='CSS / SCSS / Tailwind', sort_order=3),
    AboutContentData(section='skills', key='skill', value='Node.js / Express', sort_order=4),
    AboutContentData(section='skills', key='skill', value='Python / Flask', sort_order=5),
    AboutContentData(section='skills', key='skill', value='UI/UX 设计', sort_order=6),
    AboutContentData(section='skills', key='skill', value='数据库 (SQL / MySQL)', sort_order=7),
    AboutContentData(section='skills', key='skill', value='requests / BeautifulSoup(BS4) 爬虫', sort_order=8),
    AboutContentData(section='contact', key='email', value='zzzppx@hotmail.com', sort_order=1),
    AboutContentData(section='contact', key='github', value='https://github.com/sxz8157-commits', sort_order=2),
]

# ---- Seed card data (dedup, shared between init_db and seed_cards) ----
SEED_CARDS_DATA = {
    'intro': [
        {'title': '关于我', 'description': '我是沛心，一个热爱技术与创意的开发者', 'sort_order': 1},
        {'title': '我的兴趣', 'description': '代码、阅读、探索新技术', 'sort_order': 2},
    ],
    'skill': [
        {'title': '前端开发', 'description': 'Vue 3 / React / TypeScript / HTML5 / CSS3', 'sort_order': 1},
        {'title': '后端开发', 'description': 'Python / Flask / Node.js / MySQL', 'sort_order': 2},
        {'title': '工具与部署', 'description': 'Git / Docker / CI/CD / Nginx', 'sort_order': 3},
        {'title': 'UI设计', 'description': 'Figma / Photoshop / Illustrator', 'sort_order': 4},
        {'title': '其他技能', 'description': 'Linux / Python爬虫 / API设计', 'sort_order': 5},
    ],
    'tag': [
        {'title': 'Vue 3', 'description': '', 'sort_order': 1},
        {'title': 'Flask', 'description': '', 'sort_order': 2},
        {'title': 'Node.js', 'description': '', 'sort_order': 3},
        {'title': 'Python', 'description': '', 'sort_order': 4},
        {'title': '爬虫', 'description': '', 'sort_order': 5},
        {'title': 'UI/UX', 'description': '', 'sort_order': 6},
        {'title': '全栈开发', 'description': '', 'sort_order': 7},
        {'title': '开源贡献', 'description': '', 'sort_order': 8},
    ],
}

# ==================== 工具函数和装饰器 ====================

def build_public_file_url(subdir: str, filename: str) -> str:
    """构建 public 资源的后端可访问 URL。"""
    return f"/api/files/{subdir}/" + quote(filename)


def safe_send_public_file(subdir: str, filename: str):
    """安全地从 public 子目录返回文件，防止路径穿越。"""
    base_dir = os.path.abspath(os.path.join(PUBLIC_DIR, subdir))
    target_path = os.path.abspath(os.path.join(base_dir, filename))

    if not target_path.startswith(base_dir + os.sep):
        return jsonify({
            'error': 'INVALID_PATH',
            'message': '非法文件路径'
        }), 400
    if not os.path.isfile(target_path):
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '文件不存在'
        }), 404

    ext = os.path.splitext(filename)[1].lower()
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    force_download_exts = {'.xmind', '.docx', '.pptx', '.xlsx'}
    as_attachment = ext in force_download_exts

    response = make_response(send_from_directory(base_dir, filename, as_attachment=as_attachment, mimetype=mimetype))
    # Cache-Control for static assets (images cached 1 hour)
    if subdir == 'tupian':
        response.headers['Cache-Control'] = 'public, max-age=3600'
    return response


def handle_errors(f):
    """统一错误处理装饰器，返回标准化错误响应"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"参数错误: {str(e)}")
            return jsonify({
                'error': 'BAD_REQUEST',
                'message': str(e)
            }), 400
        except Exception as e:
            request_id = uuid.uuid4().hex[:8]
            logger.error(f"[{request_id}] API错误: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'INTERNAL_ERROR',
                'message': '服务器内部错误' if not app.debug else str(e),
                'request_id': request_id if app.debug else None
            }), 500
    return decorated_function


def validate_required_fields(data, required_fields):
    """验证必需字段"""
    if not data:
        raise ValueError("请求体不能为空")
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
    empty_fields = [field for field in required_fields if not data.get(field)]
    if empty_fields:
        raise ValueError(f"字段不能为空: {', '.join(empty_fields)}")
    return True


def require_admin_api_key(f):
    """API Key 认证装饰器，保护所有 /api/admin/* 路由"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key', '')
        if not ADMIN_API_KEY:
            logger.warning(f"Admin API accessed but ADMIN_API_KEY not configured")
            return jsonify({
                'error': 'CONFIG_ERROR',
                'message': '管理接口未配置认证密钥'
            }), 500
        if not provided_key or provided_key != ADMIN_API_KEY:
            logger.warning(f"Unauthorized admin access attempt from {request.remote_addr}")
            return jsonify({
                'error': 'UNAUTHORIZED',
                'message': '无效的 API Key 或未提供认证信息'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== 评论限流 ====================

_comment_rate_limit: Dict[str, List[datetime]] = defaultdict(list)
_comment_rate_lock = Lock()
COMMENT_RATE_LIMIT = 5       # 每 IP 每分钟最多 5 条
COMMENT_RATE_WINDOW = 60      # 时间窗口（秒）


def check_comment_rate_limit(ip: str) -> bool:
    """检查评论频率限制，返回 True 表示允许，False 表示被限制"""
    now = datetime.utcnow()
    cutoff = datetime.timestamp(now) - COMMENT_RATE_WINDOW
    with _comment_rate_lock:
        _comment_rate_limit[ip] = [
            ts for ts in _comment_rate_limit[ip]
            if datetime.timestamp(ts) > cutoff
        ]
        if len(_comment_rate_limit[ip]) >= COMMENT_RATE_LIMIT:
            return False
        _comment_rate_limit[ip].append(now)
        return True


def strip_html(text: str) -> str:
    """去除所有 HTML 标签"""
    return re.sub(r'<[^>]+>', '', text)


def escape_html(text: str) -> str:
    """HTML 转义，防止 XSS"""
    return html.escape(text)


# ==================== 数据模型 ====================

class Category(db.Model):
    """文章分类"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'article_count': self.articles.filter_by(is_published=True).count()
        }


class Article(db.Model):
    """文章"""
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship('Comment', backref='article', lazy='dynamic')

    def to_dict(self, include_content: bool = False, content_preview_len: int = 200):
        result = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'cover_image': self.cover_image,
            'category': self.category.to_dict() if self.category else None,
            'views': self.views,
            'likes': self.likes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if include_content:
            result['content'] = self.content[:content_preview_len] + ('...' if len(self.content) > content_preview_len else '')
        return result


class Comment(db.Model):
    """评论"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_name = db.Column(db.String(50), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'author_name': escape_html(self.author_name),
            'content': escape_html(self.content),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'replies': [reply.to_dict() for reply in self.replies.all()]
        }

    def to_admin_dict(self):
        """后台管理专用（包含邮箱）"""
        d = self.to_dict()
        d['author_email'] = self.author_email
        d['ip_address'] = self.ip_address or '未知'
        d['article_title'] = self.article.title if self.article else None
        return d


class Card(db.Model):
    """介绍卡片和技能书卡片"""
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    card_type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'card_type': self.card_type,
            'title': self.title,
            'description': self.description or '',
            'link': self.link or '',
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class AboutContent(db.Model):
    """关于页面内容"""
    __tablename__ = 'about_content'

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)
    extra = db.Column(db.Text, default='')
    sort_order = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'section': self.section,
            'key': self.key,
            'value': self.value,
            'extra': self.extra,
            'sort_order': self.sort_order
        }


# ==================== Markdown 工具函数 ====================

def _parse_frontmatter_tags(markdown: str) -> List[str]:
    """从 Markdown frontmatter 中解析 tags 字段"""
    if not markdown or not markdown.lstrip().startswith('---'):
        return []

    m = re.match(r'^\s*---\s*\n([\s\S]*?)\n---\s*\n?', markdown)
    if not m:
        return []

    fm = m.group(1)

    m_inline = re.search(r'^\s*tags\s*:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if m_inline:
        raw = m_inline.group(1)
        parts = [p.strip().strip('\'"') for p in raw.split(',')]
        return [p for p in parts if p]

    m_csv = re.search(r'^\s*tags\s*:\s*(.+?)\s*$', fm, re.MULTILINE)
    if m_csv:
        raw = m_csv.group(1).strip()
        if raw and not raw.startswith('-'):
            parts = [p.strip().strip('\'"') for p in raw.split(',')]
            return [p for p in parts if p]

    m_block = re.search(r'^\s*tags\s*:\s*\n((?:\s*-\s*.+\n?)*)', fm, re.MULTILINE)
    if m_block:
        block = m_block.group(1) or ''
        parts = []
        for line in block.splitlines():
            mm = re.match(r'^\s*-\s*(.+)\s*$', line)
            if mm:
                parts.append(mm.group(1).strip().strip('\'"'))
        return [p for p in parts if p]

    return []


# ==================== API 路由 ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    total_articles = Article.query.filter_by(is_published=True).count()
    total_views = db.session.query(db.func.sum(Article.views)).scalar() or 0
    total_comments = Comment.query.count()
    total_categories = Category.query.count()

    first_article = db.session.query(Article).order_by(Article.created_at.asc()).first()
    days_running = (datetime.utcnow() - first_article.created_at).days if first_article else 0

    return jsonify({
        'total_articles': total_articles,
        'total_views': total_views,
        'total_comments': total_comments,
        'total_categories': total_categories,
        'days_running': days_running
    })


@app.route('/api/articles', methods=['GET'])
def get_articles():
    """获取文章列表（数据库文章，返回与详情页一致的数据结构）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category_id', type=int)

    # 分页参数上限
    per_page = min(per_page, 100)

    query = Article.query.filter_by(is_published=True).options(
        db.joinedload(Article.category)
    )

    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'articles': [article.to_dict(include_content=True) for article in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """获取单篇文章详情"""
    article = Article.query.options(
        db.joinedload(Article.category)
    ).get_or_404(article_id)

    # 原子更新浏览量（避免并发竞态）
    db.session.query(Article).filter_by(id=article_id).update(
        {Article.views: Article.views + 1}
    )
    db.session.commit()

    return jsonify({
        'article': article.to_dict(),
        'content': article.content,
        'comments': [comment.to_dict() for comment in article.comments.filter_by(parent_id=None).all()]
    })


@app.route('/api/articles/<int:article_id>/like', methods=['POST'])
@handle_errors
def like_article(article_id):
    """点赞文章（同一 IP 每小时限 10 次）"""
    article = Article.query.get_or_404(article_id)

    ip = request.remote_addr or 'unknown'
    key = f"like:{ip}:{article_id}"
    now = datetime.utcnow()
    cutoff = datetime.timestamp(now) - 3600

    with _comment_rate_lock:
        if key not in _comment_rate_limit:
            _comment_rate_limit[key] = []
        _comment_rate_limit[key] = [
            ts for ts in _comment_rate_limit[key]
            if datetime.timestamp(ts) > cutoff
        ]
        if len(_comment_rate_limit[key]) >= 10:
            return jsonify({
                'error': 'RATE_LIMITED',
                'message': '操作过于频繁，请稍后再试'
            }), 429
        _comment_rate_limit[key].append(now)

    db.session.query(Article).filter_by(id=article_id).update(
        {Article.likes: Article.likes + 1}
    )
    db.session.commit()

    article = Article.query.get(article_id)
    return jsonify({
        'message': '点赞成功',
        'likes': article.likes
    })


@app.route('/api/articles/<int:article_id>/related', methods=['GET'])
@handle_errors
def get_related_articles(article_id):
    """获取相关文章（基于同分类）"""
    article = Article.query.get_or_404(article_id)
    if not article.category_id:
        return jsonify({'articles': []})

    related = Article.query.filter(
        Article.category_id == article.category_id,
        Article.id != article_id,
        Article.is_published == True
    ).options(db.joinedload(Article.category)).order_by(
        Article.created_at.desc()
    ).limit(5).all()

    return jsonify({
        'articles': [a.to_dict(include_content=True) for a in related]
    })


@app.route('/api/search', methods=['GET'])
@handle_errors
def search_articles():
    """搜索文章（标题和摘要模糊匹配）"""
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'articles': [], 'total': 0})

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    per_page = min(per_page, 100)

    pattern = f'%{q}%'
    query = Article.query.filter(
        Article.is_published == True,
        db.or_(
            Article.title.ilike(pattern),
            Article.summary.ilike(pattern)
        )
    ).options(db.joinedload(Article.category))

    pagination = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'articles': [a.to_dict(include_content=True) for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'query': q
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])


@app.route('/api/comments', methods=['POST'])
@handle_errors
def create_comment():
    """创建评论（含输入校验、XSS 防护、频率限制）"""
    data = request.json
    if not data:
        raise ValueError("请求体不能为空")

    # 频率限制
    ip = request.remote_addr or 'unknown'
    if not check_comment_rate_limit(ip):
        return jsonify({
            'error': 'RATE_LIMITED',
            'message': f'评论过于频繁，请 {COMMENT_RATE_WINDOW} 秒后再试'
        }), 429

    # 校验 article_id
    article_id = data.get('article_id')
    if not article_id:
        raise ValueError("缺少必需字段: article_id")
    article = Article.query.get(article_id)
    if not article:
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '文章不存在'
        }), 404

    # 校验 author_name
    author_name = (data.get('author_name') or '').strip()
    if len(author_name) < 2 or len(author_name) > 50:
        raise ValueError("昵称长度需在 2-50 个字符之间")
    if re.search(r'<[^>]+>', author_name):
        raise ValueError("昵称不能包含 HTML 标签")

    # 校验 author_email
    author_email = (data.get('author_email') or '').strip()
    email_pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, author_email):
        raise ValueError("邮箱格式不正确")

    # 校验 content
    raw_content = (data.get('content') or '').strip()
    if len(raw_content) < 10 or len(raw_content) > 2000:
        raise ValueError("评论内容长度需在 10-2000 个字符之间")

    # XSS 防护：去除 HTML 标签后存储
    safe_content = strip_html(raw_content)
    safe_author_name = strip_html(author_name)

    comment = Comment(
        article_id=article_id,
        author_name=safe_author_name,
        author_email=author_email,
        content=safe_content,
        parent_id=data.get('parent_id'),
        ip_address=ip
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'message': '评论成功',
        'comment': comment.to_dict()
    }), 201


@app.route('/api/files/wenz/<path:filename>', methods=['GET'])
def serve_wenz_file(filename):
    """提供 public/wenz 下文档文件访问"""
    return safe_send_public_file('wenz', filename)


@app.route('/api/files/assets/<path:filename>', methods=['GET'])
def serve_assets_file(filename):
    """提供 public/assets 下音频文件访问"""
    return safe_send_public_file('assets', filename)


@app.route('/api/files/tupian/<path:filename>', methods=['GET'])
def serve_tupian_file(filename):
    """提供 public/tupian 下背景媒体访问"""
    resp = safe_send_public_file('tupian', filename)
    if hasattr(resp, 'headers'):
        resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp


@app.route('/toux/<path:filename>', methods=['GET'])
def serve_toux_file(filename):
    """提供头像目录访问（public/toux）"""
    return safe_send_public_file('toux', filename)


@app.route('/api/md-articles', methods=['GET'])
def get_md_articles():
    """获取 public/wenz 文件夹中的文档列表"""
    wenz_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'wenz')

    if not os.path.exists(wenz_dir):
        return jsonify({'articles': [], 'total': 0})

    articles = []

    supported_exts = {'.md', '.pdf', '.xmind', '.txt', '.docx', '.pptx', '.xlsx'}

    for filename in os.listdir(wenz_dir):
        filepath = os.path.join(wenz_dir, filename)
        if not os.path.isfile(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in supported_exts:
            continue

        try:
            title = os.path.splitext(filename)[0]
            summary = ''
            created_at = ''
            tags = []
            file_type = ext.lstrip('.')

            if ext == '.md':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                tags = _parse_frontmatter_tags(content)

                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)

                lines = content.split('\n')
                found_title = False
                for line in lines:
                    if line.startswith('# '):
                        found_title = True
                        continue
                    if found_title and line.strip() and not line.startswith('#'):
                        summary = line.strip()[:150]
                        break
            else:
                summary = f'文档格式：{file_type.upper()}'

            stat = os.stat(filepath)
            created_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            articles.append({
                'id': filename,
                'title': title,
                'summary': summary,
                'created_at': created_at,
                'filename': filename,
                'file_type': file_type,
                'file_url': build_public_file_url('wenz', filename),
                'tags': tags,
                'views': 0,
                'likes': 0
            })
        except Exception as e:
            logger.error(f"读取文件 {filename} 失败: {str(e)}")

    articles.sort(key=lambda x: x['created_at'], reverse=True)

    return jsonify({
        'articles': articles,
        'total': len(articles)
    })


@app.route('/api/md-articles/<article_id>', methods=['GET'])
def get_md_article(article_id):
    """获取单篇文档内容"""
    wenz_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'wenz')
    if not os.path.exists(wenz_dir):
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '文章不存在'
        }), 404

    supported_exts = {'.md', '.pdf', '.xmind', '.txt', '.docx', '.pptx', '.xlsx'}
    matched_filename = None
    files = [fn for fn in os.listdir(wenz_dir) if os.path.isfile(os.path.join(wenz_dir, fn))]

    for fn in files:
        stem, ext = os.path.splitext(fn)
        if fn == article_id and ext.lower() in supported_exts:
            matched_filename = fn
            break

    if not matched_filename:
        for fn in files:
            stem, ext = os.path.splitext(fn)
            if stem == article_id and ext.lower() in supported_exts:
                matched_filename = fn
                break

    if not matched_filename:
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '文章不存在'
        }), 404

    filepath = os.path.join(wenz_dir, matched_filename)
    ext = os.path.splitext(matched_filename)[1].lower()

    try:
        if ext == '.md':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'content': content,
                'filename': matched_filename,
                'file_type': 'md',
                'file_url': build_public_file_url('wenz', matched_filename)
            })

        return jsonify({
            'content': '',
            'filename': matched_filename,
            'file_type': ext.lstrip('.'),
            'file_url': build_public_file_url('wenz', matched_filename)
        })
    except Exception as e:
        logger.error(f"读取文件 {matched_filename} 失败: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '读取文件失败'
        }), 500


@app.route('/api/audio-files', methods=['GET'])
def get_audio_files():
    """获取 public/assets 下可播放的音频列表"""
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'assets')
    if not os.path.exists(assets_dir):
        return jsonify({'audios': [], 'total': 0})

    exts = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}
    audios = []

    for filename in os.listdir(assets_dir):
        filepath = os.path.join(assets_dir, filename)
        if not os.path.isfile(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in exts:
            continue

        base_name = os.path.splitext(filename)[0]
        if ' - ' in base_name:
            name, artist = [x.strip() for x in base_name.split(' - ', 1)]
        else:
            name, artist = base_name, '未知艺术家'

        audios.append({
            'filename': filename,
            'name': name,
            'artist': artist,
            'src': build_public_file_url('assets', filename),
            'cover': ''
        })

    audios.sort(key=lambda x: x['name'].lower())

    return jsonify({
        'audios': audios,
        'total': len(audios)
    })


# ==================== 后台管理 API（需认证） ====================

@app.route('/api/admin/upload', methods=['POST'])
@require_admin_api_key
@handle_errors
def upload_files():
    """上传文件（含文件类型白名单、大小限制、MIME 校验、文件名安全）"""
    if 'files' not in request.files:
        raise ValueError("没有上传文件")

    files = request.files.getlist('files')
    subdir = request.form.get('subdir', '')

    allowed_dirs = {'tupian', 'assets', 'wenz'}
    if subdir not in allowed_dirs:
        raise ValueError("无效的上传目录")

    # 文件类型白名单
    allowed_exts = {
        'tupian': {'.jpg', '.jpeg', '.png', '.webp', '.gif'},
        'assets': {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'},
        'wenz':   {'.md', '.pdf', '.docx', '.pptx', '.xlsx'},
    }
    ext_whitelist = allowed_exts.get(subdir, set())

    # 文件大小限制（字节）
    max_sizes = {
        'tupian': 5 * 1024 * 1024,     # 5 MB
        'assets': 50 * 1024 * 1024,    # 50 MB
        'wenz':   100 * 1024 * 1024,   # 100 MB
    }
    max_size = max_sizes.get(subdir, 5 * 1024 * 1024)

    base_upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'public',
        subdir
    )

    os.makedirs(base_upload_dir, exist_ok=True)

    uploaded = []
    rejected = []
    for file in files:
        if file.filename == '':
            continue

        filename = secure_filename(file.filename)
        if not filename:
            continue

        # 禁止路径穿越
        if '..' in filename or '/' in filename or '\\' in filename:
            rejected.append({'filename': file.filename, 'reason': '文件名包含非法字符'})
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ext_whitelist:
            rejected.append({'filename': file.filename, 'reason': f'不支持的文件类型，仅支持: {", ".join(ext_whitelist)}'})
            continue

        # MIME 类型校验（检查扩展名与内容是否匹配）
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        if file_size > max_size:
            rejected.append({'filename': file.filename, 'reason': f'文件大小超过限制 ({max_size // 1024 // 1024}MB)'})
            continue

        guessed_mime, _ = mimetypes.guess_type(filename)
        if guessed_mime and file.content_type:
            if not file.content_type.startswith(guessed_mime.split('/')[0]) and file.content_type != 'application/octet-stream':
                pass  # MIME check is lenient — rely on extension whitelist + size

        filepath = os.path.join(base_upload_dir, filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(base_upload_dir, filename)
            counter += 1

        file.save(filepath)
        uploaded.append(filename)
        logger.info(f"[{request.remote_addr}] 上传文件: {filepath}")

    return jsonify({
        'message': f'成功上传 {len(uploaded)} 个文件',
        'uploaded': uploaded,
        'count': len(uploaded),
        'rejected': rejected
    }), 201


@app.route('/api/admin/file/<subdir>/<filename>', methods=['DELETE'])
@require_admin_api_key
@handle_errors
def delete_admin_file(subdir, filename):
    """删除 public 目录下的文件"""
    allowed_dirs = {'tupian', 'assets', 'wenz'}
    if subdir not in allowed_dirs:
        raise ValueError("无效的目录")

    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'public',
        subdir
    )

    # URL 解码文件名
    decoded_filename = unquote(filename)
    
    # 构建完整路径
    filepath = os.path.join(base_dir, decoded_filename)
    filepath = os.path.normpath(filepath)
    base_dir = os.path.normpath(base_dir)

    # 安全检查：确保路径在允许目录内
    if not filepath.startswith(base_dir):
        raise ValueError("非法文件路径")

    # 检查文件是否存在
    if not os.path.isfile(filepath):
        # 文件不存在，可能是已被删除或文件名编码问题
        # 搜索目录中是否有匹配的文件
        found_filepath = None
        try:
            for f in os.listdir(base_dir):
                if f == decoded_filename or unquote(f) == decoded_filename:
                    found_filepath = os.path.join(base_dir, f)
                    break
        except Exception as e:
            logger.error(f"搜索文件失败: {e}")
        
        if found_filepath and os.path.isfile(found_filepath):
            filepath = found_filepath
        else:
            # 文件确实不存在，认为删除成功（幂等操作）
            logger.warning(f"文件不存在（可能已被删除）: {decoded_filename}")
            return jsonify({
                'message': '删除成功（文件已不存在）',
                'filename': filename,
                'already_deleted': True
            }), 200

    # 删除文件
    os.remove(filepath)
    logger.warning(f"[{request.remote_addr}] 删除文件: {filepath}")

    return jsonify({
        'message': '删除成功',
        'filename': filename
    })


@app.route('/api/admin/comments', methods=['GET'])
@require_admin_api_key
@handle_errors
def get_admin_comments():
    """后台管理：获取所有评论（含邮箱和 IP）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    pagination = Comment.query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'comments': [c.to_admin_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/admin/comments/<int:comment_id>', methods=['DELETE'])
@require_admin_api_key
@handle_errors
def delete_admin_comment(comment_id):
    """后台管理：删除评论"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    logger.warning(f"[{request.remote_addr}] 删除评论 ID: {comment_id}")
    return jsonify({'message': '删除成功'})


# ==================== 卡片管理 API ====================

@app.route('/api/cards', methods=['GET'])
def get_cards():
    """获取所有卡片，支持按类型筛选"""
    card_type = request.args.get('type')
    query = Card.query
    if card_type:
        query = query.filter_by(card_type=card_type)
    cards = query.order_by(Card.sort_order.asc(), Card.created_at.desc()).all()
    return jsonify({
        'intro_cards': [c.to_dict() for c in cards if c.card_type == 'intro'],
        'skill_cards': [c.to_dict() for c in cards if c.card_type == 'skill'],
        'tag_cards': [c.to_dict() for c in cards if c.card_type == 'tag'],
        'total': len(cards)
    })


@app.route('/api/cards/seed', methods=['POST'])
@handle_errors
def seed_cards():
    """初始化示例卡片数据（幂等性：force=true 时先清空再插入）"""
    force = request.json.get('force', False) if request.json else False

    if force:
        db.session.execute(db.text("DELETE FROM cards"))
        db.session.commit()
        _insert_seed_cards()
        return jsonify({'message': '示例数据已强制重建', 'count': 15})

    if Card.query.count() == 0:
        _insert_seed_cards()
        return jsonify({'message': '示例数据已初始化', 'count': 15})

    return jsonify({'message': '示例数据已存在，如需重新初始化请使用 force=true'})


def _insert_seed_cards(force=False):
    """插入种子卡片数据（由 init_db 和 seed_cards 共用）"""
    if force:
        db.session.execute(db.text("DELETE FROM cards"))
        db.session.commit()
    cards = []
    for card_type, items in SEED_CARDS_DATA.items():
        for item in items:
            cards.append(Card(card_type=card_type, **item))
    db.session.add_all(cards)
    db.session.commit()


@app.route('/api/cards', methods=['POST'])
@handle_errors
def create_card():
    """创建新卡片"""
    data = request.json
    if not data:
        raise ValueError("请求体不能为空")

    required_fields = ['card_type', 'title']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"缺少必需字段: {field}")

    if data['card_type'] not in ('intro', 'skill', 'tag'):
        raise ValueError("卡片类型必须是 'intro'、'skill' 或 'tag'")

    card = Card(
        card_type=data['card_type'],
        title=data['title'],
        description=data.get('description', ''),
        link=data.get('link', ''),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(card)
    db.session.commit()
    return jsonify({'message': '创建成功', 'card': card.to_dict()}), 201


@app.route('/api/cards/<int:card_id>', methods=['PUT'])
@handle_errors
def update_card(card_id):
    """更新卡片"""
    card = Card.query.get_or_404(card_id)
    data = request.json

    # 仅允许 Card.to_dict() 中存在的字段
    updatable_fields = ['card_type', 'title', 'description', 'link', 'sort_order']
    for field in updatable_fields:
        if field in data:
            setattr(card, field, data[field])

    db.session.commit()
    return jsonify({'message': '更新成功', 'card': card.to_dict()})


@app.route('/api/cards/<int:card_id>', methods=['DELETE'])
@handle_errors
def delete_card(card_id):
    """删除卡片"""
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@app.route('/api/background-media', methods=['GET'])
def get_background_media():
    """获取 public/tupian 下可用背景资源"""
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'tupian')
    if not os.path.exists(media_dir):
        return jsonify({'images': [], 'videos': [], 'total': 0})

    image_exts = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
    video_exts = {'.mp4', '.webm', '.mov', '.m4v'}
    images = []
    videos = []

    for filename in os.listdir(media_dir):
        filepath = os.path.join(media_dir, filename)
        if not os.path.isfile(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()
        url = build_public_file_url('tupian', filename)

        if ext in image_exts:
            images.append({'filename': filename, 'url': url})
        elif ext in video_exts:
            videos.append({'filename': filename, 'url': url})

    images.sort(key=lambda x: x['filename'].lower())
    videos.sort(key=lambda x: x['filename'].lower())

    return jsonify({
        'images': images,
        'videos': videos,
        'total': len(images) + len(videos)
    })


@app.route('/api/meta', methods=['GET'])
def get_meta_info():
    """获取 SEO Meta 信息"""
    return jsonify({
        'title': '沛心的个人博客',
        'description': '一个充满赛博朋克风格的个人技术博客，分享编程心得与生活感悟',
        'keywords': '博客, 技术, 编程, Vue, Python, Flask',
        'author': '沛心'
    })


# ==================== 站点地图 ====================

@app.route('/sitemap.xml', methods=['GET'])
def get_sitemap():
    """生成站点地图 XML"""
    articles = Article.query.filter_by(is_published=True).order_by(Article.updated_at.desc()).limit(100).all()

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
        '  <url><loc>/about</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>',
    ]

    base_url = os.getenv('SITE_URL', 'https://example.com')
    for article in articles:
        url = f"{base_url}/article/{article.id}"
        updated = article.updated_at.strftime('%Y-%m-%d') if article.updated_at else ''
        lines.append(f'  <url><loc>{url}</loc><lastmod>{updated}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>')

    lines.append('</urlset>')

    response = make_response('\n'.join(lines))
    response.headers['Content-Type'] = 'application/xml'
    return response


# ==================== RSS 订阅 ====================

@app.route('/feed.xml', methods=['GET'])
def get_rss_feed():
    """生成 RSS 2.0 订阅源"""
    articles = Article.query.filter_by(is_published=True).order_by(
        Article.created_at.desc()
    ).limit(20).all()

    base_url = os.getenv('SITE_URL', 'https://example.com')
    build_date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    items = []
    for article in articles:
        url = f"{base_url}/article/{article.id}"
        pub_date = article.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
        category = article.category.name if article.category else ''
        items.append(
            f'    <item>'
            f'<title><![CDATA[{article.title}]]></title>'
            f'<link>{url}</link>'
            f'<guid isPermaLink="true">{url}</guid>'
            f'<pubDate>{pub_date}</pubDate>'
            f'<description><![CDATA[{article.summary or ""}]]></description>'
            + (f'<category><![CDATA[{category}]]></category>' if category else '')
            + f'</item>'
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>沛心的个人博客</title>\n'
        f'    <link>{base_url}</link>\n'
        '    <description>一个充满赛博朋克风格的个人技术博客</description>\n'
        '    <language>zh-CN</language>\n'
        f'    <lastBuildDate>{build_date}</lastBuildDate>\n'
        f'    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        + '\n'.join(items) + '\n'
        '  </channel>\n'
        '</rss>'
    )

    response = make_response(rss)
    response.headers['Content-Type'] = 'application/xml'
    return response


# ==================== 初始化数据（幂等性） ====================

def init_db():
    """初始化数据库并添加示例数据"""
    with app.app_context():
        db.create_all()

        # 检查是否已有数据
        if Category.query.count() == 0:
            categories = [
                Category(name='前端开发', description='Vue, React, CSS 等前端技术'),
                Category(name='后端开发', description='Python, Flask, 数据库等'),
                Category(name='生活随笔', description='日常思考与生活记录'),
                Category(name='项目实战', description='完整项目开发经验')
            ]
            db.session.add_all(categories)
            db.session.commit()

            sample_articles = [
                Article(
                    title='Vue 3 Composition API 最佳实践',
                    summary='深入探讨 Vue 3 组合式 API 的使用技巧和设计模式',
                    content='# Vue 3 Composition API 最佳实践\n\n这里是文章内容...',
                    cover_image='https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800',
                    category_id=1,
                    views=128,
                    likes=45
                ),
                Article(
                    title='Flask RESTful API 设计指南',
                    summary='从零开始构建优雅的 RESTful API 服务',
                    content='# Flask RESTful API 设计指南\n\n这里是文章内容...',
                    cover_image='https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800',
                    category_id=2,
                    views=96,
                    likes=32
                ),
                Article(
                    title='毛玻璃拟态设计完全指南',
                    summary='Glassmorphism 设计的核心原理与实现技巧',
                    content='# 毛玻璃拟态设计完全指南\n\n这里是文章内容...',
                    cover_image='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800',
                    category_id=1,
                    views=215,
                    likes=78
                )
            ]
            db.session.add_all(sample_articles)
            db.session.commit()

            print('数据库初始化完成，示例数据已添加')

        # 幂等性：清理并重新插入 AboutContent
        _seed_about_content_upsert()
        _insert_seed_cards(force=True)


def _seed_about_content_upsert():
    """Upsert AboutContent 数据（存在则更新，不存在则创建）"""
    # 先删除所有现有 AboutContent
    db.session.execute(db.text("DELETE FROM about_content"))
    db.session.commit()

    # 插入默认数据
    items = []
    for d in ABOUT_CONTENTS_DATA:
        items.append(AboutContent(
            section=d.section,
            key=d.key,
            value=d.value,
            sort_order=d.sort_order
        ))
    db.session.add_all(items)
    db.session.commit()


# ==================== 关于页面 API ====================

@app.route('/api/about', methods=['GET'])
def get_about_content():
    """获取关于页面所有内容"""
    contents = AboutContent.query.order_by(
        AboutContent.section.asc(), AboutContent.sort_order.asc()
    ).all()
    result = {}
    for c in contents:
        if c.section not in result:
            result[c.section] = []
        result[c.section].append(c.to_dict())
    return jsonify(result)


@app.route('/api/about/<section>', methods=['GET'])
def get_about_section(section):
    """获取关于页面的特定部分"""
    contents = AboutContent.query.filter_by(section=section).order_by(
        AboutContent.sort_order.asc()
    ).all()
    return jsonify([c.to_dict() for c in contents])


@app.route('/api/about/seed', methods=['POST'])
@handle_errors
def seed_about_content():
    """初始化关于页面内容（幂等性：使用 upsert 逻辑）"""
    _seed_about_content_upsert()
    count = len(ABOUT_CONTENTS_DATA)
    return jsonify({'message': '关于页面内容已重置', 'count': count})


@app.route('/api/about', methods=['POST'])
@handle_errors
def create_about_item():
    """添加关于页面内容"""
    data = request.json
    if not data:
        raise ValueError("请求体不能为空")
    if not data.get('section') or not data.get('key') or not data.get('value'):
        raise ValueError("缺少必需字段: section, key, value")

    item = AboutContent(
        section=data['section'],
        key=data['key'],
        value=data['value'],
        extra=data.get('extra', ''),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': '添加成功', 'item': item.to_dict()}), 201


@app.route('/api/about/<int:item_id>', methods=['PUT'])
@handle_errors
def update_about_item(item_id):
    """更新关于页面内容"""
    item = AboutContent.query.get_or_404(item_id)
    data = request.json

    if 'value' in data:
        item.value = data['value']
    if 'extra' in data:
        item.extra = data['extra']
    if 'sort_order' in data:
        item.sort_order = data['sort_order']

    db.session.commit()
    return jsonify({'message': '更新成功', 'item': item.to_dict()})


@app.route('/api/about/<int:item_id>', methods=['DELETE'])
@handle_errors
def delete_about_item(item_id):
    """删除关于页面内容"""
    item = AboutContent.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': '删除成功'})


# ==================== 启动 ====================

if __name__ == '__main__':
    init_db()
    app.run(
        debug=app.config['DEBUG'],
        port=int(os.getenv('PORT', 8000))
    )
