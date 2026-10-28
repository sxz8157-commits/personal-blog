"""复用现有文章和内容表提供后台编辑，不变更数据库结构。"""
import copy
import json
import os
import tempfile

from flask import jsonify, request

try:
    from .security import require_admin, validate_url
    from .page_defaults import PAGE_DEFAULTS
    from .uploads import public_path
except ImportError:
    from security import require_admin, validate_url
    from page_defaults import PAGE_DEFAULTS
    from uploads import public_path


def text_value(data, key, limit=2000, required=False):
    value = data.get(key, '')
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise ValueError(f'{key}必须是{limit}字以内的文本' + ('且不能为空' if required else ''))
    return value


def read_pages(Content):
    pages = copy.deepcopy(PAGE_DEFAULTS)
    for item in Content.query.filter(Content.section.like('page_%')).all():
        page = item.section[5:]
        if page not in pages or item.key not in pages[page]:
            continue
        if item.key == 'timeline':
            try:
                pages[page][item.key] = json.loads(item.value)
            except (ValueError, TypeError):
                # 损坏的数据不覆盖默认文案；写入接口会校验结构。
                import logging
                logging.getLogger(__name__).warning('时间线内容格式错误，记录 ID：%s', item.id)
        else:
            pages[page][item.key] = item.value
    return pages


