import os
import logging
import mimetypes
from datetime import datetime
from functools import wraps
from urllib.parse import quote
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== 工具函数和装饰器 ====================

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask配置
app.config['JSON_AS_ASCII'] = False  # 支持中文
app.config['JSON_SORT_KEYS'] = False  # 保持JSON键的顺序

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public')


def build_public_file_url(subdir: str, filename: str) -> str:
    """构建 public 资源的后端可访问 URL。"""
    return f"/api/files/{subdir}/" + quote(filename)


def safe_send_public_file(subdir: str, filename: str):
    """安全地从 public 子目录返回文件，防止路径穿越。"""
    base_dir = os.path.abspath(os.path.join(PUBLIC_DIR, subdir))
    target_path = os.path.abspath(os.path.join(base_dir, filename))

    if not target_path.startswith(base_dir + os.sep):
        return jsonify({'error': '非法文件路径'}), 400
    if not os.path.isfile(target_path):
        return jsonify({'error': '文件不存在'}), 404

    ext = os.path.splitext(filename)[1].lower()
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    force_download_exts = {'.xmind', '.docx', '.pptx', '.xlsx'}
    as_attachment = ext in force_download_exts

    return send_from_directory(
        base_dir,
        filename,
        as_attachment=as_attachment,
        mimetype=mimetype
    )