def register_content_routes(app, db, Article, Category, Comment, Content, handle_errors):
    def admin_article(article):
        return {**article.to_dict(), 'content': article.content, 'is_published': article.is_published, 'category_id': article.category_id}

    def article_payload(data):
        if not isinstance(data, dict):
            raise ValueError('请求体必须是对象')
        title = text_value(data, 'title', 200, required=True).strip()
        content = text_value(data, 'content', 1024 * 1024)
        published = data.get('is_published', False)
        if not isinstance(published, bool):
            raise ValueError('is_published 必须是布尔值')
        if published and not content.strip():
            raise ValueError('发布文章需要填写正文')
        category_id = data.get('category_id')
        if category_id is not None and (type(category_id) is not int or not db.session.get(Category, category_id)):
            raise ValueError('分类不存在')
        return dict(title=title, content=content, summary=text_value(data, 'summary', 5000),
                    cover_image=validate_url(data.get('cover_image', ''), '封面地址'),
                    category_id=category_id, is_published=published)

    @app.route('/api/admin/articles', methods=['GET'])
    @require_admin
    @handle_errors
    def admin_articles():
        page = max(1, request.args.get('page', 1, type=int))
        per_page = max(1, min(100, request.args.get('per_page', 20, type=int)))
        query = Article.query.options(db.joinedload(Article.category)).order_by(Article.updated_at.desc(), Article.id.desc())
        q = request.args.get('q', '').strip()[:200]
        if q:
            query = query.filter(Article.title.contains(q, autoescape=True))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify(articles=[{**a.to_dict(), 'is_published': a.is_published, 'category_id': a.category_id} for a in pagination.items],
                       total=pagination.total, pages=pagination.pages, current_page=page)

    @app.route('/api/admin/articles/<int:article_id>', methods=['GET'])
    @require_admin
    @handle_errors
    def admin_article_detail(article_id):
        return jsonify(article=admin_article(db.get_or_404(Article, article_id)))

    @app.route('/api/admin/articles', methods=['POST'])
    @require_admin
    @handle_errors
    def create_admin_article():
        article = Article(**article_payload(request.get_json(silent=True)))
        db.session.add(article)
        db.session.commit()
        return jsonify(message='文章已保存', article=admin_article(article)), 201

    @app.route('/api/admin/articles/<int:article_id>', methods=['PUT'])
    @require_admin
    @handle_errors
    def update_admin_article(article_id):
        article = db.get_or_404(Article, article_id)
        for key, value in article_payload(request.get_json(silent=True)).items():
            setattr(article, key, value)
        db.session.commit()
        return jsonify(message='文章已保存', article=admin_article(article))

    @app.route('/api/admin/articles/<int:article_id>', methods=['DELETE'])
    @require_admin
    @handle_errors
    def delete_admin_article(article_id):
        article = db.get_or_404(Article, article_id)
        Comment.query.filter_by(article_id=article_id).delete(synchronize_session=False)
        db.session.delete(article)
        db.session.commit()
        return jsonify(message='文章及其评论已删除')

    @app.route('/api/pages', methods=['GET'])
    def get_pages():
        return jsonify(pages=read_pages(Content))

    @app.route('/api/admin/pages/<page>', methods=['PUT'])
    @require_admin
    @handle_errors
    def save_page(page):
        if page not in PAGE_DEFAULTS:
            return jsonify(error='NOT_FOUND', message='页面不存在'), 404
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or set(data) - set(PAGE_DEFAULTS[page]):
            raise ValueError('文案字段不合法')
        values = {}
        for key, value in data.items():
            if key == 'timeline':
                if not isinstance(value, list) or len(value) > 50:
                    raise ValueError('时间线最多 50 项')
                rows = []
                for row in value:
                    if not isinstance(row, dict) or set(row) - {'date', 'title', 'desc'}:
                        raise ValueError('时间线字段不合法')
                    rows.append({k: text_value(row, k, 2000 if k == 'desc' else 200, required=k == 'title') for k in ('date', 'title', 'desc')})
                values[key] = json.dumps(rows, ensure_ascii=False)
            else:
                values[key] = text_value(data, key, 2000, required=key in ('title', 'brand'))
        for key, value in values.items():
            item = Content.query.filter_by(section='page_' + page, key=key).first()
            if item:
                item.value = value
            else:
                db.session.add(Content(section='page_' + page, key=key, value=value))
        db.session.commit()
        return jsonify(message='页面文案已保存', pages=read_pages(Content))

    @app.route('/api/admin/about', methods=['PUT'])
    @require_admin
    @handle_errors
    def save_about():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValueError('请求体必须是对象')
        intro, contact = data.get('intro'), data.get('contact')
        if not isinstance(intro, dict) or not isinstance(contact, dict):
            raise ValueError('简介和联系方式格式错误')
        rows = [('intro', key, text_value(intro, key, required=key == 'name')) for key in ('name', 'subtitle', 'bio')]
        email = text_value(contact, 'email', 120).strip()
        if email and ('@' not in email or any(c.isspace() for c in email)):
            raise ValueError('邮箱格式错误')
        rows.extend([('contact', 'email', email), ('contact', 'github', validate_url(contact.get('github', ''), 'GitHub 地址'))])
        for section, key in [('tags', 'tag'), ('skills', 'skill')]:
            values = data.get(section)
            if not isinstance(values, list) or len(values) > 100:
                raise ValueError(f'{section}必须是最多 100 项的数组')
            for value in values:
                rows.append((section, key, text_value({'value': value}, 'value', 200, required=True).strip()))
        # 校验全部通过后才替换，删除与插入由同一个事务提交。
        Content.query.filter(Content.section.in_(['intro', 'contact', 'tags', 'skills'])).delete(synchronize_session=False)
        for index, (section, key, value) in enumerate(rows):
            db.session.add(Content(section=section, key=key, value=value, sort_order=index))
        db.session.commit()
        return jsonify(message='关于页面已保存')

    @app.route('/api/admin/documents/<filename>', methods=['GET', 'PUT'])
    @require_admin
    @handle_errors
    def edit_document(filename):
        path = public_path(app.config['PUBLIC_DIR'], 'wenz', filename)
        if not path.is_file() or path.suffix.lower() not in ('.md', '.txt'):
            return jsonify(error='NOT_FOUND', message='仅支持编辑现有 Markdown/TXT 文档'), 404
        if path.stat().st_size > 1024 * 1024:
            raise ValueError('在线编辑文档不能超过 1MB')
        if request.method == 'GET':
            return jsonify(filename=filename, content=path.read_text(encoding='utf-8-sig'))
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValueError('请求体必须是对象')
        content = text_value(data, 'content', 1024 * 1024)
        if len(content.encode('utf-8')) > 1024 * 1024:
            raise ValueError('文档不能超过 1MB')
        # 临时文件与原文件同盘，原子替换避免写入失败破坏原文。
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as output:
                temporary = output.name
                output.write(content)
            os.replace(temporary, path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
        return jsonify(message='文档已保存')