def handle_errors(f):
    """错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API错误: {str(e)}", exc_info=True)
            return jsonify({
                'error': '服务器内部错误',
                'message': str(e) if app.debug else '请稍后重试'
            }), 500
    return decorated_function

def validate_required_fields(data, required_fields):
    """验证必需字段"""
    if not data:
        raise ValueError("请求体不能为空")
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
    
    # 验证字段是否为空
    empty_fields = [field for field in required_fields if not data.get(field)]
    if empty_fields:
        raise ValueError(f"字段不能为空: {', '.join(empty_fields)}")
    
    return True

# ==================== 数据模型 ====================

class Category(db.Model):
    """文章分类"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    articles = db.relationship('Article', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'article_count': len(self.articles)
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
    
    comments = db.relationship('Comment', backref='article', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'cover_image': self.cover_image,
            'category': self.category.to_dict() if self.category else None,
            'views': self.views,
            'likes': self.likes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Comment(db.Model):
    """评论"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'author_name': self.author_name,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'replies': [reply.to_dict() for reply in self.replies]
        }


class Card(db.Model):
    """介绍卡片和技能书卡片"""
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    card_type = db.Column(db.String(20), nullable=False)  # 'intro' 或 'skill'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))  # 外部链接（可选）
    sort_order = db.Column(db.Integer, default=0)  # 排序
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
    section = db.Column(db.String(50), nullable=False)  # intro, tags, skills, contact
    key = db.Column(db.String(100), nullable=False)  # 字段键名
    value = db.Column(db.Text, nullable=False)  # 字段值
    extra = db.Column(db.Text, default='')  # 额外数据（JSON字符串）
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


# ==================== API 路由 ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    total_articles = Article.query.filter_by(is_published=True).count()
    total_views = db.session.query(db.func.sum(Article.views)).scalar() or 0
    total_comments = Comment.query.count()
    total_categories = Category.query.count()
    
    # 计算运行时长（从第一篇文章创建时间开始）
    first_article = Article.query.order_by(Article.created_at.asc()).first()
    if first_article:
        start_date = first_article.created_at
        days_running = (datetime.utcnow() - start_date).days
    else:
        days_running = 0
    
    return jsonify({
        'total_articles': total_articles,
        'total_views': total_views,
        'total_comments': total_comments,
        'total_categories': total_categories,
        'days_running': days_running
    })


@app.route('/api/articles', methods=['GET'])
def get_articles():
    """获取文章列表（支持数据库文章和MD文章）"""
    source = request.args.get('source', 'database')  # 'database' 或 'md'
    
    if source == 'md':
        return get_md_articles()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category_id', type=int)
    
    query = Article.query.filter_by(is_published=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    pagination = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'articles': [article.to_dict() for article in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """获取单篇文章详情"""
    article = Article.query.get_or_404(article_id)
    
    # 增加浏览量
    article.views += 1
    db.session.commit()
    
    return jsonify({
        'article': article.to_dict(),
        'content': article.content,
        'comments': [comment.to_dict() for comment in article.comments if not comment.parent_id]
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])


@app.route('/api/comments', methods=['POST'])
def create_comment():
    """创建评论"""
    data = request.json
    
    comment = Comment(
        article_id=data['article_id'],
        author_name=data['author_name'],
        author_email=data['author_email'],
        content=data['content'],
        parent_id=data.get('parent_id')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({'message': '评论成功', 'comment': comment.to_dict()}), 201


@app.route('/api/files/wenz/<path:filename>', methods=['GET'])
def serve_wenz_file(filename):
    """提供 public/wenz 下文档文件访问。"""
    return safe_send_public_file('wenz', filename)


@app.route('/api/files/assets/<path:filename>', methods=['GET'])
def serve_assets_file(filename):
    """提供 public/assets 下音频文件访问。"""
    return safe_send_public_file('assets', filename)


@app.route('/api/files/tupian/<path:filename>', methods=['GET'])
def serve_tupian_file(filename):
    """提供 public/tupian 下背景媒体访问。"""
    return safe_send_public_file('tupian', filename)


@app.route('/toux/<path:filename>', methods=['GET'])
def serve_toux_file(filename):
    """提供头像目录访问（public/toux）"""
    return safe_send_public_file('toux', filename)


@app.route('/api/md-articles', methods=['GET'])
def get_md_articles():
    """获取 public/wenz 文件夹中的文档列表（md/pdf/xmind/...）"""
    import os
    import re
    
    wenz_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'wenz')
    
    if not os.path.exists(wenz_dir):
        return jsonify({'articles': [], 'total': 0})
    
    articles = []
    
    def parse_frontmatter_tags(markdown: str):
        """
        解析 markdown 顶部的 YAML frontmatter tags.
        支持：
        - tags: [a, b]
        - tags: a, b
        - tags:
            - a
            - b
        """
        if not markdown or not markdown.lstrip().startswith('---'):
            return []

        # 只解析顶部第一段 frontmatter
        m = re.match(r'^\s*---\s*\n([\s\S]*?)\n---\s*\n?', markdown)
        if not m:
            return []

        fm = m.group(1)

        # 1) tags: [a, b]
        m_inline = re.search(r'^\s*tags\s*:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
        if m_inline:
            raw = m_inline.group(1)
            parts = [p.strip().strip('\'"') for p in raw.split(',')]
            return [p for p in parts if p]

        # 2) tags: a, b
        m_csv = re.search(r'^\s*tags\s*:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m_csv:
            raw = m_csv.group(1).strip()
            # 排除 tags: 之后跟着空（可能是 yaml list）
            if raw and not raw.startswith('-'):
                parts = [p.strip().strip('\'"') for p in raw.split(',')]
                return [p for p in parts if p]

        # 3) tags:
        #      - a
        #      - b
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

    supported_exts = {'.md', '.pdf', '.xmind', '.txt', '.docx', '.pptx', '.xlsx'}

    # 扫描支持的文档文件
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

                tags = parse_frontmatter_tags(content)

                # 提取标题（第一个 # 标题）
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)

                # 提取摘要（标题后的第一行非空文本）
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

            # 获取文件修改时间
            stat = os.stat(filepath)
            created_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            articles.append({
                # Use full filename as stable unique id to avoid collisions
                # between files sharing same stem but different extensions.
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
    
    # 按创建时间排序（最新的在前）
    articles.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'articles': articles,
        'total': len(articles)
    })


@app.route('/api/md-articles/<article_id>', methods=['GET'])
def get_md_article(article_id):
    """获取单篇文档内容（md 返回正文，其他格式返回文件链接）"""
    import os
    
    wenz_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'wenz')
    if not os.path.exists(wenz_dir):
        return jsonify({'error': '文章不存在'}), 404

    supported_exts = {'.md', '.pdf', '.xmind', '.txt', '.docx', '.pptx', '.xlsx'}
    matched_filename = None
    files = [fn for fn in os.listdir(wenz_dir) if os.path.isfile(os.path.join(wenz_dir, fn))]

    # 1) exact filename match (new id strategy)
    for fn in files:
        stem, ext = os.path.splitext(fn)
        if fn == article_id and ext.lower() in supported_exts:
            matched_filename = fn
            break

    # 2) fallback for old routes using stem only (backward compatibility)
    if not matched_filename:
        for fn in files:
            stem, ext = os.path.splitext(fn)
            if stem == article_id and ext.lower() in supported_exts:
                matched_filename = fn
                break

    if not matched_filename:
        return jsonify({'error': '文章不存在'}), 404

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
        return jsonify({'error': '读取文件失败'}), 500


@app.route('/api/audio-files', methods=['GET'])
def get_audio_files():
    """获取 public/assets 下可播放的音频列表"""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'assets')
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


# ==================== 后台管理 API ====================

@app.route('/api/admin/upload', methods=['POST'])
@handle_errors
def upload_files():
    """上传文件到 public 目录"""
    from werkzeug.utils import secure_filename

    if 'files' not in request.files:
        raise ValueError("没有上传文件")

    files = request.files.getlist('files')
    subdir = request.form.get('subdir', '')

    allowed_dirs = {'tupian', 'assets', 'wenz'}
    if subdir not in allowed_dirs:
        raise ValueError("无效的上传目录")

    base_upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'public',
        subdir
    )

    os.makedirs(base_upload_dir, exist_ok=True)

    uploaded = []
    for file in files:
        if file.filename == '':
            continue

        filename = secure_filename(file.filename)
        if not filename:
            continue

        filepath = os.path.join(base_upload_dir, filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(base_upload_dir, filename)
            counter += 1

        file.save(filepath)
        uploaded.append(filename)
        logger.info(f"上传文件: {filepath}")

    return jsonify({
        'message': f'成功上传 {len(uploaded)} 个文件',
        'uploaded': uploaded,
        'count': len(uploaded)
    }), 201


@app.route('/api/admin/file/<subdir>/<filename>', methods=['DELETE'])
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

    # URL 解码文件名，处理中文文件名
    from urllib.parse import unquote
    decoded_filename = unquote(filename)
    safe_filename = secure_filename(decoded_filename)

    # 如果 secure_filename 返回空字符串，使用解码后的文件名
    if not safe_filename:
        safe_filename = decoded_filename

    filepath = os.path.abspath(os.path.join(base_dir, safe_filename))

    if not filepath.startswith(base_dir + os.sep):
        raise ValueError("非法文件路径")

    if not os.path.isfile(filepath):
        raise ValueError("文件不存在")

    os.remove(filepath)
    logger.info(f"删除文件: {filepath}")

    return jsonify({
        'message': '删除成功',
        'filename': filename
    })


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
    """初始化示例卡片数据（支持强制重新初始化）"""
    force = request.json.get('force', False) if request.json else False

    if Card.query.count() == 0 or force:
        # 清除现有数据
        Card.query.delete()
        db.session.commit()

        intro_cards = [
            Card(card_type='intro', title='关于我', description='我是沛心，一个热爱技术与创意的开发者', sort_order=1),
            Card(card_type='intro', title='我的兴趣', description='代码、阅读、探索新技术', sort_order=2),
        ]
        skill_cards = [
            Card(card_type='skill', title='前端开发', description='Vue 3 / React / TypeScript / HTML5 / CSS3', sort_order=1),
            Card(card_type='skill', title='后端开发', description='Python / Flask / Node.js / MySQL', sort_order=2),
            Card(card_type='skill', title='工具与部署', description='Git / Docker / CI/CD / Nginx', sort_order=3),
            Card(card_type='skill', title='UI设计', description='Figma / Photoshop / Illustrator', sort_order=4),
            Card(card_type='skill', title='其他技能', description='Linux / Python爬虫 / API设计', sort_order=5),
        ]
        tag_cards = [
            Card(card_type='tag', title='Vue 3', description='', sort_order=1),
            Card(card_type='tag', title='Flask', description='', sort_order=2),
            Card(card_type='tag', title='Node.js', description='', sort_order=3),
            Card(card_type='tag', title='Python', description='', sort_order=4),
            Card(card_type='tag', title='爬虫', description='', sort_order=5),
            Card(card_type='tag', title='UI/UX', description='', sort_order=6),
            Card(card_type='tag', title='全栈开发', description='', sort_order=7),
            Card(card_type='tag', title='开源贡献', description='', sort_order=8),
        ]
        db.session.add_all(intro_cards + skill_cards + tag_cards)
        db.session.commit()
        return jsonify({'message': '示例数据已初始化', 'count': 15})
    return jsonify({'message': '示例数据已存在，如需重新初始化请使用强制模式'})


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
    
    updatable_fields = ['card_type', 'title', 'description', 'icon', 'link', 'color', 'sort_order']
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
    """获取 public/tupian 下可用背景资源（图片/视频）"""
    media_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'tupian')
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


# ==================== 初始化数据 ====================

def init_db():
    """初始化数据库并添加示例数据"""
    with app.app_context():
        db.create_all()
        
        # 检查是否已有数据
        if Category.query.count() == 0:
            # 创建分类
            categories = [
                Category(name='前端开发', description='Vue, React, CSS 等前端技术'),
                Category(name='后端开发', description='Python, Flask, 数据库等'),
                Category(name='生活随笔', description='日常思考与生活记录'),
                Category(name='项目实战', description='完整项目开发经验')
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            # 创建示例文章
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

            # 初始化关于页面内容
            about_contents = [
                AboutContent(section='intro', key='name', value='沛心', sort_order=1),
                AboutContent(section='intro', key='subtitle', value='全栈开发者 / 赛博美学探索者 / 代码诗人', sort_order=2),
                AboutContent(section='intro', key='bio', value='我是一名热爱技术与艺术交汇的开发者。在这里，我用代码编织梦想，用像素绘制灵感。从前端交互的丝滑动效，到后端逻辑的精妙设计，每一个细节都是对完美的追求。欢迎来到我的数字花园，这里记录着我在赛博空间中的每一次探索与成长。', sort_order=3),
                AboutContent(section='tags', key='tag', value='Vue 3', sort_order=1),
                AboutContent(section='tags', key='tag', value='Flask', sort_order=2),
                AboutContent(section='tags', key='tag', value='Node.js', sort_order=3),
                AboutContent(section='tags', key='tag', value='Python', sort_order=4),
                AboutContent(section='tags', key='tag', value='爬虫', sort_order=5),
                AboutContent(section='tags', key='tag', value='UI/UX', sort_order=6),
                AboutContent(section='tags', key='tag', value='全栈开发', sort_order=7),
                AboutContent(section='tags', key='tag', value='开源贡献', sort_order=8),
                AboutContent(section='skills', key='skill', value='Vue 3 / Composition API', sort_order=1),
                AboutContent(section='skills', key='skill', value='JavaScript / TypeScript', sort_order=2),
                AboutContent(section='skills', key='skill', value='CSS / SCSS / Tailwind', sort_order=3),
                AboutContent(section='skills', key='skill', value='Node.js / Express', sort_order=4),
                AboutContent(section='skills', key='skill', value='Python / Flask', sort_order=5),
                AboutContent(section='skills', key='skill', value='UI/UX 设计', sort_order=6),
                AboutContent(section='skills', key='skill', value='数据库 (SQL / MySQL)', sort_order=7),
                AboutContent(section='skills', key='skill', value='requests / BeautifulSoup(BS4) 爬虫', sort_order=8),
                AboutContent(section='contact', key='email', value='zzzppx@hotmail.com', sort_order=1),
                AboutContent(section='contact', key='github', value='https://github.com/sxz8157-commits', sort_order=2),
            ]
            db.session.add_all(about_contents)
            db.session.commit()

            print('✅ 数据库初始化完成，示例数据已添加')

        # 确保关于页面内容存在（独立检查）
        if AboutContent.query.count() == 0:
            about_contents = [
                AboutContent(section='intro', key='name', value='沛心', sort_order=1),
                AboutContent(section='intro', key='subtitle', value='全栈开发者 / 赛博美学探索者 / 代码诗人', sort_order=2),
                AboutContent(section='intro', key='bio', value='我是一名热爱技术与艺术交汇的开发者。在这里，我用代码编织梦想，用像素绘制灵感。从前端交互的丝滑动效，到后端逻辑的精妙设计，每一个细节都是对完美的追求。欢迎来到我的数字花园，这里记录着我在赛博空间中的每一次探索与成长。', sort_order=3),
                AboutContent(section='tags', key='tag', value='Vue 3', sort_order=1),
                AboutContent(section='tags', key='tag', value='Flask', sort_order=2),
                AboutContent(section='tags', key='tag', value='Node.js', sort_order=3),
                AboutContent(section='tags', key='tag', value='Python', sort_order=4),
                AboutContent(section='tags', key='tag', value='爬虫', sort_order=5),
                AboutContent(section='tags', key='tag', value='UI/UX', sort_order=6),
                AboutContent(section='tags', key='tag', value='全栈开发', sort_order=7),
                AboutContent(section='tags', key='tag', value='开源贡献', sort_order=8),
                AboutContent(section='skills', key='skill', value='Vue 3 / Composition API', sort_order=1),
                AboutContent(section='skills', key='skill', value='JavaScript / TypeScript', sort_order=2),
                AboutContent(section='skills', key='skill', value='CSS / SCSS / Tailwind', sort_order=3),
                AboutContent(section='skills', key='skill', value='Node.js / Express', sort_order=4),
                AboutContent(section='skills', key='skill', value='Python / Flask', sort_order=5),
                AboutContent(section='skills', key='skill', value='UI/UX 设计', sort_order=6),
                AboutContent(section='skills', key='skill', value='数据库 (SQL / MySQL)', sort_order=7),
                AboutContent(section='skills', key='skill', value='requests / BeautifulSoup(BS4) 爬虫', sort_order=8),
                AboutContent(section='contact', key='email', value='zzzppx@hotmail.com', sort_order=1),
                AboutContent(section='contact', key='github', value='https://github.com/sxz8157-commits', sort_order=2),
            ]
            db.session.add_all(about_contents)
            db.session.commit()
            print('✅ 关于页面内容已初始化')


# ==================== 关于页面 API ====================

@app.route('/api/about', methods=['GET'])
def get_about_content():
    """获取关于页面所有内容"""
    contents = AboutContent.query.order_by(AboutContent.section.asc(), AboutContent.sort_order.asc()).all()
    result = {}
    for c in contents:
        if c.section not in result:
            result[c.section] = []
        result[c.section].append(c.to_dict())
    return jsonify(result)


@app.route('/api/about/<section>', methods=['GET'])
def get_about_section(section):
    """获取关于页面的特定部分"""
    contents = AboutContent.query.filter_by(section=section).order_by(AboutContent.sort_order.asc()).all()
    return jsonify([c.to_dict() for c in contents])


@app.route('/api/about/seed', methods=['POST'])
@handle_errors
def seed_about_content():
    """初始化关于页面示例内容"""
    if AboutContent.query.count() == 0:
        contents = [
            AboutContent(section='intro', key='name', value='沛心', sort_order=1),
            AboutContent(section='intro', key='subtitle', value='全栈开发者 / 赛博美学探索者 / 代码诗人', sort_order=2),
            AboutContent(section='intro', key='bio', value='我是一名热爱技术与艺术交汇的开发者。在这里，我用代码编织梦想，用像素绘制灵感。从前端交互的丝滑动效，到后端逻辑的精妙设计，每一个细节都是对完美的追求。欢迎来到我的数字花园，这里记录着我在赛博空间中的每一次探索与成长。', sort_order=3),
            AboutContent(section='tags', key='tag', value='Vue 3', sort_order=1),
            AboutContent(section='tags', key='tag', value='Flask', sort_order=2),
            AboutContent(section='tags', key='tag', value='Node.js', sort_order=3),
            AboutContent(section='tags', key='tag', value='Python', sort_order=4),
            AboutContent(section='tags', key='tag', value='爬虫', sort_order=5),
            AboutContent(section='tags', key='tag', value='UI/UX', sort_order=6),
            AboutContent(section='tags', key='tag', value='全栈开发', sort_order=7),
            AboutContent(section='tags', key='tag', value='开源贡献', sort_order=8),
            AboutContent(section='skills', key='skill', value='Vue 3 / Composition API', sort_order=1),
            AboutContent(section='skills', key='skill', value='JavaScript / TypeScript', sort_order=2),
            AboutContent(section='skills', key='skill', value='CSS / SCSS / Tailwind', sort_order=3),
            AboutContent(section='skills', key='skill', value='Node.js / Express', sort_order=4),
            AboutContent(section='skills', key='skill', value='Python / Flask', sort_order=5),
            AboutContent(section='skills', key='skill', value='UI/UX 设计', sort_order=6),
            AboutContent(section='skills', key='skill', value='数据库 (SQL / MySQL)', sort_order=7),
            AboutContent(section='skills', key='skill', value='requests / BeautifulSoup(BS4) 爬虫', sort_order=8),
            AboutContent(section='contact', key='email', value='zzzppx@hotmail.com', sort_order=1),
            AboutContent(section='contact', key='github', value='https://github.com/sxz8157-commits', sort_order=2),
        ]
        db.session.add_all(contents)
        db.session.commit()
        return jsonify({'message': '关于页面内容已初始化', 'count': len(contents)})
    return jsonify({'message': '关于页面内容已存在'})


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


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8000)
